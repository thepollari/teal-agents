from typing import List

import aiohttp
from pydantic import BaseModel

from group_orchestrator.agents.invokable_agent import InvokableAgent
from group_orchestrator.agents.types import BaseAgent


class PlanningBaseAgent(BaseModel):
    name: str
    description: str


class GeneratePlanRequest(BaseModel):
    overall_goal: str
    agent_list: List[PlanningBaseAgent]


class Task(BaseModel):
    task_id: str
    prerequisite_tasks: List[str]
    task_goal: str
    task_agent: str


class Step(BaseModel):
    step_number: int
    step_tasks: List[Task]


class GeneratePlanResponse(BaseModel):
    can_succeed: bool
    reasoning: str | None = None
    steps: List[Step] | None


class PlanningAgent(InvokableAgent):
    async def generate_plan(
        self,
        overall_goal: str,
        task_agents: List[BaseAgent],
    ) -> GeneratePlanResponse:
        planning_task_agents = [
            PlanningBaseAgent(
                name=f"{agent.name}:{agent.version}", description=agent.description
            )
            for agent in task_agents
        ]
        request = GeneratePlanRequest(
            overall_goal=overall_goal, agent_list=planning_task_agents
        )
        async with aiohttp.ClientSession() as session:
            response = await self.invoke(session, request)
        return GeneratePlanResponse(**response["output_pydantic"])
