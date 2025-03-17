from typing import List

from group_orchestrator.planning_agent import PlanningAgent
from group_orchestrator.types import TaskAgent, Step


class PlanManager:
    def __init__(self, planning_agent: PlanningAgent):
        self.planning_agent = planning_agent

    def generate_plan(
        self, overall_goal: str, agent_list: List[TaskAgent]
    ) -> List[Step]:
        pass

    def re_plan(
        self, overall_goal: str, agent_list: List[TaskAgent], current_plan: List[Step]
    ) -> List[Step]:
        pass

    def plan_complete(self, plan: List[Step]) -> bool:
        pass
