# app.py
# last modified 11.4.22

import time
from deskapp import (
    Frontend, Backend, Logic, callback, callbacks, Keys,
)

from deskapp.mods import About, Fire, Buttons

# TODO: FIX THIS
def log_print(msg):
    with open('log.txt', 'a') as log:
        if type(msg) == type([]):
            for line in msg:
                log.write(str(line))
        else:
            log.write(str(msg))

        log.write('\n')

print = log_print


class App:
    """
    DESKAPP Entry point. This Constructor should build the application
    entirely. further calls to the App should be avoided.
    """
    def __init__(self,
            modules:       list = [], 
            splash_screen: bool = False,
            demo_mode:     bool = True,
            name:           str = "Deskapp",
            title:          str = "Deskapp",
            header:         str = "This is working.",
            v_split:      float = 0.16,
            h_split:      float = 0.16,
            autostart:     bool = True,
        ) -> None:
        """This is the main entry point. This Constructor should hold as
            many possible configuration options... as possible.
        """
        self.error_log = []
        self.app = self
        self.appdata = {'message_log':[]}
        self.splash_screen = splash_screen
        self.frontend = Frontend(
            h_split=h_split,
            v_split=v_split,
            title=title
            )

        # APP
        self.name = name
        self.header_string = header
        self.title_string = title
        self._menu = []
        self.modules = modules
        self.high_low = True

        # SETUP
        self.demo_mode = demo_mode
        self.autostart = autostart
        self.is_setup = False
        if autostart:
            self.setup()

        self.callbacks = callbacks
        self.ERROR = lambda x: self.print(x)

    def setup(self):
        """Run the init on eac of the modules."""
        self.frontend.main_screen(self.title_string)
        self.logic = Logic(self)
        self.repanel = self.logic.repanel
        self.backend = Backend(self)
        if self.demo_mode:
            self.modules.append(About)
            self.modules.append(Fire)
            self.modules.append(Buttons)
        for mod in self.modules:
                mod(self)
        self.is_setup = True

    def print(self, message, cr=False, clear=False):
        """Prints Text to the message output screen.
        params: cr=False | removes previous message,
                clear=False | removes all previous messages
        """
        # format the message
        # t = time.strftime("%b %d, %Y|%I:%M%p", time.localtime())
        t = time.strftime("%b %d|%I:%M", time.localtime())
        mesg = f"[{t}] {message}"
        # if cr:  # carrage return
        #     self.appdata['message_log'].pop(-1)
        # if clear:
        #     self.appdata['message_log'] = []
        self.appdata['message_log'].append(mesg)

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, mod_list: list) -> None:
        self._menu = mod_list

    def set_header(self, title_string: str):
        self.header_string = title_string
        self.logic.redraw_header(title_string)

    def get_header(self):
        return self.header_string

    def set_title(self, title_string: str):
        self.title_string = title_string
        
    def get_title(self):
        return self.title_string

    def start(self) -> None:
        if not self.is_setup:
            self.setup()
        if self.splash_screen:
            self.frontend.splash_screen()
        # self.frontend.main_screen(self.title_string)
        self.logic.setup_panels()

        # NEW THING!
        # LETS HAVE A MESSAGE PANEL OWNED BY THE APP
        self.message_panel = self.frontend.winrightlower

        self.backend.start()

    def close(self) -> bool:
        self.backend.running = False
        return True
    
    """
    NEW FUNCTIONALITY!! so you want the app itself to carry some data
    between some modules?? we should be able to handle that!
    """

    @property
    def data(self):
        return self.appdata

    @data.setter
    def data(self, k, v):
        self.appdata[k] = v

    """
    Key Press callback functions.
    ## ID=1  MEANS THIS IS THE CORE APP SENDING THE SIGNAL
    ## ANOTHER MOD MIGHT OVERRIDE THIS ID WHEN TAKING A 
    ## CALLBACK TO ENSURE ERROR CODES REPORT ACCURATELY.
    """
    
    @callback(ID=1, keypress=Keys.BACKSPACE) # backspace
    def on_backspace(self, *args, **kwargs):
        self.app.print("pressed backspace!")
        self.frontend.v_split_pct = .1
    
    @callback(ID=1, keypress=Keys.TAB)  # tab
    def on_tab(self, *args, **kwargs):
        self.frontend.screen_mode = False
    
    @callback(ID=1, keypress=Keys.Q)  # q
    def on_q(self, *args, **kwargs):
        self.backend.running = False
    
    @callback(ID=1, keypress=Keys.PG_DOWN)  # pg_down
    def on_pg_down(self, *args, **kwargs):
        if self.logic.cur < len(self.menu)-1:
            self.logic.cur += 1
        else:
            self.logic.cur = 0
    
    @callback(ID=1, keypress=Keys.PG_UP)  # pg_up
    def on_pg_up(self, *args, **kwargs):
        if self.logic.cur > 0:
            self.logic.cur -= 1
        else:
            self.logic.cur = len(self.menu)-1
