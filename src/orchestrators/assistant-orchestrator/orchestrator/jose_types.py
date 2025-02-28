import json
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ExtraDataElement(BaseModel):
    key: str
    value: str


class ExtraData(BaseModel):
    items: List[ExtraDataElement]

    def new_from_json(json_str: str) -> "ExtraData":
        return ExtraData(**json.loads(json_str))


class Spec(BaseModel):
    fallback_agent: str
    agent_chooser: str
    agents: List[str]


class Config(BaseModel):
    model_config = ConfigDict(extra="allow")

    apiVersion: str
    description: Optional[str] = None
    service_name: str
    version: float
    spec: Spec
