"""Sidedesk package init."""

from .mods import (
	Login,
	Status,
	Users,
	Chat,
	Log,
	Settings,
	Test,
	Ollama,
	Gemini,
	OpenAI,
	Hugface,
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
	"Gemini",
	"OpenAI",
	"Hugface",
	"client",
]
