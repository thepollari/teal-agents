from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TypeVar, Generic, Optional, Union

from dapr.ext.workflow import DaprWorkflowContext
from durabletask.client import OrchestrationState
from pydantic import BaseModel, ConfigDict


@dataclass
class DataClass:
    pass


T = TypeVar("T", bound=DataClass)
TAgentInput = TypeVar("TAgentInput", bound=DataClass)
TAgentOutput = TypeVar("TAgentOutput", bound=DataClass)


@dataclass
class AgentActivityInput(Generic[TAgentInput, TAgentOutput]):
    agent_name: str
    agent_version: str
    agent_input: TAgentInput
    output_type: dict | None = None


class Workflow(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def setup():
        pass

    @staticmethod
    @abstractmethod
    def entrypoint(ctx: DaprWorkflowContext, workflow_input: T):
        pass


class Config(BaseModel):
    model_config = ConfigDict(extra="allow")

    apiVersion: str
    kind: str
    description: Optional[str] = None
    service_name: str
    version: float
    entrypoint: str
    input_type: str


class ScheduleWorkflowResponse(BaseModel):
    instance_id: str


class WorkflowState(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    instance_id: str
    name: str
    runtime_status: str
    created_at: datetime
    last_updated_at: datetime
    serialized_input: Union[str, None]
    serialized_output: Union[str, None]
    serialized_custom_status: Union[str, None]

    @staticmethod
    def new_from_orchestrator_state(orch_state: OrchestrationState) -> "WorkflowState":
        return WorkflowState(
            instance_id=orch_state.instance_id,
            name=orch_state.name,
            runtime_status=str(orch_state.runtime_status),
            created_at=orch_state.created_at,
            last_updated_at=orch_state.last_updated_at,
            serialized_input=orch_state.serialized_input,
            serialized_output=orch_state.serialized_output,
            serialized_custom_status=orch_state.serialized_custom_status,
        )


class EventData(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class WorkflowEvent(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    event_name: str
    event_data: EventData


class WorkflowAction(Enum):
    PAUSE: str = "pause"
    RESUME: str = "resume"
    TERMINATE: str = "terminate"


class WorkflowUpdateRequest(BaseModel):
    action: WorkflowAction
