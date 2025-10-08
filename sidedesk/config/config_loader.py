"""
Config Loader for SideDesk AI Backend
Loads and manages TOML configuration
Created by: Claude Sonnet 4.5
Date: 10-06-25
"""

import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """
    Configuration loader for SideDesk AI backend.
    Handles TOML config file loading and defaults.
    """

    def __init__(
        self,
        config_path: Optional[str] = None
    ):
        """
        Initialize config loader.

        Args:
            config_path: Path to config file
        """
        self.config_path = config_path or self.GetDefaultPath()
        self.config: Dict[str, Any] = {}
        self.LoadConfig()

    @staticmethod
    def GetDefaultPath() -> str:
        """
        Get default config path.

        Returns:
            Default config file path
        """
        return os.path.expanduser("~/.sidedesk/config.toml")

    def LoadConfig(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if successful
        """
        if not os.path.exists(self.config_path):
            self.config = self.GetDefaults()
            return False

        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                self.config = self.GetDefaults()
                return False

        try:
            with open(self.config_path, "rb") as f:
                self.config = tomllib.load(f)
            return True
        except Exception:
            self.config = self.GetDefaults()
            return False

    @staticmethod
    def GetDefaults() -> Dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Default config dict
        """
        return {
            "ollama": {
                "host": "http://localhost:11434",
                "default_model": "llama3.2",
                "temperature": 0.7,
                "context_window": 4096
            },
            "vector_store": {
                "persist_directory": "~/.sidedesk/embeddings",
                "collection_name": "sidedesk_knowledge",
                "embedding_model": "nomic-embed-text"
            },
            "mcp": {
                "enabled_servers": [
                    "filesystem",
                    "terminal",
                    "git"
                ]
            },
            "ai": {
                "system_prompt": (
                    "You are a helpful AI assistant in SideDesk."
                ),
                "max_history_turns": 10,
                "stream_responses": True
            }
        }

    def Get(
        self,
        section: str,
        key: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """
        Get configuration value.

        Args:
            section: Config section name
            key: Optional key within section
            default: Default value if not found

        Returns:
            Config value or default
        """
        if section not in self.config:
            return default

        if key is None:
            return self.config[section]

        return self.config[section].get(key, default)

    def Set(self, section: str, key: str, value: Any) -> bool:
        """
        Set configuration value.

        Args:
            section: Config section name
            key: Key within section
            value: Value to set

        Returns:
            True if successful
        """
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value
        return True

    def SaveConfig(self) -> bool:
        """
        Save configuration to file.

        Returns:
            True if successful
        """
        try:
            import tomli_w
        except ImportError:
            return False

        try:
            os.makedirs(
                os.path.dirname(self.config_path),
                exist_ok=True
            )
            with open(self.config_path, "wb") as f:
                tomli_w.dump(self.config, f)
            return True
        except Exception:
            return False

    def GetOllamaConfig(self) -> Dict[str, Any]:
        """
        Get Ollama configuration.

        Returns:
            Ollama config dict
        """
        return self.Get("ollama", default={})

    def GetVectorStoreConfig(self) -> Dict[str, Any]:
        """
        Get vector store configuration.

        Returns:
            Vector store config dict
        """
        return self.Get("vector_store", default={})

    def GetMCPConfig(self) -> Dict[str, Any]:
        """
        Get MCP configuration.

        Returns:
            MCP config dict
        """
        return self.Get("mcp", default={})

    def GetAIConfig(self) -> Dict[str, Any]:
        """
        Get AI configuration.

        Returns:
            AI config dict
        """
        return self.Get("ai", default={})
