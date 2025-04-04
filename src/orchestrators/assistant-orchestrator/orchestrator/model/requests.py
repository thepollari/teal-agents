from pydantic import BaseModel


class ConversationMessageRequest(BaseModel):
    message: str
