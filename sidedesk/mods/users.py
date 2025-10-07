import random
from deskapp import Module, callback, Keys
from deskapp.apis import get_provider
from sidedesk.client.manager import status as client_status, add_bot, bot_say

Users_ID = random.random()


class Users(Module):
    name = "Users"

    def __init__(self, app):
        super().__init__(app, Users_ID)
        # Horizontal selector state
        self.providers = ["ollama", "gemini", "openai", "hugface"]
        self.sel = 0

    def page(self, panel):
        self.index = 2
        st = client_status()
        heading = f"Users ({'logged in' if st.get('logged_in') else 'not logged in'})"
        self.write(panel, self.index, 2, heading, "yellow")
        self.index += 2

        # Horizontal selector row
        y = self.index
        x = 4
        for i, name in enumerate(self.providers):
            label = f"[ {name} ]" if i == self.sel else f"  {name}  "
            color = "green" if i == self.sel else "white"
            if x + len(label) > self.w - 2:
                break
            self.write(panel, y, x, label, color)
            x += len(label) + 2
        self.index += 2

        users = self.app.data.get('users', [])
        if not users:
            msg = "No users online." if not st.get('logged_in') else "Logged in, waiting for user list…"
            self.write(panel, self.index, 4, msg, "blue")
        else:
            for u in users:
                self.write(panel, self.index, 4, f"• {u}", "white")
                self.index += 1

    @callback(Users_ID, Keys.LEFT)
    def on_left(self, *args, **kwargs):
        self.sel = (self.sel - 1) % len(self.providers)

    @callback(Users_ID, Keys.RIGHT)
    def on_right(self, *args, **kwargs):
        self.sel = (self.sel + 1) % len(self.providers)

    @callback(Users_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        name = self.providers[self.sel]
        cls = get_provider(name)
        if cls is None:
            self.print(f"element clicked: {name}")
            return
        provider = cls()
        status = provider.status()
        self.print(f"element clicked: {name} -> {status}")
        if name in ('ollama', 'gemini'):
            # Shared logic: pick stored default or first available model
            default_key = f"{name}_default"
            model = self.app.data.get(default_key)
            if not model:
                try:
                    models = provider.list_models()
                    # Ollama may return tuples; Gemini returns list of str
                    models = [m[0] if isinstance(m, (list, tuple)) and m else m for m in models]
                    model = models[0] if models else None
                except Exception:
                    model = None
            if model:
                bot_name = model
                add_bot(bot_name, 'standard', provider=name)
                greeting = "Hello, I'm your Gemini bot." if name == 'gemini' else "Hello, I'm your Ollama bot. Ask me something!"
                bot_say(bot_name, greeting)
