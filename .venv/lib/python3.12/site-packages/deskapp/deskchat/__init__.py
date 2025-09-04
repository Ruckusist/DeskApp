"""Deskchat package init (migrated from Sidedesk)."""

from .mods import (
    Login,
    Status,
    Users,
    Chat,
    Log,
    Settings,
    Test,
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
    "client",
]
