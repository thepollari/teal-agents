from ska_utils import AppConfig, Config as UtilConfig

from sk_agents.ska_types import ChatCompletionFactory, ModelType


class MockGeminiFactory(ChatCompletionFactory):

    _GEMINI_MODELS: list[str] = [
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    _CONFIGS: list[UtilConfig] = []

    def __init__(self, app_config: AppConfig):
        pass

    @staticmethod
    def get_configs():
        return MockGeminiFactory._CONFIGS

    def get_chat_completion_for_model_name(self, model_name: str, service_id: str):
        if model_name in MockGeminiFactory._GEMINI_MODELS:
            return {"service_id": service_id, "ai_model_id": model_name, "mock": True}
        raise ValueError(f"Model {model_name} not supported by MockGeminiFactory")

    def get_model_type_for_name(self, model_name: str) -> ModelType:
        if model_name in MockGeminiFactory._GEMINI_MODELS:
            return ModelType.GOOGLE
        else:
            raise ValueError(f"Unknown model name {model_name}")

    def model_supports_structured_output(self, model_name: str) -> bool:
        if model_name in MockGeminiFactory._GEMINI_MODELS:
            return True
        else:
            raise ValueError(f"Unknown model name {model_name}")
