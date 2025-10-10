"""
Chat Module for SideDesk.
Multi-user chat with optional Ollama assistant participation.
Commands:
    $ attach ollama                Attach with current model
    $ attach ollama model <name>   Switch + attach specific model
    $ detach ollama                Detach assistant

Updated by: Claude Sonnet 4.5
Ollama integration rename + commands by: GPT5 on 2025-10-07
Refactor: wrapping/scrolling + BotWorker by GitHub Copilot on 2025-10-09
Profile scroller spacing + attach helper by GitHub Copilot on 2025-10-09
"""

import random
import textwrap
from typing import Optional

from deskapp import Module, callback, Keys
from sidedesk.client.manager import (
    chat_local,
    status as client_status,
)
from sidedesk.backend.bot_worker import BotWorker
from sidedesk.backend import OllamaClient
from sidedesk.config.config_loader import ConfigLoader

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
        self.wrap_width = 0
        self.last_wrap_count = -1
        self.wrapped_lines = []
        self.profile_index = 0
        self.is_ai_responding = False

        data = self.app.data
        if "ollama_attached" not in data:
            data["ollama_attached"] = False
        if "last_message_count" not in data:
            data["last_message_count"] = 0
        if "bot_worker" not in data:
            data["bot_worker"] = None
        if "bot_pending" not in data:
            data["bot_pending"] = {"job_id": 0, "text": ""}

        loader = ConfigLoader()
        if "ollama_profiles" not in data:
            data["ollama_profiles"] = loader.ListOllamaProfiles()
        if "ollama_profile_index" not in data:
            data["ollama_profile_index"] = (
                self._detect_profile_index(loader)
            )
        self.profile_index = data.get("ollama_profile_index", 0)

    def page(self, panel):
        self.index = 1
        status = client_status()

        ai_status = ""
        if self.app.data.get("ollama_attached"):
            client = self.app.data.get("ollama_client")
            if client and client.IsConnected():
                ai_status = f" | Ollama: {client.model}"
            else:
                ai_status = " | Ollama: offline"

        pending = self.app.data.get(
            "bot_pending",
            {"job_id": 0, "text": ""}
        )
        if pending.get("job_id"):
            ai_status += " [typing…]"

        header = (
            f"Chat ({'online' if status.get('logged_in') else 'offline'}"
            f"{ai_status})"
        )
        self.write(panel, self.index, 2, header, "yellow")
        self.index += 1

        if self.index < self.h - 1:
            self.index += 1

        self._draw_profile_scroller(panel)

        self._poll_bot_stream()
        self._rebuild_wrap_cache_if_needed()
        visible = max(0, self.h - self.index - 1)
        self._clamp_scroll_offset(visible)
        total = len(self.wrapped_lines)
        start = max(0, total - visible - self.scroll_offset)
        view = self.wrapped_lines[start:start + visible]

        row = self.index
        for text, color in view:
            self.write(panel, row, 1, text, color)
            row += 1

        self.CheckForNewMessages()

    def _color_for(self, user: str):
        if user not in self.user_colors:
            idx = (len(self.user_colors) % len(self.colors))
            self.user_colors[user] = self.colors[idx]
        return self.user_colors[user]

    def handle_text(self, input_string: str):
        """Handle user input - regular chat or commands."""
        me = client_status().get("username") or "me"
        text = input_string.strip()
        if not text:
            return

        if text.startswith("$ "):
            self.HandleCommand(text[2:])
        else:
            chat_local(me, text)
            self.scroll_offset = 0
            self.last_wrap_count = -1

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

            client = self.app.data.get("ollama_client")
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
                        f"Model not found: {model_name}. Available: {sample}"
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

            self._attach_current_profile()
            return

        if cmd == "attach ollama":
            self._attach_current_profile()
            return

        if cmd == "detach ollama":
            if self.app.data.get("ollama_attached"):
                self.app.data["ollama_attached"] = False
                chat_local("System", "Ollama detached from chat")
                worker = self.app.data.get("bot_worker")
                if worker:
                    worker.cancel()
                    worker.detach_client()
            else:
                chat_local("System", "Ollama not attached")
            return

        chat_local("System", f"Unknown command: $ {command}")

    def CheckForNewMessages(self):
        """Check for new messages and respond if Ollama attached."""
        if not self.app.data.get("ollama_attached"):
            return

        # legacy busy flag remains, but worker will queue
        if self.is_ai_responding:
            return

        chat_log = self.app.data.get("chat_log", [])
        current_count = len(chat_log)
        last_count = self.app.data.get("last_message_count", 0)

        if current_count <= last_count:
            return

        new_messages = chat_log[last_count:]
        self.app.data["last_message_count"] = current_count

        for msg in new_messages:
            user = msg.get("user", "")
            text = msg.get("text", "")

            if user in ["Ollama", "System"]:
                continue

            if text.startswith("$"):
                continue

            self.RespondToMessage(user, text)
            break

    def RespondToMessage(self, user: str, message: str):
        """Generate AI response to a message."""
        client = self.app.data.get("ollama_client")
        if not client or not client.IsConnected():
            self.app.data["ollama_attached"] = False
            chat_local("System", "Ollama disconnected - detaching")
            return

        # Submit to background worker
        worker = self.app.data.get("bot_worker")
        if not worker:
            worker = BotWorker()
            worker.start()
            self.app.data["bot_worker"] = worker
        worker.attach_client(client)

        job_id = worker.submit(user, message)
        self.app.data["bot_pending"] = {"job_id": job_id, "text": ""}
        # optional typing indicator (commented to avoid spam)
        # chat_local("System", "Ollama is typing…")
        self.scroll_offset = 0
        self.last_wrap_count = -1

    @callback(Chat_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        """Scroll up by one wrapped line."""
        self.scroll_offset += 1
        self._clamp_scroll_offset()

    @callback(Chat_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        """Scroll down one wrapped line."""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
        self._clamp_scroll_offset()

    @callback(Chat_ID, Keys.PG_UP)
    def on_pg_up(self, *args, **kwargs):
        """Page up by viewport height."""
        viewport = max(1, self.h - 4)
        self.scroll_offset += viewport
        self._clamp_scroll_offset()

    @callback(Chat_ID, Keys.PG_DOWN)
    def on_pg_down(self, *args, **kwargs):
        """Page down by viewport height."""
        viewport = max(1, self.h - 4)
        self.scroll_offset = max(0, self.scroll_offset - viewport)
        self._clamp_scroll_offset()

    @callback(Chat_ID, Keys.HOME)
    def on_home(self, *args, **kwargs):
        """Jump to top of history."""
        self._rebuild_wrap_cache_if_needed()
        max_lines = max(0, self.h - 2)
        total = len(self.wrapped_lines)
        self.scroll_offset = max(0, total - max_lines)

    @callback(Chat_ID, Keys.END)
    def on_end(self, *args, **kwargs):
        """Jump to bottom (follow tail)."""
        self.scroll_offset = 0

    @callback(Chat_ID, Keys.LEFT)
    def on_left(self, *args, **kwargs):
        """Cycle Ollama profile left."""
        self._cycle_profile(-1)

    @callback(Chat_ID, Keys.RIGHT)
    def on_right(self, *args, **kwargs):
        """Cycle Ollama profile right."""
        self._cycle_profile(1)

    @callback(Chat_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        """Attach current profile via scroller selection."""
        self._attach_current_profile()

    # ----- internals -----
    def _rebuild_wrap_cache_if_needed(self):
        """Reflow chat_log into wrapped display lines if needed."""
        width = max(1, self.w - 2)
        chat_log = self.app.data.get("chat_log", [])
        if (width == self.wrap_width and
                len(chat_log) == self.last_wrap_count):
            return

        # include in-progress streaming text as a temporary message
        pending = self.app.data.get(
            "bot_pending",
            {"job_id": 0, "text": ""}
        )
        if pending.get("job_id") and pending.get("text"):
            tmp_log = list(chat_log) + [{
                "user": "Ollama",
                "text": pending.get("text", "")
            }]
        else:
            tmp_log = chat_log

        wrapped = []
        for entry in tmp_log:
            user = entry.get("user", "?")
            text = entry.get("text", "")
            color = self._color_for(user)
            prefix = f"{user}: "
            indent = " " * len(prefix)
            raw_parts = str(text).splitlines() or [""]
            parts = []
            prev_blank = False
            for part in raw_parts:
                is_blank = (part.strip() == "")
                if is_blank and prev_blank:
                    continue
                parts.append(part)
                prev_blank = is_blank
            first = True
            for part in parts:
                head = prefix if first else indent
                wrapper = textwrap.TextWrapper(
                    width=width,
                    expand_tabs=True,
                    replace_whitespace=False,
                    drop_whitespace=False,
                    break_long_words=True,
                    subsequent_indent=indent,
                )
                # wrap head+part so first line includes prefix
                lines = wrapper.wrap(head + part)
                for line in lines:
                    wrapped.append((line, color))
                first = False

        self.wrapped_lines = wrapped
        self.wrap_width = width
        self.last_wrap_count = len(chat_log)

    def _poll_bot_stream(self):
        """Drain stream queue and aggregate into a single reply."""
        worker = self.app.data.get("bot_worker")
        if not worker:
            return
        chunks = worker.fetch_stream()
        if not chunks:
            return
        pending = self.app.data.get(
            "bot_pending",
            {"job_id": 0, "text": ""}
        )
        cur_id = pending.get("job_id", 0)
        text_accum = pending.get("text", "")
        changed = False

        for msg in chunks:
            if msg.get("id") != cur_id:
                # ignore stale chunks for old jobs
                continue
            if msg.get("error"):
                self.app.data["ollama_attached"] = False
                chat_local("System", msg.get("text", "error"))
                text_accum = ""
                cur_id = 0
                changed = True
                break
            if not msg.get("done"):
                piece = msg.get("text", "")
                if piece:
                    text_accum += piece
                    changed = True
            else:
                # finalize
                final = text_accum
                if final:
                    chat_local("Ollama", final)
                self.app.data["last_message_count"] = len(
                    self.app.data.get("chat_log", [])
                )
                text_accum = ""
                cur_id = 0
                changed = True

        if not changed:
            return

        if cur_id:
            self.app.data["bot_pending"] = {
                "job_id": cur_id,
                "text": text_accum,
            }
        else:
            self.app.data["bot_pending"] = {"job_id": 0, "text": ""}

        self.wrap_width = 0

    def _draw_profile_scroller(self, panel):
        """Render horizontal profile scroller under header."""
        profiles = self.app.data.get("ollama_profiles", [])
        selected = self.app.data.get("ollama_profile_index", 0)
        row = self.index
        col = 2
        if profiles and row < self.h - 1:
            for idx, profile in enumerate(profiles):
                name = profile.get("name", f"Profile {idx + 1}")
                text = f"  {name}  "
                color = "yellow" if idx == selected else "cyan"
                max_len = max(0, self.w - 3 - col)
                if max_len <= 0:
                    break
                truncated = text[:max_len]
                self.write(panel, row, col, truncated, color)
                col += len(truncated)
            self.index += 1
            if self.index < self.h - 1:
                hint = "Left/Right selects • Enter attaches"
                hint = hint[:self.w - 4]
                self.write(panel, self.index, 2, hint, "white")
                self.index += 1
        if self.index < self.h - 1:
            self.index += 1

    def _cycle_profile(self, delta: int):
        profiles = self.app.data.get("ollama_profiles", [])
        if not profiles:
            return
        current = self.app.data.get("ollama_profile_index", 0)
        count = len(profiles)
        new_idx = (current + delta) % count
        self._apply_profile(new_idx)

    def _apply_profile(self, idx: int) -> bool:
        profiles = self.app.data.get("ollama_profiles", [])
        if not profiles:
            return False
        idx = max(0, min(idx, len(profiles) - 1))
        profile = profiles[idx]
        host = profile.get("host", "").strip()
        model = profile.get("default_model", "").strip()
        name = profile.get("name", "Profile")
        self.app.data["ollama_profile_index"] = idx
        self.profile_index = idx
        if not host or not model:
            self.print(
                f"{name}: configure host/model in config loader first"
            )
            return False
        loader = ConfigLoader()
        base = loader.GetOllamaConfig()
        temperature = base.get("temperature", 0.7)
        context = base.get("context_window", 4096)
        client = OllamaClient(
            host=host,
            model=model,
            temperature=temperature,
            context_window=context
        )
        self.app.data["ollama_client"] = client
        worker = self.app.data.get("bot_worker")
        if worker:
            worker.detach_client()
        self.app.data["ollama_attached"] = False
        self.print(f"Switched Ollama profile -> {name}")
        return True

    def _detect_profile_index(self, loader: ConfigLoader) -> int:
        profiles = loader.ListOllamaProfiles()
        current = loader.GetOllamaConfig()
        host = current.get("host", "").strip()
        model = current.get("default_model", "").strip()
        for idx, profile in enumerate(profiles):
            if (profile.get("host") == host and
                    profile.get("default_model") == model):
                return idx
        return 0

    def _clamp_scroll_offset(self, visible_lines: Optional[int] = None):
        """Ensure scroll_offset stays within valid bounds."""
        self._rebuild_wrap_cache_if_needed()
        if visible_lines is None:
            visible_lines = max(0, self.h - 4)
        total = len(self.wrapped_lines)
        max_offset = max(0, total - visible_lines)
        if self.scroll_offset > max_offset:
            self.scroll_offset = max_offset
        if self.scroll_offset < 0:
            self.scroll_offset = 0
        return max_offset

    def _attach_current_profile(self) -> bool:
        client = self.app.data.get("ollama_client")
        if not client:
            chat_local("System", "Ollama not initialized")
            return False
        if not client.IsConnected():
            chat_local("System", "Ollama offline - check server")
            return False

        worker = self.app.data.get("bot_worker")
        if not worker:
            worker = BotWorker()
            worker.start()
            self.app.data["bot_worker"] = worker
        worker.attach_client(client)

        self.app.data["ollama_attached"] = True
        self.app.data["last_message_count"] = len(
            self.app.data.get("chat_log", [])
        )
        chat_local(
            "System",
            f"Ollama ({client.model}) attached to chat"
        )
        return True
