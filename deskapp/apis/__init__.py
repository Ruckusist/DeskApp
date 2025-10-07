"""
Shared provider API for Deskapp.

This module exposes a small registry and base class so both deskapp and
Sidedesk can access providers uniformly (e.g., ollama, gemini, openai).
"""

from .base import Provider
from .registry import get_provider, list_providers

__all__ = ["Provider", "get_provider", "list_providers"]
