import random
from deskapp import Module, callback, Keys

Buttons_ID = random.random()
class Buttons(Module):
    name = "Buttons"
    def __init__(self, app):
        super().__init__(app, Buttons_ID)
        self.elements = ['this', 'that', 'other']
        self.index = 1

    def page(self, panel):
        panel.win.addstr(2,2, "Button zone.")
        self.index = 3
        h_index = 0
        for index, element in enumerate(self.elements):
            color = self.front.chess_white if index is not self.cur_el else self.front.chess_black
            panel.win.addstr(self.index, 2+h_index, element, color)
            h_index += 1 + len(element)
        self.index += 1
        

    @callback(Buttons_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("Pressed Enter Button!BUTTONS! Lets GOOO!!!!")