import random
from deskapp import Module, callback, Keys

Test_ID = random.random()
class Test(Module):
    name = "Test"
    def __init__(self, app):
        super().__init__(app, Test_ID)

    def page(self, panel):
        self.write(panel, 2, 2, "Test Window (placeholder)", "yellow")
