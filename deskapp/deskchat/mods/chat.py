import random
from deskapp import Module, callback, Keys
from deskapp.deskchat.client.manager import chat_local, status as client_status


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

    def page(self, panel):
        self.index = 1
        st = client_status()
        header = f"Chat ({'online' if st.get('logged_in') else 'offline'})"
        self.write(panel, self.index, 2, header, "yellow")
        self.index += 1
        # render chat messages oldest -> newest, scrollable
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
        # For now, local echo only; server broadcast can be added later
        chat_local(me, text)
        # Nudge view to bottom when sending
        self.scroll_offset = 0

    @callback(Chat_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        # Scroll up one line if possible
        total = len(self.app.data.get('chat_log', []))
        max_lines = max(0, self.h - 3)
        if total > max_lines:
            self.scroll_offset = min(self.scroll_offset + 1, total - max_lines)

    @callback(Chat_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        # Scroll down one line
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
