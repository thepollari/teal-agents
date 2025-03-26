from typing import List

from pydantic import BaseModel
from semantic_kernel.kernel_pydantic import KernelBaseModel


class Agent(BaseModel):
    name: str
    description: str


class PlanningAgentInput(KernelBaseModel):
    overall_goal: str
    agent_list: List[Agent]


class Task(BaseModel):
    task_id: str
    prerequisite_tasks: List[str]
    task_goal: str
    task_agent: str


class Step(BaseModel):
    step_number: int
    step_tasks: List[Task]


class PlanningAgentOutput(KernelBaseModel):
    can_succeed: bool
    reasoning: str | None = None
    steps: List[Step] | None
