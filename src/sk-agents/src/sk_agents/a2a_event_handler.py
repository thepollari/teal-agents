import asyncio
import json
import logging
from contextlib import nullcontext
from typing import Any

from opentelemetry.propagate import extract
from pydantic import ValidationError
from ska_utils import AppConfig, get_telemetry

from dapr.clients import DaprClient
from dapr.clients.grpc._response import TopicEventResponse
from sk_agents.a2a_types import (
    A2AErrorResponse,
    A2AEventType,
    A2AInvokeEvent,
    A2ANonRecoverableError,
)
from sk_agents.configs import TA_A2A_EVENT_SOURCE_NAME
from sk_agents.ska_types import BaseConfig, BaseHandler
from sk_agents.skagents import handle as skagents_handle
from sk_agents.utils import invoke_response_to_a2a_event


class A2AEventHandler:
    def __init__(self, app_config: AppConfig, config: BaseConfig, root_handler: str):
        self.app_config = app_config
        self.config = config
        self.root_handler = root_handler

        self.client = DaprClient()
        self.close_fn = None

        self.pubsub_name = app_config.get(TA_A2A_EVENT_SOURCE_NAME.env_name)

        self.topic_name = f"{self.config.name}/{self.config.version}"
        self.dead_letter_topic = f"{self.topic_name}_DEAD"

    async def initialize(self) -> None:
        self.close_fn = self.client.subscribe_with_handler(
            pubsub_name=self.pubsub_name,
            topic=self.topic_name,
            handler_fn=self.handle_event,
            dead_letter_topic=self.dead_letter_topic,
        )

    async def shutdown(self) -> None:
        if self.close_fn:
            self.close_fn()
        self.client.close()

    def _publish_task_event(self, event_id: str, event: str):
        self.client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name=f"{self.topic_name}/{event_id}",
            data=event,
            data_content_type="application/json",
        )

    @staticmethod
    def _authorize_task(event: A2AInvokeEvent) -> str:
        # TODO - How to retrieve authorization token?
        #  If the task is not authorized, raise NonRecoverableError
        return "dummy-token"

    async def publish_stream(
        self, event_id: str, handler: BaseHandler, inputs: dict[str, Any]
    ) -> None:
        # noinspection PyTypeChecker
        async for result in handler.invoke_stream(inputs):
            self._publish_task_event(event_id, invoke_response_to_a2a_event(result))

    def _publish_error_event(self, event_id: str, status_code: int, message: str):
        self._publish_task_event(
            event_id,
            invoke_response_to_a2a_event(
                A2AErrorResponse(
                    status_code=status_code,
                    detail=message,
                )
            ),
        )

    def _parse_event_data(self, event) -> dict:
        event_data_raw = event.data()
        try:
            if isinstance(event_data_raw, str):
                event_data = json.loads(event_data_raw)
            else:
                event_data = event_data_raw
            return event_data
        except Exception as e:
            logging.error(f"Error parsing event data: {e}")
            logging.error(f"Event data: {event_data_raw}")
            raise A2ANonRecoverableError("Invalid event data format") from e

    def _parse_invoke_event(self, event_data) -> A2AInvokeEvent:
        try:
            data = A2AInvokeEvent(**event_data)
            return data
        except (ValidationError, TypeError, ValueError) as e:
            event_id = "unknown"
            if "event_id" in event_data:
                event_id = event_data["event_id"]
            elif hasattr(event_data, "event_id"):
                event_id = event_data.event_id
            self._publish_error_event(event_id, 400, f"Invalid event data: {event_data}")
            raise A2ANonRecoverableError(f"Invalid event data: {event_data}") from e

    def _get_handler(self, event_id: str, authorization: str):
        if self.root_handler == "skagents":
            try:
                return skagents_handle(self.config, self.app_config, authorization)
            except Exception as e:
                self._publish_error_event(event_id, 500, str(e))
                raise A2ANonRecoverableError(str(e)) from e
        else:
            self._publish_error_event(
                event_id, 500, f"Unknown apiVersion: {self.config.apiVersion}"
            )
            raise A2ANonRecoverableError(f"Unknown apiVersion: {self.config.apiVersion}")

    def _invoke_stream(self, event_id: str, handler: BaseHandler, inputs: dict[str, Any]):
        try:
            asyncio.run(self.publish_stream(event_id, handler, inputs))
            return TopicEventResponse("success")
        except Exception as e:
            self._publish_error_event(event_id, 500, str(e))
            raise A2ANonRecoverableError(str(e)) from e

    def _invoke(self, event_id: str, handler: BaseHandler, inputs: dict[str, Any]):
        try:
            output = asyncio.run(handler.invoke(inputs=inputs))
            self._publish_task_event(event_id, invoke_response_to_a2a_event(output))
            return TopicEventResponse("success")
        except Exception as e:
            self._publish_error_event(event_id, 500, str(e))
            raise A2ANonRecoverableError(str(e)) from e

    def _invoke_appropriately(
        self,
        event_type: A2AEventType,
        event_id: str,
        handler: BaseHandler,
        inputs: dict[str, Any],
    ):
        if event_type == A2AEventType.INVOKE_STREAM:
            return self._invoke_stream(event_id, handler, inputs)
        elif event_type == A2AEventType.INVOKE:
            return self._invoke(event_id, handler, inputs)
        else:
            self._publish_error_event(event_id, 400, f"Invalid event type{event_type}")
            raise A2ANonRecoverableError(f"Invalid event type{event_type}")

    def handle_event(self, event) -> TopicEventResponse:
        try:
            event_data = self._parse_event_data(event)
            data = self._parse_invoke_event(event_data)

            extensions = event.extensions()

            st = get_telemetry()
            context = extract(extensions)

            with (
                st.tracer.start_as_current_span(
                    f"{self.config.name}-{str(self.config.version)}-invoke",
                    context=context,
                )
                if st.telemetry_enabled()
                else nullcontext()
            ):
                authorization = A2AEventHandler._authorize_task(data)
                handler = self._get_handler(data.event_id, authorization)
                inv_inputs = data.event_data.__dict__

                return self._invoke_appropriately(
                    data.event_type, data.event_id, handler, inv_inputs
                )
        except A2ANonRecoverableError:
            return TopicEventResponse("drop")
        except Exception as e:
            logging.error(f"Unrecoverable exception: {e}")
            logging.error("Message dropped")
            return TopicEventResponse("drop")
