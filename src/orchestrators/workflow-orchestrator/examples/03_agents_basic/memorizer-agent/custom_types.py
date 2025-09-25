from typing import List

from pydantic import Field
from pydantic import BaseModel


class Memory(BaseModel):
    """
    A memory based on some previous interaction
    """

    memory_id: str = Field(description="The unique identifier for the memory")
    user_id: str = Field(description="The user to whom the memory belongs")
    access_count: int = Field(
        description="The number of times the memory has been accessed"
    )
    content: str = Field(description="The content of the memory")


class MemorizerInput(BaseModel):
    """
    An interaction between a user and the assistant
    """

    user_id: str = Field(description="The ID of the user involved in the interaction")
    message: str = Field(description="The message sent by the user")
    response: str = Field(description="The response sent by the assistant")
    memories: List[Memory] = Field(
        description="Memories potentially associated with the interaction"
    )
