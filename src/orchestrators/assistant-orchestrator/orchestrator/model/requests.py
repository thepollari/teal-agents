from pydantic import BaseModel, Field


class ConversationMessageRequest(BaseModel):
    message: str
