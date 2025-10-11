"""
01_panels.py - Panel System Tour

DeskApp has 8 different panel types that can display content:
1. Header - Top banner (toggle with NUM1)
2. Footer - Bottom input/status (toggle with NUM2)
3. Menu - Left sidebar (toggle with NUM3)
4. Main - Primary content area (toggle with NUM4)
5. Messages - Bottom message log (toggle with NUM5)
6. Right - Right sidebar (toggle with NUM7)
7. Info - Small 3-line status (toggle with NUM8)
8. Floating - Overlay panel (toggle with NUM9)

Press NUM6 to show/hide all panels at once.
Press NUM1-9 to toggle individual panels.
Press Q to quit.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
import random

PanelID = random.random()


class PanelDemo(Module):
    """Demonstrates all available panel types."""
    name = "Panel Demo"

    def __init__(self, app):
        super().__init__(app, PanelID)
        self.counter = 0

    def page(self, panel):
        """Main panel - primary content area."""
        h, w = panel.h, panel.w
        
        # Title
        panel.win.addstr(1, 2, "DeskApp Panel System", 
                        self.front.color_white)
        
        # Instructions
        y = 3
        panel.win.addstr(y, 2, "Press NUM1-9 to toggle panels:", 
                        self.front.color_cyan)
        y += 2
        panel.win.addstr(y, 4, "NUM1 - Header (top)", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "NUM2 - Footer (bottom)", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "NUM3 - Menu (left)", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "NUM4 - Main (this panel)", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "NUM5 - Messages (bottom log)", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "NUM6 - Show/Hide All", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, "NUM7 - Right (sidebar)", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "NUM8 - Info (status)", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "NUM9 - Floating (overlay)", 
                        self.front.color_white)
        
        # Counter demo
        y += 3
        panel.win.addstr(y, 2, f"Press SPACE to increment: "
                              f"{self.counter}", 
                        self.front.color_green)

    def PageRight(self, panel):
        """Right panel - optional sidebar content."""
        panel.win.addstr(1, 2, "Right Panel", 
                        self.front.color_white)
        panel.win.addstr(3, 2, "This sidebar", 
                        self.front.color_cyan)
        panel.win.addstr(4, 2, "appears when", 
                        self.front.color_cyan)
        panel.win.addstr(5, 2, "you toggle", 
                        self.front.color_cyan)
        panel.win.addstr(6, 2, "NUM7", self.front.color_yellow)
        panel.win.addstr(8, 2, "Width set by", 
                        self.front.color_cyan)
        panel.win.addstr(9, 2, "app.r_split", 
                        self.front.color_cyan)

    def PageInfo(self, panel):
        """Info panel - 3-line status area."""
        panel.win.addstr(0, 2, "Info Panel (3 lines max)", 
                        self.front.color_white)
        panel.win.addstr(1, 2, f"Counter: {self.counter}", 
                        self.front.color_green)
        panel.win.addstr(2, 2, "Press NUM8 to toggle", 
                        self.front.color_cyan)

    def PageFloat(self, panel):
        """Floating panel - overlay on top of main."""
        h, w = panel.h, panel.w
        
        panel.win.addstr(1, 2, "Floating Overlay Panel", 
                        self.front.color_yellow)
        panel.win.addstr(3, 2, "This panel floats over", 
                        self.front.color_white)
        panel.win.addstr(4, 2, "the main content area.", 
                        self.front.color_white)
        panel.win.addstr(6, 2, "Toggle with NUM9", 
                        self.front.color_cyan)
        panel.win.addstr(8, 2, f"Size: {h}x{w}", 
                        self.front.color_green)

    @callback(PanelID, Keys.SPACE)
    def increment(self, *args, **kwargs):
        """SPACE increments counter and shows in messages."""
        self.counter += 1
        self.print(f"Counter incremented to {self.counter}")

    @callback(PanelID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        self.logic.should_stop = True


if __name__ == "__main__":
    # Create app with right panel visible and info panel enabled
    app = App(
        modules=[PanelDemo],
        title="Panel System Demo",
        show_right=True,   # Right panel visible on start
        show_info=True,    # Info panel visible on start
        r_split=0.25,      # Right panel uses 25% of width
    )
