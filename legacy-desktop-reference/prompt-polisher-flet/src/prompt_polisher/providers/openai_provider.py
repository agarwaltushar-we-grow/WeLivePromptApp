"""OpenAI-compatible provider."""
from openai import OpenAI, OpenAIError
from prompt_polisher.providers.base import LLMProvider, ProviderError

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> None:
        if not api_key.strip():
            raise ProviderError("Missing API key. Add it in the UI or set OPENAI_API_KEY.")
        self.client = OpenAI(api_key=api_key.strip(), base_url=base_url.strip())

    def generate(self, messages: list[dict[str, str]], model: str) -> str:
        try:
            response = self.client.chat.completions.create(model=model, messages=messages, temperature=0.2, response_format={"type": "json_object"})
            return response.choices[0].message.content or ""
        except OpenAIError as exc:
            raise ProviderError(f"API provider error: {exc}") from exc
        except Exception as exc:
            raise ProviderError(f"Unexpected API provider error: {exc}") from exc
