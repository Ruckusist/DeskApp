"""
DeskApp Module Base Class
Provides hooks for page rendering, input handling, and utilities.

Updated by Claude Sonnet 4.5 10-09-25:
- Added PageFloat(panel) optional hook for floating panel content
- Modules can now override PageFloat() to render overlay dialogs

Updated by Claude Sonnet 4.5 10-10-25:
- Added event system convenience methods
- emit_event(), on_event(), off_event() helpers
"""

import subprocess
from deskapp import SubClass, Keys, callback, callbacks



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
        self.mouse_input = None
        # Generic per-module storage to reduce boilerplate in mods
        self.context = {}

        # Horizontal action bar state (for h-scroller style UIs)
        # Items are simple labels; selection + keys handled in modules.
        self.action_bar_items = []
        self.action_bar_index = 0

        # Event listeners registered by this module
        # Added by Claude Sonnet 4.5 10-10-25
        self._event_handlers = []

    @property
    def h(self):
        return self.app.logic.current_dims()[0]

    @property
    def w(self):
        return self.app.logic.current_dims()[1]

    def write(self, panel, row, col, string, color=None):
        """
        Write text to panel with bounds checking and color support.

        Args:
            panel: Panel object to write to
            row: Vertical position (0 = top)
            col: Horizontal position (0 = left)
            string: Text to write
            color: Color name string (yellow, red, green, blue, black,
                   cyan, white)

        Returns:
            True on success, False on error

        Added by GPT5 10-07-25: improved write using panel dims
        Updated by AI 10-11-25: renamed x,y to row,col for clarity
        """
        try:
            ph, pw = int(panel.dims[0]), int(panel.dims[1])
        except Exception:
            ph, pw = self.h, self.w
        if color == "yellow": c = self.front.color_yellow
        elif color == "red": c = self.front.color_red
        elif color == "green": c = self.front.color_green
        elif color == "blue": c = self.front.color_blue
        elif color == "black": c = self.front.color_black
        elif color == "cyan": c = self.front.color_cyan
        else: c = self.front.color_white
        # if row >= ph:
        #     self.print(f"write row OOB row={row} ph={ph}")
        #     return False
        # if int(col) >= pw:
        #     self.print(f"write col OOB col={col} pw={pw}")
        #     return False
        # max_len = pw - col
        # text = string if len(string) <= max_len else string[:max_len]
        text = string # string[:max(0, pw - col)]
        try:
            panel.win.addstr(row, col, text, c)
            return True
        except Exception as e:
            self.print(f"write err: {e}")
            return False

    def element_scroller(self, panel):
        # self.index = 3
        for index, element in enumerate(self.scroll_elements):
            color = self.front.chess_white if index is not self.scroll else self.front.color_black
            cursor = ">> " if index is self.scroll else "   "
            panel.win.addstr(index+self.index, 2, cursor+element, color)
        self.index += len(self.scroll_elements)

    def register_module(self):
        self.app.menu.append(self)

    ## EVENT SYSTEM HELPERS
    ## Added by: Claude Sonnet 4.5 10-10-25

    def emit_event(self, event_type: str, data: dict = None) -> bool:
        """Emit an event from this module.

        Automatically includes source=self.name.

        Args:
            event_type: Event identifier (e.g., 'data.update')
            data: Event payload

        Returns:
            True if queued, False if dropped
        """
        return self.app.emit(event_type, data, source=self.name)

    def on_event(self, event_type: str, handler) -> None:
        """Register event listener for this module.

        Tracks handlers for cleanup on module teardown.

        Args:
            event_type: Event to listen for
            handler: Callback function(event) -> None
        """
        self.app.on(event_type, handler)
        self._event_handlers.append((event_type, handler))

    def off_event(self, event_type: str, handler) -> bool:
        """Unregister event listener.

        Args:
            event_type: Event type
            handler: Handler to remove

        Returns:
            True if removed, False if not found
        """
        result = self.app.off(event_type, handler)
        if result:
            try:
                self._event_handlers.remove((event_type, handler))
            except ValueError:
                pass
        return result

    def cleanup_events(self) -> None:
        """Remove all event listeners registered by this module.

        Called automatically on module teardown.
        """
        for event_type, handler in self._event_handlers:
            self.app.off(event_type, handler)
        self._event_handlers.clear()


    #TODO: Page needs a clear function. it needs to clear the panel before writing to it.
    #TODO: but maybe not always?

    def page(self, panel):
        self.write(panel, 2, 2, "This is working!")

    # Added by GPT5 10-07-25
    # Optional secondary/right side panel content.
    def PageRight(self, panel):
        """Optional right-side panel hook.
        Override in modules to draw supplemental content.
        Default: no output.
        """
        return None

    # Added by GPT5 10-07-25
    # Optional info panel (3-line) content provider.
    def PageInfo(self, panel):
        """Optional info panel hook (3 lines max).
        Override in modules for custom info content.
        Default: return None to trigger fallback.
        """
        return None

    # Added by Claude Sonnet 4.5 10-09-25
    # Optional floating panel content provider.
    def PageFloat(self, panel):
        """Optional floating panel hook for overlays/dialogs.
        Override in modules for custom floating content.
        Default: no output (fallback message shown).
        """
        return None

    # Added by GPT5 10-07-25
    def default_page_info(self, panel):
        """Fallback info panel content (exactly 3 lines, spec).
        Lines:
          1: App / Module
          2: Keys summary
          3: FPS / Frame time / Memory / Terminal size
        Added by GPT5 10-07-25 (reverted 3-line spec)
        Updated by Claude Sonnet 4.5 10-09-25: added FPS display
        Updated by Claude Sonnet 4.5 10-10-25: added Memory (Session 1 Step 4)
        """
        try:
            cur_mod = self.app.logic.current_mod()
            mod_name = getattr(cur_mod, "name", "Unknown")
        except Exception:
            mod_name = "Unknown"
        try:
            term_h = self.front.h
            term_w = self.front.w
        except Exception:
            term_h = 0
            term_w = 0
        fps = self.app.data.get('fps', 0.0)
        frame_time = self.app.data.get('frame_time', 0.0)
        mem_str = self.app.memory.get_formatted()
        maxw = max(0, self.front.w - 4)
        line1 = f"App: {getattr(self.app, 'name', 'DeskApp')} | Mod: {mod_name}"[:maxw]
        line2 = "Keys: Tab=Input Q=Quit 1-8 Panels PgUp/Dn Switch"[:maxw]
        line3 = f"FPS: {fps} | Mem: {mem_str} | {term_w}x{term_h}"[:maxw]
        lines = [line1, line2, line3]
        colors = [self.front.color_cyan, self.front.color_green,
                  self.front.color_yellow]
        try:
            for idx, text in enumerate(lines, start=1):
                if idx >= panel.dims[0]:
                    break
                panel.win.addstr(idx, 2, text, colors[idx-1])
        except Exception:
            pass

    def mouse_decider(self, mouse): pass

    def string_decider(self, input_string):
        """Called when the user submits text in input mode (press Enter after Tab).
        Subclasses can override this, or more simply override handle_text()."""
        self.input_string = input_string
        try:
            self.handle_text(input_string)
        except Exception as e:
            self.print(f"Error handling text input: {e}")

    def end_safely(self):
        """Module cleanup on shutdown.

        Updated by Claude Sonnet 4.5 10-10-25: cleanup event listeners
        """
        self.cleanup_events()

    # Convenience hooks and helpers for building modules
    def handle_text(self, input_string: str):
        """Hook for subclasses: handle submitted text.
        Override in your module instead of string_decider for simplicity."""
        # Default behavior: log minimal debug
        self.print(f"Input: {input_string}")

    def run_shell(self, command: str, timeout: int = 10):
        """Run a shell command and return (returncode, stdout_lines, stderr_lines).
        Intended to avoid boilerplate in modules that need to shell out."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            out_lines = result.stdout.splitlines() if result.stdout else []
            err_lines = result.stderr.splitlines() if result.stderr else []
            return result.returncode, out_lines, err_lines
        except subprocess.TimeoutExpired:
            return 124, [], ["Command timed out"]
        except Exception as e:
            return 1, [], [f"Error: {e}"]

    def render_lines(self, panel, lines, start_line: int = 1, color=None, max_lines: int = None):
        """Render a list of strings into the given panel with bounds checks and truncation.
        Returns the next line index after rendering."""
        if color is None:
            color = self.front.color_white
        h = self.h
        w = self.w
        if max_lines is None:
            max_lines = max(0, h - start_line - 1)
        # Only render the tail that fits
        to_render = list(lines)[-max_lines:]
        for i, line in enumerate(to_render):
            y = start_line + i
            if y >= h - 1:
                break
            text = str(line)
            if len(text) > w - 2:
                text = text[:w-2]
            try:
                panel.win.addstr(y, 1, text, color)
            except Exception as e:
                # Best-effort: try to indicate a draw error
                try:
                    panel.win.addstr(y, 1, f"Draw err: {str(e)[:18]}", self.front.color_error)
                except:
                    pass
        return start_line + len(to_render)

    def render_vertical_progress(self, panel, progress: float, label: str = None):
        """Render a vertical progress bar in the given panel.

        Uses the full height of the panel minus a small margin.
        progress: 0.0 - 1.0
        label: optional string shown near the middle as percentage.
        """
        try:
            ph, pw = int(panel.dims[0]), int(panel.dims[1])
        except Exception:
            ph, pw = self.h, self.w

        # One column wide bar, centered horizontally.
        col = max(1, pw // 2)
        top = 1
        bottom = max(1, ph - 1)
        height = max(1, bottom - top)

        # Clamp progress.
        if progress < 0.0:
            progress = 0.0
        if progress > 1.0:
            progress = 1.0

        filled = int(height * progress)
        full_block = "\u2588"  # full block character

        # Use a high-contrast color for the bar itself.
        bar_color = getattr(self.front, "color_yellow", self.front.color_white)
        text_color = getattr(self.front, "color_red", self.front.color_white)

        for i in range(height):
            y = bottom - i
            char = full_block if i < filled else " "
            try:
                panel.win.addstr(y, col, char, bar_color)
            except Exception:
                continue

        if label is not None:
            try:
                pct = int(progress * 100)
                text = f"{label} {pct}%"
                mid = top + height // 2
                x = max(1, col - len(text) // 2)
                panel.win.addstr(mid, x, text[: max(0, pw - 2)], text_color)
            except Exception:
                pass

    def render_horizontal_progress(self, panel, progress: float,
                                   label: str = None, row: int = 1):
        """Render a left-to-right progress bar across the panel.

        Intended for wide panels like the info panel or footer.
        progress: 0.0 - 1.0
        label: optional string centered over the bar.
        row: vertical row inside the panel to draw the bar.
        """
        try:
            ph, pw = int(panel.dims[0]), int(panel.dims[1])
        except Exception:
            ph, pw = self.h, self.w

        if progress < 0.0:
            progress = 0.0
        if progress > 1.0:
            progress = 1.0

        # Leave one column padding inside borders.
        start_x = 1
        end_x = max(1, pw - 2)
        width = max(1, end_x - start_x)
        full_block = "\u2588"

        filled = int(width * progress)
        bar_color = getattr(self.front, "color_yellow", self.front.color_white)
        empty_color = getattr(self.front, "color_black", self.front.color_white)

        for x in range(width):
            ch = full_block if x < filled else " "
            try:
                panel.win.addstr(row, start_x + x, ch,
                                 bar_color if x < filled else empty_color)
            except Exception:
                continue

        if label is not None:
            try:
                pct = int(progress * 100)
                text = f"{label} {pct}%"
                x = max(1, start_x + (width - len(text)) // 2)
                panel.win.addstr(row, x,
                                 text[: max(0, width)],
                                 getattr(self.front, "color_red",
                                         self.front.color_white))
            except Exception:
                pass

    def render_action_bar(self, panel, row: int = 0):
        """Render a horizontal action bar with a selected item.

        - Uses self.action_bar_items as a flat list of labels.
        - Highlights self.action_bar_index.
        - Intended to be controlled via LEFT/RIGHT + ENTER in modules.
        """
        if not self.action_bar_items:
            return
        try:
            _, pw = int(panel.dims[0]), int(panel.dims[1])
        except Exception:
            pw = self.w
        maxw = max(0, pw - 2)

        x = 1
        for idx, label in enumerate(self.action_bar_items):
            if x >= maxw:
                break
            text = f" {label} "
            color = "yellow" if idx == self.action_bar_index else "cyan"
            # Truncate if needed
            visible = text[: max(0, maxw - x)]
            if not visible:
                break
            self.write(panel, row, x, visible, color=color)
            x += len(text) + 1

    @callback(0, keypress=Keys.UP)
    def on_up(self, *args, **kwargs):
        if self.scroll < 1:
            self.scroll = len(self.scroll_elements)-1
        else: self.scroll -= 1

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

