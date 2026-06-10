# Prompt Polisher Desktop

Prompt Polisher is a packaged Flet desktop application for rewriting unclear Japanese or English prompts into structured, higher-quality prompts.

This version is designed for non-technical end users:

- Users launch the app from a normal desktop icon or executable.
- Users do not need VS Code, a terminal, `.env` files, Python knowledge, or Ollama.
- A developer/admin logs in once from **Admin Settings**, saves the provider API key and model, and normal users only paste prompts.
- The app supports OpenAI-compatible APIs by default and still keeps Ollama as an optional local provider.

## What changed in this packaged version

1. Added a local admin settings store at `prompt_polisher/settings_store.py`.
2. Added an **Admin Settings** tab with password login, provider selection, model selection, base URL, API key storage, and admin password change.
3. Removed API key entry from the normal user workflow.
4. Added `src/main.py` as the Flet build entry point.
5. Updated `pyproject.toml` with Flet packaging metadata so `flet build windows`, `flet build macos`, or `flet build linux` can create desktop builds.
6. Exported files now go to the user's Documents folder instead of the source directory.

## First admin login

The initial admin password is:

```text
admin
```

Change it immediately in **Admin Settings** before distributing the app.

## Developer build commands

Install dependencies in a clean environment:

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run locally during development:

```bash
python -m prompt_polisher
```

Build a Windows desktop app on Windows:

```bash
flet build windows
```

Build a macOS desktop app on macOS:

```bash
flet build macos
```

Build a Linux desktop app on Linux:

```bash
flet build linux
```

Flet's official publishing documentation says `flet build` packages a Flet app into a standalone executable or installable package. Windows builds must be run on Windows and may require Visual Studio with the Desktop development with C++ workload.

## Security boundary

This desktop package stores settings on the local machine. That is acceptable for a small internal/offline desktop utility, but it is not the same as a real multi-user SaaS backend.

For broad external distribution, the safer architecture is:

```text
Desktop app -> your backend API -> LLM provider
```

In that architecture, provider keys live only on your server, not inside every desktop installation.
