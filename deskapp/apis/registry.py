from typing import Dict, Type, Optional

from .base import Provider
from .stubs.ollama import OllamaProvider
from .stubs.gemini import GeminiProvider
from .stubs.openai import OpenAIProvider
from .stubs.hugface import HugfaceProvider


_REGISTRY: Dict[str, Type[Provider]] = {
    "ollama": OllamaProvider,
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "hugface": HugfaceProvider,
}


def get_provider(name: str) -> Optional[Type[Provider]]:
    return _REGISTRY.get(name)


def list_providers():
    return list(_REGISTRY.keys())
