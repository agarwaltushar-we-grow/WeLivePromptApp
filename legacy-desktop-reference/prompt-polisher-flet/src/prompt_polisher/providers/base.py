"""Provider abstraction for swappable LLM backends."""
from abc import ABC, abstractmethod

class ProviderError(RuntimeError):
    """Raised when an LLM provider fails in a user-recoverable way."""

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: list[dict[str, str]], model: str) -> str:
        """Return a text completion for chat-style messages."""
