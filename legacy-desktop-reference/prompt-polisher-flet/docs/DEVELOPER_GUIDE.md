# Developer Guide

## Architecture

The app has three layers:

```text
Flet UI -> PromptOptimizationService -> Provider adapter
```

The packaged version adds:

```text
Admin Settings UI -> settings_store.py -> local app-data settings.json
```

The normal user screen never asks for API keys. The admin screen saves the OpenAI-compatible provider key once.

## Files added or changed

- `src/main.py`: Flet build entry point.
- `src/prompt_polisher/settings_store.py`: local settings persistence, admin password hash, API key storage.
- `src/prompt_polisher/config.py`: loads packaged-app settings instead of relying only on `.env`.
- `src/prompt_polisher/ui/app_view.py`: adds normal user tab and admin settings tab.
- `pyproject.toml`: adds Flet packaging metadata.
- `docs/BUILD_AND_DISTRIBUTE.md`: release instructions.

## Local settings location

- Windows: `%APPDATA%/PromptPolisher/settings.json`
- macOS: `~/Library/Application Support/PromptPolisher/settings.json`
- Linux: `~/.config/PromptPolisher/settings.json`

Set `PROMPT_POLISHER_CONFIG_DIR` during tests to redirect the settings file.

## Backend recommendation

For internal use, local settings are acceptable. For broad external distribution, create a backend API and remove provider keys from the desktop client entirely.
