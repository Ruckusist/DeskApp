#!/usr/bin/env python3
"""
Ollama Chat Application using DeskApp

A simple chat interface that connects to Ollama for AI conversations.
Shows only main, info, and input panels for a clean chat experience.

Features:
- Connect to local Ollama instance
- Send and receive messages with word wrapping
- Scrollable chat history
- Clean, minimal interface

Controls:
- TAB - Enter text input mode
- ENTER - Send message (in input mode)
- ESC - Cancel input (in input mode)
- UP/DOWN - Scroll chat history
- Q - Quit application

Usage:
    python ollama.py

Requirements:
    pip install ollama

Created: 2025-10-20 by Claude 3.5 Sonnet
"""

import textwrap
import time
import random
from typing import List, Tuple, Optional

import deskapp
from deskapp import App, Module, callback, Keys

try:
    import ollama
except ImportError:
    print("Error: ollama package not installed.")
    print("Please install it with: pip install ollama")
    exit(1)

OllamaID = random.random()


class OllamaChat(Module):
    """Main Ollama chat module with scrollable conversation display."""

    name = "Ollama Chat"

    def __init__(self, app):
        super().__init__(app, OllamaID)

        # Chat state
        self.messages: List[dict] = []  # Full conversation history
        self.wrapped_lines: List[Tuple[str, str]] = []  # (text, color) for display
        self.scroll_offset = 0
        self.input_text = ""
        self.is_responding = False
        self.last_user_message = ""

        # Ollama configuration
        self.model = "gpt-oss"  # Default model
        self.ollama_host = "http://localhost:11434"  # Default Ollama host
        self.max_history = 50  # Keep last 50 messages

        # Word wrap settings
        self.wrap_width = 70  # Will be updated based on panel width
        self.last_panel_width = 0

        # Test Ollama connection
        self._test_connection()

        # Add welcome message
        self.add_message("system", f"Ollama Chat started. Model: {self.model}")
        self.add_message("system", "Type a message and press ENTER to chat.")

    def _test_connection(self):
        """Test connection to Ollama and get available models."""
        try:
            # Try to list models to test connection
            models_response = ollama.list()
            available_models = [model['name'] for model in models_response.get('models', [])]

            if not available_models:
                self.add_message("error", "No models found. Install one with: ollama pull llama3.2")
                return False

            # Use first available model if default not found
            if self.model not in available_models:
                self.model = available_models[0]
                self.add_message("system", f"Using available model: {self.model}")

            return True

        except Exception as e:
            self.add_message("error", f"Failed to connect to Ollama: {str(e)}")
            self.add_message("error", "Make sure Ollama is running: ollama serve")
            return False

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        timestamp = time.strftime("%H:%M:%S")

        # Add to full history
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        self.messages.append(message)

        # Trim history if too long
        if len(self.messages) > self.max_history:
            # Keep system messages at start, trim user/assistant messages
            system_msgs = [m for m in self.messages if m["role"] == "system"]
            other_msgs = [m for m in self.messages if m["role"] != "system"]

            # Keep last 40 non-system messages
            if len(other_msgs) > 40:
                other_msgs = other_msgs[-40:]

            self.messages = system_msgs + other_msgs

        # Force rewrap on next render and scroll to bottom for new messages
        self.last_panel_width = 0
        self.scroll_offset = 0  # Auto-scroll to bottom to see new message

    def _wrap_messages(self, panel_width: int):
        """Wrap all messages for display based on panel width."""
        self.wrapped_lines.clear()
        self.wrap_width = max(40, panel_width - 4)  # Leave margins

        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]
            timestamp = msg["timestamp"]

            # Choose color based on role
            if role == "user":
                color = "cyan"
                prefix = f"[{timestamp}] You: "
            elif role == "assistant":
                color = "green"
                prefix = f"[{timestamp}] AI: "
            elif role == "error":
                color = "red"
                prefix = f"[{timestamp}] ERROR: "
            else:  # system
                color = "yellow"
                prefix = f"[{timestamp}] "

            # Wrap the content
            full_text = prefix + content
            wrapped = textwrap.wrap(
                full_text,
                width=self.wrap_width,
                subsequent_indent="    "  # Indent continuation lines
            )

            # Add wrapped lines with color
            for line in wrapped:
                self.wrapped_lines.append((line, color))

            # Add blank line between messages (except for consecutive system messages)
            if (role != "system" or
                (len(self.wrapped_lines) >= 2 and self.wrapped_lines[-2][1] != "yellow")):
                self.wrapped_lines.append(("", "white"))

    def _clamp_scroll(self, visible_lines: int):
        """Ensure scroll offset is within valid range."""
        max_scroll = max(0, len(self.wrapped_lines) - visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def page(self, panel):
        """Render the chat conversation with scrolling."""
        h, w = self.h, self.w

        # Rewrap if panel size changed
        if w != self.last_panel_width:
            self._wrap_messages(w)
            self.last_panel_width = w

        # Calculate visible area
        header_lines = 2
        visible_lines = h - header_lines

        # Title
        status = "responding..." if self.is_responding else "ready"
        title = f"Ollama Chat ({self.model}) - {status}"
        panel.win.addstr(1, 2, title, self.front.color_white)

        # Scroll info
        if self.wrapped_lines:
            total_lines = len(self.wrapped_lines)
            showing_start = max(0, total_lines - visible_lines - self.scroll_offset)
            showing_end = min(total_lines, showing_start + visible_lines)
            scroll_info = f"Lines {showing_start+1}-{showing_end} of {total_lines}"
            if self.scroll_offset > 0:
                scroll_info += f" (scroll: +{self.scroll_offset})"
        else:
            scroll_info = "No messages"

        # Right-align scroll info
        info_x = max(2, w - len(scroll_info) - 2)
        panel.win.addstr(2, info_x, scroll_info, self.front.color_cyan)

        # Clamp scroll and render messages
        self._clamp_scroll(visible_lines)

        if self.wrapped_lines:
            # Show most recent messages at bottom, allow scrolling up
            total = len(self.wrapped_lines)
            start_idx = max(0, total - visible_lines - self.scroll_offset)
            end_idx = min(total, start_idx + visible_lines)

            visible_msgs = self.wrapped_lines[start_idx:end_idx]

            # Render from top of available space
            row = header_lines + 1
            for text, color in visible_msgs:
                if row >= h - 1:  # Leave space at bottom
                    break

                # Color mapping
                if color == "cyan":
                    color_attr = self.front.color_cyan
                elif color == "green":
                    color_attr = self.front.color_green
                elif color == "red":
                    color_attr = self.front.color_red
                elif color == "yellow":
                    color_attr = self.front.color_yellow
                else:
                    color_attr = self.front.color_white

                # Truncate if too long
                display_text = text[:w-4] if len(text) > w-4 else text
                panel.win.addstr(row, 2, display_text, color_attr)
                row += 1

    def PageInfo(self, panel):
        """Show chat status in info panel."""
        # Connection status
        panel.win.addstr(0, 2, f"Model: {self.model}", self.front.color_white)

        # Message count
        user_msgs = len([m for m in self.messages if m["role"] == "user"])
        ai_msgs = len([m for m in self.messages if m["role"] == "assistant"])
        panel.win.addstr(1, 2, f"Messages: {user_msgs} sent, {ai_msgs} received",
                        self.front.color_cyan)

        # Controls
        controls = "TAB=type, ↑↓=scroll, Q=quit"
        panel.win.addstr(2, 2, controls, self.front.color_yellow)

    def _send_message(self, message: str):
        """Send a message to Ollama."""
        if not message.strip():
            return

        # Add user message immediately
        self.add_message("user", message)

        # Send to Ollama
        try:
            self.is_responding = True

            # Prepare conversation context (last 10 messages for context)
            context_messages = []
            for msg in self.messages[-10:]:
                if msg["role"] in ["user", "assistant"]:
                    context_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=context_messages,
                stream=False
            )

            # Add AI response
            ai_response = response.get('message', {}).get('content', 'No response')
            self.add_message("assistant", ai_response)

        except Exception as e:
            self.add_message("error", f"Ollama error: {str(e)}")
        finally:
            self.is_responding = False

    # =========================================================================
    # CALLBACKS - Input handling and controls
    # =========================================================================

    def handle_text(self, input_string: str):
        """Handle text input from the user."""
        message = input_string.strip()
        if message:
            self._send_message(message)
        else:
            self.add_message("system", "Empty message - nothing sent")

    @callback(OllamaID, Keys.TAB)
    def enter_input_mode(self, *args, **kwargs):
        """TAB enters text input mode."""
        if not self.front.key_mode:
            self.front.key_mode = True
            self.input_text = ""
            self.add_message("system", "Input mode - type your message and press ENTER")

    @callback(OllamaID, Keys.ESC)
    def cancel_input(self, *args, **kwargs):
        """ESC cancels input mode."""
        if self.front.key_mode:
            self.front.key_mode = False
            self.print("Input canceled")

    @callback(OllamaID, Keys.UP)
    def scroll_up(self, *args, **kwargs):
        """UP arrow scrolls chat history up."""
        self.scroll_offset += 3
        # Clamping handled in render

    @callback(OllamaID, Keys.DOWN)
    def scroll_down(self, *args, **kwargs):
        """DOWN arrow scrolls chat history down."""
        self.scroll_offset = max(0, self.scroll_offset - 3)

    @callback(OllamaID, Keys.PG_UP)
    def page_up(self, *args, **kwargs):
        """Page Up scrolls faster."""
        self.scroll_offset += 10

    @callback(OllamaID, Keys.PG_DOWN)
    def page_down(self, *args, **kwargs):
        """Page Down scrolls faster."""
        self.scroll_offset = max(0, self.scroll_offset - 10)

    @callback(OllamaID, Keys.HOME)
    def scroll_to_top(self, *args, **kwargs):
        """Home goes to top of conversation."""
        self.scroll_offset = len(self.wrapped_lines)

    @callback(OllamaID, Keys.END)
    def scroll_to_bottom(self, *args, **kwargs):
        """End goes to bottom of conversation."""
        self.scroll_offset = 0

    @callback(OllamaID, Keys.Q)
    def quit_app(self, *args, **kwargs):
        """Q quits the application."""
        self.logic.should_stop = True


def main():
    """Create and run the Ollama chat application."""
    # Create app with minimal UI - only main, info, and input panels
    app = App(
        modules=[OllamaChat],
        title="Ollama Chat",
        name="ollama-chat",
        demo_mode=False,  # No demo modules

        # Show only essential panels
        show_main=True,
        show_info_panel=True,
        show_messages=True,  # This becomes the input area

        # Hide other panels for clean interface
        show_header=False,
        show_footer=False,
        show_menu=False,
        show_right_panel=False,
        show_floating=False,

        # Adjust splits for better chat layout
        h_split=0.2,  # More space for chat
        v_split=0.0,  # No left panel needed
    )


if __name__ == "__main__":
    main()
