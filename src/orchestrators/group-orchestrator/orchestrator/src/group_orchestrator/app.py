from enum import Enum
from typing import List

from pydantic import BaseModel

from group_orchestrator.task_result_manager import TaskResultManager
from group_orchestrator.types import TaskResult


class StepStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    COMPLETED = "COMPLETED"


class TaskAgent:
    pass


class Task:
    task_id: str
    prerequisite_tasks: List[str]
    task_goal: str
    task_agent: str


class Step:
    step_number: int
    step_tasks: List[Task]
    step_status: StepStatus


class ExecutionTask(BaseModel):
    overall_goal: str
    agent_name: str
    prerequisites: List[TaskResult]
    task_goal: str


class TaskExecutor:
    def execute_task(self, execution_task: ExecutionTask) -> TaskResult:
        pass

    def execute_tasks(self, execution_tasks: List[ExecutionTask]) -> List[TaskResult]:
        pass


class PlanManager:
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


task_result_manager = TaskResultManager()
task_executor = TaskExecutor()
plan_manager = PlanManager()


def execute_step(overall_goal: str, step: Step) -> None:
    execution_tasks: List[ExecutionTask] = []
    for task in step.step_tasks:
        task_prereqs = task_result_manager.get_tasks_results(task.prerequisite_tasks)
        execution_tasks.append(
            ExecutionTask(
                overall_goal=overall_goal,
                agent_name=task.task_agent,
                prerequisites=task_prereqs,
                task_goal=task.task_goal,
            )
        )
    tasks_results = task_executor.execute_tasks(execution_tasks)
    task_result_manager.save_tasks_results(tasks_results)
    step.step_status = StepStatus.COMPLETED


def execute_next_step(overall_goal: str, step_list: List[Step]) -> None:
    for step in step_list:
        if step.step_status == StepStatus.NOT_STARTED:
            execute_step(overall_goal, step)
            return


def plan_and_execute(
    overall_goal: str, agent_list: List[TaskAgent]
) -> List[TaskResult]:
    current_plan: List[Step] = plan_manager.generate_plan(overall_goal, agent_list)
    while not plan_manager.plan_complete(current_plan):
        execute_next_step(overall_goal, current_plan)
        current_plan = plan_manager.re_plan(overall_goal, agent_list, current_plan)
    return task_result_manager.get_tasks_results(
        [task.task_id for task in current_plan[-1].step_tasks]
    )
