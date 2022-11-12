import time
from timeit import default_timer as timer


class Logic:
    def __init__(self, app):
        self.app = app
        self.print = app.print  # this is the newHotness

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
                    if index > self.app.frontend.winright_upper_dims[0]-3: break
                    panel.win.addstr(index+1, 1, line[:self.app.frontend.winright_upper_dims[1]-2])
            
        # UPDATE THE HEADER
        self.redraw_header()
        # and update the footer.
        self.redraw_footer()
        self.redraw_messages()
        # time.sleep(.001)  # this isnt necessary because of the screenrate.

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
        head_panel[0].addstr(1,1,head_text, self.app.frontend.palette[3])

    def redraw_footer(self):
        # TODO: THIS NEEDS TO BE ANOTHER THING...
        if self.app.frontend.screen_mode:
            options = ["|q| to quit   |Tab| to enter Text  |enter| to start service", "|pgUp| change menu |pgDn| change menu |space| resize mesg cntr"]
        else:
            options = [" Cool stuff goes here...", "|enter| submit   |'stop'| to kill service"]
        self.app.frontend.redraw_window(self.app.frontend.debug)
        self.app.frontend.debug[0].addstr(1, 1, options[0], self.app.frontend.color_gb)
        self.app.frontend.debug[0].addstr(2, 1, options[1], self.app.frontend.color_gb)

    def end_safely(self):
        for mod_name in list(self.available_panels):
            mod = self.available_panels[mod_name][0]
            mod.end_safely()

        self.app.frontend.end_safely()
    
    def decider(self, keypress):
        """Callback decider system."""
        cur_idx = list(self.available_panels)[self.cur]
        cur_mod = self.available_panels[cur_idx]

        mod_class = cur_mod[0]
        mod_panel = cur_mod[1]
        
        if isinstance(keypress, str):
            mod_class.string_decider(keypress)

        elif isinstance(keypress, tuple):
            mod_class.mouse_decider(keypress)

        elif isinstance(keypress, int):
            try:
                all_calls_for_button = list(filter(lambda callback: callback['key'] in [int(keypress)], self.app.callbacks))
                call_for_button = list(filter(lambda callback: callback['classID'] in [mod_class.classID,0,1], all_calls_for_button))[0]
                callback = call_for_button['func']
                callback(mod_class, mod_panel)

            except Exception as ex:
                self.print(f"k: {keypress} has no function")
