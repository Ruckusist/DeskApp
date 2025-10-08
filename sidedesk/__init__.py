"""Sidedesk package init.

Renamed AI module export to Ollama on 2025-10-07 by GPT5.
"""

from .mods import (
    Login,
    Status,
    Users,
    Chat,
    Log,
    Settings,
    Test,
    Ollama,
)

# Re-export client API for convenience if needed later
from .client import manager as client

__all__ = [
    "Login",
    "Status",
    "Users",
    "Chat",
    "Log",
    "Settings",
    "Test",
    "Ollama",
    "client",
]
