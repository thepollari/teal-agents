from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SpecBase(BaseModel):
    model_config = ConfigDict(extra="allow")

    agents: List[str]


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    apiVersion: str
    kind: str
    description: Optional[str] = None
    service_name: str
    version: float
    spec: SpecBase
