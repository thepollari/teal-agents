from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Generic, Optional, TypeVar, Any, AsyncIterable, List, Literal

from pydantic import BaseModel, ConfigDict
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.kernel_pydantic import KernelBaseModel
from ska_utils import Config as UtilConfig, AppConfig

from sk_agents.extra_data_collector import (
    ExtraDataCollector,
    ExtraData,
)


class ModelType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ContentType(Enum):
    IMAGE = "image"
    TEXT = "text"


class EmbeddedImage(BaseModel):
    format: str
    data: str


class BaseEmbeddedImage(KernelBaseModel):
    embedded_image: EmbeddedImage


class MultiModalItem(BaseModel):
    content_type: ContentType
    content: str


class HistoryMultiModalMessage(BaseModel):
    role: Literal["user", "assistant"]
    items: List[MultiModalItem]


class BaseMultiModalInput(KernelBaseModel):
    chat_history: Optional[List[HistoryMultiModalMessage]] = None


class HistoryMessage(BaseModel):
    """A single interaction in a chat history.<br/>
    'role' - Either 'user' (requestor) or 'assistant' (responder) indicating
    who sent the message.<br/>
    'content' - The content of the message"""

    role: Literal["user", "assistant"]
    content: str


class BaseInput(KernelBaseModel):
    """The history of a chat interaction between an automated assistant and a
    human."""

    chat_history: Optional[List[HistoryMessage]] = None


class BaseInputWithUserContext(KernelBaseModel):
    """The history of a chat interaction between an automated assistant and a
    human, along with context about the user."""

    chat_history: Optional[List[HistoryMessage]] = None
    user_context: Optional[Dict[str, str]] = None


class Config(BaseModel):
    model_config = ConfigDict(extra="allow")

    apiVersion: str
    description: Optional[str] = None
    service_name: str
    version: float
    input_type: str
    output_type: Optional[str] = None


class TokenUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


T = TypeVar("T")


class InvokeResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    token_usage: TokenUsage
    extra_data: Optional[ExtraData] = None
    output_raw: str
    output_pydantic: Optional[T] = None


class BaseHandler:
    async def invoke(self, inputs: Optional[Dict[str, Any]] = None) -> InvokeResponse:
        pass

    async def invoke_stream(
        self, inputs: Optional[Dict[str, Any]] = None
    ) -> AsyncIterable[str]:
        pass


class BasePlugin:
    def __init__(
        self,
        authorization: str | None = None,
        extra_data_collector: ExtraDataCollector | None = None,
    ):
        self.authorization = authorization
        self.extra_data_collector = extra_data_collector


class ChatCompletionFactory(ABC):
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config

    @staticmethod
    @abstractmethod
    def get_configs() -> List[UtilConfig]:
        pass

    @abstractmethod
    def get_chat_completion_for_model_name(
        self, model_name: str, service_id: str
    ) -> ChatCompletionClientBase:
        pass

    @abstractmethod
    def get_model_type_for_name(self, model_name: str) -> ModelType:
        pass
