"""
SideDesk Backend Module
Backend services for AI integration
Created by: Claude Sonnet 4.5
Date: 10-06-25
"""

from .ollama_client import OllamaClient
from .vector_store import VectorStore
from .mcp_manager import MCPManager

__all__ = [
    "OllamaClient",
    "VectorStore",
    "MCPManager",
]
