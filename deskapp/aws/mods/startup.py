import random
from deskapp import Module, callback, Keys

Startup_ID = random.random()

class Startup(Module):
    name = "Startup"
    def __init__(self, app):
        super().__init__(app, Startup_ID)
        self.index = 1

    def page(self, panel):
        # Basic welcome and instructions
        panel.win.addstr(1, 2, "Deskapp AWS is ready.", self.front.color_yellow)
        panel.win.addstr(2, 2, "Press <TAB> to enter text, <Q> to quit.", self.front.color_green)
        panel.win.addstr(4, 2, "This is the Startup module.", self.front.color_cyan)

    @callback(Startup_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("Startup: Enter pressed.")

