import random, os, threading, time
from deskapp import Module, Keys, callback


class Fire_:
    def __init__(self, size):
        self.w, self.h = size
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
        w = self.w
        h = self.h
        b = self.b
        size = self.size
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
        # while self.should_continue:
        while True:
            if self.breaker: break
            try:
                self.one_pass()
                time.sleep(0.01)
            except Exception as e:
                self.gameboard = [str(e), ['this is not working']]
        self.is_running = False
        self.breaker = False


classID = random.random()
class Fire(Module):
    """My Cool Fire Animation."""

    name = "Fire"

    def __init__(self, app):
        super().__init__(app)
        self.started = False
        self.start_flag = 0
        self.background_process = True
        self.classID = classID
        self.register_module()
        self.fire = None

    @callback(classID, Keys.ENTER)   
    def on_enter(self, *args, **kwargs):
        if not self.fire:
            self.fire = Fire_((
            int(self.app.frontend.winright_upper_dims[1] - 2),
            int(self.app.frontend.winright_upper_dims[0] - 2)
        ))

        # TURN OFF
        if self.fire.is_running:
            if not self.fire.breaker: 
                self.fire.breaker = True

        # TURN ON
        if not self.fire.is_running:
            self.background_thread = threading.Thread(target=self.fire.multipass)
            self.background_thread.start()

    def end_safely(self):
        if self.fire:
            self.fire.breaker = True

    def page(self, panel) -> None:
        max_w = int(self.app.frontend.winright_upper_dims[1] - 2)
        max_h = int(self.app.frontend.winright_upper_dims[0] - 2)

        if self.fire:
            for index, line in enumerate(reversed(self.fire.gameboard)):
                if max_h <=1: break
                # panel.addstr(max_h, 1, f"{''.join(line)[:max_w]}")
                for index_y, char in enumerate(line):
                    panel.addstr(max_h, index_y+1, char, 
                    self.app.frontend.curses.color_pair(4) if char == '@' else (self.app.frontend.curses.color_pair(2) if char in ["^", "~", "*", "|"] else self.app.frontend.curses.color_pair(5)))
                max_h -= 1
        else:
            panel.addstr(1, 1, "Press Enter to Start/Stop the Fire.")
