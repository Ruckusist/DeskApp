import random
from deskapp import Module, callback, Keys
from deskapp.apis import get_provider


Ollama_ID = random.random()


class Ollama(Module):
    name = "Ollama"

    def __init__(self, app):
        super().__init__(app, Ollama_ID)
        self.models = []
        self.sel = 0
        self.provider = None

    def _load(self):
        cls = get_provider("ollama")
        self.provider = cls() if cls else None
        self.models = self.provider.list_models() if self.provider else []
        # normalize to just names if provider returns tuples
        names = [m[0] if isinstance(m, (list, tuple)) and m else m for m in self.models]
        self.models = names
        # pick first as selected; default stored in app.data
        default = self.app.data.get('ollama_default')
        if default in self.models:
            self.sel = self.models.index(default)
        else:
            self.sel = 0

    def page(self, panel):
        if self.provider is None:
            self._load()
        self.index = 2
        title = "Ollama models (choose default with Enter)"
        self.write(panel, self.index, 2, title, "yellow")
        self.index += 1
        status = self.provider.status() if self.provider else "unavailable"
        self.write(panel, self.index, 4, f"Status: {status}", "white")
        self.index += 1
        cur = self.app.data.get('ollama_default')
        self.write(panel, self.index, 4, f"Current default: {cur or '-'}", "green")
        self.index += 1

        # Vertical selector
        start_y = self.index + 1
        max_rows = max(0, self.h - start_y - 1)
        if not self.models:
            self.write(panel, start_y, 4, "No models found. Is Ollama running?", "red")
            return
        view = self.models[:max_rows]
        for i, name in enumerate(view):
            color = "green" if i == self.sel else "white"
            prefix = "> " if i == self.sel else "  "
            self.write(panel, start_y + i, 4, f"{prefix}{name}", color)

    @callback(Ollama_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        if self.models:
            self.sel = (self.sel - 1) % len(self.models)

    @callback(Ollama_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        if self.models:
            self.sel = (self.sel + 1) % len(self.models)

    @callback(Ollama_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.models:
            chosen = self.models[self.sel]
            # Store in app state for other modules (e.g., Users) to use
            self.app.data['ollama_default'] = chosen
            self.app.print(f"Ollama default set to: {chosen}")

    @callback(Ollama_ID, Keys.R)
    def on_R(self, *args, **kwargs):
        # Refresh provider and list
        self._load()
