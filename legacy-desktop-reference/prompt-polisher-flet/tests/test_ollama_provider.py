import pytest

from prompt_polisher.providers.base import ProviderError
from prompt_polisher.providers.ollama_provider import OllamaProvider


def test_ollama_provider_blocks_tiny_models_before_generation():
    provider = OllamaProvider()
    with pytest.raises(ProviderError) as exc:
        provider.generate([], "llama3.2:1b")
    assert "too small" in str(exc.value)
    assert "qwen2.5:7b" in str(exc.value)
