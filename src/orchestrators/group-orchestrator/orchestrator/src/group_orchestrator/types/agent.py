from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TokenUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class ExtraDataElement(BaseModel):
    key: str
    value: str


class ExtraData(BaseModel):
    items: List[ExtraDataElement]


class AgentResponse(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    token_usage: TokenUsage
    extra_data: Optional[ExtraData] = None
    output_raw: str
