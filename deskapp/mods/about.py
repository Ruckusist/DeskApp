import random
from deskapp import Module, callback, Keys

About_ID = random.random()
class About(Module):
    name = "About"
    def __init__(self, app):
        super().__init__(app, About_ID)

    def page(self, panel):
        self.write(panel, 1, 1, "This is working", color="yellow")

    @callback(About_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("Welcome to the about page!")

