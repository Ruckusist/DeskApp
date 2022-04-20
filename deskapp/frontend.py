#!/usr/bin/env python
"""
Another AlphaGriffin Project.
"""
__author__ = "Eric Petersen @Ruckusist"
__copyright__ = "Copyright 2022, The Alpha Griffin Project"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.6"
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
    def __init__(self):
        print("[i] Starting Cursing Frontend.")
        self.curses = curses
        # curses.filter()
        self.screen = curses.initscr()
        self.palette = []
        curses.start_color()
        self.setup_color()
        curses.noecho()
        curses.cbreak()
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
                    self.keystroke(x)
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

    def recalc_winsizes(self):
        h = self.screen_h
        w = self.screen_w

        # HEADER
        self.header_dims = [3, w, 0, 0]
        # WINLEFT
        self.h_split = int(w / 6) - 1
        self.winleft_dims = [h-3-4-3, self.h_split, 3, 0]
        # WINRIGHT
        self.v_split = int((h-3-4-3)/6)
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

    def main_screen(self, header='Deskapp'):
        """This is attempting a new main panel configuration"""
        self.recalc_winsizes()
        self.header = self.make_panel(self.header_dims, header)
        self.winleft = self.make_panel(self.winleft_dims, "Menu")
        self.winrightlower = self.make_panel(self.winright_upper_dims, "Panel 3")
        self.winrightupper = self.make_panel(self.winright_lower_dims, "Messages")      
        self.footer = self.make_panel(self.footer_dims, "Input")      
        self.debug = self.make_panel(self.debug_dims, "Meta")
        curses.panel.update_panels()
        self.screen.refresh()

    def __call__(self) -> None:
        self.splash_screen()
        self.main_screen()
        time.sleep(10)
        self.end_safely()


class Window(object):
    """The Alphagriffin Curses frontend template."""

    def __init__(self, stdscr=None):
        """Setup basic curses interface."""
        if stdscr is None:
            stdscr = curses.initscr()
        self.curses = curses
        self.screen = stdscr
        self.palette = []
        curses.start_color()
        # curses.use_default_colors()
        self.setup_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0) # 0: invisible, 1: visible, 2: bright
        self.screen.keypad(1)
        self.screen.nodelay(1)
        self.screen_h, self.screen_w = self.screen.getmaxyx()
        self.screen_mode = True

    def get_input(self):
        """Pass curses control capture to another class."""
        x = 0
        # self.footer[0].addstr(1, 1, "Mode: KeyStroke")
        # self.screen.nodelay(True)
        if self.screen_mode:
            x = self.screen.getch()
            try:
                if int(x) > 0:
                    self.keystroke(x)
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

    def main_screen(self, msg="RuckusTUI"):
        """Standard screen template."""
        h = self.screen_h
        w = self.screen_w

        header_dims = [3, w, 0, 0]
        split = int(w / 6) - 1
        winleft_dims = [h-3-4-3, split, 3, 0]
        self.winright_dims = [h-3-4-3, w - split-1, 3, split + 1]
        footer_dims = [3, w, h-3, 0]
        debug_dims = [4, w, h-7, 0]
        self.header = self.make_panel(header_dims, "header", box=True)
        self.winleft = self.make_panel(winleft_dims, "options", True, box=True)
        self.winright = self.make_panel(self.winright_dims, "screen", True, box=True)
        self.debug = self.make_panel(debug_dims, "debugs", True, box=True)
        self.footer = self.make_panel(footer_dims, "interface", True, box=True)
        self.keystroke = lambda x: self.footer[0].addstr(1, w-9, "<K: {}>".format(x))
        curses.panel.update_panels()
        self.screen.addstr(h-1,w-9,"<{},{}>".format(h, w))
        self.screen.addstr(h-1,w-19,"<FPS: 30>".format(h, w))
        self.fps = lambda x: self.screen.addstr(h-1,w-19,"<FPS: {}>".format(x))
        self.header[0].addstr(1, 1, msg, self.color_gb)
        self.screen.refresh()

    def dual_main_screen(self, msg='Message Center'):
        h = self.screen_h
        w = self.screen_w

        h_split = int(w / 6) - 1
        v_split = int((h-3-4-3)/6)

        winright_upper_dims = [v_split, w - h_split-1, h-7-v_split, h_split + 1]
        self.winright = self.make_panel(winright_upper_dims, "Panel 3")

        winright_lower_dims = [(h-3-4-3)-v_split, w - h_split-1, 3, h_split + 1]
        self.winlower = self.make_panel(winright_lower_dims, "Panel 4")
        
    def make_panel(self, dims, label, scroll=False, box=True, banner=True):
        """Panel factory."""
        options = {'dims': dims}
        win = curses.newwin(dims[0], dims[1], dims[2], dims[3])
        win.scrollok(scroll)
        panel = curses.panel.new_panel(win)
        self.redraw_window([win, panel, label], box, banner)
        return win, panel, label, options

    def redraw_window(self, win, box=True, banner=True):
        """Basic refresh to screen."""
        win[0].erase()
        if box: win[0].box()
        if banner: win[0].addstr(0, 1, str("| {} |".format(win[2])))

    def spash_screen(self, template=None):
        win, _, _, _ = self.make_panel(
            [self.screen_h, self.screen_w, 0, 0], 
            "splash", 
            box=False,
            banner=False
        )
        curses.panel.update_panels()
        self.screen.refresh()
        if template:
            for index, line in enumerate(template):
                if index == self.screen_h-1: break
                win.addstr(line[:self.screen_w-4], index, 1)
            win.refresh()
        else:
            # test spashscreen
            cycled = cycle([x for x in range(len(self.palette))])
            for x in range(self.screen_h):
                if x == int(self.screen_h/2):
                    win.addstr(x, int(self.screen_w/2)-7, " Ruckusist.com")
                    win.refresh()
                    time.sleep(.95)
                else:
                    matrix = ["&", "^", "&", "$", "R", "\\", "|", "/", "-"]
                    cycled_matrix = cycle([x for x in matrix])
                    for y in range(self.screen_w):
                        if x == self.screen_h-1 and y == self.screen_w-1: break # hacks.
                        win.addstr(x, y, next(cycled_matrix), self.palette[next(cycled)] )
                        win.refresh()
                        time.sleep(0.0001)
        time.sleep(2)
        self.screen.erase()

    def main_test(self):
        """Sanity Checks."""
        win1, panel1, _, __ = self.make_panel([10, 13, 5, 5], "Panel 1")
        win2, panel2, _, __ = self.make_panel([10, 13, 8, 8], "Panel 2")
        curses.panel.update_panels()
        self.screen.refresh()
        time.sleep(1)
        panel1.top()
        curses.panel.update_panels()
        self.screen.refresh()
        time.sleep(1)

        for i in range(5):
            panel2.move(8, 8 + i)
            # curses.panel.update_panels()
            self.screen.refresh()
            time.sleep(0.1)

        # time.sleep(2.5)
        #self.dialog_box()
        #self.dialog[1].top()
        #self.screen.refresh()
        #time.sleep(2.5)
        #self.dialog[0].erase()
        #self.dialog[0].refresh()
        
        # self.screen.refresh()
        # time.sleep(2.5)
        return True

    def new_main(self):
        """This is attempting a new main panel configuration"""
        h = self.screen_h
        w = self.screen_w

        # HEADER
        header_dims = [3, w, 0, 0]
        header = self.make_panel(header_dims, "Panel 1")

        
        h_split = int(w / 6) - 1
        winleft_dims = [h-3-4-3, h_split, 3, 0]
        winleft = self.make_panel(winleft_dims, "Panel 2")

        v_split = int((h-3-4-3)/6)

        winright_upper_dims = [v_split, w - h_split-1, h-7-v_split, h_split + 1]
        winrightupper = self.make_panel(winright_upper_dims, "Panel 3")

        winright_lower_dims = [(h-3-4-3)-v_split, w - h_split-1, 3, h_split + 1]
        winrightlower = self.make_panel(winright_lower_dims, "Panel 4")

        footer_dims = [3, w, h-3, 0]
        winfooter = self.make_panel(footer_dims, "Panel 5")

        debug_dims = [4, w, h-7, 0]
        windebug = self.make_panel(debug_dims, "Panel 6")


        curses.panel.update_panels()
        self.screen.refresh()
        time.sleep(3)

    def warning(self, label, text, callback):
        self.screen.refresh()
        self.dialog_box(label)
        win, pan = self.dialog
        pan.top()
        win.addstr(1, 2, text, self.palette[7])
        start_warning = timer()
        option = True
        while timer() <= start_warning + 10:
            keypress = abs(self.get_input())
            if keypress == 260 or keypress == 261: # left/right
                option = False if option else True
            elif keypress == 10: # enter
                break
            win.addstr(3, 2, "Cancel", self.palette[1] if option else self.palette[0])
            win.addstr(3, 9, "Confirm", self.palette[1] if not option else self.palette[0])
            win.refresh()
            self.screen.refresh()
        if not option:
            threading.Thread(target=callback).start()
        win.erase()
        win.refresh()
        self.screen.refresh()

    def error(self, label:str, mesg:list, timeout=10):
        self.screen.refresh()
        self.dialog_box(label)
        win, pan = self.dialog
        # pan.top()
        start_timer = timer()
        counter = 3
        # 
        for line in mesg:
            win.addstr(counter, 2, line, self.palette[7])
            counter += 1
        win.refresh()
        self.screen.refresh()
        # pan.top()
        while timer() <= start_timer + timeout: time.sleep(0.1)

        win.erase()
        win.refresh()
        self.screen.refresh()

    def dialog_box(self, label="Warning"):
        win, panel, _, _ = self.make_panel([
            8, 40, int(self.screen_h/2)-int(7/2), int(self.screen_w/2)-int(40/2)
        ], label, box=True, banner=True)
        # win.addstr(3, 2, "Cancel", self.palette[1])
        # win.addstr(3, 9, "Confirm")
        win.refresh()
        self.dialog = (win, panel)
        return win, panel

    def __call__(self):
        self.spash_screen()
        time.sleep(5)
        self.main_test()
        time.sleep(5)
        self.dialog_box()
        self.dialog[1].top()
        self.screen.refresh()
        time.sleep(2.5)
        self.dialog[0].erase()
        self.dialog[0].refresh()
        self.screen.refresh()
        time.sleep(2.5)
        self.end_safely()


def main():
    os.system('clear')
    app = Frontend()
    app()


if __name__ == '__main__':
    main()
