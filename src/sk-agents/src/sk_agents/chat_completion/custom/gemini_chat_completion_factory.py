from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.connectors.ai.google.google_ai.services.google_ai_chat_completion import (
    GoogleAIChatCompletion,
)
from ska_utils import Config as UtilConfig

from sk_agents.ska_types import ChatCompletionFactory, ModelType


class GeminiChatCompletionFactory(ChatCompletionFactory):
    _GEMINI_MODELS: list[str] = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
    ]

    GEMINI_API_KEY = UtilConfig(
        env_name="GEMINI_API_KEY",
        is_required=True,
        default_value=None,
    )

    _CONFIGS: list[UtilConfig] = [GEMINI_API_KEY]

    def __init__(self, app_config):
        super().__init__(app_config)
        self.api_key = app_config.get(self.GEMINI_API_KEY.env_name)

    @staticmethod
    def get_configs() -> list[UtilConfig]:
        return GeminiChatCompletionFactory._CONFIGS

    def get_chat_completion_for_model_name(
        self, model_name: str, service_id: str
    ) -> ChatCompletionClientBase:
        if model_name in self._GEMINI_MODELS:
            return GoogleAIChatCompletion(
                service_id=service_id,
                ai_model_id=model_name,
                api_key=self.api_key,
            )
        else:
            raise ValueError(f"Model {model_name} not supported by GeminiChatCompletionFactory")

    def get_model_type_for_name(self, model_name: str) -> ModelType:
        if model_name in self._GEMINI_MODELS:
            return ModelType.GOOGLE
        else:
            raise ValueError(f"Unknown model name {model_name}")

    def model_supports_structured_output(self, model_name: str) -> bool:
        if model_name in self._GEMINI_MODELS:
            return True
        else:
            raise ValueError(f"Unknown model name {model_name}")

    def create_chat_completion(self, **kwargs):
        model_name = kwargs.get("model_name", "gemini-1.5-flash")
        service_id = kwargs.get("service_id", "gemini_service")
        return self.get_chat_completion_for_model_name(model_name, service_id)
