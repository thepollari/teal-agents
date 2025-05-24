from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    Message,
    Part,
    TextPart,
    FilePart,
    DataPart,
    Role,
    TaskStatusUpdateEvent,
    TaskStatus,
    TaskState,
    TaskArtifactUpdateEvent,
)
from a2a.utils import new_agent_text_message, new_text_artifact
from ska_utils import AppConfig
from typing_extensions import override

from sk_agents.ska_types import (
    BaseConfig,
    BaseHandler,
    InvokeResponse,
    BaseMultiModalInput,
    MultiModalItem,
    ContentType,
    HistoryMultiModalMessage,
)
from sk_agents.skagents import handle as skagents_handle


# TODO:
#   - Define how to determine if this is ACTUALLY the final response or input required
#   - Implement the cancel method
#   - How to handle chat history in the case of a response to an input required
#   - Persistent task store
class A2AAgentExecutor(AgentExecutor):

    def __init__(
        self,
        config: BaseConfig,
        app_config: AppConfig,
    ):
        self.config = config
        self.app_config = app_config

    @staticmethod
    def _part_to_multi_modal_item(part: Part) -> MultiModalItem:
        if isinstance(part.root, TextPart):
            return MultiModalItem(content_type=ContentType.TEXT, content=part.root.text)
        elif isinstance(part.root, DataPart):
            return MultiModalItem(
                content_type=ContentType.TEXT, content=str(part.root.data)
            )
        elif isinstance(part.root, FilePart):
            return MultiModalItem(
                content_type=ContentType.IMAGE,
                content=f"data:{part.root.file.mimeType};base64,{part.root.file.data}",
            )
        else:
            raise ValueError(f"Unsupported part type: {type(part.root)}")

    @staticmethod
    def _message_to_base_multi_modal_input(message: Message) -> BaseMultiModalInput:
        return BaseMultiModalInput(
            session_id=message.taskId,
            chat_history=[
                HistoryMultiModalMessage(
                    role="user" if message.role == Role.user else "assistant",
                    items=[
                        A2AAgentExecutor._part_to_multi_modal_item(part)
                        for part in message.parts
                    ],
                )
            ],
        )

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        message = context.message

        event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                contextId=message.contextId,
                taskId=message.taskId,
                final=False,
                status=TaskStatus(
                    state=TaskState.working,
                    message=new_agent_text_message("Processing request"),
                ),
            )
        )

        try:
            handler: BaseHandler = skagents_handle(self.config, self.app_config, None)

            inputs = A2AAgentExecutor._message_to_base_multi_modal_input(message)
            response: InvokeResponse = await handler.invoke(inputs=inputs.__dict__)
            event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    contextId=message.contextId,
                    taskId=message.taskId,
                    append=False,
                    lastChunk=True,
                    artifact=new_text_artifact(
                        name="final-response",
                        description="The final response",
                        text=response.output_raw,
                    ),
                    metadata=response.token_usage.__dict__,
                )
            )
            event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    contextId=message.contextId,
                    taskId=message.taskId,
                    final=True,
                    status=TaskStatus(
                        state=TaskState.completed,
                    ),
                )
            )
        except Exception as e:
            event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    contextId=message.contextId,
                    taskId=message.taskId,
                    final=True,
                    status=TaskStatus(
                        state=TaskState.failed,
                        message=new_agent_text_message(str(e)),
                    ),
                )
            )

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        pass
