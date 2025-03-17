import uuid
from typing import List

from dapr.clients import DaprClient
from pydantic import BaseModel

from group_orchestrator.plan_manager import PlanManager
from group_orchestrator.task_result_manager import TaskResultManager
from group_orchestrator.types import TaskResult, TaskAgent, Step, StepStatus


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


dapr_client = DaprClient()
task_result_manager = TaskResultManager(dapr_client)

task_executor = TaskExecutor()
plan_manager = PlanManager()


def execute_step(run_id: str, overall_goal: str, step: Step) -> None:
    execution_tasks: List[ExecutionTask] = []
    for task in step.step_tasks:
        task_prereqs = task_result_manager.get_tasks_results(
            run_id, task.prerequisite_tasks
        )
        execution_tasks.append(
            ExecutionTask(
                overall_goal=overall_goal,
                agent_name=task.task_agent,
                prerequisites=task_prereqs,
                task_goal=task.task_goal,
            )
        )
    tasks_results = task_executor.execute_tasks(execution_tasks)
    task_result_manager.save_tasks_results(run_id, tasks_results)
    step.step_status = StepStatus.COMPLETED


def execute_next_step(run_id: str, overall_goal: str, step_list: List[Step]) -> None:
    for step in step_list:
        if step.step_status == StepStatus.NOT_STARTED:
            execute_step(run_id, overall_goal, step)
            return


def plan_and_execute(
    overall_goal: str, agent_list: List[TaskAgent]
) -> List[TaskResult]:
    run_id = str(uuid.uuid4())

    current_plan: List[Step] = plan_manager.generate_plan(overall_goal, agent_list)
    while not plan_manager.plan_complete(current_plan):
        execute_next_step(run_id, overall_goal, current_plan)
        current_plan = plan_manager.re_plan(overall_goal, agent_list, current_plan)
    return task_result_manager.get_tasks_results(
        run_id, [task.task_id for task in current_plan[-1].step_tasks]
    )


if __name__ == "__main__":
    # Example usage
    overall_goal = "Build a house"
    agent_list = [TaskAgent(), TaskAgent()]
    results = plan_and_execute(overall_goal, agent_list)
    print(results)
