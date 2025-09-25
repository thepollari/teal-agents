"""Mock Gemini completion factory for E2E testing."""

from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents import AuthorRole, ChatMessageContent
from ska_utils import AppConfig, Config as UtilConfig

from sk_agents.ska_types import ChatCompletionFactory, ModelType


class MockGeminiChatCompletionFactory(ChatCompletionFactory):
    """Mock implementation of Gemini chat completion factory for testing."""

    _GEMINI_MODELS: list[str] = [
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    _CONFIGS: list[UtilConfig] = []

    def __init__(self, app_config: AppConfig):
        super().__init__(app_config)
        self.api_key = "mock_gemini_api_key"

    @staticmethod
    def get_configs() -> list[UtilConfig]:
        return MockGeminiChatCompletionFactory._CONFIGS

    def get_chat_completion_for_model_name(
        self, model_name: str, service_id: str
    ) -> ChatCompletionClientBase:
        """Return mock chat completion client."""
        if model_name in self._GEMINI_MODELS:
            return MockGeminiChatCompletion(service_id=service_id, model_name=model_name)
        else:
            raise ValueError(f"Model {model_name} not supported by MockGeminiChatCompletionFactory")

    def get_model_type_for_name(self, model_name: str) -> ModelType:
        if model_name in self._GEMINI_MODELS:
            return ModelType.GOOGLE
        else:
            raise ValueError(f"Unknown model name {model_name}")

    def model_supports_structured_output(self, model_name: str) -> bool:
        return model_name in self._GEMINI_MODELS


class MockGeminiChatCompletion(ChatCompletionClientBase):
    """Mock Gemini chat completion client that implements the full Semantic Kernel interface."""

    def __init__(self, service_id: str, model_name: str):
        super().__init__(service_id=service_id, ai_model_id=model_name)
        self.ai_model_id = model_name

    def instantiate_prompt_execution_settings(self, **kwargs) -> PromptExecutionSettings:
        """Return mock prompt execution settings."""
        kwargs.pop("service_id", None)
        kwargs.pop("ai_model_id", None)
        return PromptExecutionSettings(
            service_id=self.service_id, ai_model_id=self.ai_model_id, **kwargs
        )

    async def get_chat_message_contents(self, *args, **kwargs):
        """Return mock chat response with proper metadata."""
        content = (
            "I found several universities in Finland. Here are the details:\n\n"
            "**1. Aalto University**\n🌍 **Country:** Finland\n"
            "🔗 **Website:** https://www.aalto.fi\n📧 **Domain:** aalto.fi\n\n"
            "**2. University of Helsinki**\n🌍 **Country:** Finland\n"
            "🔗 **Website:** https://www.helsinki.fi\n📧 **Domain:** helsinki.fi"
        )
        
        message = ChatMessageContent(
            role=AuthorRole.ASSISTANT,
            content=content,
        )
        
        class MockUsage:
            def __init__(self):
                self.output_tokens = len(content.split())
                self.input_tokens = 50
                
        class MockInnerContent:
            def __init__(self):
                self.usage = MockUsage()
        
        message.inner_content = MockInnerContent()
        
        return [message]

    async def get_streaming_chat_message_contents(self, *args, **kwargs):
        """Return mock streaming chat response."""
        content = (
            "I found several universities in Finland. Here are the details:\n\n"
            "**1. Aalto University**\n🌍 **Country:** Finland\n"
            "🔗 **Website:** https://www.aalto.fi\n📧 **Domain:** aalto.fi"
        )
        yield [ChatMessageContent(role=AuthorRole.ASSISTANT, content=content)]
