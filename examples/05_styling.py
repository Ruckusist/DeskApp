"""
05_styling.py - Colors & Formatting

DeskApp provides a color system for styling terminal output:
- color_white, color_red, color_green, color_blue
- color_cyan, color_yellow, color_magenta
- color_black, color_orange, color_purple

Plus formatting helpers:
- self.write() for colored text output
- show_box parameter for panel borders
- show_banner parameter for titles

Press 1-9 to see different color combinations.
Press B to toggle borders.
Press T to toggle title banner.
Press Q to quit.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
import random

StyleID = random.random()


class StyleDemo(Module):
    """Demonstrates color system and text formatting."""
    name = "Style Demo"

    def __init__(self, app):
        super().__init__(app, StyleID)
        
        # Current color scheme
        self.color_num = 1
        self.show_borders = True
        self.show_titles = True
        
        # Color names for display
        self.colors = [
            ("white", self.front.color_white),
            ("red", self.front.color_red),
            ("green", self.front.color_green),
            ("blue", self.front.color_blue),
            ("cyan", self.front.color_cyan),
            ("yellow", self.front.color_yellow),
            ("magenta", self.front.color_magenta),
            ("orange", self.front.color_orange),
            ("purple", self.front.color_purple),
        ]

    def page(self, panel):
        """Display color samples and formatting examples."""
        h, w = panel.h, panel.w
        
        # Title with current color
        title = "Color & Styling Tutorial"
        _, color = self.colors[self.color_num % len(self.colors)]
        panel.win.addstr(1, 2, title, color)
        
        # Color palette
        y = 3
        panel.win.addstr(y, 2, "Available Colors:", 
                        self.front.color_white)
        y += 1
        
        for i, (name, color) in enumerate(self.colors):
            if y >= h - 2:
                break
            
            # Show color name in that color
            marker = ">>>" if i == self.color_num % len(self.colors) \
                          else "   "
            panel.win.addstr(y, 4, f"{marker} {name}", color)
            y += 1
        
        # Formatting examples
        y += 1
        if y < h - 2:
            panel.win.addstr(y, 2, "Text Formatting:", 
                            self.front.color_yellow)
            y += 1
        
        # Different styles
        if y < h - 2:
            panel.win.addstr(y, 4, "Normal text", 
                            self.front.color_white)
            y += 1
        if y < h - 2:
            panel.win.addstr(y, 4, "Highlighted text", 
                            self.front.color_green)
            y += 1
        if y < h - 2:
            panel.win.addstr(y, 4, "Error text", 
                            self.front.color_red)
            y += 1
        if y < h - 2:
            panel.win.addstr(y, 4, "Warning text", 
                            self.front.color_yellow)
            y += 1
        if y < h - 2:
            panel.win.addstr(y, 4, "Info text", 
                            self.front.color_cyan)
            y += 1
        
        # Controls
        y += 1
        if y < h - 2:
            panel.win.addstr(y, 2, "Controls:", 
                            self.front.color_yellow)
            y += 1
        if y < h - 2:
            panel.win.addstr(y, 4, "1-9 - Change color scheme", 
                            self.front.color_white)
            y += 1
        if y < h - 2:
            panel.win.addstr(y, 4, "B - Toggle borders", 
                            self.front.color_white)
            y += 1
        if y < h - 2:
            panel.win.addstr(y, 4, "T - Toggle title banner", 
                            self.front.color_white)

    def PageRight(self, panel):
        """Right panel with color examples."""
        # Rainbow effect
        colors = [
            self.front.color_red,
            self.front.color_orange,
            self.front.color_yellow,
            self.front.color_green,
            self.front.color_cyan,
            self.front.color_blue,
            self.front.color_purple,
            self.front.color_magenta,
        ]
        
        panel.win.addstr(1, 2, "Rainbow", self.front.color_white)
        panel.win.addstr(2, 2, "Panel", self.front.color_white)
        
        y = 4
        for i, color in enumerate(colors):
            if y >= panel.h - 1:
                break
            panel.win.addstr(y, 2, "████████", color)
            y += 1

    def PageInfo(self, panel):
        """Info panel with current settings."""
        name, color = self.colors[self.color_num % len(self.colors)]
        panel.win.addstr(0, 2, f"Color: {name}", color)
        panel.win.addstr(1, 2, f"Borders: "
                              f"{'ON' if self.show_borders else 'OFF'}", 
                        self.front.color_green if self.show_borders 
                        else self.front.color_red)
        panel.win.addstr(2, 2, f"Titles: "
                              f"{'ON' if self.show_titles else 'OFF'}", 
                        self.front.color_green if self.show_titles 
                        else self.front.color_red)

    # =========================================================================
    # COLOR CONTROLS
    # =========================================================================

    @callback(StyleID, Keys.NUM1)
    def set_color_1(self, *args, **kwargs):
        """1 sets color scheme 1."""
        self.color_num = 0
        self.print(f"Color: {self.colors[0][0]}")

    @callback(StyleID, Keys.NUM2)
    def set_color_2(self, *args, **kwargs):
        """2 sets color scheme 2."""
        self.color_num = 1
        self.print(f"Color: {self.colors[1][0]}")

    @callback(StyleID, Keys.NUM3)
    def set_color_3(self, *args, **kwargs):
        """3 sets color scheme 3."""
        self.color_num = 2
        self.print(f"Color: {self.colors[2][0]}")

    @callback(StyleID, Keys.B)
    def toggle_borders(self, *args, **kwargs):
        """B toggles panel borders."""
        self.show_borders = not self.show_borders
        # Note: Border toggling would need app-level support
        # This is a demonstration of the concept
        self.print(f"Borders: "
                  f"{'ON' if self.show_borders else 'OFF'}")

    @callback(StyleID, Keys.T)
    def toggle_titles(self, *args, **kwargs):
        """T toggles title banners."""
        self.show_titles = not self.show_titles
        # Note: Title toggling would need app-level support
        # This is a demonstration of the concept
        self.print(f"Titles: {'ON' if self.show_titles else 'OFF'}")

    @callback(StyleID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        self.logic.should_stop = True


if __name__ == "__main__":
    app = App(
        modules=[StyleDemo],
        title="Styling Tutorial",
        show_right=True,
        show_info=True,
        show_box=True,      # Enable panel borders
        show_banner=True,   # Enable title banners
    )
