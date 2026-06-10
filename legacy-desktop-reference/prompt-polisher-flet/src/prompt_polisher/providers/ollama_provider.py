"""Ollama provider using the local HTTP API."""

from __future__ import annotations

import json
import re

import requests

from prompt_polisher.providers.base import LLMProvider, ProviderError


RECOMMENDED_OLLAMA_MODELS = [
    "qwen2.5:7b",
    "llama3.1:8b",
    "mistral-nemo:12b",
]

MINIMUM_MODEL_GUIDANCE = (
    "Use qwen2.5:7b, llama3.1:8b, mistral-nemo:12b, or stronger. "
    "Avoid 0.5b, 1b, 1.5b, 2b, and 3b models for prompt optimization quality."
)


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def _installed_models(self) -> set[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.ConnectionError as exc:
            raise ProviderError(
                "Could not connect to Ollama. Start Ollama with `ollama serve`, then try again."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise ProviderError(f"Ollama HTTP error while checking installed models: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ProviderError("Ollama returned invalid JSON while checking installed models.") from exc

        models = data.get("models", [])
        names = {m.get("name", "") for m in models if isinstance(m, dict)}
        # Ollama sometimes displays names with or without explicit tags. Keep exact names only here;
        # the error message below gives the precise pull command if the requested model is missing.
        return {name for name in names if name}

    @staticmethod
    def _is_too_small_for_quality(model: str) -> bool:
        normalized = (model or "").lower().strip()
        # These models are fast but repeatedly produce generic 40-65/100 optimized prompts.
        weak_patterns = [
            r"(^|:)0\.5b($|-)",
            r"(^|:)1b($|-)",
            r"(^|:)1\.5b($|-)",
            r"(^|:)2b($|-)",
            r"(^|:)3b($|-)",
        ]
        weak_names = ["tiny", "mini", "small"]
        return any(re.search(pattern, normalized) for pattern in weak_patterns) or any(
            name in normalized for name in weak_names
        )

    def _validate_model(self, model: str) -> None:
        selected = (model or "").strip()
        if not selected:
            raise ProviderError(
                "No Ollama model selected. Recommended: qwen2.5:7b. "
                "Install it with `ollama pull qwen2.5:7b`."
            )

        if self._is_too_small_for_quality(selected):
            raise ProviderError(
                f"The selected Ollama model `{selected}` is too small for the target output quality. "
                f"{MINIMUM_MODEL_GUIDANCE} Recommended command: `ollama pull qwen2.5:7b`."
            )

        installed = self._installed_models()
        if selected not in installed:
            recommended = ", ".join(RECOMMENDED_OLLAMA_MODELS)
            installed_text = ", ".join(sorted(installed)) if installed else "none detected"
            raise ProviderError(
                f"Ollama model `{selected}` is not installed. Installed models: {installed_text}. "
                f"Run `ollama pull {selected}` or use one of: {recommended}."
            )

    def generate(self, messages: list[dict[str, str]], model: str) -> str:
        self._validate_model(model)

        payload = {
            "model": model,
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {
                # Keep this low enough for reliable JSON, but not zero. Zero tends to repeat
                # generic templates in local models.
                "temperature": 0.2,
                "top_p": 0.9,
                "repeat_penalty": 1.08,
                "num_ctx": 8192,
            },
        }

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=240)
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {})
            return message.get("content", "")
        except requests.exceptions.ConnectionError as exc:
            raise ProviderError(
                "Could not connect to Ollama. Start Ollama with `ollama serve`, then try again."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise ProviderError(f"Ollama HTTP error: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ProviderError("Ollama returned invalid JSON from its HTTP API.") from exc
