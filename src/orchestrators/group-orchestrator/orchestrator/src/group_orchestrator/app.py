import asyncio
from typing import List

from ska_utils import AppConfig, strtobool

from group_orchestrator.agents import AgentGateway
from group_orchestrator.agents import BaseAgent
from group_orchestrator.agents import PlanningAgent
from group_orchestrator.agents.task_agent import TaskAgent
from group_orchestrator.configs import CONFIGS, TA_AGW_HOST, TA_AGW_SECURE, TA_AGW_KEY
from group_orchestrator.plan_manager import PlanManager
from group_orchestrator.step_executor import StepExecutor


def _get_planning_agent(agent_gateway: AgentGateway) -> PlanningAgent:

    base_planning_agent: BaseAgent = BaseAgent(
        name="PlanningAgent", version="0.1", description="A planning agent"
    )
    planning_agent = PlanningAgent(agent=base_planning_agent, gateway=agent_gateway)
    return planning_agent


async def run(overall_goal: str, base_task_agents: List[BaseAgent]):
    AppConfig.add_configs(CONFIGS)
    app_config = AppConfig()

    agent_gateway = AgentGateway(
        host=app_config.get(TA_AGW_HOST.env_name),
        secure=strtobool(app_config.get(TA_AGW_SECURE.env_name)),
        agw_key=app_config.get(TA_AGW_KEY.env_name),
    )

    planning_agent = _get_planning_agent(agent_gateway)
    plan_manager = PlanManager(planning_agent)

    task_agents: List[TaskAgent] = []
    for base_agent in base_task_agents:
        task_agent = TaskAgent(agent=base_agent, gateway=agent_gateway)
        task_agents.append(task_agent)

    plan = await plan_manager.generate_plan(
        overall_goal=overall_goal, task_agents=base_task_agents
    )
    print(plan)

    step_executor = StepExecutor(task_agents)
    for step in plan.steps:
        await step_executor.execute_step(step)
    print(plan.steps[-1].step_tasks[0].result)


if __name__ == "__main__":
    test_task_agents: List[BaseAgent] = [
        BaseAgent(
            name="TravelPlannerAgent",
            version="0.1",
            description="A helpful assistant that can plan trips.",
        ),
        BaseAgent(
            name="LocalAgent",
            version="0.1",
            description="A local assistant that can suggest local activities or places to visit.",
        ),
        BaseAgent(
            name="LanguageAgent",
            version="0.1",
            description="A helpful assistant that can provide language tips for a given destination.",
        ),
        BaseAgent(
            name="TravelSummaryAgent",
            version="0.1",
            description="A helpful assistant that can summarize the travel plan.",
        ),
    ]
    asyncio.run(
        run(
            "Plan a 3 day trip to Nepal.",
            test_task_agents,
        )
    )
