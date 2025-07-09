# Abstract base class
from pydantic import BaseModel
from abc import ABC, abstractmethod

# Dummy data model while AgentTask model implementation is completed.
class AgentTask(BaseModel):
    task: str
    task_id: str

class TaskPersistenceManager(ABC):
    
    @abstractmethod
    async def create(task: AgentTask) -> None:
        pass

    @abstractmethod
    async def load(task_id: str) -> AgentTask | None:
        pass

    @abstractmethod
    async def update(task: AgentTask) -> None:
        pass

    @abstractmethod
    async def delete(task_id: str) -> None:
        pass
