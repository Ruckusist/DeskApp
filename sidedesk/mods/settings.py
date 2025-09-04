import random
from deskapp import Module, callback, Keys

Settings_ID = random.random()
class Settings(Module):
    name = "Settings"
    def __init__(self, app):
        super().__init__(app, Settings_ID)

    def page(self, panel):
        self.write(panel, 2, 2, "Settings Window (placeholder)", "yellow")
