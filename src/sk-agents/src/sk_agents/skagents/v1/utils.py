from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.messages.base import BaseMessageChunk

from sk_agents.ska_types import (
    ContentType,
    ModelType,
    MultiModalItem,
    TokenUsage,
)


def item_to_content(item: MultiModalItem) -> str | None:
    match item.content_type:
        case ContentType.TEXT:
            return item.content
        case ContentType.IMAGE:
            return f"[Image: {item.content}]"
        case _:
            return None


def parse_chat_history(
    chat_history: BaseChatMessageHistory, inputs: dict[str, Any] | None = None
) -> BaseChatMessageHistory:
    if inputs is not None and "chat_history" in inputs and inputs["chat_history"] is not None:
        for message in inputs["chat_history"]:
            if hasattr(message, "content"):
                items = [MultiModalItem(content_type=ContentType.TEXT, content=message.content)]
            elif hasattr(message, "items"):
                items = message.items
            else:
                return chat_history

            content_parts = []
            for item in items:
                content_part = item_to_content(item)
                if content_part:
                    content_parts.append(content_part)
            content = " ".join(content_parts)

            if message.role == "user":
                chat_history.add_user_message(content)
            elif message.role == "assistant":
                chat_history.add_ai_message(content)
            else:
                chat_history.add_message(HumanMessage(content=content))
    return chat_history


def get_token_usage_for_response(
    model_type: ModelType, content: BaseMessage | BaseMessageChunk
) -> TokenUsage:
    # Check if the content contains usage information
    if (
        hasattr(content, "usage_metadata")
        and content.usage_metadata is not None
    ):
        if model_type == ModelType.OPENAI:
            return get_token_usage_for_openai_response(content)
        elif model_type == ModelType.ANTHROPIC:
            return get_token_usage_for_anthropic_response(content)
        elif model_type == ModelType.GOOGLE:
            return get_token_usage_for_google_response(content)
    return TokenUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0)


def get_token_usage_for_openai_response(content: BaseMessage | BaseMessageChunk) -> TokenUsage:
    return TokenUsage(
        completion_tokens=content.usage_metadata.get("output_tokens", 0),
        prompt_tokens=content.usage_metadata.get("input_tokens", 0),
        total_tokens=content.usage_metadata.get("total_tokens", 0),
    )


def get_token_usage_for_anthropic_response(
    content: BaseMessage | BaseMessageChunk,
) -> TokenUsage:
    return TokenUsage(
        completion_tokens=content.usage_metadata.get("output_tokens", 0),
        prompt_tokens=content.usage_metadata.get("input_tokens", 0),
        total_tokens=content.usage_metadata.get("total_tokens", 0),
    )


def get_token_usage_for_google_response(
    content: BaseMessage | BaseMessageChunk,
) -> TokenUsage:
    return TokenUsage(
        completion_tokens=content.usage_metadata.get("output_tokens", 0),
        prompt_tokens=content.usage_metadata.get("input_tokens", 0),
        total_tokens=content.usage_metadata.get("total_tokens", 0),
    )
