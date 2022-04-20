# STOCK IMPORTS
import os, time, getpass, socket, asyncio, sys, inspect
from termcolor import colored

# IMPORT CORE UITLS
from deskapp.frontend import Frontend
from deskapp.callback import callback, callbacks
from deskapp.keys import Keys

# IMPORT MODS
from deskapp.mods import About
from deskapp.mods import Fire


def log_print(msg):
    with open('log.txt', 'a') as log:
        log.write(str(msg))
        log.write('\n')

print = log_print


class Logic:
    def __init__(self, engine):
        self.engine = engine  # access to the kill switch.
        self.app = engine  # Trying to rebrand this...
        # self.working_panels = []       # the list of pointers
        self.cur = 0                   # the current working panel
        self.available_panels = {}     # V.2 of this idea.

    def setup_panel(self, mod):
        # Panel object is a named tuple (win, panel, label, dims)
        panel = self.app.frontend.make_panel(
                    self.app.frontend.winright_upper_dims,
                    mod.name,  # Item is a Title String.
                    True)
        self.available_panels[mod.name] = [mod,panel]

    def setup_panels(self, mod=None):
        if not mod:
            for mod in self.app.menu:
                self.setup_panel(mod)
        else:
            self.setup_panel(mod)
            
        self.all_page_update()
        self.redraw_header()

    def all_page_update(self):
        """
        This is run every round and rebuilds the windows.
        """
        self.app.frontend.redraw_window(self.app.frontend.winleft)

        for index, mod_name in enumerate(list(self.available_panels)):
            color    = self.app.frontend.color_rw if index == self.cur else self.app.frontend.color_cb
            message  = lambda x: self.app.frontend.winleft[0].addstr(index+1, 1, x, color)
            mod, panel      = self.available_panels[mod_name]

            if not mod.visible: continue
            # panel = self.available_panels[mod_name][1]
            
            message(mod.name)
            # panel[0].clear()
            rendered_page = mod.page(panel[0])
            
            if index == self.cur:
                panel.panel.top()

            if rendered_page:  # or did the page render itself??
                for index, line in enumerate(rendered_page.split('\n')):
                    if index > self.engine.frontend.winright_upper_dims[0]-2: break
                    panel.win.addstr(index+1, 1, line[:self.engine.frontend.winright_upper_dims[1]-2])
            
        # and update the footer.
        self.redraw_footer()
        time.sleep(.001)

    def redraw_header(self):
        # and update the header.
        head_text = self.app.header()
        head_panel = self.app.frontend.header
        # if not self.app.error_timeout:
        head_panel[0].addstr(1,1,head_text, self.engine.frontend.palette[3])

    def redraw_footer(self):
        # TODO: THIS NEEDS TO BE ANOTHER THING...
        if self.engine.frontend.screen_mode:
            options = ["|q| to quit   |Tab| to enter Text  |enter| to start service", "|pgUp| change menu |pgDn| change menu"]
        else:
            options = [" Cool stuff goes here...", "|enter| submit   |'stop'| to kill service"]
        self.engine.frontend.redraw_window(self.engine.frontend.debug)
        self.engine.frontend.debug[0].addstr(1, 1, options[0], self.engine.frontend.color_gb)
        self.engine.frontend.debug[0].addstr(2, 1, options[1], self.engine.frontend.color_gb)

    def end_safely(self):
        for mod_name in list(self.available_panels):
            mod = self.available_panels[mod_name][0]
            mod.end_safely()

        self.app.frontend.end_safely()

    def decider(self, keypress):
        """Callback decider system."""
        mod_g = self.available_panels[
            list(self.available_panels)[self.cur]
        ]
        mod = mod_g[0]
        panel = mod_g[1]
        app_callbacks = self.app.callbacks
        if type(keypress) is str: 
            mod.string_decider(panel, keypress)
            return
        if int(keypress) < 1: return
        try:
            all_calls_for_button =\
                list(filter(lambda d: d['key'] in [keypress], app_callbacks))
            call_for_button =\
                list(filter(lambda d: d['classID'] in [mod.classID,0,1], all_calls_for_button))[0]
        except Exception as e:
            self.engine.ERROR(f"k: {keypress} has no function")
            return
        try:
            callback = call_for_button['func']
            callback(mod, panel)
        except Exception as e:
            self.engine.ERROR(f"{call_for_button['func'].__name__} | {e}")


class Backend:
    """This is the Main_Loop"""
    def __init__(self, parent):
        self.app = parent
        self.running = True
        self.error_log = self.app.error_log
        
    def logger(self, message:list, message_type:str):       
        # for line in message:
        #     print(f"[{message_type}]\t{line}")
        #  TODO
        self.error_log.append((message, message_type))

    def get_user(self): return colored(f"{getpass.getuser()}@{socket.gethostname()}", "cyan")

    def get_time(self): return colored(time.strftime("%b %d, %Y|%I:%M%p", time.localtime()), "yellow")

    def error_handler(self, exception, outer_err, offender, logfile="", verbose=True):
        try:
            outer_off = ''.join([x.strip(' ').strip('\n') for x in outer_err[4]])
            off = ''.join([x.strip(' ').strip('\n') for x in offender[4]])
            error_msg = []
            error_msg.append(f"╔══| Errors® |═[{self.get_time()}]═[{self.get_user()}]═[{colored(os.getcwd(), 'green')}]═══>>")
            error_msg.append(f"║ {outer_err[1]} :: {'__main__' if outer_err[3] == '<module>' else outer_err[3]}")
            error_msg.append(f"║ \t{outer_err[2]}: {outer_off}  -->")
            error_msg.append(f"║ ++ {offender[1]} :: Func: {offender[3]}()")
            error_msg.append(f"║ -->\t{offender[2]}: {off}")
            error_msg.append(f"║ [ERR] {exception[0]}: {exception[1]}")
            error_msg.append(f"╚══════════════════════════>>")
            msg = "\n".join(error_msg)
            # print(msg)
            # return msg
            return (error_msg, "ERROR")
        except: print("There has been Immeasureable damage. Good day.")

    def print_error(self, err):
        error_mesg = err[0]
        print(err[1])
        for line in error_mesg:
            print(line)

    @property
    def is_running(self):
        return self.running

    async def main(self):
        while self.is_running:
            self.app.frontend.refresh()
            keypress = 0
            keypress = self.app.frontend.get_input()
            if keypress:
                self.app.logic.decider(keypress)
            self.app.logic.all_page_update()
  
    def start(self):
        try:
            # print("Starting main loop.")
            asyncio.run(self.main())
        except KeyboardInterrupt:
            # so it should never end this way.
            print("Keyboard Interrupt: Ending Safely.")
        except Exception:
            exception = sys.exc_info()
            outer_err = inspect.stack()[-1]
            offender = inspect.trace()[-1]
            error = self.error_handler(
                exception, 
                outer_err, 
                offender
            )
            # The error isnt working because its not printing.
            print(error)

        finally:
            self.exit_program()

    def exit_program(self):
        self.app.logic.end_safely()


class App:
    name = "Deskapp"

    def __init__(self, modules:list = [], demo_mode=True) -> None:
        self.error_log = []
        self.frontend = Frontend()
        self.logic = Logic(self)
        self.backend = Backend(self)

        # APP
        self._menu = []
        self.modules = modules
        if demo_mode:
            self.modules.append(About)
            self.modules.append(Fire)
        self.appdata = {}

        # SETUP
        for mod in self.modules:
            mod(self)

        self.callbacks = callbacks
        self.ERROR = lambda x: self.backend.logger([x], "ERROR")

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, mod_list: list) -> None:
        self._menu = mod_list

    def header(self):
        return "This is working!"

    def start(self) -> None:
        # self.frontend.spash_screen()
        self.frontend.main_screen("|~  Deskapp  ~|")
        self.logic.setup_panels()
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
