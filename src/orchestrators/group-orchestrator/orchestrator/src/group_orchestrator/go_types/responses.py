from enum import Enum
from typing import Dict, Type, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class EventType(Enum):
    PLAN = "PLAN"
    AGENT_REQUEST = "AGENT_REQUEST"
    AGENT_RESPONSE = "AGENT_RESPONSE"
    FINAL = "FINAL"


class EventResponse(BaseModel, Generic[T]):
    event_type: EventType
    data: T


def new_event_response(event_type: EventType, data: T) -> str:
    return f"event: {event_type.value}\ndata: {data.model_dump_json()}\n\n"
