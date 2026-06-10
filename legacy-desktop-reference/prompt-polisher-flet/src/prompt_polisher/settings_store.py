"""Local application settings for packaged desktop use.

The app stores settings outside the source directory so non-technical users can
run a packaged app without editing .env files or using a terminal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import stat
import sys
from typing import Any

APP_DIR_NAME = "PromptPolisher"
CONFIG_FILE_NAME = "settings.json"
DEFAULT_ADMIN_PASSWORD = "admin"


def app_data_dir() -> Path:
    """Return a writable per-user app data directory."""
    override = os.getenv("PROMPT_POLISHER_CONFIG_DIR")
    if override:
        return Path(override).expanduser()

    if sys.platform.startswith("win"):
        root = os.getenv("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(root) / APP_DIR_NAME

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME

    return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_DIR_NAME


@dataclass
class StoredSettings:
    locale: str = "ja"
    provider: str = "openai"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    admin_password_salt: str = ""
    admin_password_hash: str = ""


def _config_path() -> Path:
    return app_data_dir() / CONFIG_FILE_NAME


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        base64.b64decode(salt.encode("ascii")),
        240_000,
    )
    return base64.b64encode(digest).decode("ascii")


def make_password_record(password: str) -> tuple[str, str]:
    raw_salt = secrets.token_bytes(16)
    salt = base64.b64encode(raw_salt).decode("ascii")
    return salt, _hash_password(password, salt)


def verify_password(password: str, settings: StoredSettings) -> bool:
    if not settings.admin_password_salt or not settings.admin_password_hash:
        fallback = os.getenv("PROMPT_POLISHER_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
        return hmac.compare_digest(password or "", fallback)

    expected = _hash_password(password or "", settings.admin_password_salt)
    return hmac.compare_digest(expected, settings.admin_password_hash)


def load_stored_settings() -> StoredSettings:
    """Load settings from disk, then overlay environment defaults where useful."""
    settings = StoredSettings(
        locale=os.getenv("APP_LOCALE", "ja"),
        provider=os.getenv("LLM_PROVIDER", "openai"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    )

    path = _config_path()
    if not path.exists():
        return settings

    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        valid_keys = set(asdict(settings).keys())
        merged = asdict(settings)
        merged.update({k: v for k, v in data.items() if k in valid_keys})
        return StoredSettings(**merged)
    except Exception:
        return settings


def save_stored_settings(settings: StoredSettings) -> Path:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")

    # Best-effort local privacy: readable/writable only by current user on POSIX.
    if os.name != "nt":
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    return path


def mask_secret(value: str) -> str:
    value = value or ""
    if not value:
        return "Not configured"
    if len(value) <= 8:
        return "Configured"
    return f"Configured: {value[:4]}...{value[-4:]}"
