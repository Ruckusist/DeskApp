import time
from timeit import default_timer as timer
from deskapp import SubClass, Keys

class Backend(SubClass):
    def __init__(self, app, show_header, show_footer,
                 show_menu, show_messages, show_main):
        super().__init__(app)
        self.should_stop = False
        self.update_timeout = .1
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
        # class_id = random.random()
        active_module = mod(self.app)
        dims = self._calc_main_dims()
        panel       = self.front.make_panel(dims, active_module.name, box=self.app.show_box, banner=self.app.show_banner)
        self.app.logic.available_panels[mod.name] = [active_module, panel, dims]

    def redraw_mods(self):
        dims = self._calc_main_dims()
        for mod_name in self.app.logic.available_panels:
            active = self.app.logic.available_panels[mod_name]
            panel = self.front.make_panel(dims, active[0].name, box=self.app.show_box, banner=self.app.show_banner)
            active[1] = panel
            active[2] = dims

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
        self.messages_w = dims[1]-2
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
