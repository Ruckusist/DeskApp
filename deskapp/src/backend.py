"""
DeskApp Backend
Manages the main event loop, panel rendering, and user input handling.

Updated by: Claude Sonnet 4.5 10-09-25
- Fixed global box parameter: all panels now respect app.show_box setting
- Updated all make_panel calls to pass box=self.app.show_box parameter
- Implemented clean panel refresh with win.erase() to eliminate artifacts
- Each panel redraws box/banner after clearing for proper rendering
"""

import time
from timeit import default_timer as timer
from deskapp import SubClass, Keys

class Backend(SubClass):
    def __init__(self, app):
        super().__init__(app)
        self.should_stop = False
        self.update_timeout = .1
        self.last_update = timer()

        # display toggles.
        #self.screen_size_changed = False
        self.show_header    = app.show_header
        self.show_footer    = app.show_footer
        self.show_menu      = app.show_menu
        self.show_messages  = app.show_messages
        self.show_main      = app.show_main
        # Added by GPT5 10-07-25 new panels
        self.show_right_panel = getattr(app, 'show_right_panel', False)
        self.show_info_panel  = getattr(app, 'show_info_panel', True)

        self.footer_buffer  = ""
        self.menu_w         = 15
        self.message_h      = 3
        self.messages_w     = 20

        self.redraw_mains()
        self.prev_panels_shown = (self.show_header, self.show_footer,
                                  self.show_menu, self.show_messages,
                                  self.show_main, self.show_right_panel,
                                  self.show_info_panel)

    # Added compute_layout by GPT5 10-07-25 v0.1.9 plan
    def compute_layout(self):
        """Centralize all panel dimension math.

        Returns dict with keys:
          total_w, total_h
          header_h, footer_h, info_h
          content_top, content_bottom
          menu_w, right_w
          content_w_left (width available to main/messages stack)
          main_h, messages_h, main_top, messages_top
        """
        total_h = self.front.h
        total_w = self.front.w
        header_h = 3 if self.show_header else 0
        footer_h = 3 if self.show_footer else 0
        info_h   = 5 if self.show_info_panel else 0

        vertical_available = total_h - header_h - footer_h - info_h
        if vertical_available < 3:
            vertical_available = 3

        # Split between main and messages (stacked) if both visible
        if self.show_main and self.show_messages:
            msg_part = int(vertical_available * self.app.v_split)
            if msg_part < 1:
                msg_part = 1
            main_h = vertical_available - msg_part
            if main_h < 1:
                main_h = 1
            messages_h = msg_part
        elif self.show_main and not self.show_messages:
            main_h = vertical_available
            messages_h = 0
        elif self.show_messages and not self.show_main:
            # occupy all with messages
            main_h = 0
            messages_h = vertical_available
        else:
            # neither shown -> keep space but assign to main for panel safety
            main_h = vertical_available
            messages_h = 0

        # Horizontal splits
        menu_w = int(total_w * self.app.h_split) if self.show_menu else 0
        right_w = int(total_w * getattr(self.app, 'r_split', 0.16)) \
            if self.show_right_panel else 0
        if right_w and right_w < 8:
            right_w = 8
        content_w_left = total_w - menu_w - right_w
        if content_w_left < 10:
            content_w_left = 10

        main_top = header_h
        messages_top = header_h + main_h

        layout = {
            'total_w': total_w,
            'total_h': total_h,
            'header_h': header_h,
            'footer_h': footer_h,
            'info_h': info_h,
            'content_top': header_h,
            'content_bottom': header_h + vertical_available,
            'menu_w': menu_w,
            'right_w': right_w,
            'content_w_left': content_w_left,
            'main_h': main_h,
            'messages_h': messages_h,
            'main_top': main_top,
            'messages_top': messages_top,
        }
        return layout

    def redraw_mains(self):
        self.header_panel    = self.draw_header()
        self.footer_panel    = self.draw_footer()
        self.menu_panel      = self.draw_menu()
        self.messages_panel  = self.draw_messages()
        # Added by GPT5 10-07-25
        self.right_panel     = self.draw_right_panel()
        self.info_panel      = self.draw_info_panel()

    def setup_mods(self):
        # first time setup of all mods.
        for mod in self.app.menu:
            self.setup_mod(mod)

    def _calc_main_dims(self):
        layout = self.compute_layout()
        height = layout['main_h'] if self.show_main else layout['messages_h']
        width = layout['content_w_left']
        top_left_x = layout['main_top']
        top_left_y = layout['menu_w']
        # Safety clamps added by GPT5 10-07-25 v0.1.10
        if height < 1:
            height = 1
        if width < 1:
            width = 1
        return [height, width, top_left_x, top_left_y]

    def setup_mod(self, mod):
        # class_id = random.random()
        active_module = mod(self.app)
        dims = self._calc_main_dims()
        if dims[0] < 1: dims[0] = 1
        if dims[1] < 1: dims[1] = 1
        panel = self.front.make_panel(
            dims,
            active_module.name,
            box=self.app.show_box,
            banner=self.app.show_banner
        )
        self.app.logic.available_panels[mod.name] = [
            active_module, panel, dims
        ]

    def redraw_mods(self):
        dims = self._calc_main_dims()
        for mod_name in self.app.logic.available_panels:
            active = self.app.logic.available_panels[mod_name]
            safe_dims = list(dims)
            if safe_dims[0] < 1: safe_dims[0] = 1
            if safe_dims[1] < 1: safe_dims[1] = 1
            panel = self.front.make_panel(
                safe_dims,
                active[0].name,
                box=self.app.show_box,
                banner=self.app.show_banner
            )
            active[1] = panel
            active[2] = safe_dims

    def draw_header(self):
        height      = 3
        width       = self.front.w
        top_left_x  = 0
        top_left_y  = 0
        dims        = [height, width, top_left_x, top_left_y]
        dims_string = ' ,'.join([str(x) for x in dims])
        # self.print(f"Header dims: {dims_string}")
        panel       = self.front.make_panel(
            dims, self.app.title, box=self.app.show_box
        )
        return panel

    def draw_footer(self):
        height      = 3
        width       = self.front.w
        top_left_x  = self.front.h - 3
        top_left_y  = 0
        dims        = [height, width, top_left_x, top_left_y]
        panel       = self.front.make_panel(
            dims, "Input", box=self.app.show_box
        )
        if not self.front.key_mode:
            panel.win.addstr(
                1, 2,
                f"Press <tab> to enter text; <h> for help.",
                self.front.color_green
            )
        return panel

    def draw_menu(self):
        height = self.front.h
        if self.show_footer:
            height -= 3
        if self.show_header:
            height -= 3
        if self.show_info_panel:
            height -= 5

        menu_split = int(self.front.w * self.app.h_split)
        width = menu_split
        top_left_x = 0
        if self.show_header:
            top_left_x += 3
        top_left_y = 0

        dims = [height, width, top_left_x, top_left_y]
        self.menu_w = width
        # Usable inner height (minus top/bottom box)
        self.menu_h = max(0, height - 2)
        panel = self.front.make_panel(
            dims, "Menu", box=self.app.show_box
        )
        return panel

    def draw_messages(self):
        layout = self.compute_layout()
        if not self.show_messages:
            # minimal dummy panel
            dims = [1,1,layout['main_top'], layout['menu_w']]
            panel = self.front.make_panel(
                dims, "Messages", box=self.app.show_box
            )
            return panel
        height = (layout['messages_h'] if self.show_main
                  else layout['messages_h'])
        top_left_x = (layout['messages_top'] if self.show_main
                      else layout['main_top'])
        width = layout['content_w_left']
        top_left_y = layout['menu_w']
        if height < 1: height = 1
        if width < 1: width = 1
        dims = [height, width, top_left_x, top_left_y]
        self.messages_h = max(0, height - 2)
        self.messages_w = max(0, width - 2)
        panel = self.front.make_panel(
            dims, "Messages", box=self.app.show_box
        )
        return panel

    # Added by GPT5 10-07-25
    def draw_right_panel(self):
        layout = self.compute_layout()
        if not self.show_right_panel:
            dims = [1,1,layout['main_top'], layout['total_w']-1]
            return self.front.make_panel(
                dims, "R", box=self.app.show_box
            )
        # Align vertical span with menu panel logic: full working vertical
        # area (under header, above footer & info panel) independent of
        # main/messages split.
        total_h = self.front.h
        height = total_h
        if self.show_footer:
            height -= 3
        if self.show_header:
            height -= 3
        if self.show_info_panel:
            height -= 5
        if height < 1:
            height = 1
        width = layout['right_w'] if layout['right_w'] else 1
        if width < 1:
            width = 1
        top_left_x = 0
        if self.show_header:
            top_left_x += 3
        top_left_y = self.front.w - width
        dims = [height, width, top_left_x, top_left_y]
        panel = self.front.make_panel(
            dims, "Right", box=self.app.show_box
        )
        return panel

    # Added by GPT5 10-07-25
    def draw_info_panel(self):
        if not self.show_info_panel:
            # minimal dummy panel when disabled
            dims = [1,1,self.front.h-1,0]
            return self.front.make_panel(
                dims, "I", box=self.app.show_box
            )
        # 5-line info panel: provides 3 writable lines inside box
        height = 5
        width = self.front.w  # full width
        # start from bottom of screen, move up by footer (if present)
        # and panel height
        footer_offset = 3 if self.show_footer else 0
        top_left_x = self.front.h - footer_offset - height
        top_left_y = 0
        dims = [height, width, top_left_x, top_left_y]
        panel = self.front.make_panel(
            dims, "Info", box=self.app.show_box
        )
        return panel

    def update_header(self):
        try:
            # Clear panel to prevent artifacts
            self.header_panel.win.erase()
            # Redraw border and banner if needed
            if self.app.show_box:
                self.header_panel.win.box()
            if self.app.show_banner:
                banner_text = f"| {self.app.title} |"
                maxw = max(0, self.front.w - 2)
                self.front.safe_addstr(
                    self.header_panel.win, 0, 2,
                    banner_text[:maxw]
                )
            # Draw content
            text = str(self.app.header)
            maxw = max(0, self.front.w - 4)
            if len(text) > maxw:
                text = text[:maxw]
            self.header_panel.win.addstr(
                1, 3, text, self.front.color_blue
            )
        except Exception:
            pass

    def update_footer(self):
        try:
            # Clear panel to prevent artifacts
            self.footer_panel.win.erase()
            # Redraw border and banner if needed
            if self.app.show_box:
                self.footer_panel.win.box()
            if self.app.show_banner:
                banner_text = "| Input |"
                maxw = max(0, self.front.w - 2)
                self.front.safe_addstr(
                    self.footer_panel.win, 0, 2,
                    banner_text[:maxw]
                )
            # Draw content
            if self.front.key_mode:
                maxw = max(0, self.front.w - 6)
                buf = self.front.key_buffer[:maxw]
                pad = " " * max(0, maxw - len(buf))
                self.footer_panel.win.addstr(
                    1, 2, f": {buf}{pad}",
                    self.front.color_yellow
                )
            else:
                text = "Press <tab> to enter text; <h> for help."
                maxw = max(0, self.front.w - 4)
                if len(text) > maxw:
                    text = text[:maxw]
                self.footer_panel.win.addstr(
                    1, 2, text, self.front.color_green
                )
        except Exception:
            pass

    def update_messages(self):
        try:
            # Clear panel to prevent artifacts
            self.messages_panel.win.erase()
            # Redraw border and banner if needed
            if self.app.show_box:
                self.messages_panel.win.box()
            if self.app.show_banner:
                banner_text = "| Messages |"
                maxw = max(0, self.messages_w)
                self.front.safe_addstr(
                    self.messages_panel.win, 0, 2,
                    banner_text[:maxw]
                )
            # Draw content
            max_lines = max(0, self.messages_h)
        except Exception:
            max_lines = 0
        # Only render what fits
        lines = list(self.app.data['messages'])[-max_lines:]
        for idx, mesg in enumerate(lines):
            if idx >= max_lines:
                break
            text = str(mesg)
            width = max(0, self.messages_w - 2)
            if len(text) > width:
                text = text[:width]
            else:
                text = text + (" " * (width - len(text)))
            y = idx + 1
            x = 1
            try:
                self.messages_panel.win.addstr(
                    y, x, text, self.front.color_cyan
                )
            except Exception:
                # Swallow draw errors to avoid crashing the UI
                pass

    def update_menu(self):
        # Clear panel to prevent artifacts
        try:
            self.menu_panel.win.erase()
            # Redraw border and banner if needed
            if self.app.show_box:
                self.menu_panel.win.box()
            if self.app.show_banner:
                banner_text = "| Menu |"
                maxw = max(0, self.menu_w)
                self.front.safe_addstr(
                    self.menu_panel.win, 0, 2,
                    banner_text[:maxw]
                )
        except Exception:
            pass

        max_lines = getattr(self, 'menu_h', max(0, self.front.h - 2))
        max_text_w = max(0, self.menu_w - 2)
        cur = self.app.logic.current
        for i, mod in enumerate(self.app.menu[:max_lines]):
            try:
                text = str(mod.name)
                if len(text) > max_text_w:
                    text = text[:max_text_w]
                color = (self.front.color_select if i == cur
                         else self.front.color_red)
                self.menu_panel.win.addstr(i+1, 1, text, color)
            except Exception:
                # avoid crashing on draw errors
                pass

    # Added by GPT5 10-07-25
    # Updated by Claude Sonnet 4.5 10-09-25: use erase() for clean refresh
    def update_right_panel(self):
        if not self.show_right_panel:
            return
        try:
            # Clear panel to prevent artifacts
            self.right_panel.win.erase()
            # Redraw border and banner if needed
            if self.app.show_box:
                self.right_panel.win.box()
            if self.app.show_banner:
                banner_text = "| Right |"
                maxw = max(0, self.right_panel.dims[1] - 2)
                self.front.safe_addstr(
                    self.right_panel.win, 0, 2,
                    banner_text[:maxw]
                )
            # Draw module content
            current_mod = self.app.logic.current_mod()
            if hasattr(current_mod, 'PageRight'):
                current_mod.PageRight(self.right_panel)
        except Exception:
            pass

    # Added by GPT5 10-07-25
    # Updated by Claude Sonnet 4.5 10-09-25: use erase() for clean refresh
    def update_info_panel(self):
        if not self.show_info_panel:
            return
        try:
            # Clear panel to prevent artifacts
            self.info_panel.win.erase()
            # Redraw border and banner if needed
            if self.app.show_box:
                self.info_panel.win.box()
            if self.app.show_banner:
                banner_text = "| Info |"
                maxw = max(0, self.info_panel.dims[1] - 2)
                self.front.safe_addstr(
                    self.info_panel.win, 0, 2,
                    banner_text[:maxw]
                )
            # Draw module content or fallback
            current_mod = self.app.logic.current_mod()
            if (hasattr(current_mod, 'PageInfo') and
                    current_mod.PageInfo(self.info_panel) is not None):
                return
            # fallback
            current_mod.default_page_info(self.info_panel)
        except Exception:
            pass

    def loop(self):
        # HANDLE THE INPUT
        key_mouse = self.front.get_input()
        if key_mouse == Keys.RESIZE:
            self.front.resized()
        else:
            self.app.logic.decider( key_mouse )

        # HANDLE PANEL RESIZE ->
        cur_panels_shown = (self.show_header, self.show_footer, self.show_menu,
                             self.show_messages, self.show_main,
                             self.show_right_panel, self.show_info_panel)
        if ((cur_panels_shown != self.prev_panels_shown) or
            self.front.has_resized_happened):
            # self.print("Resizing...")
            self.redraw_mains()
            self.redraw_mods()
            self.front.has_resized_happened = False

        # RUN A FRAME ON EVERY MOD
        for mod in self.app.logic.available_panels:
            panel = self.app.logic.available_panels[mod][1]
            # Clear panel to prevent artifacts
            try:
                panel.win.erase()
                # Redraw border and banner if needed
                if self.app.show_box:
                    panel.win.box()
                if self.app.show_banner:
                    banner_text = f"| {mod} |"
                    maxw = max(0, panel.dims[1] - 2)
                    self.front.safe_addstr(
                        panel.win, 0, 2, banner_text[:maxw]
                    )
            except Exception:
                pass
            # Render module content
            self.app.logic.available_panels[mod][0].page(panel)

        # UPDATE THE BUILT IN STUFF.
        self.update_messages()
        self.update_header()
        self.update_footer()
        self.update_menu()
        self.update_right_panel()
        self.update_info_panel()

        # REDRAW THE SCREEN
        if self.show_header:   self.header_panel.panel.show()
        else:                  self.header_panel.panel.hide()
        if self.show_footer:   self.footer_panel.panel.show()
        else:                  self.footer_panel.panel.hide()
        if self.show_menu:     self.menu_panel.panel.show()
        else:                  self.menu_panel.panel.hide()
        if self.show_messages: self.messages_panel.panel.show()
        else:                  self.messages_panel.panel.hide()
        if self.show_right_panel: self.right_panel.panel.show()
        else: self.right_panel.panel.hide()
        if self.show_info_panel: self.info_panel.panel.show()
        else: self.info_panel.panel.hide()
        cur_panel = self.app.logic.current_panel()
        if self.show_main:
            cur_panel.panel.show()
            cur_panel.panel.top()
            # keep side panels above main if visible
            try:
                if self.show_right_panel:
                    self.right_panel.panel.top()
                if self.show_info_panel:
                    self.info_panel.panel.top()
            except Exception:
                pass
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
                if sleepfor < 0:
                    sleepfor = 0
                time.sleep(sleepfor)

            except KeyboardInterrupt:
                break

            except Exception as e:
                if not self.should_stop:
                    self.print(f"Error off main loop: {e} ** carrying on **")
                raise


        self.front.end_safely()
    # Avoid direct console print on shutdown to keep screen clean
