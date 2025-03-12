from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    role: Optional[str] = None
    model: str
    system_prompt: str
    plugins: Optional[List[str]] = None
    remote_plugins: Optional[List[str]] = None
