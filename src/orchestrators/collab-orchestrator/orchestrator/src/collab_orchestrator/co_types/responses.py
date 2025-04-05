from enum import Enum
from typing import TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class EventType(Enum):
    PLAN = "PLAN"
    MANAGER_RESPONSE = "MANAGER_RESPONSE"
    AGENT_REQUEST = "AGENT_REQUEST"
    AGENT_RESPONSE = "AGENT_RESPONSE"
    PARTIAL_AGENT_RESPONSE = "PARTIAL_AGENT_RESPONSE"
    FINAL = "FINAL"
    ERROR = "ERROR"


class EventResponse(BaseModel, Generic[T]):
    event_type: EventType
    data: T


class ErrorResponse(BaseModel):
    status_code: int
    detail: str


def new_event_response(event_type: EventType, data: T) -> str:
    return f"event: {event_type.value}\ndata: {data.model_dump_json()}\n\n"
