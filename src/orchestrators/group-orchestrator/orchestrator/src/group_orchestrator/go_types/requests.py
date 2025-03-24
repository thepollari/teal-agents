from pydantic import BaseModel


class GroupOrchestratorRequest(BaseModel):
    overall_goal: str
