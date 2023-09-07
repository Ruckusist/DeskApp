import random
from deskapp import Module, callback, Keys

Buttons_ID = random.random()
class Buttons(Module):
    name = "Buttons"
    def __init__(self, app):
        super().__init__(app, Buttons_ID)

    def page(self, panel):
        panel.win.addstr(2,2, "Button zone.")

    @callback(Buttons_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("Pressed Enter Button!BUTTONS! Lets GOOO!!!!")