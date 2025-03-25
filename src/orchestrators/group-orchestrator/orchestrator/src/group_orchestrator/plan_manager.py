from typing import List

from group_orchestrator.agents import BaseAgent, PlanningAgent
from group_orchestrator.go_types import Plan, PlanningFailedException


class PlanManager:
    def __init__(self, planning_agent: PlanningAgent):
        self.planning_agent = planning_agent

    async def generate_plan(
        self,
        overall_goal: str,
        task_agents: List[BaseAgent],
    ) -> Plan:
        gen_plan_response = await self.planning_agent.generate_plan(
            overall_goal, task_agents
        )
        if not gen_plan_response.can_succeed:
            raise PlanningFailedException(
                f"Planning failed: {gen_plan_response.reasoning}"
            )
        return Plan.new_from_response(gen_plan_response)
