"""
Chat Model Factory for creating LangChain chat models.

Replaces Semantic Kernel's chat completion factories with LangChain equivalents,
supporting OpenAI, Azure OpenAI, Anthropic, and Google Gemini.
"""

import logging
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from sk_agents.ska_types import ModelType

logger = logging.getLogger(__name__)


class ChatModelFactory:
    """
    Factory for creating LangChain chat models based on model name.
    
    Supports:
    - OpenAI models (gpt-4, gpt-3.5-turbo, etc.)
    - Azure OpenAI models (prefix with 'azure-')
    - Anthropic models (claude-*)
    - Google Gemini models (gemini-*)
    """

    STRUCTURED_OUTPUT_MODELS = {
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-3.5-turbo-1106",
    }

    @staticmethod
    def get_model_type_for_name(model_name: str) -> ModelType:
        """
        Determine the model type from the model name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelType enum value
        """
        model_lower = model_name.lower()
        
        if model_lower.startswith("azure-"):
            return ModelType.AZURE_OPENAI
        elif "claude" in model_lower:
            return ModelType.ANTHROPIC
        elif "gemini" in model_lower:
            return ModelType.GEMINI
        elif "gpt" in model_lower or "text-" in model_lower:
            return ModelType.OPENAI
        else:
            logger.warning(f"Unknown model type for {model_name}, defaulting to OPENAI")
            return ModelType.OPENAI

    @staticmethod
    def model_supports_structured_output(model_name: str) -> bool:
        """
        Check if a model supports structured output.
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model supports structured output
        """
        clean_name = model_name.replace("azure-", "")
        return clean_name in ChatModelFactory.STRUCTURED_OUTPUT_MODELS

    @staticmethod
    def create_chat_model(
        model_name: str,
        temperature: float | None = None,
        **kwargs: Any
    ):
        """
        Create a LangChain chat model based on model name.
        
        Args:
            model_name: Name of the model
            temperature: Temperature setting (0.0-1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            LangChain BaseChatModel instance
        """
        model_type = ChatModelFactory.get_model_type_for_name(model_name)
        
        model_kwargs = {}
        if temperature is not None:
            model_kwargs["temperature"] = temperature
        model_kwargs.update(kwargs)
        
        try:
            if model_type == ModelType.AZURE_OPENAI:
                return ChatModelFactory._create_azure_openai(model_name, model_kwargs)
            elif model_type == ModelType.ANTHROPIC:
                return ChatModelFactory._create_anthropic(model_name, model_kwargs)
            elif model_type == ModelType.GEMINI:
                return ChatModelFactory._create_gemini(model_name, model_kwargs)
            else:  # OPENAI
                return ChatModelFactory._create_openai(model_name, model_kwargs)
        except Exception as e:
            logger.exception(f"Error creating chat model for {model_name}: {e}")
            raise

    @staticmethod
    def _create_openai(model_name: str, kwargs: dict[str, Any]) -> ChatOpenAI:
        """Create OpenAI chat model."""
        return ChatOpenAI(
            model=model_name,
            **kwargs
        )

    @staticmethod
    def _create_azure_openai(
        model_name: str,
        kwargs: dict[str, Any]
    ) -> AzureChatOpenAI:
        """
        Create Azure OpenAI chat model.
        
        Model name should be formatted as: azure-{deployment_name}
        """
        deployment_name = model_name.replace("azure-", "")
        
        return AzureChatOpenAI(
            azure_deployment=deployment_name,
            **kwargs
        )

    @staticmethod
    def _create_anthropic(model_name: str, kwargs: dict[str, Any]) -> ChatAnthropic:
        """Create Anthropic chat model."""
        if "max_tokens" not in kwargs:
            kwargs["max_tokens"] = 4096
            
        return ChatAnthropic(
            model=model_name,
            **kwargs
        )

    @staticmethod
    def _create_gemini(
        model_name: str,
        kwargs: dict[str, Any]
    ) -> ChatGoogleGenerativeAI:
        """Create Google Gemini chat model."""
        return ChatGoogleGenerativeAI(
            model=model_name,
            **kwargs
        )
