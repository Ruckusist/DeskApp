import random
from deskapp import Module
from deskapp.apis import get_provider


OpenAI_ID = random.random()


class OpenAI(Module):
    name = "OpenAI"

    def __init__(self, app):
        super().__init__(app, OpenAI_ID)

    def page(self, panel):
        self.index = 2
        self.write(panel, self.index, 2, "OpenAI (placeholder)", "yellow")
        self.index += 2
        cls = get_provider("openai")
        status = cls().status() if cls else "unavailable"
        self.write(panel, self.index, 4, f"Provider status: {status}", "white")
