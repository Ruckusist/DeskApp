import deskapp
import random

classIDEx2 = random.random()
class Ex2(deskapp.Module):
    name = "Example 2"
    def __init__(self, app):
        super().__init__(app)
        self.classID = classIDEx2

        self.elements = ['this', 'that', 'other']
        self.index = 1  # Verticle Print Position

        self.register_module()

    def page(self, panel):
        panel.addstr(1,1,"Example Two.")
        self.index = 3  # reset this to the top of the box every round

        # HORIZONTAL SCROLLER
        h_index = 0  # HORIZONTAL index
        for index, element in enumerate(self.elements):
            color = self.frontend.chess_white if index is not self.cur_el else self.frontend.color_rw
            panel.addstr(self.index, 2+h_index, element, color)
            h_index += 1 + len(element)

        self.index += 1  # increment the Verticle Print Position
        panel.addstr(self.index, 4, "NEXT THING", self.frontend.chess_white)

        return False

if __name__ == "__main__":
    app = deskapp.App([Ex2])
    app.start()