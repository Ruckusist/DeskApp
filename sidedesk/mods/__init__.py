"""Sidedesk modules package.

AI module renamed to Ollama on 2025-10-07 by GPT5.
"""

from .login import Login
from .status import Status
from .users import Users
from .chat import Chat
from .log import Log
from .settings import Settings
from .test import Test
from .ollama import Ollama

__all__ = [
    "Login",
    "Status",
    "Users",
    "Chat",
    "Log",
    "Settings",
    "Test",
    "Ollama",
]
