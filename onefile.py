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


class Draw(SubClass):
    def __init__(self, app):
        super().__init__(app)
        self.menu_split = int(self.front.w*self.app.h_split)
        self.message_split = int(self.front.h*self.app.v_split)

        # pointers
        self._header = None
        self._footer = None
        self._menu   = None
        self._messages = None

        # flags
        self.show_header = True
        self.show_footer = True
        self.show_menu = True
        self.show_messages = True
        self.show_help = False

    def update(self):
        """This was blowing out the screen when the
        panel was not being held by a variable, if you
        just thow a panel out there. this will erase it."""
        self.front.curses.panel.update_panels()
        self.front.screen.refresh()

    def header(self):
        dims = [3, self.front.w, 0, 0]
        panel = self.front.make_panel(dims, self.app.title)
        panel.win.addstr(1,3, self.app.header, self.front.color_blue)
        self._header = panel

    def footer(self):
        dims = [3, self.front.w, self.front.h-3, 0]
        panel = self.front.make_panel(dims, "Input")
        # panel.win.addstr(1,10, self.app.header)
        panel.win.addstr(1,2, f"Press <tab> to enter text.", self.front.color_green)
        self._footer = panel

    def menu(self):
        # BUILD DIMS.
        # height       = self.front.h-3-3
        height = self.front.h
        if self.show_footer: height -= 3
        if self.show_header: height -= 3

        menu_split = int(self.front.w*self.app.h_split)
        width        = self.menu_split
        top_left_x   = 3
        if not self.show_header: top_left_x -= 3
        top_left_y   = 0
        dims = [height, width, top_left_x, top_left_y]
        # dims = [self.front.h-3-3, self.menu_split, 3, 0]
        panel = self.front.make_panel(dims, "Menu")
        for idx, mod in enumerate(self.app.menu):
            cur = self.app.logic.current
            color = self.front.color_select if idx==cur else self.front.color_red
            panel.win.addstr(idx+1, 1, f"{mod.name}", color)
        self._menu = panel

    def messages(self):
        dims = [self.message_split-3, self.front.w-self.menu_split, self.front.h-self.message_split, self.menu_split]
        panel = self.front.make_panel(dims, "messages")
        for idx, mesg in enumerate(self.app.data['messages'][-(self.message_split-5):]):
            # changed 2-25-23: force mesg to str.
            panel.win.addstr(idx+1,1, f"{str(mesg):20s}", self.front.color_cyan)
        self._messages = panel

    def mod(self, mod):
        dims = [
            self.front.h-self.message_split-3, 
            self.front.w-self.menu_split, 3, 
            self.menu_split
            ]
        panel = self.front.make_panel(dims, mod.name)
        # panel.win.addstr(1,1, f"This is working", self.front.color_yellow)
        return panel


class Backend(SubClass):
    def __init__(self, app):
        super().__init__(app)
        self.should_stop = False
        self.update_timeout = .05
        self.last_update = timer()

        # display toggles.
        self.show_header   = True
        self.show_footer   = True
        self.show_menu     = True
        self.show_messages = True
        self.show_main     = True
        self.prev_display_toggles = (self.show_header, self.show_footer, self.show_menu, self.show_messages, self.show_main)
        self.display_toggles = (self.show_header, self.show_footer, self.show_menu, self.show_messages, self.show_main)

    def setup_mods(self):
        # first time setup of all mods.
        for mod in self.app.menu:
            self.setup_mod(mod)

    def setup_mod(self, mod):
        message_split = int(self.front.h*self.app.v_split)
        height      = self.front.h
        if self.show_header: height -= 3
        if self.show_footer: height -= 3
        if self.show_messages: height -= message_split
        width       = 0
        top_left_x  = 0
        top_left_y  = 0
        # dims = [
        #     self.front.h-self.message_split-3, 
        #     self.front.w-self.menu_split, 3, 
        #     self.menu_split
        #     ]
        class_id = random.random()
        active_module = mod(self.app, class_id)
        active_panel = self.app.draw.mod(active_module)
        self.app.logic.available_panels[mod.name] = [active_module, active_panel]

    def rebuild_mod_panels(self):
        
        for mod in self.app.logic.available_panels:
            active = self.app.logic.available_panels[mod]
            new_panel = self.app.draw.mod(active[0])
            active[1] = new_panel


    
    def loop(self):
        # HANDLE A RESIZE?
        if self.prev_display_toggles != self.display_toggles:
            self.rebuild_mod_panels()


        # HANDLE THE INPUT
        self.app.logic.decider( self.front.get_input() )

        # RUN A FRAME ON EVERY MOD
        for mod in self.app.logic.available_panels:
            self.app.logic.available_panels[mod][0].page(
                self.app.logic.available_panels[mod][1] )

        # REDRAW THE SCREEN
        if self.show_header:
            self.app.draw.header()
        if self.show_footer:
            self.app.draw.footer()
        if self.show_menu:
            self.app.draw.menu()
        if self.show_messages:
            self.app.draw.messages()
        if self.show_main:
            cur_panel = self.app.logic.current_panel()
            cur_panel.panel.top()
        self.app.draw.update()

        self.prev_display_toggles = (self.show_header, self.show_footer, self.show_menu, self.show_messages, self.show_main)

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
        # panel.addstr(2,2,"This is happening.")
        panel.win.addstr(1,1, f"This is working", self.front.color_yellow)

class Buttons(Module):
    name = "Button Test"
    def __init__(self, app, class_id):
        super().__init__(app, class_id)
        # self.class_id = buttonID
        # self.register_module()

    def page(self, panel):
        panel.win.addstr(2,2, "Button zone.")
########

class App:
    def __init__(self,
                 modules:       list = [],
                 splash_screen: bool = False,
                 demo_mode:     bool = True,
                 name:           str = "Deskapp",
                 title:          str = "Deskapp",
                 header:         str = "This is working.",
                 v_split:      float = 0.4,
                 h_split:      float = 0.16,
                 autostart:     bool = True,
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

        self.front = Curse()
        self.draw  = Draw(self)
        self.back  = Backend(self)
        self.logic = Logic(self)

        # APP FUNCTIONALITY
        global messages
        self.data = {'messages': messages, 'errors': []}
        self.menu = self.user_modules
        if self.show_demo:
            self.menu.extend([About, Buttons])

        # Start the Game.
        if self.should_autostart:
            self.back.main()

    def start(self):
        self.back.main()

    def print(self, message=""):
        self.data['messages'].append(message)
        if len(self.data['messages']) > 15:
            self.data['messages'].pop(0)

    
    @callback(ID=1, keypress=Keys.NUM1)  # F1
    def on_NUM1(self, *args, **kwargs):
        self.print("pressed NUM1 ...")
        pass

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


if __name__ == "__main__":
    main()