import random
from deskapp import Module, callback, Keys

Log_ID = random.random()
class Log(Module):
    name = "Log"
    def __init__(self, app):
        super().__init__(app, Log_ID)

    def page(self, panel):
        self.index = 1
        self.write(panel, self.index, 2, "Chat Log", "yellow")
        self.index += 1
        # Render chat log oldest->newest
        lines = [f"{e.get('user', '?')}: {e.get('text','')}" for e in self.app.data.get('chat_log', [])]
        self.render_lines(panel, lines, start_line=self.index)
