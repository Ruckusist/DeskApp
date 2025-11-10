from deskapp import App, Module, callback, Keys
import random

HelloID = random.random()

class Hello(Module):
    name = "Hello"

    def __init__(self, app):
        super().__init__(app, HelloID)

    def page(self, panel):
        self.write(panel, 2, 2, "Hello, DeskApp!", self.front.color_white)
        self.write(panel, 4, 2, "Press Q to quit", self.front.color_white)

if __name__ == "__main__":
    app = App(modules=[Hello], title="Hello World", demo_mode=False)
