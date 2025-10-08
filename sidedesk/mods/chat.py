"""
Chat Module for SideDesk.
Multi-user chat with optional Ollama assistant participation.
Commands:
    $ attach ollama                Attach with current model
    $ attach ollama model <name>   Switch + attach specific model
    $ detach ollama                Detach assistant
Updated by: Claude Sonnet 4.5
Ollama integration rename + commands by: GPT5 on 2025-10-07
Date: 10-06-25
"""

import random
from deskapp import Module, callback, Keys
from sidedesk.client.manager import (
    chat_local,
    status as client_status
)

Chat_ID = random.random()


class Chat(Module):
    """Chat room with optional Ollama responder."""
    name = "Chat"

    def __init__(self, app):
        super().__init__(app, Chat_ID)
        self.colors = [
            "white", "green", "red", "blue", "yellow"
        ]
        self.user_colors = {}
        self.scroll_offset = 0
        # Store bot state in app.data for persistence
        if 'ollama_attached' not in self.app.data:
            self.app.data['ollama_attached'] = False
        if 'last_message_count' not in self.app.data:
            self.app.data['last_message_count'] = 0
        self.is_ai_responding = False

    def page(self, panel):
        self.index = 1
        st = client_status()

        ai_status = ""
        if self.app.data.get('ollama_attached'):
            client = self.app.data.get('ollama_client')
            if client and client.IsConnected():
                ai_status = f" | Ollama: {client.model}"
            else:
                ai_status = " | Ollama: offline"

        header = (
            f"Chat ({'online' if st.get('logged_in') else 'offline'}"
            f"{ai_status})"
        )
        self.write(panel, self.index, 2, header, "yellow")
        self.index += 1

        lines = []
        for entry in self.app.data.get('chat_log', []):
            u = entry.get('user', '?')
            t = entry.get('text', '')
            color = self._color_for(u)
            lines.append((f"{u}: {t}", color))

        max_lines = max(0, self.h - self.index - 1)
        start = max(0, len(lines) - max_lines - self.scroll_offset)
        view = lines[start:start + max_lines]

        y = self.index
        for text, color in view:
            truncated = text[:self.w - 2]
            self.write(panel, y, 1, truncated, color)
            y += 1

        self.CheckForNewMessages()

    def _color_for(self, user: str):
        if user not in self.user_colors:
            idx = (len(self.user_colors) % len(self.colors))
            self.user_colors[user] = self.colors[idx]
        return self.user_colors[user]

    def handle_text(self, input_string: str):
        """Handle user input - regular chat or commands."""
        me = client_status().get('username') or 'me'
        text = input_string.strip()
        if not text:
            return

        if text.startswith("$ "):
            self.HandleCommand(text[2:])
        else:
            chat_local(me, text)
            self.scroll_offset = 0

    def HandleCommand(self, command: str):
        """
        Handle special commands.

        Args:
            command: Command text after $
        """
        raw = command.strip()
        cmd = raw.lower()

    # Added model-specific attach 2025-10-07 by GPT5
        if cmd.startswith("attach ollama model "):
            parts = raw.split()
            if len(parts) >= 4:
                model_name = " ".join(parts[3:]).strip()
            else:
                chat_local(
                    "System",
                    "Usage: $ attach ollama model <name>"
                )
                return

            client = self.app.data.get('ollama_client')
            if not client:
                chat_local("System", "Ollama not initialized")
                return
            if not client.IsConnected():
                chat_local("System", "Ollama offline - check server")
                return

            # Fetch available models and attempt switch
            models = client.ListModels()
            if model_name not in models:
                if models:
                    sample = ", ".join(models[:6])
                    chat_local(
                        "System",
                        f"Model not found: {model_name}. "
                        f"Available: {sample}"
                    )
                else:
                    chat_local(
                        "System",
                        "No models. Pull one: ollama pull llama3.2"
                    )
                return

            if not client.SwitchModel(model_name):
                chat_local(
                    "System",
                    f"Failed to switch to model {model_name}"
                )
                return

            self.app.data['ollama_attached'] = True
            self.app.data['last_message_count'] = len(
                self.app.data.get('chat_log', [])
            )
            chat_local(
                "System",
                f"Ollama ({client.model}) attached to chat"
            )
            return

        if cmd == "attach ollama":
            client = self.app.data.get('ollama_client')
            if not client:
                chat_local("System", "Ollama not initialized")
                return

            if not client.IsConnected():
                chat_local("System", "Ollama offline - check server")
                return

            self.app.data['ollama_attached'] = True
            self.app.data['last_message_count'] = len(
                self.app.data.get('chat_log', [])
            )
            chat_local(
                "System",
                f"Ollama ({client.model}) attached to chat"
            )

        elif cmd == "detach ollama":
            if self.app.data.get('ollama_attached'):
                self.app.data['ollama_attached'] = False
                chat_local("System", "Ollama detached from chat")
            else:
                chat_local("System", "Ollama not attached")
        else:
            chat_local("System", f"Unknown command: $ {command}")

    def CheckForNewMessages(self):
        """Check for new messages and respond if Ollama attached."""
        if not self.app.data.get('ollama_attached'):
            return

        if self.is_ai_responding:
            return

        chat_log = self.app.data.get('chat_log', [])
        current_count = len(chat_log)
        last_count = self.app.data.get('last_message_count', 0)

        if current_count <= last_count:
            return

        new_messages = chat_log[last_count:]
        self.app.data['last_message_count'] = current_count

        for msg in new_messages:
            user = msg.get('user', '')
            text = msg.get('text', '')

            if user in ['Ollama', 'System']:
                continue

            if text.startswith("$"):
                continue

            self.RespondToMessage(user, text)
            break

    def RespondToMessage(self, user: str, message: str):
        """
        Generate AI response to a message.

        Args:
            user: Username who sent message
            message: Message text
        """
        client = self.app.data.get('ollama_client')
        if not client or not client.IsConnected():
            self.app.data['ollama_attached'] = False
            chat_local("System", "Ollama disconnected - detaching")
            return

        if self.is_ai_responding:
            chat_local(
                "System",
                "Ollama busy - wait for current response"
            )
            return

        try:
            self.is_ai_responding = True
            response = ""

            for chunk in client.Chat(message, stream=True):
                response += chunk

            self.is_ai_responding = False

            chat_local("Ollama", response)
            self.scroll_offset = 0
            self.app.data['last_message_count'] = len(
                self.app.data.get('chat_log', [])
            )

        except Exception as e:
            self.is_ai_responding = False
            self.app.data['ollama_attached'] = False
            chat_local("System", f"Ollama error: {str(e)}")

    @callback(Chat_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        """Scroll up one line if possible."""
        total = len(self.app.data.get('chat_log', []))
        max_lines = max(0, self.h - 3)
        if total > max_lines:
            self.scroll_offset = min(
                self.scroll_offset + 1,
                total - max_lines
            )

    @callback(Chat_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        """Scroll down one line."""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
