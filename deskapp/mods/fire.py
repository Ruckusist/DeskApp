import random
import time
import threading
from deskapp import Module, callback, Keys


class Flames:
    def __init__(self, module):
        self.parent = module
        self.h = self.parent.h - 1
        self.w = self.parent.w - 1
        self.size = self.w * self.h
        self.og_chars = [" ", ".", ":", "^", "*", "x", "s", "S", "#", "$"]
        self.chars = [" ", ",", "^", "~", "*", "|", "H", "$", "#", "@"]
        self.b = []
        for x in range(self.size + self.w * 2 + 2):
            self.b.append(0)

        self.gameboard = [["*" for x in range(self.w)] for y in range(self.h)]

        self.should_continue = False
        self.counter = 0

        self.is_running = False
        self.breaker = False

    def make_gameboard(self):
        self.size = self.parent.w * self.parent.h
        self.b = []
        for x in range(self.size + self.parent.w * 2 + 2):
            self.b.append(0)
        self.gameboard = [["*" for x in range(self.parent.w)]
                          for y in range(self.parent.h)]

    def one_pass(self):
        w = self.parent.w - 1
        h = self.parent.h - 1
        b = self.b
        size = h * w
        c = self.chars
        for i in range(int(w / 9)):
            b[int((random.random() * w) + w * (h - 1))] = 105

        for i in range(size):
            b[i] = int((
                b[i] + b[i + 1] + b[i + 2] + b[i + w] + b[i + w + 1] +
                b[i + w + 2] + b[i + w * 2] + b[i + w * 2 + 1] +
                b[i + w * 2 + 2]
            ) / 9)

            if i < size - 1:
                self.gameboard[int(i / w)][i % w] = c[
                    (9 if b[i] > 9 else b[i])
                ]

    def multipass(self):
        self.should_continue = True
        self.is_running = True
        while True:
            if self.breaker:
                break
            try:
                self.one_pass()
                time.sleep(0.01)
            except Exception as e:
                self.gameboard = ["this is not working", str(e)]
        self.is_running = False
        self.breaker = False


Fire_ID = random.random()


class Fire(Module):
    name = "FireApp"

    def __init__(self, app):
        super().__init__(app, Fire_ID)
        self.fire = None

    def end_safely(self):
        if self.fire:
            self.fire.breaker = True
            self.fire.is_running = False

    def page(self, panel):
        self.write(panel, 0, 0,
                   " - FireApp - by Ruckusist",
                   color="green")
        max_h = self.h - 1
        max_y = self.w - 1

        def blank():
            nonlocal max_h
            nonlocal max_y
            self.write(panel, 1, 0,
                       "Press Enter to Start the Fire.")
            for i, line in enumerate(range(max_h - 2)):
                try:
                    panel.win.addstr(max_h, 0, " " * max_y)
                except Exception:
                    break
                max_h -= 1

        if not self.fire:
            blank()
            return
        if not self.fire.is_running:
            return

        for i, line in enumerate(reversed(self.fire.gameboard)):
            line = "".join(line)

            for y, char in enumerate(line):
                if y > max_y:
                    break
                try:
                    color = (self.app.front.chess_black
                             if char == "@" else (
                                 self.app.front.color_magenta
                                 if char in ["^", "~", "*", "|"]
                                 else self.app.front.chess_white))
                    panel.win.addstr(max_h, y, str(char), color)
                except Exception as e:
                    self.print(e)
                    break

            max_h -= 1

    @callback(Fire_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if not self.fire:
            self.fire = Flames(self)
            self.print("Initializing fire.")
            self.print("Fire initialized.")

        if self.fire.is_running:
            if not self.fire.breaker:
                self.fire.breaker = True
            self.print("Turning fire off.")
            self.fire.is_running = False
        else:
            self.flame_thread = threading.Thread(
                target=self.fire.multipass
            ).start()
            self.fire.is_running = True
            self.print("Turning fire on.")