"""Flet UI for Prompt Polisher."""

from datetime import datetime
from pathlib import Path
import os
import traceback

import flet as ft

from prompt_polisher.config import load_config
from prompt_polisher.core.models import PromptAnalysis
from prompt_polisher.core.service import PromptOptimizationService
from prompt_polisher.i18n.messages import t
from prompt_polisher.providers.base import ProviderError
from prompt_polisher.providers.factory import create_provider
from prompt_polisher.settings_store import (
    DEFAULT_ADMIN_PASSWORD,
    StoredSettings,
    load_stored_settings,
    make_password_record,
    mask_secret,
    save_stored_settings,
    verify_password,
)


def analysis_to_markdown(result: PromptAnalysis) -> str:
    lines: list[str] = []

    sections = result.sections or []
    for s in sections:
        if s.issue or s.recommendation:
            lines.append(
                f"### {s.name}\n"
                f"- Current detail: {s.content or '(not specified)'}\n"
                f"- Improvement note: {s.recommendation or s.issue or '-'}"
            )

    warnings = result.warnings or []
    if warnings:
        lines.append("### Notes\n" + "\n".join(f"- {w}" for w in warnings))

    return "\n\n".join(lines) if lines else "No major improvement notes."


def build_app(page: ft.Page) -> None:
    config = load_config()
    stored_settings = load_stored_settings()
    locale = config.locale
    admin_logged_in = False

    page.title = "Prompt Polisher"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 1120
    page.window_height = 900

    status = ft.Text(t(locale, "ready"), selectable=True)
    detected_text = ft.Text(f"{t(locale, 'detected')}: -", selectable=True)
    system_status = ft.Text(selectable=True)

    input_field = ft.TextField(
        label=t(locale, "input"),
        multiline=True,
        min_lines=8,
        max_lines=14,
        expand=True,
        autofocus=True,
    )

    clarification_field = ft.TextField(
        label=t(locale, "clarifications"),
        multiline=True,
        min_lines=2,
        max_lines=5,
        expand=True,
    )

    optimized_en = ft.TextField(
        label=t(locale, "optimized_en"),
        multiline=True,
        read_only=True,
        expand=True,
        min_lines=18,
        max_lines=35,
    )

    optimized_ja = ft.TextField(
        label=t(locale, "optimized_ja"),
        multiline=True,
        read_only=True,
        expand=True,
        min_lines=18,
        max_lines=35,
        visible=False,
    )

    questions_md = ft.Markdown(
        "",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
    )

    analysis_md = ft.Markdown(
        "",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
    )

    # Admin controls. API key stays out of the normal user workflow.
    admin_password_field = ft.TextField(
        label="Admin password",
        password=True,
        can_reveal_password=True,
        width=260,
    )
    admin_login_status = ft.Text(selectable=True)
    admin_panel = ft.Column(visible=False, spacing=12)

    admin_provider = ft.Dropdown(
        label="Provider",
        value=stored_settings.provider,
        width=260,
        options=[
            ft.dropdown.Option("openai", "OpenAI-compatible API"),
            ft.dropdown.Option("ollama", "Ollama local"),
        ],
    )
    admin_api_key = ft.TextField(
        label="OpenAI-compatible API key",
        password=True,
        can_reveal_password=True,
        width=420,
        hint_text="Leave blank to keep the existing saved key.",
    )
    admin_base_url = ft.TextField(
        label="OpenAI-compatible base URL",
        value=stored_settings.openai_base_url,
        width=420,
    )
    admin_openai_model = ft.TextField(
        label="OpenAI-compatible model",
        value=stored_settings.openai_model,
        width=280,
    )
    admin_ollama_url = ft.TextField(
        label="Ollama URL",
        value=stored_settings.ollama_base_url,
        width=280,
    )
    admin_ollama_model = ft.TextField(
        label="Ollama model",
        value=stored_settings.ollama_model,
        width=280,
    )
    admin_locale = ft.Dropdown(
        label="UI language",
        value=stored_settings.locale,
        width=180,
        options=[ft.dropdown.Option("ja", "Japanese"), ft.dropdown.Option("en", "English")],
    )
    admin_new_password = ft.TextField(
        label="New admin password",
        password=True,
        can_reveal_password=True,
        width=300,
        hint_text="Strongly recommended after first login.",
    )
    admin_save_status = ft.Text(selectable=True)

    def active_settings() -> StoredSettings:
        return load_stored_settings()

    def refresh_system_status() -> None:
        settings = active_settings()
        current_model = settings.ollama_model if settings.provider == "ollama" else settings.openai_model
        if settings.provider == "openai":
            key_state = mask_secret(settings.openai_api_key)
            system_status.value = f"Provider: OpenAI-compatible API | Model: {current_model} | API key: {key_state}"
        else:
            system_status.value = f"Provider: Ollama local | Model: {current_model} | URL: {settings.ollama_base_url}"

    def selected_model(settings: StoredSettings) -> str:
        if settings.provider == "ollama":
            return (settings.ollama_model or "qwen2.5:7b").strip()
        return (settings.openai_model or "gpt-4o-mini").strip()

    def run_optimization(_: ft.ControlEvent) -> None:
        status.value = "Running..."
        optimized_en.value = ""
        optimized_ja.value = ""
        questions_md.value = ""
        analysis_md.value = ""
        page.update()

        try:
            settings = active_settings()
            selected_provider = settings.provider or "openai"
            model = selected_model(settings)

            if selected_provider == "openai" and not (settings.openai_api_key or "").strip():
                status.value = (
                    "This app has not been fully set up yet. "
                    "Please ask your WeLive helper to finish the setup."
                )
                page.update()
                return

            provider = create_provider(
                selected_provider,
                settings.openai_api_key or "",
                settings.openai_base_url or "https://api.openai.com/v1",
                settings.ollama_base_url or "http://localhost:11434",
            )

            result = PromptOptimizationService(provider).optimize(
                input_field.value or "",
                model,
                clarification_field.value or "",
            )

            detected_text.value = f"{t(locale, 'detected')}: {result.detected_language}"

            optimized_en.value = (
                result.optimized_prompt_en
                or "No optimized prompt was generated. Try a clearer prompt or a stronger model."
            )

            optimized_ja.value = result.optimized_prompt_ja or ""
            optimized_ja.visible = bool(result.optimized_prompt_ja)

            questions = result.clarification_questions or []
            questions_md.value = "\n".join(f"- {q}" for q in questions) if questions else "-"

            try:
                analysis_md.value = analysis_to_markdown(result)
            except Exception:
                analysis_md.value = "Improvement notes could not be displayed."

            status.value = "Done."

        except ProviderError as exc:
            error_text = str(exc)

            if "insufficient_quota" in error_text or "429" in error_text:
                status.value = (
                    "The app connection is not available right now. "
                    "Please ask your WeLive helper to check the setup."
                )
            else:
                status.value = error_text

        except Exception as exc:
            status.value = f"Unexpected error: {exc}"
            analysis_md.value = f"```text\n{traceback.format_exc()}\n```"

        page.update()

    async def copy_text(value: str) -> None:
        if value:
            await page.set_clipboard_async(value)
            status.value = "Copied to clipboard."
            page.update()

    def export_prompt(_: ft.ControlEvent) -> None:
        export_dir = Path.home() / "Documents" / "PromptPolisherExports"
        export_dir.mkdir(parents=True, exist_ok=True)

        path = export_dir / f"optimized-prompt-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"

        path.write_text(
            "\n".join(
                [
                    "# Optimized English Prompt",
                    optimized_en.value or "",
                    "",
                    "# Japanese Translation",
                    optimized_ja.value or "",
                    "",
                    "# Clarification Questions",
                    questions_md.value or "",
                    "",
                    "# Improvement Notes",
                    analysis_md.value or "",
                ]
            ),
            encoding="utf-8",
        )

        status.value = f"Exported to {path}"
        page.update()

    def clear(_: ft.ControlEvent) -> None:
        for field in [input_field, clarification_field, optimized_en, optimized_ja]:
            field.value = ""

        analysis_md.value = ""
        questions_md.value = ""
        optimized_ja.visible = False
        detected_text.value = f"{t(locale, 'detected')}: -"
        status.value = t(locale, "ready")
        page.update()

    def admin_login(_: ft.ControlEvent) -> None:
        nonlocal admin_logged_in
        settings = active_settings()
        if verify_password(admin_password_field.value or "", settings):
            admin_logged_in = True
            admin_panel.visible = True
            admin_login_status.value = "Admin unlocked. Configure provider settings below."
            if not settings.admin_password_hash:
                admin_login_status.value += (
                    f" Default password is '{DEFAULT_ADMIN_PASSWORD}'. Change it before distribution."
                )
        else:
            admin_logged_in = False
            admin_panel.visible = False
            admin_login_status.value = "Invalid admin password."
        page.update()

    def save_admin_settings(_: ft.ControlEvent) -> None:
        if not admin_logged_in:
            admin_save_status.value = "Log in as admin before saving."
            page.update()
            return

        settings = active_settings()
        settings.provider = admin_provider.value or "openai"
        settings.locale = admin_locale.value or "ja"
        settings.openai_base_url = (admin_base_url.value or "https://api.openai.com/v1").strip()
        settings.openai_model = (admin_openai_model.value or "gpt-4o-mini").strip()
        settings.ollama_base_url = (admin_ollama_url.value or "http://localhost:11434").strip()
        settings.ollama_model = (admin_ollama_model.value or "qwen2.5:7b").strip()

        new_key = (admin_api_key.value or "").strip()
        if new_key:
            settings.openai_api_key = new_key
            admin_api_key.value = ""

        new_password = (admin_new_password.value or "").strip()
        if new_password:
            if len(new_password) < 8:
                admin_save_status.value = "Admin password must be at least 8 characters."
                page.update()
                return
            settings.admin_password_salt, settings.admin_password_hash = make_password_record(new_password)
            admin_new_password.value = ""

        path = save_stored_settings(settings)
        refresh_system_status()
        admin_save_status.value = f"Saved settings to {path}. Restart is recommended after language changes."
        page.update()

    admin_panel.controls = [
        ft.Text("Provider configuration", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([admin_provider, admin_locale], wrap=True),
        ft.Row([admin_base_url, admin_openai_model], wrap=True),
        admin_api_key,
        ft.Row([admin_ollama_url, admin_ollama_model], wrap=True),
        admin_new_password,
        ft.ElevatedButton("Save admin settings", icon=ft.Icons.SAVE, on_click=save_admin_settings),
        admin_save_status,
        ft.Text(
            "Security note: this desktop package stores settings on the local machine. "
            "For a truly centralized multi-user SaaS setup, move API calls to a server-side backend "
            "and never ship provider keys inside client apps.",
            selectable=True,
        ),
    ]

    refresh_system_status()

    user_tab = ft.Column(
        [
            ft.Text(t(locale, "title"), size=30, weight=ft.FontWeight.BOLD),
            ft.Text("Paste your rough prompt below. Click Optimize. Copy the final prompt."),
            input_field,
            clarification_field,
            ft.Row(
                [
                    ft.ElevatedButton(t(locale, "run"), icon=ft.Icons.EDIT, on_click=run_optimization),
                    ft.OutlinedButton(
                        t(locale, "copy_en"),
                        on_click=lambda e: page.run_task(copy_text, optimized_en.value or ""),
                    ),
                    ft.OutlinedButton(
                        t(locale, "copy_ja"),
                        on_click=lambda e: page.run_task(copy_text, optimized_ja.value or ""),
                    ),
                    ft.OutlinedButton(t(locale, "export"), icon=ft.Icons.SAVE, on_click=export_prompt),
                    ft.TextButton(t(locale, "clear"), icon=ft.Icons.CLEAR, on_click=clear),
                ],
                wrap=True,
            ),
            status,
            detected_text,
            ft.Container(optimized_en, expand=True),
            ft.Container(optimized_ja, expand=True),
            ft.Row(
                [
                    ft.Container(
                        ft.Column([ft.Text(t(locale, "questions"), size=20, weight=ft.FontWeight.BOLD), questions_md]),
                        expand=True,
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                    ),
                    ft.Container(
                        ft.Column([ft.Text("Improvement Notes", size=20, weight=ft.FontWeight.BOLD), analysis_md]),
                        expand=True,
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=14,
        expand=True,
    )

    admin_tab = ft.Column(
        [
            ft.Text("Admin Settings", size=30, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Developer/admin login. Paste the provider key once and save it so normal users do not need coding tools, VS Code, command prompt, .env files, or Ollama.",
                selectable=True,
            ),
            ft.Row(
                [
                    admin_password_field,
                    ft.ElevatedButton("Log in", icon=ft.Icons.LOCK_OPEN, on_click=admin_login),
                ],
                wrap=True,
            ),
            admin_login_status,
            admin_panel,
        ],
        spacing=14,
        expand=True,
    )

    # Beginner-safe default: normal users see only the prompt optimizer.
    # Developer/admin settings are still available when the app is launched with
    # PROMPT_POLISHER_ADMIN_MODE=1, which the internal admin launcher uses.
    if os.getenv("PROMPT_POLISHER_ADMIN_MODE") == "1":
        # Compatibility-safe admin mode. Some Flet versions do not support
        # ft.Tab(text=...), so admin mode avoids Tabs entirely and shows both
        # sections on one scrollable page. Normal users still see only the
        # simple prompt optimizer screen.
        page.add(
            ft.Column(
                [
                    user_tab,
                    ft.Divider(),
                    admin_tab,
                ],
                spacing=24,
                expand=True,
            )
        )
    else:
        page.add(user_tab)
