#!/usr/bin/env python
"""
Another AlphaGriffin Project.
"""
__author__ = "Eric Petersen @Ruckusist"
__copyright__ = "Copyright 2022, The Alpha Griffin Project"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.7"
__maintainer__ = "Eric Petersen"
__email__ = "ruckusist@alphagriffin.com"
__status__ = "Prototype"

import os, sys, time, threading
import curses
import curses.panel
# except ImportError: print("this doesnt work in windows"); exit(1)

# new color support reqires this. it should just be there... like print.
from itertools import cycle
from timeit import default_timer as timer

from collections import namedtuple


class Cursing:
    def __init__(self, h_split=.16, v_split=.16, title="Deskapp"):
        self.curses = curses
        self.title = title
        self.h_split_pct = h_split
        self.v_split_pct = v_split
        # curses.filter()
        self.screen = curses.initscr()
        self.palette = []
        curses.start_color()
        self.setup_color()
        curses.noecho()
        curses.cbreak()
        # curses.init_color(0, 0, 0, 0)
        curses.curs_set(0) # 0: invisible, 1: visible, 2: bright
        self.screen.keypad(1)
        self.screen.nodelay(1)
        self.screen_h, self.screen_w = self.screen.getmaxyx()
        self.screen_mode = True

    def setup_color(self):
        """Load a custom theme."""
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.color_rw = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        self.color_cb = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.color_gb = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_RED)
        self.chess_black = curses.color_pair(4)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
        self.chess_white = curses.color_pair(5)
        self.color_bold = curses.A_BOLD
        self.color_blink = curses.A_BLINK
        self.color_error = self.color_bold | self.color_blink | self.color_rw
        # Palette of all available colors... == 8 wtf
        try:
            for i in range(0, curses.COLORS):
                if i == 0: curses.init_pair(i+1, i, curses.COLOR_WHITE)
                else: curses.init_pair(i+1, i, curses.COLOR_BLACK)
                self.palette.append(curses.color_pair(i))
        except:
            print("failing to setup color!")
            for i in range(0, 7):
               if i == 0: curses.init_pair(i+1, i, curses.COLOR_WHITE)
               else: curses.init_pair(i+1, i, curses.COLOR_BLACK)
               self.palette.append(curses.color_pair(i))
            pass
        finally:
            # print(f"len(curses.COLORS) = {len(self.palette)}")
            # time.sleep(2)
            pass

    def get_input(self):
        """Pass curses control capture to another class."""
        x = 0
        # self.footer[0].addstr(1, 1, "Mode: KeyStroke")
        # self.screen.nodelay(True)
        if self.screen_mode:
            x = self.screen.getch()
            try:
                if int(x) > 0:
                    # self.keystroke(x)
                    # self.footer[0].addstr(1, 1, f"{x}")
                    pass
            except: pass
        else:
            self.screen.keypad(0)
            curses.echo()
            self.redraw_window(self.footer)
            x = self.footer[0].getstr(1, 1).decode('UTF-8')
            self.screen.keypad(1)
            curses.noecho()
            self.screen_mode = True
            self.redraw_window(self.footer)
        return x
        
    def refresh(self):
        """This should check for a screen resize."""
        # TODO: add screensize checker!
        #
        # curses.resizeterm(y, x)
        self.screen.refresh()
        curses.panel.update_panels()

    def end_safely(self):
        """Return control to the shell."""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()
        print("[*] Ended Safely.")

    def test(self):
        self.screen.addstr(0, 0, '[%] this is working.1')
        self.screen.refresh()
        self.screen.addstr(1, 0, '[%] this is working.2')
        self.screen.refresh()
        time.sleep(5)

    def make_panel(self, dims, label, scroll=False, box=True, banner=True):
        """Panel factory."""
        panel_type = namedtuple('Panel', 'win panel label dims')
        win = curses.newwin(dims[0], dims[1], dims[2], dims[3])
        win.scrollok(scroll)
        _panel = curses.panel.new_panel(win)
        panel = panel_type(win, _panel, label, dims)
        self.redraw_window(panel, box, banner)
        return panel

    def redraw_window(self, panel, box=True, banner=True):
        """Basic refresh to screen."""
        panel.win.erase()
        if box: panel.win.box()
        if banner: panel.win.addstr(0, 1, str("| {} |".format(panel.label)))

    def __call__(self, *args, **kwds) -> None:
        self.test()
        self.end_safely()
        pass


class Frontend_TEST(Cursing):
    def panel_test(self):
        """Sanity Checks."""
        panel_1 = self.make_panel([10, 13, 5, 5], "Panel 1")
        panel_2 = self.make_panel([10, 13, 8, 8], "Panel 2")
        curses.panel.update_panels()
        self.screen.refresh()
        time.sleep(1)
        panel_1.panel.top()
        curses.panel.update_panels()
        self.screen.refresh()
        time.sleep(1)

        for i in range(15):
            panel_2.panel.move(8, 8 + i)
            curses.panel.update_panels()
            self.screen.refresh()
            time.sleep(0.1)
        time.sleep(2)

    def __call__(self) -> None:
        self.panel_test()
        self.end_safely()
        pass


class Frontend(Cursing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = None
        self.winleft = None
        self.winrightupper = None
        self.winrightlower = None
        self.footer = None
        self.debug = None

    def recalc_winsizes(self):
        h = self.screen_h
        w = self.screen_w

        # HEADER
        self.header_dims = [3, w, 0, 0]
        # WINLEFT
        self.h_split = int(w *self.h_split_pct) - 1
        self.winleft_dims = [h-3-4-3, self.h_split, 3, 0]
        # WINRIGHT
        self.v_split = int((h-3-4-3)*self.v_split_pct)
        self.winright_lower_dims = [self.v_split, w - self.h_split-1, h-7-self.v_split, self.h_split + 1]
        #WINRIGHT AGAIN
        self.winright_upper_dims = [(h-3-4-3)-self.v_split, w - self.h_split-1, 3, self.h_split + 1]
        # FOOTER
        self.footer_dims = [3, w, h-3, 0]
        # DEBUG
        self.debug_dims = [4, w, h-7, 0]

    def splash_screen(self):
        splash = self.make_panel(
            [self.screen_h, self.screen_w, 0, 0], 
            "splash", 
            box=False,
            banner=False
        )
        curses.panel.update_panels()
        self.screen.refresh()

        cycled = cycle([x for x in range(len(self.palette))])
        for x in range(self.screen_h):
            if x == int(self.screen_h/2):
                splash.win.addstr(x, int(self.screen_w/2)-7, " Ruckusist.com")
                splash.win.refresh()
                time.sleep(.95)
            else:
                matrix = ["&", "^", "&", "$", "R", "\\", "|", "/", "-"]
                cycled_matrix = cycle([x for x in matrix])
                for y in range(self.screen_w):
                    if x == self.screen_h-1 and y == self.screen_w-1: break # hacks.
                    splash.win.addstr(x, y, next(cycled_matrix), self.palette[next(cycled)] )
                    splash.win.refresh()
                    time.sleep(0.0001)
        time.sleep(2)
        self.screen.erase()

    def redraw_message_panel(self):
        # del self.winrightlower
        self.winrightlower = self.make_panel(self.winright_lower_dims, "Messages")

    def main_screen(self, header='Deskapp'):
        """This is attempting a new main panel configuration"""
        self.header = None
        self.winleft = None
        self.winrightupper = None
        self.winrightlower = None
        self.footer = None
        self.debug = None
        self.recalc_winsizes()
        self.screen.refresh()
        self.header = self.make_panel(self.header_dims, header)
        self.winleft = self.make_panel(self.winleft_dims, "Menu")
        self.winrightupper = self.make_panel(self.winright_upper_dims, "Panel 3")
        self.winrightlower = self.make_panel(self.winright_lower_dims, "Messages")      
        self.footer = self.make_panel(self.footer_dims, "Input")      
        self.debug = self.make_panel(self.debug_dims, "Meta")
        curses.panel.update_panels()
        self.screen.refresh()

    def __call__(self, header='Deskapp') -> None:
        self.splash_screen()
        self.main_screen(header)
        time.sleep(10)
        self.end_safely()


def main():
    os.system('clear')
    app = Frontend()
    app()


if __name__ == '__main__':
    main()
