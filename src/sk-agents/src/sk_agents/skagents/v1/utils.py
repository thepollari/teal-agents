from typing import Optional, Dict, Any, List

from semantic_kernel.contents import TextContent, ImageContent, ChatMessageContent
from semantic_kernel.contents.chat_history import ChatHistory

from sk_agents.ska_types import (
    MultiModalItem,
    ContentType,
)


def item_to_content(item: MultiModalItem) -> TextContent | ImageContent | None:
    match item.content_type:
        case ContentType.TEXT:
            return TextContent(text=item.content)
        case ContentType.IMAGE:
            return ImageContent(data_uri=item.content)
        case _:
            return None


def parse_chat_history(inputs: Optional[Dict[str, Any]] = None) -> ChatHistory:
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
                chat_message_items.append(item_to_content(item))
            message_content = ChatMessageContent(
                role=message.role, items=chat_message_items
            )
            chat_history.add_message(message_content)
    return chat_history
