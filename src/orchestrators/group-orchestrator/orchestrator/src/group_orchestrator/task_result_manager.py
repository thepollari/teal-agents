from typing import List

from group_orchestrator.types import TaskResult


class TaskResultManager:
    def get_task_result(self, task_id) -> TaskResult:
        pass

    def get_tasks_results(self, task_ids: List[str]) -> List[TaskResult]:
        pass

    def save_task_result(self, task_result: TaskResult) -> None:
        pass

    def save_tasks_results(self, tasks_results: List[TaskResult]) -> None:
        pass