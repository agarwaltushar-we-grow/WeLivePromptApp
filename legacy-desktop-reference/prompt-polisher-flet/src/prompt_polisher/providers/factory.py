"""Provider factory."""
from prompt_polisher.providers.base import LLMProvider, ProviderError
from prompt_polisher.providers.openai_provider import OpenAICompatibleProvider
from prompt_polisher.providers.ollama_provider import OllamaProvider

def create_provider(provider_name: str, api_key: str, openai_base_url: str, ollama_base_url: str) -> LLMProvider:
    normalized = provider_name.lower().strip()
    if normalized == "openai":
        return OpenAICompatibleProvider(api_key=api_key, base_url=openai_base_url)
    if normalized == "ollama":
        return OllamaProvider(base_url=ollama_base_url)
    raise ProviderError(f"Unsupported provider: {provider_name}")
