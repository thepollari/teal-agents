import threading
from typing import override

from pydantic import BaseModel

from sk_agents.ska_types import HistoryMultiModalMessage
from sk_agents.state.state_manager import StateManager


class _Task(BaseModel):
    task_id: str
    cancelled: bool = False
    messages: list[HistoryMultiModalMessage] = []


class InMemoryStateManager(StateManager):
    _tasks: dict[str, _Task]
    _lock: threading.RLock

    def __init__(self):
        self._tasks = {}
        self._lock = threading.RLock()

    @override
    async def update_task_messages(
        self, task_id: str, new_message: HistoryMultiModalMessage
    ) -> list[HistoryMultiModalMessage]:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].messages.append(new_message)
            else:
                self._tasks[task_id] = _Task(
                    task_id=task_id, cancelled=False, messages=[new_message]
                )
            # Return a copy to prevent external modification without synchronization
            return list(self._tasks[task_id].messages)

    @override
    async def set_canceled(self, task_id: str) -> None:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].cancelled = True

    @override
    async def is_canceled(self, task_id) -> bool:
        with self._lock:
            if task_id in self._tasks:
                return self._tasks[task_id].cancelled
            return False
