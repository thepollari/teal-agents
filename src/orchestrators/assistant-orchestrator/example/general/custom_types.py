from typing import List

from sk_agents.ska_types import BaseInput

from pydantic import BaseModel


class Agent(BaseModel):
    name: str
    description: str


class GeneralInput(BaseInput):
    agents: List[Agent]
