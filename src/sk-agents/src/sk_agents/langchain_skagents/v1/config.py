"""
Configuration types for LangChain agents.

These are simplified versions of the SK agent configs, without SK dependencies.
"""
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    name: str
    role: str | None = None
    model: str
    system_prompt: str | None = None
    temperature: float | None = None
    plugins: list[str] | None = None
    remote_plugins: list[str] | None = None


class TaskConfig(BaseModel):
    """Configuration for a task in sequential execution."""
    name: str
    task_no: int
    description: str | None = None
    instructions: str
    agent: str
    output_key: str | None = None
