import deskapp
import random

classIDEx1 = random.random()
class Ex1(deskapp.Module):
    name = "Example 1"
    def __init__(self, app):
        super().__init__(app)
        self.classID = classIDEx1

        self.register_module()

    def page(self, panel):
        panel.addstr(1,1,"Example One.")
        return False

if __name__ == "__main__":
    app = deskapp.App([Ex1])
    app.start()