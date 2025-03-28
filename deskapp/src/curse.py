"""
Deskapp 1.0
curse.py
last updated: 10-2-23
updated by: Ruckusist
State: Good. Stable.
"""


import curses  
import curses.panel
from collections import namedtuple
from itertools import cycle
import time

from deskapp import Keys

class Curse:
    def __init__(self, use_mouse=False, use_focus=False):
        self.use_mouse = use_mouse
        self.use_focus = use_focus
        self.curses = curses
        self.screen = curses.initscr()
        curses.flushinp()
        self.palette = []
        curses.start_color()
        self.setup_color()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.nodelay(1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(0)
        self.key_mode = False
        self.key_buffer = ""
        self.has_resized_happened = False
        self.h = curses.LINES
        self.w = curses.COLS

    def setup_color(self):
        """Load a custom theme."""
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.color_white = curses.color_pair(1)
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_BLACK)
        self.color_black = curses.color_pair(11)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        self.color_magenta = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.color_green = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_RED)
        self.chess_black = curses.color_pair(4)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
        self.chess_white = curses.color_pair(5)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        self.color_cyan = curses.color_pair(6)
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.color_yellow = curses.color_pair(7)
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)
        self.color_red = curses.color_pair(8)
        curses.init_pair(9, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.color_blue = curses.color_pair(9)
        curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
        self.color_select = curses.color_pair(10)

        self.color_bold = curses.A_BOLD
        self.color_blink = curses.A_BLINK
        self.color_error = self.color_bold | self.color_blink | self.color_red

        try:
            for i in range(0, curses.COLORS):
                if i == 0: curses.init_pair(i+1, i, curses.COLOR_WHITE)
                else: curses.init_pair(i+1, i, curses.COLOR_BLACK)
                self.palette.append(curses.color_pair(i))
        except:
            for i in range(0, 7):
               if i == 0: curses.init_pair(i+1, i, curses.COLOR_WHITE)
               else: curses.init_pair(i+1, i, curses.COLOR_BLACK)
               self.palette.append(curses.color_pair(i))

    def w(self):
        return self.curses.COLS

    def h(self):
        return self.curses.LINES

    def resized(self):
        self.h, self.w = self.screen.getmaxyx()
        self.screen.clear()
        # self.curses.resizeterm(self.w, self.h)
        self.screen.refresh()
        curses.flushinp()
        self.has_resized_happened = True

    def get_click(self):
        _, x, y, _, btn = curses.getmouse()
        return tuple([(x,y),btn])

    def get_input(self):
        # BUILT IN CURSES INPUT
        try:     push = self.screen.getch()
        except:  return 0

        # ALWAYS THROWS A 0 when nothing is happening. some sort 
        # of a timeout. anyway, throw it out.
        if push == 0: return 0

        # MOUSE EVENT
        # THIS IS TOGGLED BY THE USE_MOUSE PARAMETER
        if push == curses.KEY_MOUSE:
            try:
                if self.use_mouse: return self.get_click()
                else: return 0
            except: return 0

        # GAIN AND LOSE FOCUS.
        if push == Keys.FOCUS:
            if self.use_focus: return push
            return 0
        if push == Keys.LOST_FOCUS:
            if self.use_focus: return push
            return 0

        # KEYMODE IS A SPECIAL MODE THAT ALLOWS FOR THE INPUT OF
        # STRINGS. THIS IS USED FOR THE COMMAND LINE.
        if self.key_mode:
            # RETURN ON ENTER PUSH, THIS SHOULD BE COMMON.
            if push == Keys.ENTER:
                self.key_mode = False
                return self.key_buffer  # any string will trigger the end of this.
            
            # ADDED FUNCTIONALITY TO HANDLE BACKSPACE
            if push == 263:  # backspace
                self.key_buffer = "".join(list(self.key_buffer)[:-1])
                return 0
            try:
                # THIS IS WORKING. IT'S A LITTLE HACKY, BUT IT WORKS.
                key = chr(push)
                self.key_buffer += key
                return 0
            except:
                return 0
            
        return push

    def make_panel(self, dims, label, scroll=False, box=True, banner=True):
        """Panel factory."""
        panel_type = namedtuple('Panel', 'win panel label dims')
        win = curses.newwin(dims[0], dims[1], dims[2], dims[3])
        win.scrollok(scroll)
        _panel = curses.panel.new_panel(win)
        if box:
            win.box()
        if banner:
            win.addstr(0, 2, f"| {label} |"[:dims[1]-2])

        panel = panel_type( win, _panel, label, dims )
        return panel

    def end_safely(self):
        """Return control to the shell."""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.flushinp()
        curses.endwin()

    def splash_screen(self):
        splash = self.make_panel(
            [self.h, self.w, 0, 0],
            "splash",
            box=False,
            banner=False
        )
        curses.panel.update_panels()
        self.screen.refresh()

        cycled = cycle([x for x in range(len(self.palette))])
        for x in range(self.h):
            if x == int(self.h/2):
                splash.win.addstr(x, int(self.w/2)-7, " Deskapp.org")
                splash.win.refresh()
                time.sleep(.95)
            else:
                matrix = ["&", "^", "&", "$", "R", "\\", "|", "/", "-"]
                cycled_matrix = cycle([x for x in matrix])
                for y in range(self.w):
                    if x == self.h-1 and y == self.w-1: break # hacks.
                    splash.win.addstr(x, y, next(cycled_matrix), self.palette[next(cycled)] )
                    splash.win.refresh()
                    time.sleep(0.0001)
        time.sleep(2)
        self.screen.erase()
