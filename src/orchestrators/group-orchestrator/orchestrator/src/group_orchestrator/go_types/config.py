from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Spec(BaseModel):
    planning_agent: str
    agents: List[str]


class Config(BaseModel):
    model_config = ConfigDict(extra="allow")

    apiVersion: str
    kind: str
    description: Optional[str] = None
    service_name: str
    version: float
    spec: Spec
