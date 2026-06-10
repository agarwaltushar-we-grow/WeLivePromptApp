"""Application configuration loaded from local packaged-app settings."""
from dataclasses import dataclass
from dotenv import load_dotenv

from prompt_polisher.settings_store import load_stored_settings

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    locale: str
    provider: str
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    ollama_base_url: str
    ollama_model: str


def load_config() -> AppConfig:
    stored = load_stored_settings()
    return AppConfig(
        locale=stored.locale,
        provider=stored.provider,
        openai_api_key=stored.openai_api_key,
        openai_base_url=stored.openai_base_url,
        openai_model=stored.openai_model,
        ollama_base_url=stored.ollama_base_url,
        ollama_model=stored.ollama_model,
    )
