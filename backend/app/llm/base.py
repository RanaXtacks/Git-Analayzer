from abc import ABC, abstractmethod


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass


class LLMTimeoutError(LLMProviderError):
    """Raised when LLM call exceeds timeout."""
    pass


class LLMUnavailableError(LLMProviderError):
    """Raised when inference server cannot be contacted."""
    pass


class LLMProvider(ABC):
    """Abstract Base Class for LLM Inference Backends (Ollama, vLLM, etc.)."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate raw completion string from system and user prompts.
        Must return JSON formatted text.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify inference server availability."""
        pass
