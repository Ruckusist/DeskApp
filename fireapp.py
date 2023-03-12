import random, time, threading
from onefile import App,Module,Keys,callback

class Flames:
    def __init__(self, module):
        self.parent = module
        self.h = self.parent.front.h-1
        self.w = self.parent.front.w-1
        self.size = self.w * self.h
        self.og_chars = [" ", ".", ":", "^", "*", "x", "s", "S", "#", "$"]
        self.chars = [" ", ",", "^", "~", "*", "|", "H", "$", "#", "@"]
        # self.b = [0 for x in range(self.size + self.w + 1)]
        self.b = []
        for x in range(self.size + self.w * 2 + 2):
            self.b.append(0)
            
        self.gameboard = [['*' for x in range(self.w)] for y in range(self.h)]

        self.should_continue = False
        self.counter = 0

        self.is_running = False
        self.breaker = False

    def one_pass(self):
        # credit : https://medium.com/sweetmeat/python-curses-based-ascii-art-fire-animation-259e9e007767
        w = self.parent.front.w-1
        h = self.parent.front.h-1
        b = self.b
        size = h*w
        c = self.chars
        for i in range(int(w/9)):
            b[int((random.random()*w)+w*(h-1))] = 105

        for i in range(size):
            b[i] = int((
                b[i] + b[i+1] + b[i+2] + b[i+w] + b[i+w+1] + b[i+w+2] + b[i+w*2] + b[i+w*2+1] + b[i+w*2+2]
            )/9)

            if i < size-1:
                self.gameboard[int(i/w)][i%w] = c[(9 if b[i] > 9 else b[i])]

    def multipass(self): 
        self.should_continue = True
        self.is_running = True
        while True:
            if self.breaker: break
            try:
                self.one_pass()
                time.sleep(0.01)
            except Exception as e:
                self.gameboard = ['this is not working', str(e)]
        self.is_running = False
        self.breaker = False


Fire_ID = random.random()
class Fire(Module):
    name = "FireApp"
    def __init__(self, app):
        super().__init__(app, Fire_ID)
        self.fire = Flames(self)

    def end_safely(self):
        self.fire.breaker = True

    def test_page(self, panel):
        panel.win.addstr(0,0," - FireApp - by Ruckusist", self.front.color_green)
        max_h = self.front.h
        max_y = self.front.w-1
        if not self.fire:
            panel.win.addstr(1,0,"Press Enter to Start the Fire.")
            for i, line in enumerate(range(max_h-2)):
                panel.win.addstr(max_h-1, 0, "".join([" "*(max_y)]))
                max_h -= 1
            return
        for i, line in enumerate(range(max_h-2)):
            panel.win.addstr(max_h-1, 0, "".join(["*"*(max_y)]))
            max_h -= 1

    def page(self, panel):

        panel.win.addstr(0,0," - FireApp - by Ruckusist", self.front.color_green)
        max_h = self.front.h-1
        max_y = self.front.w-1

        if not self.fire.is_running:
            panel.win.addstr(1,0,"Press Enter to Start the Fire.")
            for i, line in enumerate(range(max_h-2)):
                panel.win.addstr(max_h-1, 0, "".join([" "*(max_y)]))
                max_h -= 1
            return
        
        for i, line in enumerate(reversed(self.fire.gameboard)):
            line = "".join(line)

            for y, char in enumerate(line):
                panel.win.addstr(max_h,y,str(char),
                                 self.app.front.chess_black if char == '@' else (
                                    self.app.front.color_magenta if char in ["^", "~", "*", "|"] else (
                                        self.app.front.chess_white
                                    )))

            max_h -= 1

    @callback(Fire_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        # # Turn off
        if self.fire.is_running:
            if not self.fire.breaker: 
                self.fire.breaker=True
            self.print("Turning fire off.")
            self.fire.is_running = False

        else:
            self.flame_thread = threading.Thread(
                target=self.fire.multipass
            ).start()
            self.fire.is_running = True
            self.print("Turning fire on.")

def main():
    App(
        modules=[Fire],
        splash_screen=False,
        demo_mode=False,
        title="FireApp",
        show_footer=False,
        show_header=False,
        show_menu=False,
        show_messages=False,
        v_split=.2,
        show_box=False,
        show_banner=False
    )

if __name__ == "__main__":
    main()
