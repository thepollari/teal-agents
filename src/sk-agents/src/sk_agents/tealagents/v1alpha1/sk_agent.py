from collections.abc import AsyncIterable
from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

from sk_agents.ska_types import ModelType


class SKAgent:
    def __init__(
        self,
        model_name: str,
        model_attributes: dict[str, Any],
        agent: Runnable,
    ):
        self.model_name = model_name
        self.agent = agent
        self.model_attributes = model_attributes

    def get_model_type(self) -> ModelType:
        return self.model_attributes["model_type"]

    def so_supported(self) -> bool:
        return self.model_attributes["so_supported"]

    async def invoke_stream(
        self, history: BaseChatMessageHistory
    ) -> AsyncIterable[BaseMessage]:
        async for result in self.agent.invoke_stream(messages=history):
            yield result.content

    async def invoke(self, history: BaseChatMessageHistory) -> AsyncIterable[BaseMessage]:
        async for result in self.agent.invoke(messages=history):
            yield result.content
