import os

from prompt_polisher.settings_store import (
    load_stored_settings,
    make_password_record,
    save_stored_settings,
    verify_password,
)


def test_settings_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMPT_POLISHER_CONFIG_DIR", str(tmp_path))
    settings = load_stored_settings()
    settings.openai_api_key = "sk-test"
    settings.provider = "openai"
    settings.admin_password_salt, settings.admin_password_hash = make_password_record("password123")

    path = save_stored_settings(settings)
    loaded = load_stored_settings()

    assert path.exists()
    assert loaded.openai_api_key == "sk-test"
    assert loaded.provider == "openai"
    assert verify_password("password123", loaded)
    assert not verify_password("bad-password", loaded)


def test_default_admin_password_can_be_overridden(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMPT_POLISHER_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("PROMPT_POLISHER_ADMIN_PASSWORD", "local-dev-only")
    settings = load_stored_settings()

    assert verify_password("local-dev-only", settings)
    assert not verify_password("admin", settings)
