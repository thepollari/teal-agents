# In-memory implementation
import logging
import threading
from .task_persistence_manager import TaskPersistenceManager, AgentTask
from ..exceptions import (
    PersistenceCreateError, 
    PersistenceLoadError,
    PersistenceUpdateError,
    PersistenceDeleteError
)

logger = logging.getLogger(__name__)

class InMemoryPersistenceManager(TaskPersistenceManager):
    def __init__(self):
        self.in_memory: dict[str, AgentTask] = {}
        logger.info("InMemoryPersistenceManager initialized.")

        self._lock = threading.Lock()
        
    async def create(self, task: AgentTask) -> None:
        with self._lock:
            try:
                if task.task_id in self.in_memory:
                    raise PersistenceCreateError(message=f"Task with ID '{task.task_id}' already exists.")
                self.in_memory[task.task_id] = task
                logger.info(f"Task '{task.task_id}' created successfully.")
            except PersistenceCreateError:
                raise
            except Exception as e:
                raise PersistenceCreateError(message=f"Unexpected error creating task '{task.task_id}': {e}")

    async def load(self, task_id: str) -> AgentTask | None:
        with self._lock:
            try:
                task = self.in_memory.get(task_id)
                if task is None:
                    raise ValueError(f"Task with ID '{task_id}' not found.")
                logger.info(f"Task '{task_id}' loaded successfully.")
                return task
            except ValueError:
                raise
            except Exception as e:
                raise PersistenceLoadError(message=f"Unexpected error loading task {task_id} with error message: {e}")
    
    async def update(self, task: AgentTask) -> None:
        with self._lock:
            try:
                if task.task_id not in self.in_memory:
                    raise ValueError(f"Task with ID '{task.task_id}' does not exist for update.")
                self.in_memory[task.task_id] = task
                logger.info(f"Task '{task.task_id}' updated successfully.")
            except ValueError:
                raise
            except Exception as e:
                raise PersistenceUpdateError(f"Unexpected error updating task '{task.task_id}': {e}")
        
    async def delete(self, task_id: str) -> None:
        with self._lock:
            try:
                if task_id not in self.in_memory:
                    raise ValueError(f"Task with ID '{task_id}' does not exist for deletion.")
                del self.in_memory["task_id"]
                logger.info(f"Task '{task_id}' deleted successfully.")
            except ValueError:
                raise
            except Exception as e:
                raise PersistenceDeleteError(f"Unexpected error deleting task '{task_id}': {e}")