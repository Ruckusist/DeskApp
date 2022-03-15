import random, threading
import deskapp


ClassID = random.random()
class Game_Map(deskapp.Module):
    name = "The Game Map"
    def __init__(self, app):
        super().__init__(app)

        self.elements = ['Global', 'Region', 'Local']
        self.index = 1  # Verticle Print Position
        # LAST THING!
        self.register_module()

    def page(self, panel):
        panel.addstr(1,1,"Game Map")
        self.index = 3  # reset this to the top of the box every round

        # HORIZONTAL SCROLLER
        h_index = 0  # HORIZONTAL index
        for index, element in enumerate(self.elements):
            color = self.frontend.chess_white if index is not self.cur_el else self.frontend.color_rw
            panel.addstr(self.index, 2+h_index, element, color)
            h_index += 1 + len(element)

        self.index += 1  # increment the Verticle Print Position
        panel.addstr(self.index, 4, "Map Goes Here", self.frontend.chess_white)

        return False