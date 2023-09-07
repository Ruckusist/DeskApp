"""
Deskapp 1.0
app.py
last updated: 6-10-23
updated by: Ruckusist
State: Good. Stable.
"""


from deskapp import Curse, Logic, Backend, Module, Keys, callback, callbacks
from deskapp.mods import About, Buttons, Fire

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
                 show_box:        bool = True,
                 show_banner:     bool = True,
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
        self.show_box = show_box
        self.show_banner = show_banner
        self.name = name
        self.title = title
        self.header = header
        self.v_split = v_split
        self.h_split = h_split
        self.should_autostart = autostart

        # APP FUNCTIONALITY
        self.data = {'messages': [], 'errors': []}
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

    def exit(self):
        self.close()

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