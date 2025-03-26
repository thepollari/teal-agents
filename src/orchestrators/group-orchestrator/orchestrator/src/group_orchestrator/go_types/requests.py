from typing import List, Literal

from pydantic import BaseModel


class GroupOrchestratorRequest(BaseModel):
    overall_goal: str


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatHistory(BaseModel):
    chat_history: List[ChatHistoryItem]
