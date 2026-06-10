# Build and Distribution Guide

## Goal

Create a one-time downloadable desktop app for users who are not familiar with coding. End users should not use VS Code, command prompt, Python commands, `.env`, or Ollama.

## Recommended release model

Use Flet's desktop packaging flow:

```bash
flet build windows
flet build macos
flet build linux
```

Build each platform on its matching operating system. Windows builds are run on Windows; macOS builds are run on macOS; Linux builds are run on Linux.

## Windows developer machine prerequisites

Windows builds can require:

- Windows 10/11 64-bit
- Python 3.10+
- Flet dependencies
- Visual Studio with “Desktop development with C++” workload
- Windows Developer Mode if symlink support errors appear

## First-run admin setup

1. Open the packaged app.
2. Go to **Admin Settings**.
3. Log in with the initial password: `admin`.
4. Set provider to `openai`.
5. Paste the organization/provider API key once.
6. Set the model, for example `gpt-4o-mini` for cost efficiency or a stronger OpenAI-compatible model for higher quality.
7. Change the admin password to a private password of at least 8 characters.
8. Click **Save admin settings**.
9. Restart the app before giving it to normal users.

## Normal user flow

1. Open Prompt Polisher from the desktop/app launcher.
2. Paste a rough prompt.
3. Optionally add clarification notes.
4. Click **Analyze and optimize**.
5. Copy or export the result.

## Important security limitation

This implementation hides the API key from the normal UI and stores it in the local per-user app-data folder. It does not provide central user management, payment controls, usage metering, or server-side secret isolation.

For public distribution or many external customers, use a backend service:

```text
Prompt Polisher desktop client
        ↓
WeLive backend authentication + usage limits + logging
        ↓
OpenAI-compatible provider
```

That backend should own the provider key, enforce rate limits, log usage, and return only the model output to the desktop app.
