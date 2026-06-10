"""Application entry point."""
import flet as ft
from prompt_polisher.ui.app_view import build_app

def main() -> None:
    ft.app(target=build_app)

if __name__ == "__main__":
    main()
