from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import SystemMessage
from langchain_core.messages.base import BaseMessage

from sk_agents.ska_types import (
    ContentType,
    ModelType,
    MultiModalItem,
    TokenUsage,
)


def item_to_content(item: MultiModalItem) -> str:
    match item.content_type:
        case ContentType.TEXT:
            return item.content
        case ContentType.IMAGE:
            return f"[Image: {item.content}]"
        case _:
            return ""


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
                content_parts.append(item_to_content(item))
            content = " ".join(content_parts)

            if message.role == "user":
                chat_history.add_user_message(content)
            elif message.role == "assistant":
                chat_history.add_ai_message(content)
            else:
                chat_history.add_message(SystemMessage(content=content))
    return chat_history


def get_token_usage_for_response(model_type: ModelType, content: BaseMessage) -> TokenUsage:
    # Check if the content is a BaseMessage object and if it contains usage information
    if (
        isinstance(content, BaseMessage)
        and hasattr(content, "response_metadata")
        and content.response_metadata
        and "token_usage" in content.response_metadata
    ):
        if model_type == ModelType.OPENAI:
            return get_token_usage_for_openai_response(content)
        elif model_type == ModelType.ANTHROPIC:
            return get_token_usage_for_anthropic_response(content)
    return TokenUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0)


def get_token_usage_for_openai_response(content: BaseMessage) -> TokenUsage:
    return TokenUsage(
        completion_tokens=content.response_metadata.get("token_usage", {}).get(
            "completion_tokens", 0
        ),
        prompt_tokens=content.response_metadata.get("token_usage", {}).get("prompt_tokens", 0),
        total_tokens=content.response_metadata.get("token_usage", {}).get("total_tokens", 0),
    )


def get_token_usage_for_anthropic_response(
    content: BaseMessage,
) -> TokenUsage:
    return TokenUsage(
        completion_tokens=content.response_metadata.get("usage", {}).get("output_tokens", 0),
        prompt_tokens=content.response_metadata.get("usage", {}).get("input_tokens", 0),
        total_tokens=content.response_metadata.get("usage", {}).get("total_tokens", 0),
    )
