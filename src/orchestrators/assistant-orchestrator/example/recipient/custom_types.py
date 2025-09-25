from typing import List, Union

from pydantic import BaseModel as KernelBaseModel


class Agent(KernelBaseModel):
    name: str
    description: str


class UserMessage(KernelBaseModel):
    content: str
    recipient: str


class AgentMessage(KernelBaseModel):
    content: str
    sender: str


class Conversation(KernelBaseModel):
    history: List[Union[UserMessage, AgentMessage]]


class AgentSelectorInput(KernelBaseModel):
    conversation_history: Conversation
    agent_list: List[Agent]
    current_message: str


class SelectedAgent(KernelBaseModel):
    agent_name: str
    confidence: str
    is_followup: bool
