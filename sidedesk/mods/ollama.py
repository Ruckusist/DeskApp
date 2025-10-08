"""
Ollama Settings Module for SideDesk.
Lists locally installed Ollama models and lets user switch.
Original author: Claude Sonnet 4.5 (earlier AI module).
Refactored/renamed: GPT5 on 2025-10-07.
"""

import random
from deskapp import Module, callback, Keys

OllamaID = random.random()


class Ollama(Module):
    """Model management UI for Ollama (list + select)."""

    name = "Ollama"

    def __init__(self, app):
        """Initialize Ollama settings module."""
        super().__init__(app, OllamaID)
        self.available_models = []
        self.selected_index = 0
        self.current_model = "none"
        self.is_connected = False
        self.scroll_offset = 0
        self.InitializeBackend()

    def InitializeBackend(self):
        """Initialize Ollama backend and get shared client."""
        try:
            if not self.app.data.get('ollama_client'):
                from sidedesk.backend import OllamaClient
                from sidedesk.config import ConfigLoader

                config = ConfigLoader()
                ollama_config = config.GetOllamaConfig()

                self.app.data['ollama_client'] = OllamaClient(
                    host=ollama_config.get(
                        "host", "http://localhost:11434"
                    ),
                    model=ollama_config.get(
                        "default_model", "llama3.2"
                    ),
                    temperature=ollama_config.get(
                        "temperature", 0.7
                    ),
                    context_window=ollama_config.get(
                        "context_window", 4096
                    ),
                )
                self.print("Ollama backend initialized")

            self.RefreshModels()

        except Exception as e:
            self.print(f"Ollama init error: {str(e)}")

    def RefreshModels(self):
        """Refresh list of available models from Ollama."""
        try:
            client = self.app.data.get('ollama_client')
            if client:
                self.is_connected = client.IsConnected()
                if self.is_connected:
                    self.available_models = client.ListModels()
                    self.current_model = client.model
                    if self.current_model in self.available_models:
                        self.selected_index = (
                            self.available_models.index(
                                self.current_model
                            )
                        )
                else:
                    self.available_models = []
                    self.current_model = "disconnected"
        except Exception as e:
            self.print(f"Model refresh error: {str(e)}")
            self.is_connected = False
            self.available_models = []

    def page(self, panel):
        """Render Ollama model management interface."""
        self.index = 1

        status = "connected" if self.is_connected else "offline"
        header = f"Ollama Models ({status})"
        self.write(panel, self.index, 2, header, "yellow")
        self.index += 1

        if not self.is_connected:
            self.write(
                panel, self.index, 2,
                "Ollama server not reachable", "red"
            )
            self.index += 1
            self.write(
                panel, self.index, 2,
                "Start Ollama: ollama serve", "white"
            )
            return

        if not self.available_models:
            self.write(
                panel, self.index, 2,
                "No models available", "red"
            )
            self.index += 1
            self.write(
                panel, self.index, 2,
                "Pull a model: ollama pull llama3.2", "white"
            )
            return

        self.write(
            panel,
            self.index,
            2,
            f"Current: {self.current_model}",
            "green"
        )
        self.index += 1
        self.write(
            panel,
            self.index,
            2,
            "Available Models (UP/DOWN, ENTER to select, R refresh):",
            "white"
        )
        self.index += 1

        max_lines = max(0, self.h - self.index - 1)
        start = max(0, self.selected_index - max_lines + 1)
        end = start + max_lines
        visible_models = self.available_models[start:end]

        for i, model in enumerate(visible_models):
            actual_index = start + i
            if actual_index == self.selected_index:
                cursor = ">> "
                color = "yellow"
            else:
                cursor = "   "
                color = "white"

            current_marker = (
                " (active)" if model == self.current_model else ""
            )
            text = f"{cursor}{model}{current_marker}"

            if self.index < self.h - 1:
                truncated = text[:self.w - 4]
                self.write(panel, self.index, 2, truncated, color)
                self.index += 1

    def handle_text(self, input_string: str):
        """Handle text input (commands)."""
        text = input_string.strip().lower()

        if text == "refresh":
            self.RefreshModels()
            self.print("Models refreshed")
        elif text == "reconnect":
            self.InitializeBackend()
            self.print("Reconnecting...")
        else:
            self.print("Commands: refresh, reconnect")

    @callback(OllamaID, Keys.UP)
    def on_up(self, *args, **kwargs):
        """Move selection up."""
        if self.available_models:
            if self.selected_index > 0:
                self.selected_index -= 1

    @callback(OllamaID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        """Move selection down."""
        if self.available_models:
            if self.selected_index < len(self.available_models) - 1:
                self.selected_index += 1

    @callback(OllamaID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        """Select current model."""
        if (self.available_models and
            0 <= self.selected_index < len(self.available_models)):
            model = self.available_models[self.selected_index]
            client = self.app.data.get('ollama_client')
            if client and client.SwitchModel(model):
                self.current_model = model
                self.print(f"Switched to {model}")
            else:
                self.print(f"Failed to switch to {model}")

    @callback(OllamaID, Keys.R)
    def on_r(self, *args, **kwargs):
        """Refresh models list."""
        self.RefreshModels()
        self.print("Models refreshed")
