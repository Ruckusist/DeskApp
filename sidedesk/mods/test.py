import random
from deskapp import Module, callback, Keys

Test_ID = random.random()
class Test(Module):
    name = "Test"
    def __init__(self, app):
        super().__init__(app, Test_ID)

    # TODO: This is supposed to create a floating window over the top of other panels.
    #       Not sure how to do that yet. Work on this.
    # TODO: This panel should come in 2 different tests, one should be a accept/cancel
    #       dialog, the other should be a text input dialog.

    def page(self, panel):
        self.write(panel, 2, 2, "Test Window (placeholder)", "yellow")
