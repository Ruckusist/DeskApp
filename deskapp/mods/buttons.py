import random
from jinja2 import Environment
from deskapp import Module, callback, Keys


buttonsID = random.random()
class Buttons(Module):
    name = "Buttons"
    def __init__(self, app):
        self.classID = buttonsID
        super().__init__(app)
        self.register_module()
        

    def page(self, panel=None):
        page = f"""{self.mouse_pos} {self.mouseClick}"""
        # template = self.templates_stock.get_template("about.j2")
        template = Environment().from_string(page)
        return template.render(context=self.context)

    def mouse_decider(self, mouse_input):
        super().mouse_decider(mouse_input)
        if self.mouseClick[0]==1:
            self.print(f"left click! @ {self.mouse_pos}")
        elif self.mouseClick[1]==1:
            self.print(f"middle click! @ {self.mouse_pos}")
        elif self.mouseClick[2]==1:
            self.print(f"right click! @ {self.mouse_pos}")

    @callback(buttonsID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("Pressed the enter button")
