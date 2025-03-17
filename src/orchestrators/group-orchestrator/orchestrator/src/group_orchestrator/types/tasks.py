from typing import List

from pydantic import BaseModel


class Task(BaseModel):
    task_id: str
    prerequisite_tasks: List[str]
    task_goal: str
    task_agent: str


class TaskResult(BaseModel):
    task_id: str
    agent_name: str
    task_result: str
