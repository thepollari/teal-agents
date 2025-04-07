from pydantic import BaseModel


class FinalResult(BaseModel):
    result: str


class AbortResult(BaseModel):
    abort_reason: str
