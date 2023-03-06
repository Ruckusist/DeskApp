import time, random
from timeit import default_timer as timer
import curses
import curses.panel
from collections import namedtuple
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


class Keys:
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
    W     = 119
    A     = 97
    S     = 115
    D     = 100

    # F KEYS
    F1    = 80 

    # NUMBER KEYS
    NUM1   = 49
    NUM2   = 50
    NUM3   = 51
    NUM4   = 52
    NUM5   = 53

    # DEFAULT KEYS
    Q       = 113
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
        curses.start_color()
        self.setup_color()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.nodelay(1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(0)
        self.screen_mode = True
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

    def get_click(self):
        _, x, y, _, btn = curses.getmouse()
        return tuple([(x,y),btn])

    def get_input(self):
        push = 0
        if self.screen_mode:  # WTF is this?
            push = self.screen.getch()

            if push == curses.KEY_MOUSE:
                return 0
        else:
            self.screen.keypad(0)
            curses.echo()  # when did i place the mouse cursor?
            # self.redraw_window(self.footer) # why are we doing this?
            # push = self.footer[0].getstr(1,1).decode('utf8')
            self.screen.keypad(1)
            curses.noecho()
            self.screen_mode = True
            # self.redraw_window(self.footer)
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


class SubClass:
    def __init__(self, app):
        self.app   = app
        self.print = app.print
        self.front = app.front


class Backend(SubClass):
    def __init__(self, app, show_header, show_footer, show_menu, show_messages, show_main):
        super().__init__(app)
        self.should_stop = False
        self.update_timeout = .05
        self.last_update = timer()

        # display toggles.
        self.screen_size_changed = False
        self.show_header    = show_header
        self.show_footer    = show_footer
        self.show_menu      = show_menu
        self.menu_w         = 15
        self.show_messages  = show_messages
        self.message_h      = 3
        self.messages_w     = 20
        self.show_main      = show_main
        self.redraw_mains()
        self.prev_panels_shown = (self.show_header, self.show_footer, self.show_menu, self.show_messages, self.show_main)

    def redraw_mains(self):
        self.header_panel    = self.draw_header()
        self.footer_panel    = self.draw_footer()
        self.menu_panel      = self.draw_menu()
        self.messages_panel  = self.draw_messages()

    def setup_mods(self):
        # first time setup of all mods.
        for mod in self.app.menu:
            self.setup_mod(mod)

    def setup_mod(self, mod):
        menu_split = int(self.front.w*self.app.h_split)
        message_split = int(self.front.h*self.app.v_split)
        height      = self.front.h
        if self.show_header: height -= 3
        if self.show_footer: height -= 3
        if self.show_messages: height -= message_split
        width       = self.front.w
        if self.show_menu: width -= menu_split
        top_left_x  = 3
        if not self.show_header: top_left_x -= 3
        top_left_y  = menu_split
        if not self.show_menu: top_left_y = 0
        dims = [height, width, top_left_x, top_left_y]
        class_id = random.random()
        active_module = mod(self.app, class_id)
        panel       = self.front.make_panel(dims, active_module.name)
        self.app.logic.available_panels[mod.name] = [active_module, panel]

    def redraw_mods(self):
        menu_split = int(self.front.w*self.app.h_split)
        message_split = int(self.front.h*self.app.v_split)
        
        height      = self.front.h
        if self.show_header: height -= 3
        if self.show_messages:
            height -= (message_split + 3)
        else:
            if self.show_footer: height -= 3

        width       = self.front.w
        if self.show_menu: width -= menu_split
        
        top_left_x  = 0
        if self.show_header: top_left_x += 3
        top_left_y  = 0
        if self.show_menu: top_left_y += menu_split

        dims = [height, width, top_left_x, top_left_y]
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
        menu_split = int(self.front.w*self.app.h_split)
        message_split = int(self.front.h*self.app.v_split)
        height      = self.front.h
        if self.show_footer: height -= 3
        if self.show_main: height -= (message_split + 4)
        else:
            if self.show_header: height -= 3

        width       = self.front.w
        if self.show_menu: width -= menu_split
        top_left_x  = 0
        if self.show_main: top_left_x += message_split + 4
        else:
            if self.show_header: top_left_x += 3
        top_left_y  = 0
        if self.show_menu: top_left_y += menu_split
        dims        = [height, width, top_left_x, top_left_y]
        self.messages_h = height-2
        self.messages_w = width-2
        panel       = self.front.make_panel(dims, "Messages")
        return panel

    def update_header(self):
        self.header_panel.win.addstr(1,3, self.app.header, self.front.color_blue)

    def update_messages(self):
        message_split = int(self.front.h*self.app.v_split)
        for idx, mesg in enumerate(self.app.data['messages'][-self.messages_h:]):
            self.messages_panel.win.addstr(idx+1,1, f"{str(mesg)[:self.messages_w-2]}", self.front.color_cyan)

    def update_menu(self):
        for idx, mod in enumerate(self.app.menu):
            cur = self.app.logic.current
            color = self.front.color_select if idx==cur else self.front.color_red
            self.menu_panel.win.addstr(idx+1, 1, f"{str(mod.name)[:self.menu_w-2]}", color)

    def loop(self):
        # HANDLE THE INPUT
        self.app.logic.decider( self.front.get_input() )

        # HANDLE SCREEN RESIZE ??? NO. NOT YET. SOON.
        if self.screen_size_changed:
            self.front.resized()

        # HANDLE PANEL RESIZE ->
        cur_panels_shown = (self.show_header, self.show_footer, self.show_menu, self.show_messages, self.show_main)
        if ((cur_panels_shown != self.prev_panels_shown) or 
            self.screen_size_changed):
            self.redraw_mains()
            self.redraw_mods()
            self.screen_size_changed = False

        

        # RUN A FRAME ON EVERY MOD
        for mod in self.app.logic.available_panels:
            self.app.logic.available_panels[mod][0].page(
                self.app.logic.available_panels[mod][1] )

        # UPDATE THE BUILT IN STUFF.
        self.update_messages()
        self.update_header()
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

    def decider(self, keypress):
        """Callback decider system."""
        # Do we have a good keypress?
        if 0 > keypress: return

        mod_name = list(self.available_panels)[self.current]
        cur_mod = self.available_panels[mod_name]

        mod_class = cur_mod[0]
        mod_panel = cur_mod[1]
        
        if isinstance(keypress, str):
            mod_class.string_decider(keypress)

        elif isinstance(keypress, tuple):
            mod_class.mouse_decider(keypress)

        elif isinstance(keypress, int):
            try:
                global callbacks
                all_calls_for_button = list(filter(lambda callback: callback['key'] in [int(keypress)], callbacks))
                if not all_calls_for_button:
                    self.print(f"{keypress} has no function.")
                    return
                # Debugs.
                # self.print(f"Number of calls on the {keypress} button: {len(all_calls_for_button)}")
                call_for_button = list(filter(lambda callback: callback['classID'] in [mod_class.class_id,0,1], all_calls_for_button))  # [0]
                # self.print(f"got some callbacks! -> {call_for_button}")
                # self.print(f"there are {len(call_for_button)} callbacks on this button. {keypress}")
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
        # self.draw  = Draw(self)
        self.logic = Logic(self)
        self.back  = Backend(self, show_header, show_footer, show_menu, show_messages, show_main)
        
        # Start the Game.
        if self.should_autostart:
            self.start()

    def start(self):
        self.back.main()

    def print(self, message=""):
        self.data['messages'].append(message)
        if len(self.data['messages']) > 300:  # 4k screens with 12pt font have 282 lines.
            self.data['messages'].pop(0)
 
    @callback(ID=1, keypress=Keys.TAB)  # set screen mode
    def on_tab(self, *args, **kwargs): pass

    @callback(ID=1, keypress=Keys.RESIZE)  # screen resize
    def on_resize(self, *args, **kwargs):
        self.app.back.screen_size_changed = True
        self.print("got a resize")

    @callback(ID=1, keypress=Keys.NUM1)  # NUM1 - header
    def on_NUM1(self, *args, **kwargs):
        self.app.back.show_header = not self.app.back.show_header
        self.print(f"pressed NUM1 ... show_header = {self.app.back.show_header}")

    @callback(ID=1, keypress=Keys.NUM2)  # NUM2 - footer
    def on_NUM2(self, *args, **kwargs):
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
    app = App()

__all__ = (Keys, Curse, Backend, Logic, Module, App)
if __name__ == "__main__":
    main()