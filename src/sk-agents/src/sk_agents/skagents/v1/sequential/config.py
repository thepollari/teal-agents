from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from sk_agents.ska_types import Config as BaseConfig


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    role: str
    model: str
    system_prompt: str
    plugins: Optional[List[str]] = None
    remote_plugins: Optional[List[str]] = None


class TaskConfig(BaseModel):
    name: str
    task_no: int
    description: str
    instructions: str
    agent: str


class Spec(BaseModel):
    agents: List[AgentConfig]
    tasks: List[TaskConfig]


class V1Config(BaseConfig):
    model_config = ConfigDict(extra="allow")

    spec: Spec


class Config:
    def __init__(self, config: BaseConfig):
        self.config: V1Config = V1Config(
            apiVersion=config.apiVersion,
            description=config.description,
            service_name=config.service_name,
            version=config.version,
            input_type=config.input_type,
            output_type=config.output_type,
            spec=config.spec,
        )

    def get_agents(self) -> List[AgentConfig]:
        return self.config.spec.agents

    def get_tasks(self) -> List[TaskConfig]:
        return self.config.spec.tasks
