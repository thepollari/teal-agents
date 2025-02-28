import logging
from typing import TypeVar

from dapr.ext.workflow import DaprWorkflowClient
from dapr.ext.workflow.workflow_context import Workflow

from workflow_orchestrator import (
    ScheduleWorkflowResponse,
    WorkflowState,
    WorkflowEvent,
    WorkflowUpdateRequest,
    WorkflowAction,
)

TInput = TypeVar("TInput")


class WorkflowNotFoundException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class WorkflowClient:
    def __init__(self):
        self._client = DaprWorkflowClient()
        self._logger = logging.getLogger("WorkflowClient")

    def schedule_new_workflow(
        self, workflow: Workflow, input: TInput | None = None
    ) -> ScheduleWorkflowResponse:
        instance_id = self._client.schedule_new_workflow(workflow=workflow, input=input)
        return ScheduleWorkflowResponse(instance_id=instance_id)

    def get_workflow_state(self, instance_id: str) -> WorkflowState:
        try:
            state = self._client._DaprWorkflowClient__obj.get_orchestration_state(
                instance_id
            )
            return WorkflowState.new_from_orchestrator_state(state)
        except Exception as e:
            self._logger.warning(f"Failed to get workflow state: {e}")
            raise WorkflowNotFoundException(f"Workflow {instance_id} not found")

    def raise_workflow_event(
        self, instance_id: str, event: WorkflowEvent
    ) -> WorkflowState:
        event_data = event.event_data.model_dump()
        self._client.raise_workflow_event(
            instance_id=instance_id,
            event_name=event.event_name,
            data=event_data,
        )
        return self.get_workflow_state(instance_id)

    def update_state(
        self, instance_id: str, update_request: WorkflowUpdateRequest
    ) -> WorkflowState:
        match update_request.action:
            case WorkflowAction.PAUSE:
                self._client.pause_workflow(instance_id)
            case WorkflowAction.RESUME:
                self._client.resume_workflow(instance_id)
            case WorkflowAction.TERMINATE:
                self._client.terminate_workflow(instance_id)
        return self.get_workflow_state(instance_id)
