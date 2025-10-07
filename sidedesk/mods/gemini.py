import random
from deskapp import Module, callback, Keys
from deskapp.apis import get_provider


Gemini_ID = random.random()


class Gemini(Module):
    name = "Gemini"

    def __init__(self, app):
        super().__init__(app, Gemini_ID)
        self.provider = None
        self.models = []
        self.sel = 0

    def _load(self):
        cls = get_provider("gemini")
        self.provider = cls() if cls else None
        try:
            self.models = self.provider.list_models() if self.provider else []
        except Exception:
            self.models = []
        default = self.app.data.get('gemini_default')
        if default in self.models:
            self.sel = self.models.index(default)
        else:
            self.sel = 0

    def page(self, panel):
        if self.provider is None:
            self._load()
        self.index = 2
        title = "Gemini models (choose default with Enter)"
        self.write(panel, self.index, 2, title, "yellow")
        self.index += 1
        status = self.provider.status() if self.provider else "unavailable"
        self.write(panel, self.index, 4, f"Status: {status}", "white")
        self.index += 1
        cur = self.app.data.get('gemini_default')
        self.write(panel, self.index, 4, f"Current default: {cur or '-'}", "green")
        self.index += 1

        start_y = self.index + 1
        max_rows = max(0, self.h - start_y - 1)
        if not self.models:
            self.write(panel, start_y, 4, "No models found. (Missing key or library?)", "red")
            return
        view = self.models[:max_rows]
        for i, name in enumerate(view):
            color = "green" if i == self.sel else "white"
            prefix = "> " if i == self.sel else "  "
            self.write(panel, start_y + i, 4, f"{prefix}{name}", color)

    @callback(Gemini_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        if self.models:
            self.sel = (self.sel - 1) % len(self.models)

    @callback(Gemini_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        if self.models:
            self.sel = (self.sel + 1) % len(self.models)

    @callback(Gemini_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.models:
            chosen = self.models[self.sel]
            self.app.data['gemini_default'] = chosen
            self.app.print(f"Gemini default set to: {chosen}")

    @callback(Gemini_ID, Keys.R)
    def on_R(self, *args, **kwargs):
        if self.provider:
            try:
                self.models = self.provider.list_models(refresh=True)
            except Exception:
                self.models = []
        default = self.app.data.get('gemini_default')
        if default in self.models:
            self.sel = self.models.index(default)
        else:
            self.sel = 0
