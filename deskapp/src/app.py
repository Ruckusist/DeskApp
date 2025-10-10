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
                 modules:              list = [],
                 splash_screen:        bool = False,
                 demo_mode:            bool = True,
                 name:                  str = "Deskapp",
                 title:                 str = "Deskapp",
                 header:                str = "This is working.",
                 # PANELS ON STARTUP
                 show_header:          bool = True,
                 disable_header:       bool = False,
                 show_footer:          bool = True,
                 disable_footer:       bool = False,
                 show_menu:            bool = True,
                 disable_menu:         bool = False,
                 show_messages:        bool = True,
                 disable_messages:     bool = False,
                 show_main:            bool = True,
                 disable_main:         bool = False,
                 show_right_panel:     bool = False,
                 disable_right_panel:  bool = False,
                 show_info_panel:      bool = True,
                 disable_info_panel:   bool = False,
                 show_box:             bool = True,
                 show_banner:          bool = True,
                 # FLOATING PANEL - Added Claude Sonnet 4.5 10-09-25
                 show_floating:        bool = False,
                 disable_floating:     bool = False,
                 floating_height:       int = 10,
                 floating_width:        int = 40,
                 # DEFAULT SPLITS
                 v_split:             float = 0.4,
                 h_split:             float = 0.16,
                 r_split:             float = 0.16,
                 autostart:            bool = True,
                 # PERFORMANCE CONTROLS - Added Claude Sonnet 4.5 10-09-25
                 fps_cap:               int = None,
                 # COMMAND CONTROLS
                 use_mouse:            bool = False,
                 use_focus:            bool = False,
            ):
        # initialize the constructor.
        self.app = self
        self.user_modules = modules
        self.show_splash = splash_screen
        self.show_demo = demo_mode
        self.show_box = show_box
        self.show_banner = show_banner
        # Added by Claude Sonnet 4.5 10-09-25
        self.show_floating = show_floating
        self.floating_height = floating_height
        self.floating_width = floating_width
        self.name = name
        self.title = title
        self.header = header
        self.v_split = v_split
        self.h_split = h_split
        self.r_split = r_split
        self.should_autostart = autostart
        # Added by Claude Sonnet 4.5 10-09-25
        self.fps_cap = fps_cap

        # PANELS ON STARTUP
        self.show_header = show_header
        self.show_footer = show_footer
        self.show_menu = show_menu
        self.show_messages = show_messages
        self.show_main = show_main
        # Added by GPT5 10-07-25
        self.show_right_panel = show_right_panel
        self.show_info_panel = show_info_panel

        # DISABLE SOME PANELS
        self.disable_header = disable_header
        self.disable_footer = disable_footer
        self.disable_menu = disable_menu
        self.disable_messages = disable_messages
        self.diable_main = disable_main
        # Added by GPT5 10-07-25
        self.disable_right_panel = disable_right_panel
        self.disable_info_panel = disable_info_panel
        # Added by Claude Sonnet 4.5 10-09-25
        self.disable_floating = disable_floating

        # APP FUNCTIONALITY
        self.data = {'messages': [], 'errors': []}
        self.menu = self.user_modules
        if self.show_demo:
            self.menu.extend([About, Buttons, Fire])  # , Deskhunter

        # CORE MODULES
        self.front = Curse(use_mouse=use_mouse, use_focus=use_focus)
        if self.show_splash:
            self.front.splash_screen()
        self.logic = Logic(self)
        self.back  = Backend(self)

        # Start the Game.
        if self.should_autostart:
            self.start()

    def start(self):
        self.back.main()

    def close(self):
        self.back.should_stop = True

    def exit(self):
        self.close()

    def print(self, message: str="", **kwargs):
        # check to see if prev message same as this one.
        prev_message = self.data['messages'][-1] if len(self.data['messages']) > 0 else ""
        if type(prev_message) == type(str):
            if message == prev_message:
                self.data["messages"][-1] = f"{message} (repeating...)"
            elif message == prev_message[:-14]:
                pass
            else:
                self.data['messages'].append(message)
        else:
            self.data['messages'].append(message)
        if len(self.data['messages']) > 300:  # 4k screens with 12pt font have 282 lines.
            self.data['messages'].pop(0)

    def error(self, message: str=""):
        self.print(message)

    def add_module(self, module: Module):
        # !! THIS Not Working properly.
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
        if not self.app.disable_header:
            self.app.back.show_header = not self.app.back.show_header
            self.print(f"pressed NUM1 ... show_header = {self.app.back.show_header}")
        else:
            self.print("Header disabled. Cannot toggle.")

    @callback(ID=1, keypress=Keys.NUM2)  # NUM2 - footer
    def on_NUM2(self, *args, **kwargs):
        if not self.app.disable_footer:
            if not self.app.front.key_mode:
                self.app.back.show_footer = not self.app.back.show_footer
                self.print(f"pressed NUM2 ... show_footer = {self.app.back.show_footer}")
        else:
            self.print("Footer disabled. Cannot toggle.")

    @callback(ID=1, keypress=Keys.NUM3)  # NUM3 - menu
    def on_NUM3(self, *args, **kwargs):
        if not self.app.disable_menu:
            self.app.back.show_menu = not self.app.back.show_menu
            self.print(f"pressed NUM3 ... show_menu = {self.app.back.show_menu}")
        else:
            self.print("Menu disabled. Cannot toggle.")

    @callback(ID=1, keypress=Keys.NUM4)  # NUM4 - main
    def on_NUM4(self, *args, **kwargs):
        # if not self.app.disable_main:
        self.app.back.show_main = not self.app.back.show_main
        self.print(f"pressed NUM4 ... show_main = {self.app.back.show_main}")
        # else:
        #     self.print("Main disabled. Cannot toggle.")

    @callback(ID=1, keypress=Keys.NUM5)  # NUM5 - messages
    def on_NUM5(self, *args, **kwargs):
        if not self.app.disable_messages:
            self.app.back.show_messages = not self.app.back.show_messages
            self.print(f"pressed NUM5 ... show_messages = {self.app.back.show_messages}")
        else:
            self.print("Messages disabled. Cannot toggle.")

    @callback(ID=1, keypress=Keys.NUM6)  # NUM5 - show all
    def on_NUM6(self, *args, **kwargs):
        if not all([self.app.back.show_messages, self.app.back.show_menu,
               self.app.back.show_main, self.app.back.show_header,
               self.app.back.show_footer, getattr(self.app.back, 'show_right_panel', True),
               getattr(self.app.back, 'show_info_panel', True)]):

            if not self.app.disable_messages:
                self.app.back.show_messages = True
            if not self.app.disable_menu:
                self.app.back.show_menu = True
            # if not self.app.disable_main:
            self.app.back.show_main = True
            if not self.app.disable_header:
                self.app.back.show_header = True
            if not self.app.disable_footer:
                self.app.back.show_footer = True
            if not self.app.disable_info_panel:
                self.app.back.show_info_panel = True
            if not self.app.disable_right_panel:
                self.app.back.show_right_panel = True
        else:
            self.app.back.show_messages = False
            self.app.back.show_menu = False
            self.app.back.show_header = False
            self.app.back.show_footer = False
            self.app.back.show_main = True
            # leave info/right off in hide-all mode
            if hasattr(self.app.back, 'show_right_panel'):
                self.app.back.show_right_panel = False
            if hasattr(self.app.back, 'show_info_panel'):
                self.app.back.show_info_panel = False

    @callback(ID=1, keypress=Keys.NUM7)
    def on_NUM7(self, *args, **kwargs):
        if not self.app.disable_info_panel:
            if not self.app.front.key_mode:
                self.app.back.show_info_panel = not self.app.back.show_info_panel
                self.print(f"pressed NUM7 ... show_info_panel = {self.app.back.show_info_panel}")
        else:
            self.print("Info panel disabled. Cannot toggle.")

    # Added by GPT5 10-07-25 NUM8 toggle info panel
    @callback(ID=1, keypress=Keys.NUM8)
    def on_NUM8(self, *args, **kwargs):
        if not self.app.disable_right_panel:
            if not self.app.front.key_mode:
                self.app.back.show_right_panel = not self.app.back.show_right_panel
                self.print(f"pressed NUM8 ... show_right_panel = {self.app.back.show_right_panel}")
        else:
            self.print("Right panel disabled. Cannot toggle.")

    # Added by Claude Sonnet 4.5 10-09-25 NUM9 toggle floating panel
    @callback(ID=1, keypress=Keys.NUM9)
    def on_NUM9(self, *args, **kwargs):
        if not self.app.disable_floating:
            if not self.app.front.key_mode:
                self.app.back.show_floating = not self.app.back.show_floating
                status = "visible" if self.app.back.show_floating else "hidden"
                self.print(f"Floating panel {status}")
        else:
            self.print("Floating panel disabled. Cannot toggle.")

    @callback(ID=1, keypress=Keys.Q)  # Q
    def on_Q(self, *args, **kwargs):
        self.app.back.should_stop = True

    @callback(ID=1, keypress=Keys.q)  # q
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
