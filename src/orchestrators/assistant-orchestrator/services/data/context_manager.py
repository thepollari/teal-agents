from abc import ABC, abstractmethod
from typing import Dict


class ContextManager(ABC):
    @abstractmethod
    def add_context(
        self, orchestrator_name: str, user_id: str, item_key: str, item_value: str
    ):
        pass

    @abstractmethod
    def update_context(
        self, orchestrator_name: str, user_id: str, item_key: str, item_value: str
    ):
        pass

    @abstractmethod
    def delete_context(self, orchestrator_name: str, user_id: str, item_key: str):
        pass

    @abstractmethod
    def get_context(self, orchestrator_name: str, user_id) -> Dict[str, str]:
        pass
