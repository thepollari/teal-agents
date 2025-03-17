from typing import List

from dapr.clients import DaprClient

from group_orchestrator.types import TaskResult

_DAPR_STORE_NAME = "statestore"


class TaskResultManager:
    @staticmethod
    def _get_state_key(run_id: str, task_id: str) -> str:
        return f"{run_id}_{task_id}"

    def __init__(self, dapr_client: DaprClient):
        self.dapr_client = dapr_client

    def get_task_result(self, run_id: str, task_id: str) -> TaskResult:
        result = self.dapr_client.get_state(
            _DAPR_STORE_NAME, TaskResultManager._get_state_key(run_id, task_id)
        )
        if result.data:
            return TaskResult(**result.json())
        raise ValueError(
            f"Task result for run_id {run_id} and task_id {task_id} not found."
        )

    def get_tasks_results(self, run_id: str, task_ids: List[str]) -> List[TaskResult]:
        return [self.get_task_result(run_id, task_id) for task_id in task_ids]

    def save_task_result(self, run_id: str, task_result: TaskResult) -> None:
        self.dapr_client.save_state(
            _DAPR_STORE_NAME,
            TaskResultManager._get_state_key(run_id, task_result.task_id),
            task_result.model_dump_json(),
        )

    def save_tasks_results(self, run_id: str, tasks_results: List[TaskResult]) -> None:
        for task_result in tasks_results:
            self.save_task_result(run_id, task_result)
