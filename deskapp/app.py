# STOCK IMPORTS
import os, time, getpass, socket, asyncio, sys, inspect
#  from termcolor import colored
from timeit import default_timer as timer
# IMPORT CORE UITLS
from deskapp.frontend import Frontend
from deskapp.callback import callback, callbacks
from deskapp.keys import Keys

# IMPORT MODS
from deskapp.mods import About
from deskapp.mods import Fire


def log_print(msg):
    with open('log.txt', 'a') as log:
        if type(msg) == type([]):
            for line in msg:
                log.write(str(line))
        else:
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

        self.last_update = timer()
        self.message_update = timer()
        self.message_log = []

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
        
    def repanel(self):
        self.app.frontend.recalc_winsizes()
        self.available_panels = {}
        for mod in self.app.menu:
            self.setup_panel(mod)
        self.app.frontend.redraw_message_panel()

    def all_page_update(self):
        """
        This is run every round and rebuilds the windows.
        """
        

        # AT LAST ! A SCREEN TIMER!
        if self.last_update + 0.03 > timer(): 
            sleeptime = 0.03
            # self.app.print("Overrun!")
            time.sleep(0.03)
            return
        self.last_update = timer()
        #############################
        self.app.frontend.redraw_window(self.app.frontend.winleft)

        for index, mod_name in enumerate(list(self.available_panels)):
            color    = self.app.frontend.color_rw if index == self.cur else self.app.frontend.color_cb
            message  = lambda x: self.app.frontend.winleft.win.addstr(index+1, 1, x, color)
            mod, panel      = self.available_panels[mod_name]

            if not mod.visible: continue
            # panel = self.available_panels[mod_name][1]
            
            # message(mod.name)
            # panel[0].clear()
            self.app.frontend.winleft.win.addstr(index+1, 1, mod.name, color)
            # self.app.frontend.redraw_window(self.app.frontend.winleft)
            rendered_page = mod.page(panel[0])
            
            if index == self.cur:
                panel.panel.top()

            if rendered_page:  # or did the page render itself??
                for index, line in enumerate(rendered_page.split('\n')):
                    if index > self.engine.frontend.winright_upper_dims[0]-2: break
                    panel.win.addstr(index+1, 1, line[:self.engine.frontend.winright_upper_dims[1]-2])
            
        # UPDATE THE HEADER
        self.redraw_header()
        # and update the footer.
        self.redraw_footer()
        self.redraw_messages()
        time.sleep(.001)

    def redraw_messages(self):
        if False:
            if self.message_update + 3 > timer(): return
            self.message_update = timer()
            self.app.appdata['message_log'].append(f"{time.ctime()} Testing a rolling message...")
        panel = self.app.frontend.winrightlower
        h = panel.dims[0]
        w = panel.dims[1]
        log = self.app.appdata['message_log'][-(h-2):]
        if log != self.message_update:
            self.message_update = log
            panel.win.clear()
            panel.win.box()
            panel.win.addstr(0, 1, "| Message Center |")
            for row in range(h):
                try:
                    message = log[row][:w-2]
                except:
                    break
                panel.win.addstr(row+1,1,message)
        
    def redraw_header(self, head_text=None):
        # and update the header.
        if not head_text:
            head_text = self.app.get_header()
        head_panel = self.app.frontend.header
        # if not self.app.error_timeout:
        head_panel[0].addstr(1,1,head_text, self.engine.frontend.palette[3])

    def redraw_footer(self):
        # TODO: THIS NEEDS TO BE ANOTHER THING...
        if self.engine.frontend.screen_mode:
            options = ["|q| to quit   |Tab| to enter Text  |enter| to start service", "|pgUp| change menu |pgDn| change menu |space| resize mesg cntr"]
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

    def get_user(self): return f"{getpass.getuser()}@{socket.gethostname()}"

    def get_time(self): return time.strftime("%b %d, %Y|%I:%M%p", time.localtime())

    def error_handler(self, exception, outer_err, offender, logfile="", verbose=True):
        try:
            outer_off = ''.join([x.strip(' ').strip('\n') for x in outer_err[4]])
            off = ''.join([x.strip(' ').strip('\n') for x in offender[4]])
            error_msg = []
            error_msg.append(f"╔══| Errors® |═[{self.get_time()}]═[{self.get_user()}]═[{os.getcwd(), 'green'}]═══>>\n")
            error_msg.append(f"║ {outer_err[1]} :: {'__main__' if outer_err[3] == '<module>' else outer_err[3]}\n")
            error_msg.append(f"║ \t{outer_err[2]}: {outer_off}  -->\n")
            error_msg.append(f"║ ++ {offender[1]} :: Func: {offender[3]}()\n")
            error_msg.append(f"║ -->\t{offender[2]}: {off}\n")
            error_msg.append(f"║ [ERR] {exception[0]}: {exception[1]}\n")
            error_msg.append(f"╚══════════════════════════>>\n\n")
            msg = "".join(error_msg)
            log_print(msg)
            # return msg
            return msg
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
            # if keypress:
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
            many possible configuration options as possible.
        """
        self.error_log = []
        self.app = self
        # self.appdata = {}
        # self.appdata['message_log'] = []
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
        # self.appdata = {}
        # self.appdata['message_log'] = []
        self.high_low = True

        # SETUP
        self.demo_mode = demo_mode
        self.autostart = autostart
        self.is_setup = False
        if autostart:
            self.setup()
        
        self.callbacks = callbacks
        self.ERROR = lambda x: self.backend.logger([x], "ERROR")

    def setup(self):
        """Run the init on eac of the modules."""
        self.frontend.main_screen(self.title_string)
        self.logic = Logic(self)
        self.repanel = self.logic.repanel
        self.backend = Backend(self)
        if self.demo_mode:
            self.modules.append(About)
            self.modules.append(Fire)
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
    
    # @callback(ID=1, keypress=Keys.BACKSPACE) # backspace
    # def on_space(self, *args, **kwargs):
    #     self.app.print("pressed backspace!")
    #     self.app.test()
    #     self.app.print("WAhooq!")
        
    # @callback(ID=1, keypress=127) # Shawns backspace
    # def on_space2(self, *args, **kwargs): 
    #     self.app.onspace(*args, **kwargs)
    
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
