from copy import deepcopy
from typing import Optional, Any, Dict, AsyncIterable, List

from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import TextContent, ImageContent, ChatMessageContent

from sk_agents.extra_data_collector import ExtraDataCollector, ExtraDataPartial
from sk_agents.ska_types import (
    InvokeResponse,
    BaseHandler,
    Config as BaseConfig,
    TokenUsage,
    MultiModalItem,
    ContentType,
)
from sk_agents.skagents.kernel_builder import KernelBuilder
from sk_agents.skagents.v1.sequential.config import Config
from sk_agents.skagents.v1.sequential.output_transformer import OutputTransformer
from sk_agents.skagents.v1.sequential.task_builder import TaskBuilder
from sk_agents.type_loader import get_type_loader


class SequentialSkagents(BaseHandler):
    def __init__(
        self,
        config: BaseConfig,
        kernel_builder: KernelBuilder,
        task_builder: TaskBuilder,
    ):
        if hasattr(config, "spec"):
            self.config = Config(config=config)
        else:
            raise ValueError("Invalid config")

        self.kernel_builder = kernel_builder

        task_configs = self.config.get_tasks()
        sorted_configs = sorted(task_configs, key=lambda x: x.task_no)
        self.tasks = []
        for task_config in sorted_configs:
            self.tasks.append(
                task_builder.build_task(task_config, self.config.get_agents())
            )

    async def _transform_output(
        self, current_response: InvokeResponse, output_type_str: str
    ) -> InvokeResponse:
        output_transformer = OutputTransformer(self.kernel_builder)

        transformed_response = await output_transformer.transform_output(
            current_response.output_raw, output_type_str
        )

        type_loader = get_type_loader()
        output_type = type_loader.get_type(output_type_str)
        response: InvokeResponse[output_type] = InvokeResponse[output_type](
            token_usage=TokenUsage(
                completion_tokens=current_response.token_usage.completion_tokens
                + transformed_response.token_usage.completion_tokens,
                prompt_tokens=current_response.token_usage.prompt_tokens
                + transformed_response.token_usage.prompt_tokens,
                total_tokens=current_response.token_usage.total_tokens
                + transformed_response.token_usage.total_tokens,
            ),
            extra_data=current_response.extra_data,
            output_raw=current_response.output_raw,
            output_pydantic=transformed_response.output_pydantic,
        )
        return response

    @staticmethod
    def _item_to_content(item: MultiModalItem) -> TextContent | ImageContent | None:
        match item.content_type:
            case ContentType.TEXT:
                return TextContent(text=item.content)
            case ContentType.IMAGE:
                return ImageContent(data_uri=item.content)
            case _:
                return None

    @staticmethod
    def _get_chat_history(inputs: Optional[Dict[str, Any]] = None) -> ChatHistory:
        chat_history = ChatHistory()
        if (
            inputs is not None
            and "chat_history" in inputs
            and inputs["chat_history"] is not None
        ):
            for message in inputs["chat_history"]:
                if hasattr(message, "content"):
                    items = [
                        MultiModalItem(
                            content_type=ContentType.TEXT, content=message.content
                        )
                    ]
                elif hasattr(message, "items"):
                    items = message.items
                else:
                    return chat_history

                chat_message_items: List[TextContent | ImageContent] = []
                for item in items:
                    chat_message_items.append(SequentialSkagents._item_to_content(item))
                message_content = ChatMessageContent(
                    role=message.role, items=chat_message_items
                )
                chat_history.add_message(message_content)
        return chat_history

    @staticmethod
    def _parse_task_inputs(
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if inputs is not None:
            task_inputs = deepcopy(inputs)
            if "chat_history" in task_inputs:
                del task_inputs["chat_history"]
        else:
            task_inputs = None
        return task_inputs

    async def invoke_stream(
        self, inputs: Optional[Dict[str, Any]] = None
    ) -> AsyncIterable[str]:
        collector = ExtraDataCollector()

        task_no = 0
        chat_history = SequentialSkagents._get_chat_history(inputs)
        task_inputs = SequentialSkagents._parse_task_inputs(inputs)
        for i in range(len(self.tasks) - 1):
            # TODO - Once usage stats are available, need to check if usage message and send consolidated stats
            i_response = await self.tasks[i].invoke(
                history=chat_history, inputs=task_inputs
            )
            task_inputs[f"_{self.tasks[i].name}"] = i_response.output_raw
            collector.add_extra_data_items(i_response.extra_data)
            task_no += 1
        async for content in self.tasks[-1].invoke_stream(
            history=chat_history, inputs=task_inputs
        ):
            try:
                extra_data_partial: ExtraDataPartial = ExtraDataPartial.new_from_json(
                    content
                )
                collector.add_extra_data_items(extra_data_partial.extra_data)
                yield collector.get_extra_data().model_dump_json()
            except Exception:
                yield content

    async def invoke(self, inputs: Optional[Dict[str, Any]] = None) -> InvokeResponse:
        task_no = 0

        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0

        collector = ExtraDataCollector()

        chat_history = SequentialSkagents._get_chat_history(inputs)
        task_inputs = SequentialSkagents._parse_task_inputs(inputs)
        for task in self.tasks:
            i_response = await task.invoke(history=chat_history, inputs=task_inputs)
            task_inputs[f"_{task.name}"] = i_response.output_raw
            completion_tokens += i_response.token_usage.completion_tokens
            prompt_tokens += i_response.token_usage.prompt_tokens
            total_tokens += i_response.token_usage.total_tokens
            collector.add_extra_data_items(i_response.extra_data)
            task_no += 1
        last_message = chat_history.messages[-1].content
        response = InvokeResponse(
            token_usage=TokenUsage(
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens,
            ),
            extra_data=collector.get_extra_data(),
            output_raw=last_message,
        )
        if self.config.config.output_type is None:
            return response
        else:
            return await self._transform_output(
                response, self.config.config.output_type
            )
