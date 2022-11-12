import random
from jinja2 import Environment
from deskapp import Module, callback, Keys


buttonsID = random.random()
class Buttons(Module):
    name = "Buttons"
    def __init__(self, app):
        super().__init__(app)
        self.classID = buttonsID
        self.register_module()

    def page(self, panel=None):
        page = f"""Click the mouse on the screen.
        
    Topleft is screen topleft. x is rows, y is cols.
    as its supposed to be.\n
    [L,M,R]  (x,y) coords 
    {self.mouseClick}  {self.mouse_pos}"""
        template = Environment().from_string(page)
        return template.render(context=self.context)

    def mouse_decider(self, mouse_input):
        # TODO: this super mouse? whats its job? this feels wrong.
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
