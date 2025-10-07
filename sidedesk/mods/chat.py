import random
import os
from textwrap import wrap
from typing import Any
from deskapp import Module, callback, Keys
from sidedesk.client.manager import send_chat, status as client_status, bot_say
from deskapp.apis import get_provider

Chat_ID = random.random()
class Chat(Module):
    name = "Chat"
    def __init__(self, app):
        super().__init__(app, Chat_ID)
        self.colors = [
            "white","green","red","blue","yellow"
        ]
        self.user_colors = {}
        self.scroll_offset = 0  # lines from bottom
        # Response mode selector (horizontal)
        self.modes = ["standard", "corperate", "loop"]
        self.mode_idx = 0
        self.app.data["bot_mode"] = self.modes[self.mode_idx]

    def page(self, panel):
        self.index = 1
        st = client_status()
        header = f"Chat ({'online' if st.get('logged_in') else 'offline'})"
        self.write(panel, self.index, 2, header, "yellow")
        self.index += 1
        # Horizontal mode menu
        y = self.index
        x = 2
        for i, name in enumerate(self.modes):
            label = f"[ {name} ]" if i == self.mode_idx else f"  {name}  "
            color = "green" if i == self.mode_idx else "white"
            if x + len(label) > self.w - 2:
                break
            self.write(panel, y, x, label, color)
            x += len(label) + 2
        self.index += 1
        # render chat messages oldest -> newest, with wrapping and scroll
        wrapped = self._get_wrapped_lines()
        max_lines = max(0, self.h - self.index - 1)
        start = max(0, len(wrapped) - max_lines - self.scroll_offset)
        view = wrapped[start:start + max_lines]
        y = self.index
        for text, color in view:
            self.write(panel, y, 1, text, color)
            y += 1

    def _color_for(self, user: str):
        if user not in self.user_colors:
            idx = (len(self.user_colors) % len(self.colors))
            self.user_colors[user] = self.colors[idx]
        return self.user_colors[user]

    def handle_text(self, input_string: str):
        me = client_status().get('username') or 'me'
        text = input_string.strip()
        if not text:
            return
        # Send to server (manager handles fallback local echo)
        send_chat(me, text)
        self.scroll_offset = 0  # jump view to bottom
        # Standard mode still generates provider replies locally (temporary)
        if self.modes[self.mode_idx] != "standard":
            return
        bots_store = self.app.data.get('bots', {})
        bots = list(bots_store.keys())
        if not bots:
            return
        history_entries = self.app.data.get('chat_log', [])
        history = "\n".join(
            f"{e.get('user', '?')}: {e.get('text', '')}" for e in history_entries
        )
        last_line = history_entries[-1]['text'] if history_entries else ''
        debug = os.getenv('CHAT_DEBUG') not in (None, '', '0', 'false', 'False')
        providers_cache: dict[str, Any] = {}

        def _prov(name: str):
            if name not in providers_cache:
                cls_ = get_provider(name)
                providers_cache[name] = cls_() if cls_ else None
            return providers_cache[name]

        for bot_name in bots:
            meta = bots_store.get(bot_name, {})
            target_provider_key = meta.get('provider') or 'ollama'
            provider_obj = _prov(target_provider_key)
            if not provider_obj:
                if target_provider_key != 'gemini':
                    provider_obj = _prov('gemini')
                if not provider_obj:
                    continue
            try:
                if target_provider_key == 'gemini':
                    final_prompt = history
                else:
                    final_prompt = f"{history}\n{bot_name}:"
                reply = provider_obj.response(final_prompt, model=bot_name)
                if not reply and target_provider_key == 'gemini':
                    reply = provider_obj.response(last_line, model=bot_name)
                if reply:
                    bot_say(bot_name, reply.strip())
                    self.scroll_offset = 0
                elif debug:
                    self.app.print(f"[chat-debug] No reply from {target_provider_key}:{bot_name}")
            except Exception as e:
                if debug:
                    self.app.print(f"[chat-debug] error {target_provider_key}:{bot_name} -> {e}")
                continue

    @callback(Chat_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        # Scroll up one wrapped line if possible
        total = len(self._get_wrapped_lines())
        max_lines = max(0, self.h - 3)
        if total > max_lines:
            self.scroll_offset = min(self.scroll_offset + 1, total - max_lines)

    @callback(Chat_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        # Scroll down one wrapped line
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    @callback(Chat_ID, Keys.LEFT)
    def on_left(self, *args, **kwargs):
        # Move selection left in mode menu
        self.mode_idx = (self.mode_idx - 1) % len(self.modes)
        self.app.data["bot_mode"] = self.modes[self.mode_idx]

    @callback(Chat_ID, Keys.RIGHT)
    def on_right(self, *args, **kwargs):
        # Move selection right in mode menu
        self.mode_idx = (self.mode_idx + 1) % len(self.modes)
        self.app.data["bot_mode"] = self.modes[self.mode_idx]

    # ---- helpers ----
    def _get_wrapped_lines(self):
        max_w = max(1, self.w - 2)
        out = []
        for entry in self.app.data.get('chat_log', []):
            user = entry.get('user', '?')
            text = str(entry.get('text', ''))
            color = self._color_for(user)
            prefix = f"{user}: "
            avail = max(1, max_w - len(prefix))
            # Wrap text for first line using available width after prefix
            parts = wrap(text, width=avail, break_long_words=True, replace_whitespace=False)
            if not parts:
                out.append((prefix, color))
                continue
            # First line with prefix
            out.append((prefix + parts[0], color))
            # Subsequent lines with indent equal to prefix length
            indent = " " * len(prefix)
            cont_w = max(1, max_w - len(indent))
            for p in parts[1:]:
                # If any piece exceeds cont_w due to wrap behavior, slice defensively
                if len(p) > cont_w:
                    p = p[:cont_w]
                out.append((indent + p, color))
        return out
