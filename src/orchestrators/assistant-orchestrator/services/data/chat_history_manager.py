from abc import ABC, abstractmethod
from typing import List

from model import ChatHistoryItem, ChatHistory


class ChatHistoryManager(ABC):
    @abstractmethod
    def set_last_session_id_for_user(
        self, orchestrator_name: str, user_id: str, session_id: str
    ):
        pass

    @abstractmethod
    def get_last_session_id_for_user(
        self, orchestrator_name: str, user_id: str
    ) -> str | None:
        pass

    @abstractmethod
    def get_session_items(
        self, orchestrator_name: str, session_id: str
    ) -> List[ChatHistoryItem]:
        pass

    @abstractmethod
    def add_session_item(
        self, orchestrator_name: str, session_id: str, item: ChatHistoryItem
    ):
        pass

    @abstractmethod
    def get_chat_history_session(
        self, orchestrator_name: str, user_id: str, session_id: str
    ) -> ChatHistory | None:
        pass

    @abstractmethod
    def add_chat_history_session(
        self, orchestrator_name: str, chat_history: ChatHistory
    ) -> None:
        pass
