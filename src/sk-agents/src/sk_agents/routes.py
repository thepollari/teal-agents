import logging
from contextlib import nullcontext

from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks.task_store import TaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentProvider, AgentSkill
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import StreamingResponse
from opentelemetry.propagate import extract
from ska_utils import AppConfig, get_telemetry

from sk_agents.a2a import A2AAgentExecutor
from sk_agents.authorization.request_authorizer import RequestAuthorizer
from sk_agents.configs import (
    TA_AGENT_BASE_URL,
    TA_PROVIDER_ORG,
    TA_PROVIDER_URL,
)
from sk_agents.ska_types import (
    BaseConfig,
    BaseHandler,
    InvokeResponse,
    PartialResponse,
)
from sk_agents.skagents import handle as skagents_handle
from sk_agents.skagents.chat_completion_builder import ChatCompletionBuilder
from sk_agents.state import StateManager
from sk_agents.tealagents.models import ResumeRequest, StateResponse, TaskStatus, UserMessage
from sk_agents.tealagents.v1alpha1.agent.handler import TealAgentsV1Alpha1Handler
from sk_agents.utils import docstring_parameter, get_sse_event_for_response

logger = logging.getLogger(__name__)


class Routes:
    @staticmethod
    def get_url(name: str, version: str, app_config: AppConfig) -> str:
        base_url = app_config.get(TA_AGENT_BASE_URL.env_name)
        if not base_url:
            logger.exception("Base URL is not provided in the app config.")
            raise ValueError("Base URL is not provided in the app config.")
        return f"{base_url}/{name}/{version}/a2a"

    @staticmethod
    def get_provider(app_config: AppConfig) -> AgentProvider:
        return AgentProvider(
            organization=app_config.get(TA_PROVIDER_ORG.env_name),
            url=app_config.get(TA_PROVIDER_URL.env_name),
        )

    @staticmethod
    def get_agent_card(config: BaseConfig, app_config: AppConfig) -> AgentCard:
        if config.metadata is None:
            logger.exception("Agent card metadata is not provided in the config.")
            raise ValueError("Agent card metadata is not provided in the config.")

        metadata = config.metadata
        skills = [
            AgentSkill(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                tags=skill.tags,
                examples=skill.examples,
                input_modes=skill.input_modes,
                output_modes=skill.output_modes,
            )
            for skill in metadata.skills
        ]
        return AgentCard(
            name=config.name,
            version=str(config.version),
            description=metadata.description,
            url=Routes.get_url(config.name, config.version, app_config),
            provider=Routes.get_provider(app_config),
            documentation_url=config.metadata.documentation_url,
            capabilities=AgentCapabilities(
                streaming=True, push_notifications=False, state_transition_history=True
            ),
            default_input_modes=["text"],
            default_output_modes=["text"],
            skills=skills,
        )

    @staticmethod
    def get_request_handler(
        config: BaseConfig,
        app_config: AppConfig,
        chat_completion_builder: ChatCompletionBuilder,
        state_manager: StateManager,
        task_store: TaskStore,
    ) -> DefaultRequestHandler:
        return DefaultRequestHandler(
            agent_executor=A2AAgentExecutor(
                config, app_config, chat_completion_builder, state_manager
            ),
            task_store=task_store,
        )

    @staticmethod
    def get_a2a_routes(
        name: str,
        version: str,
        description: str,
        config: BaseConfig,
        app_config: AppConfig,
        chat_completion_builder: ChatCompletionBuilder,
        task_store: TaskStore,
        state_manager: StateManager,
    ) -> APIRouter:
        a2a_app = A2AStarletteApplication(
            agent_card=Routes.get_agent_card(config, app_config),
            http_handler=Routes.get_request_handler(
                config, app_config, chat_completion_builder, state_manager, task_store
            ),
        )
        a2a_router = APIRouter()

        @a2a_router.post("")
        @docstring_parameter(description)
        async def handle_a2a(request: Request):
            """
            {0}

            Agent-to-Agent Invocation
            """
            return await a2a_app._handle_requests(request)

        @a2a_router.get("/.well-known/agent.json")
        @docstring_parameter(f"{name}:{version} - {description}")
        async def handle_get_agent_card(request: Request):
            """
            Retrieve agent card for {0}
            """
            return await a2a_app._handle_get_agent_card(request)

        return a2a_router

    @staticmethod
    def get_rest_routes(
        name: str,
        version: str,
        description: str,
        root_handler_name: str,
        config: BaseConfig,
        app_config: AppConfig,
        input_class: type,
        output_class: type,
    ) -> APIRouter:
        router = APIRouter()

        @router.post("")
        @docstring_parameter(description)
        async def invoke(inputs: input_class, request: Request) -> InvokeResponse[output_class]:  # type: ignore
            """
            {0}
            """
            st = get_telemetry()
            context = extract(request.headers)

            authorization = request.headers.get("authorization", None)
            with (
                st.tracer.start_as_current_span(
                    f"{name}-{version}-invoke",
                    context=context,
                )
                if st.telemetry_enabled()
                else nullcontext()
            ):
                match root_handler_name:
                    case "skagents":
                        handler: BaseHandler = skagents_handle(config, app_config, authorization)
                    case _:
                        raise ValueError(f"Unknown apiVersion: {config.apiVersion}")

                inv_inputs = inputs.__dict__
                output = await handler.invoke(inputs=inv_inputs)
                return output

        @router.post("/sse")
        @docstring_parameter(description)
        async def invoke_sse(inputs: input_class, request: Request) -> StreamingResponse:
            """
            {0}
            Initiate SSE call
            """
            st = get_telemetry()
            context = extract(request.headers)
            authorization = request.headers.get("authorization", None)
            inv_inputs = inputs.__dict__

            async def event_generator():
                with (
                    st.tracer.start_as_current_span(
                        f"{config.service_name}-{str(config.version)}-invoke_sse",
                        context=context,
                    )
                    if st.telemetry_enabled()
                    else nullcontext()
                ):
                    match root_handler_name:
                        case "skagents":
                            handler: BaseHandler = skagents_handle(
                                config, app_config, authorization
                            )
                            # noinspection PyTypeChecker
                            async for content in handler.invoke_stream(inputs=inv_inputs):
                                yield get_sse_event_for_response(content)
                        case _:
                            logger.exception(
                                "Unknown apiVersion: %s", config.apiVersion, exc_info=True
                            )
                            raise ValueError(f"Unknown apiVersion: {config.apiVersion}")

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        return router

    @staticmethod
    def get_websocket_routes(
        name: str,
        version: str,
        root_handler_name: str,
        config: BaseConfig,
        app_config: AppConfig,
        input_class: type,
    ) -> APIRouter:
        router = APIRouter()

        @router.websocket("/stream")
        async def invoke_stream(websocket: WebSocket) -> None:
            await websocket.accept()
            st = get_telemetry()
            context = extract(websocket.headers)

            authorization = websocket.headers.get("authorization", None)
            try:
                data = await websocket.receive_json()
                with (
                    st.tracer.start_as_current_span(
                        f"{name}-{str(version)}-invoke_stream",
                        context=context,
                    )
                    if st.telemetry_enabled()
                    else nullcontext()
                ):
                    inputs = input_class(**data)
                    inv_inputs = inputs.__dict__
                    match root_handler_name:
                        case "skagents":
                            handler: BaseHandler = skagents_handle(
                                config, app_config, authorization
                            )
                            async for content in handler.invoke_stream(inputs=inv_inputs):
                                if isinstance(content, PartialResponse):
                                    await websocket.send_text(content.output_partial)
                            await websocket.close()
                        case _:
                            logger.exception(
                                "Unknown apiVersion: %s", config.apiVersion, exc_info=True
                            )
                            raise ValueError(f"Unknown apiVersion %s: {config.apiVersion}")
            except WebSocketDisconnect:
                logger.exception("websocket disconnected")
                print("websocket disconnected")

        return router

    @staticmethod
    def get_stateful_routes(
        name: str,
        version: str,
        description: str,
        config: BaseConfig,
        state_manager: StateManager,
        authorizer: RequestAuthorizer,
        input_class: type[UserMessage],
    ) -> APIRouter:
        """
        Get the stateful API routes for the given configuration.
        """
        router = APIRouter()

        async def get_user_id(authorization: str = Header(None)):
            user_id = await authorizer.authorize_request(authorization)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            return user_id

        @router.post(
            "/chat",
            response_model=StateResponse,
            summary="Send a message to the agent",
            response_description="Agent response with state identifiers",
            tags=["Agent"],
        )
        async def chat(
            message: input_class,
            user_id: str = Depends(get_user_id)
        ) -> StateResponse:
            # Handle new task creation or task retrieval
            if message.task_id is None:
                # New task
                session_id, task_id = await state_manager.create_task(
                    message.session_id,
                    user_id
                )
                task_state = await state_manager.get_task(task_id)
            else:
                # Follow-on request
                task_id = message.task_id
                task_state = await state_manager.get_task(task_id)
                # Verify user ownership
                if task_state.user_id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authorized to access this task"
                    )
                session_id = task_state.session_id

            # Create a new request
            request_id = await state_manager.create_request(task_id)

            # Return response with state identifiers
            return StateResponse(
                session_id=session_id,
                task_id=task_id,
                request_id=request_id,
                status=TaskStatus.COMPLETED,
                content="Agent response"  # Replace with actual response
            )

        return router

    @staticmethod
    def get_resume_routes() -> APIRouter:
        router = APIRouter()

        @router.post("/tealagents/v1alpha1/resume/{request_id}")
        async def resume(request_id: str, request: Request, body: ResumeRequest):
            authorization = request.headers.get("authorization", None)
            try:
                return await TealAgentsV1Alpha1Handler.resume_task(
                    request_id, authorization, body.model_dump(), stream=False
                )
            except Exception as e:
                logger.exception(f"Error in resume: {e}")
                raise HTTPException(status_code=500, detail="Internal Server Error") from e

        @router.post("/tealagents/v1alpha1/resume/{request_id}/sse")
        async def resume_sse(request_id: str, request: Request, body: ResumeRequest):
            authorization = request.headers.get("authorization", None)

            async def event_generator():
                try:
                    async for content in TealAgentsV1Alpha1Handler.resume_task(
                        request_id, authorization, body.model_dump(), stream=True
                    ):
                        yield get_sse_event_for_response(content)
                except Exception as e:
                    logger.exception(f"Error in resume_sse: {e}")
                    raise HTTPException(status_code=500, detail="Internal Server Error") from e

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        return router
