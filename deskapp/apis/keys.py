import os
from typing import Optional


_DEFAULT_DIR = "/home/ruckus/.keys"


def _env_var_name(service: str) -> str:
    # Normalize to expected env var names
    mapping = {
        'google': 'GOOGLE_API_KEY',
        'gemini': 'GOOGLE_API_KEY',  # alias for gemini
        'openai': 'OPENAI_API_KEY',
        'huggingface': 'HUGGINGFACE_API_KEY',
        'hugface': 'HUGGINGFACE_API_KEY',  # alias for provider name
    }
    return mapping.get(service.lower(), f"{service.upper()}_API_KEY")


def _file_name(service: str) -> str:
    mapping = {
        'google': 'google_api_key',
        'gemini': 'google_api_key',
        'openai': 'openai_api_key',
        'huggingface': 'huggingface_api_key',
        'hugface': 'huggingface_api_key',
    }
    return mapping.get(service.lower(), f"{service.lower()}_api_key")


def get_api_key(service: str, key_dir: Optional[str] = None) -> Optional[str]:
    """Return the API key for a service if available.

    Order: environment variable, then file in key_dir (default ~/.keys).
    """
    env = _env_var_name(service)
    val = os.getenv(env)
    if val:
        return val.strip()
    directory = key_dir or _DEFAULT_DIR
    try:
        path = os.path.join(directory, _file_name(service))
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read().strip()
    except Exception:
        return None
    return None


def has_api_key(service: str, key_dir: Optional[str] = None) -> bool:
    return bool(get_api_key(service, key_dir))
