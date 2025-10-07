import random
from deskapp import Module
from deskapp.apis import get_provider


Hugface_ID = random.random()


class Hugface(Module):
    name = "Hugface"

    def __init__(self, app):
        super().__init__(app, Hugface_ID)

    def page(self, panel):
        self.index = 2
        self.write(panel, self.index, 2, "Hugface (placeholder)", "yellow")
        self.index += 2
        cls = get_provider("hugface")
        status = cls().status() if cls else "unavailable"
        self.write(panel, self.index, 4, f"Provider status: {status}", "white")
