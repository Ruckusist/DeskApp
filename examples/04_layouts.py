"""
04_layouts.py - Split Ratios & Resizing

DeskApp uses split ratios to control panel layouts:
- v_split: Menu width ratio (0.0 to 1.0)
- h_split: Message panel height ratio (0.0 to 1.0)
- r_split: Right panel width ratio (0.0 to 1.0)

These can be set at App creation or changed dynamically.

Press [ and ] to adjust menu width (v_split).
Press - and + to adjust message height (h_split).
Press < and > to adjust right panel width (r_split).
Press R to reset to defaults.
Press Q to quit.

Terminal resize is handled automatically.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
import random

LayoutID = random.random()


class LayoutDemo(Module):
    """Demonstrates layout split ratios and dynamic resizing."""
    name = "Layout Demo"

    def __init__(self, app):
        super().__init__(app, LayoutID)
        
        # Track resize events
        self.resize_count = 0
        self.terminal_size = (0, 0)

    def page(self, panel):
        """Display current layout information."""
        h, w = panel.h, panel.w
        
        # Update terminal size
        self.terminal_size = (h, w)
        
        # Title
        panel.win.addstr(1, 2, "Layout System Tutorial", 
                        self.front.color_white)
        
        # Current panel size
        y = 3
        panel.win.addstr(y, 2, f"Main panel: {h}x{w}", 
                        self.front.color_green)
        
        # Split ratios
        y += 2
        panel.win.addstr(y, 2, "Current Split Ratios:", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, f"v_split (menu): {self.app.v_split:.2f}", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, 
                        f"h_split (messages): {self.app.h_split:.2f}", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, f"r_split (right): {self.app.r_split:.2f}", 
                        self.front.color_white)
        
        # Controls
        y += 2
        panel.win.addstr(y, 2, "Controls:", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, "[ / ] - Decrease/Increase menu width", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "- / + - Decrease/Increase msg height", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "< / > - Decrease/Increase right width", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "R - Reset to defaults", 
                        self.front.color_white)
        
        # Resize info
        y += 2
        panel.win.addstr(y, 2, f"Terminal resizes: {self.resize_count}", 
                        self.front.color_cyan)
        y += 1
        panel.win.addstr(y, 2, "Try resizing your terminal window!", 
                        self.front.color_cyan)

    def PageRight(self, panel):
        """Right panel content."""
        panel.win.addstr(1, 2, "Right Panel", 
                        self.front.color_white)
        panel.win.addstr(3, 2, "Width controlled", 
                        self.front.color_cyan)
        panel.win.addstr(4, 2, "by r_split", 
                        self.front.color_cyan)
        panel.win.addstr(6, 2, f"r_split:", 
                        self.front.color_white)
        panel.win.addstr(7, 2, f"{self.app.r_split:.2f}", 
                        self.front.color_green)

    def PageInfo(self, panel):
        """Info panel showing current state."""
        panel.win.addstr(0, 2, f"v:{self.app.v_split:.2f} "
                              f"h:{self.app.h_split:.2f} "
                              f"r:{self.app.r_split:.2f}", 
                        self.front.color_white)
        h, w = self.terminal_size
        panel.win.addstr(1, 2, f"Terminal: {h}x{w}", 
                        self.front.color_cyan)
        panel.win.addstr(2, 2, f"Resizes: {self.resize_count}", 
                        self.front.color_green)

    # =========================================================================
    # LAYOUT CONTROLS
    # =========================================================================

    @callback(LayoutID, Keys.LEFT_BRACKET)
    def decrease_menu_width(self, *args, **kwargs):
        """[ decreases menu width."""
        self.app.v_split = max(0.1, self.app.v_split - 0.05)
        self.print(f"Menu width: {self.app.v_split:.2f}")

    @callback(LayoutID, Keys.RIGHT_BRACKET)
    def increase_menu_width(self, *args, **kwargs):
        """] increases menu width."""
        self.app.v_split = min(0.5, self.app.v_split + 0.05)
        self.print(f"Menu width: {self.app.v_split:.2f}")

    @callback(LayoutID, Keys.MINUS)
    def decrease_msg_height(self, *args, **kwargs):
        """- decreases message panel height."""
        self.app.h_split = max(0.05, self.app.h_split - 0.02)
        self.print(f"Message height: {self.app.h_split:.2f}")

    @callback(LayoutID, Keys.PLUS)
    def increase_msg_height(self, *args, **kwargs):
        """+ increases message panel height."""
        self.app.h_split = min(0.3, self.app.h_split + 0.02)
        self.print(f"Message height: {self.app.h_split:.2f}")

    @callback(LayoutID, Keys.LESS_THAN)
    def decrease_right_width(self, *args, **kwargs):
        """< decreases right panel width."""
        self.app.r_split = max(0.1, self.app.r_split - 0.05)
        self.print(f"Right width: {self.app.r_split:.2f}")

    @callback(LayoutID, Keys.GREATER_THAN)
    def increase_right_width(self, *args, **kwargs):
        """> increases right panel width."""
        self.app.r_split = min(0.5, self.app.r_split + 0.05)
        self.print(f"Right width: {self.app.r_split:.2f}")

    @callback(LayoutID, Keys.R)
    def reset_layout(self, *args, **kwargs):
        """R resets to default ratios."""
        self.app.v_split = 0.2
        self.app.h_split = 0.16
        self.app.r_split = 0.25
        self.print("Layout reset to defaults")

    @callback(LayoutID, Keys.RESIZE)
    def on_resize(self, *args, **kwargs):
        """
        RESIZE event is sent when terminal window changes size.
        
        DeskApp handles this automatically, but you can add
        custom logic here if needed.
        """
        self.resize_count += 1
        h, w = self.terminal_size
        self.print(f"Terminal resized to {h}x{w}")

    @callback(LayoutID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        self.logic.should_stop = True


if __name__ == "__main__":
    app = App(
        modules=[LayoutDemo],
        title="Layout Tutorial",
        show_right=True,    # Show right panel
        show_info=True,     # Show info panel
        v_split=0.2,        # Menu uses 20% of width
        h_split=0.16,       # Messages use 16% of height
        r_split=0.25,       # Right uses 25% of width
    )
