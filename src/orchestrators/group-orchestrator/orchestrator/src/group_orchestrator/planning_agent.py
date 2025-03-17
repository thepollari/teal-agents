from typing import List

from pydantic import BaseModel

from group_orchestrator.types import TaskAgent, AgentResponse, Step


class PlanningAgentRequest(BaseModel):
    overall_goal: str
    agent_list: List[TaskAgent]


class StructuredPlanResponse(BaseModel):
    steps: List[Step]


class PlanningAgentResponse(AgentResponse):
    output_pydantic: StructuredPlanResponse


class PlanningAgent:
    pass
