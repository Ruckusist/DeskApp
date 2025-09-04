import random
from deskapp import Module, callback, Keys

Fire_ID = random.random()
class Fire(Module):
    name = "Fire"
    def __init__(self, app):
        super().__init__(app, Fire_ID)

    def page(self, panel):
        panel.win.addstr(2,2, "Fire zone.")

    @callback(Fire_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("Pressed Enter Button!FIRE! Lets GOOO!!!!")