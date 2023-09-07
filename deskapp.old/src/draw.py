import time
# from deskapp import Frontend
from .frontend import Cursing

class Draw:
    def __init__(self):
        self.f = Cursing()
        self.main()

    def keypress_handler(self, keypress):
        pass

    def mouse_handler(self, keypress):
        pass

    def draw_header(self):
        dims = (10, 15, 0, 0)
        panel = self.f.make_panel(dims, "header")
        panel.win.box()
        panel.win.addstr( 1, 1, "This is WOrking!")
        panel.panel.top()


    def draw_loop(self):
        # redraw all the parts of the screen.
        # lots of if should i draw checks.
        
        # curses update stuffs
        self.f.screen.refresh()
        self.f.curses.panel.update_panels()

        # handler functionality should get moved out of here.
        self.keypress_handler( self.f.get_input() )
        # self.mouse_handler( self.f.get_click() )

        # do stuff one at a time?
        self.draw_header()
        self.f.curses.panel.update_panels()

    def main(self):
        while True:
            self.draw_loop()
            time.sleep(1)
        self.f.end_safely()