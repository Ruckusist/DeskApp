
"""SideDesk CLI entry point.

Updated 2025-10-06 by GitHub Copilot to stage post-login modules before
startup so additional panels appear after authentication.
Renamed AI module to Ollama and updated post-login modules list
on 2025-10-07 by GPT5.
"""

import atexit

from deskapp import App
from sidedesk import Ollama, Chat, Log, Login, Settings, Status, Test, Users
from sidedesk.client.manager import logout as client_logout


def cleanup():
    """Ensure the client logs out cleanly on application exit."""
    try:
        client_logout()
    except Exception:
        pass


def ConfigureModules(app: App) -> None:
    """Seed the modules that become available after a successful login."""
    app.data["post_login_modules"] = [
        Users,
        Chat,
        Ollama,
        Log,
        Settings,
        Test,
    ]


def main() -> None:
    """Run the SideDesk TUI application."""
    atexit.register(cleanup)

    app = App(
        name="Sidedesk",
        title="Sidedesk",
        splash_screen=False,
        demo_mode=False,
        header="Welcome to Sidedesk!",
        show_header=False,
        show_messages=False,
        show_menu=False,
        show_box=False,
        disable_header=True,

        modules=[Login, Status],
        autostart=False,
        use_mouse=False,
    )

    ConfigureModules(app)
    app.start()


if __name__ == "__main__":
    main()
