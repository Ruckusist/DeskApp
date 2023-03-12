import time, random
from timeit import default_timer as timer
import curses
import curses.panel
from collections import namedtuple
import enum
from itertools import cycle
import functools

# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=dangerous-default-value
# pylint: disable=useless-parent-delegation


callbacks = []
messages = []
def callback(ID, keypress):
    """
    This callback system is an original design. @Ruckusist.
    """
    global callbacks
    global messages
    def decorated_callback(func):
        @functools.wraps(func)
        def register_callback(*args, **kwargs):
            kwargs['keypress'] = keypress
            return func(*args, **kwargs)
        callbacks.append({
                'key': keypress,
                'docs': func.__doc__,
                'func': register_callback,
                'classID': ID,
            })
        # print(f"registered callback function {func.__name__}() at keypress: {keypress}")
        messages.append(f"registered callback function {func.__name__}() at keypress: {keypress} by classID: {ID}")
    return decorated_callback # Maybe it returns NOTHING... oooooohhh....


class Keys(enum.IntEnum):
    """Remap the keypresses from numbers to variables."""
    UP    = 259
    DOWN  = 258
    LEFT  = 260
    RIGHT = 261
    ENTER = 10
    SPACE = 32
    BACKSPACE = 263
    HOME  = 262
    END   = 360
    ESC   = 27
    Q = 113
    W = 119
    E = 101
    R = 114
    T = 116
    Y = 121
    U = 117
    I = 105
    O = 111
    P = 112
    A = 97
    S = 115
    D = 100
    F = 102
    G = 103
    H = 104
    J = 106
    K = 107
    L = 108
    Z = 122
    X = 120
    C = 99
    V = 118
    B = 98
    N = 110
    M = 109

    # F KEYS
    F1    = 80

    # NUMBER KEYS
    NUM1   = 49
    NUM2   = 50
    NUM3   = 51
    NUM4   = 52
    NUM5   = 53
    NUM6 = 54
    NUM7 = 55
    NUM8 = 56
    NUM9 = 57
    NUM0 = 48

    # DEFAULT KEYS
    TAB     = 9
    PG_DOWN = 338
    PG_UP   = 339

    # MOUSE CLICKS
    LEFT_CLICK_DOWN = 2
    LEFT_CLICK_UP = 1
    RIGHT_CLICK_DOWN = 2048
    RIGHT_CLICK_UP = 1024
    MIDDLE_CLICK_DOWN = 64
    MIDDLE_CLICK_UP = 32

    # SIGNALS
    RESIZE = 410


class Curse:
    def __init__(self):
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

    def setup_color(self):
        """Load a custom theme."""
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.color_white = curses.color_pair(1)
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

    @property
    def w(self):
        return self.curses.COLS

    @property
    def h(self):
        return self.curses.LINES

    def resized(self):
        y, x = self.screen.getmaxyx()
        self.screen.clear()
        self.curses.resizeterm(y, x)
        self.screen.refresh()
        curses.flushinp()
        self.has_resized_happened = True

    def get_click(self):
        _, x, y, _, btn = curses.getmouse()
        return tuple([(x,y),btn])

    def get_input(self):
        try:     push = self.screen.getch()
        except:  return 0

        if push == 0: return 0

        if push == curses.KEY_MOUSE:
            try:     return self.get_click()
            except:  return 0

        if push == Keys.RESIZE:
            return push

        if self.key_mode:
            if push == Keys.ENTER:
                self.key_mode = False
                return self.key_buffer  # any string will trigger the end of this.
            try:
                key = Keys(push).name
                if key == Keys.SPACE.name:
                    key = " "
                    self.key_buffer += key
                elif key == Keys.BACKSPACE.name:
                    self.key_buffer = "".join(list(self.keybuffer)[:-1])
                else:
                    key = key.lower()
                    self.key_buffer += key
                return 0

            except:
                if push == 33:
                    self.key_buffer += "!"

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
                splash.win.addstr(x, int(self.w/2)-7, " Ruckusist.com")
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


class SubClass:
    def __init__(self, app):
        self.app   = app
        self.print = app.print
        self.front = app.front


class Backend(SubClass):
    def __init__(self, app, show_header, show_footer,
                 show_menu, show_messages, show_main):
        super().__init__(app)
        self.should_stop = False
        self.update_timeout = .05
        self.last_update = timer()

        # display toggles.
        #self.screen_size_changed = False
        self.show_header    = show_header
        self.show_footer    = show_footer
        self.footer_buffer  = ""
        self.show_menu      = show_menu
        self.menu_w         = 15
        self.show_messages  = show_messages
        self.message_h      = 3
        self.messages_w     = 20
        self.show_main      = show_main
        self.redraw_mains()
        self.prev_panels_shown = (self.show_header, self.show_footer,
                                  self.show_menu, self.show_messages,
                                  self.show_main)

    def redraw_mains(self):
        self.header_panel    = self.draw_header()
        self.footer_panel    = self.draw_footer()
        self.menu_panel      = self.draw_menu()
        self.messages_panel  = self.draw_messages()

    def setup_mods(self):
        # first time setup of all mods.
        for mod in self.app.menu:
            self.setup_mod(mod)

    def _calc_main_dims(self):
        height      = self.front.h
        if self.show_header: height -= 3
        if self.show_footer: height -= 3
        message_split = int(height*self.app.v_split)
        if self.show_messages: height -= message_split
        top_left_x  = 0
        if self.show_header: top_left_x += 3

        menu_split = int(self.front.w*self.app.h_split)
        width       = self.front.w
        if self.show_menu: width -= menu_split
        top_left_y  = 0
        if self.show_menu: top_left_y += menu_split

        return [height, width, top_left_x, top_left_y]

    def setup_mod(self, mod):
        class_id = random.random()
        active_module = mod(self.app, class_id)
        dims = self._calc_main_dims()
        panel       = self.front.make_panel(dims, active_module.name)
        self.app.logic.available_panels[mod.name] = [active_module, panel]

    def redraw_mods(self):
        dims = self._calc_main_dims()
        for mod in self.app.logic.available_panels:
            active = self.app.logic.available_panels[mod]
            panel = self.front.make_panel(dims, active[0].name)
            active[1] = panel

    def draw_header(self):
        height      = 3
        width       = self.front.w
        top_left_x  = 0
        top_left_y  = 0
        dims        = [height, width, top_left_x, top_left_y]
        panel       = self.front.make_panel(dims, self.app.title)
        return panel

    def draw_footer(self):
        height      = 3
        width       = self.front.w
        top_left_x  = self.front.h - 3
        top_left_y  = 0
        dims        = [height, width, top_left_x, top_left_y]
        panel       = self.front.make_panel(dims, "Input")
        if not self.front.key_mode:
            panel.win.addstr(1,2, f"Press <tab> to enter text; <h> for help.", self.front.color_green)
        return panel

    def draw_menu(self):
        height = self.front.h
        if self.show_footer: height -= 3
        if self.show_header: height -= 3

        menu_split = int(self.front.w*self.app.h_split)
        width        = menu_split
        top_left_x   = 0
        if self.show_header: top_left_x += 3
        top_left_y   = 0

        dims = [height, width, top_left_x, top_left_y]
        self.menu_w = width
        panel = self.front.make_panel(dims, "Menu")
        return panel

    def draw_messages(self):
        height      = self.front.h
        if self.show_header: height -= 3
        if self.show_footer: height -= 3
        top_left_x  = 0
        if self.show_header: top_left_x += 3
        if self.show_main:
            message_split = int(height*self.app.v_split)
            height -= message_split
            top_left_x += height
            height = message_split

        menu_split = int(self.front.w*self.app.h_split)
        width       = self.front.w
        if self.show_menu: width -= menu_split
        top_left_y  = 0
        if self.show_menu: top_left_y += menu_split

        dims = [height, width, top_left_x, top_left_y]
        self.messages_h = dims[0]-2
        self.messages_w = dims[0]-2
        panel       = self.front.make_panel(dims, "Messages")
        return panel

    def update_header(self):
        self.header_panel.win.addstr(1,3, self.app.header, self.front.color_blue)

    def update_footer(self):
        if self.front.key_mode:
            pad = " " * ( self.front.w-6 - len(self.front.key_buffer) )
            self.footer_panel.win.addstr(1,2, f": {self.front.key_buffer}{pad}", self.front.color_yellow)
        else:
            self.footer_panel.win.addstr(1,2, f"Press <tab> to enter text; <h> for help.", self.front.color_green)

    def update_messages(self):
        for idx, mesg in enumerate(self.app.data['messages'][-self.messages_h:]):
            mesg = str(mesg)
            if len(mesg) < self.messages_w-2:
                dif = (self.messages_w-2) - len(mesg)
                mesg += " "*dif
            else:
                mesg = mesg[:self.messages_w-2]
            self.messages_panel.win.addstr(idx+1,1, f"{mesg}", self.front.color_cyan)

    def update_menu(self):
        for idx, mod in enumerate(self.app.menu):
            cur = self.app.logic.current
            color = self.front.color_select if idx==cur else self.front.color_red
            self.menu_panel.win.addstr(idx+1, 1, f"{str(mod.name)[:self.menu_w-2]}", color)

    def loop(self):
        # HANDLE THE INPUT
        key_mouse = self.front.get_input()
        if key_mouse == Keys.RESIZE:
            self.front.resized()
        else:
            self.app.logic.decider( key_mouse )

        # HANDLE PANEL RESIZE ->
        cur_panels_shown = (self.show_header, self.show_footer, self.show_menu, self.show_messages, self.show_main)
        if ((cur_panels_shown != self.prev_panels_shown) or
            self.front.has_resized_happened):
            self.redraw_mains()
            self.redraw_mods()
            self.front.has_resized_happened = False

        # RUN A FRAME ON EVERY MOD
        for mod in self.app.logic.available_panels:
            self.app.logic.available_panels[mod][0].page(
                self.app.logic.available_panels[mod][1] )

        # UPDATE THE BUILT IN STUFF.
        self.update_messages()
        self.update_header()
        self.update_footer()
        self.update_menu()

        # REDRAW THE SCREEN
        if self.show_header:   self.header_panel.panel.show()
        else:                  self.header_panel.panel.hide()
        if self.show_footer:   self.footer_panel.panel.show()
        else:                  self.footer_panel.panel.hide()
        if self.show_menu:     self.menu_panel.panel.show()
        else:                  self.menu_panel.panel.hide()
        if self.show_messages: self.messages_panel.panel.show()
        else:                  self.messages_panel.panel.hide()
        cur_panel = self.app.logic.current_panel()
        if self.show_main:
            cur_panel.panel.show()
            cur_panel.panel.top()
        else:
            for mod in self.app.logic.available_panels:
                self.app.logic.available_panels[mod][1].panel.hide()

        self.front.curses.panel.update_panels()
        self.front.screen.refresh()

        self.prev_panels_shown = cur_panels_shown

    def main(self):
        self.setup_mods()

        while True:
            if self.should_stop:
                for mod in self.app.logic.available_panels:
                    self.app.logic.available_panels[mod][0].end_safely()
                break

            try:
                start_loop_time = timer()
                self.loop()
                loop_runtime = timer() - start_loop_time
                sleepfor = self.update_timeout - loop_runtime
                time.sleep(sleepfor)

            except KeyboardInterrupt:
                break

        self.front.end_safely()
        print(f"[*] {self.app.title} Ended Safely.")


class Logic(SubClass):
    def __init__(self, app):
        super().__init__(app)
        self.current = 0
        self.available_panels = {}

    def current_mod(self):
        name = list(self.available_panels)[self.current]
        return self.available_panels[name][0]

    def current_panel(self):
        name = list(self.available_panels)[self.current]
        return self.available_panels[name][1]

    def string_decider(self, input_string):
        mod = self.current_mod()
        mod.string_decider(input_string)

    def decider(self, keypress):
        """Callback decider system."""
        # Do we have a good keypress?
        if isinstance(keypress, int):
            if 0 >= keypress: return

        mod_name = list(self.available_panels)[self.current]
        cur_mod = self.available_panels[mod_name]

        mod_class = cur_mod[0]
        mod_panel = cur_mod[1]

        if isinstance(keypress, str):
            mod_class.string_decider(self.front.key_buffer)
            self.front.key_buffer = ""

        elif isinstance(keypress, tuple):
            mod_class.mouse_decider(keypress)

        elif isinstance(keypress, int):
            try:
                global callbacks
                all_calls_for_button = list(filter(lambda callback: callback['key'] in [int(keypress)], callbacks))
                if not all_calls_for_button:
                    self.print(f"{keypress} has no function")
                    return
                call_for_button = list(filter(lambda callback: callback['classID'] in [mod_class.class_id,0,1], all_calls_for_button))  # [0]
                callback = call_for_button[0]['func']  # TODO: come back for this 0, cant be right.
                callback(mod_class, mod_panel)

            except Exception as e:
                self.print(e)


class Module(SubClass):
    name = "Basic Module"
    def __init__(self, app, class_id):
        super().__init__(app)
        self.class_id = class_id
        self.cur_el = 0
        self.elements = []
        self.scroll = 0
        self.scroll_elements = []
        self.input_string = ""

    def register_module(self):
        self.app.menu.append(self)

    def page(self, panel):
        panel.win.addstr(2,2,"This is working!")

    def mouse_decider(self, mouse): pass

    def string_decider(self, input_string):
        self.input_string = input_string
        self.print(f"text input: {input_string}")

    def end_safely(self): pass

    @callback(0, keypress=Keys.UP)
    def on_up(self, *args, **kwargs):
        if self.scroll < len(self.scroll_elements)-1:
            self.scroll += 1
        else: self.scroll = 0

    @callback(0, keypress=Keys.DOWN)
    def on_down(self, *args, **kwargs):
        """scroll down"""
        if self.scroll < len(self.scroll_elements)-1:
            self.scroll += 1
        else: self.scroll = 0

    @callback(0, keypress=Keys.RIGHT)
    def on_left(self, *args, **kwargs):
        """rotate clickable elements"""
        if self.cur_el < len(self.elements)-1:
            self.cur_el += 1
        else: self.cur_el = 0

    @callback(0, keypress=Keys.LEFT)
    def on_right(self, *args, **kwargs):
        """rotate clickable elements"""
        if self.cur_el > 0:
            self.cur_el -= 1
        else: self.cur_el = len(self.elements)-1

######## These Are Extension.
class About(Module):
    name = "About"
    def __init__(self, app, class_id):
        super().__init__(app, class_id)

    def page(self, panel):
        panel.win.addstr(1,1, f"This is working", self.front.color_yellow)

class Buttons(Module):
    name = "Buttons"
    def __init__(self, app, class_id):
        super().__init__(app, class_id)

    def page(self, panel):
        panel.win.addstr(2,2, "Button zone.")
########

class App:
    def __init__(self,
                 modules:         list = [],
                 splash_screen:   bool = False,
                 demo_mode:       bool = True,
                 name:             str = "Deskapp",
                 title:            str = "Deskapp",
                 header:           str = "This is working.",
                 # PANELS ON STARTUP
                 show_header:     bool = True,
                 show_footer:     bool = True,
                 show_menu:       bool = True,
                 show_messages:   bool = True,
                 show_main:       bool = True,
                 # DEFAULT SPLITS
                 v_split:        float = 0.4,
                 h_split:        float = 0.16,
                 autostart:       bool = True,
            ):
        # initialize the constructor.
        self.app = self
        self.user_modules = modules
        self.show_splash = splash_screen
        self.show_demo = demo_mode
        self.name = name
        self.title = title
        self.header = header
        self.v_split = v_split
        self.h_split = h_split
        self.should_autostart = autostart

        # APP FUNCTIONALITY
        global messages
        self.data = {'messages': messages, 'errors': []}
        self.menu = self.user_modules
        if self.show_demo:
            self.menu.extend([About, Buttons])

        # CORE MODULES
        self.front = Curse()
        if self.show_splash:
            self.front.splash_screen()
        self.logic = Logic(self)
        self.back  = Backend(self, show_header, show_footer, show_menu, show_messages, show_main)

        # Start the Game.
        if self.should_autostart:
            self.start()

    def start(self):
        self.back.main()

    def close(self):
        self.back.should_stop = True

    def print(self, message: str=""):
        self.data['messages'].append(message)
        if len(self.data['messages']) > 300:  # 4k screens with 12pt font have 282 lines.
            self.data['messages'].pop(0)

    def error(self, message: str=""):
        self.print(message)

    def add_module(self, module: Module):
        self.back.setup_mod(module)

    def remove_module(self, module: str):
        # is this important? TODO: maybe for a logout screen?
        pass

    def set_header(self, message: str):
        self.header = message

    ## CALLBACKS

    @callback(ID=1, keypress=Keys.TAB)  # set screen mode
    def on_tab(self, *args, **kwargs):
        self.front.key_mode = True
        self.app.back.show_footer = True
        self.print("pressed <tab> --> Press Enter after adding Text.")

    #@callback(ID=1, keypress=Keys.RESIZE)  # screen resize
    #def on_resize(self, *args, **kwargs):
    #    self.app.back.screen_size_changed = True
    #    self.print("got a resize")

    @callback(ID=1, keypress=Keys.NUM1)  # NUM1 - header
    def on_NUM1(self, *args, **kwargs):
        self.app.back.show_header = not self.app.back.show_header
        self.print(f"pressed NUM1 ... show_header = {self.app.back.show_header}")

    @callback(ID=1, keypress=Keys.NUM2)  # NUM2 - footer
    def on_NUM2(self, *args, **kwargs):
        if not self.app.front.key_mode:
            self.app.back.show_footer = not self.app.back.show_footer
            self.print(f"pressed NUM2 ... show_footer = {self.app.back.show_footer}")

    @callback(ID=1, keypress=Keys.NUM3)  # NUM3 - menu
    def on_NUM3(self, *args, **kwargs):
        self.app.back.show_menu = not self.app.back.show_menu
        self.print(f"pressed NUM3 ... show_menu = {self.app.back.show_menu}")

    @callback(ID=1, keypress=Keys.NUM4)  # NUM4 - main
    def on_NUM4(self, *args, **kwargs):
        self.app.back.show_main = not self.app.back.show_main
        self.print(f"pressed NUM4 ... show_main = {self.app.back.show_main}")

    @callback(ID=1, keypress=Keys.NUM5)  # NUM5 - messages
    def on_NUM5(self, *args, **kwargs):
        self.app.back.show_messages = not self.app.back.show_messages
        self.print(f"pressed NUM5 ... show_messages = {self.app.back.show_messages}")

    @callback(ID=1, keypress=Keys.NUM6)  # NUM5 - show all
    def on_NUM6(self, *args, **kwargs):
        if not all([self.app.back.show_messages, self.app.back.show_menu,
               self.app.back.show_main, self.app.back.show_header,
               self.app.back.show_footer]):

            self.app.back.show_messages = True
            self.app.back.show_menu = True
            self.app.back.show_main = True
            self.app.back.show_header = True
            self.app.back.show_footer = True
        else:
            self.app.back.show_messages = False
            self.app.back.show_menu = False
            self.app.back.show_header = False
            self.app.back.show_footer = False
            self.app.back.show_main = True

    @callback(ID=1, keypress=Keys.Q)  # q
    def on_q(self, *args, **kwargs):
        self.app.back.should_stop = True

    @callback(ID=1, keypress=Keys.PG_DOWN)  # pg_down
    def on_pg_down(self, *args, **kwargs):
        self.app.logic.current += 1
        if self.app.logic.current > len(list(self.app.logic.available_panels))-1:
            self.app.logic.current = 0

    @callback(ID=1, keypress=Keys.PG_UP)  # pg_up
    def on_pg_up(self, *args, **kwargs):
        self.app.logic.current -= 1
        if self.app.logic.current < 0:
            self.app.logic.current = len(list(self.app.logic.available_panels))-1


def main():
    app = App(
        splash_screen=True,
        show_footer=False,
        show_header=False,
        show_messages=False,
        show_menu=False
    )

__all__ = (Keys, Curse, Backend, Logic, Module, 
           App, callback, callbacks)

if __name__ == "__main__":
    main()
