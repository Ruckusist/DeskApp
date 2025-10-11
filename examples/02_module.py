"""
02_module.py - Creating Custom Modules

This tutorial teaches the fundamentals of creating DeskApp modules:
- Inheriting from Module base class
- The page() rendering hook
- Using @callback decorator for keyboard input
- Module properties (h, w, name)
- Printing messages with self.print()
- Element scroller pattern for lists

Press SPACE to add items to the list.
Press D to delete the selected item.
Press UP/DOWN to navigate the list.
Press Q to quit.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
import random

# Every module needs a unique random ID for callbacks
# This prevents callback conflicts between modules
CustomModID = random.random()


class CustomModule(Module):
    """A custom module demonstrating core features."""

    # Module name shown in the menu
    name = "Custom Module"

    def __init__(self, app):
        """Initialize the module with the app instance."""
        # Must call super().__init__ with app and module ID
        super().__init__(app, CustomModID)

        # Module state - use self for any data you need
        self.items = ["First item", "Second item", "Third item"]
        self.selected = 0  # Currently selected index
        self.item_count = 3

    def page(self, panel):
        """
        Main rendering hook - called every frame.

        The panel object has:
        - panel.win: curses window object for drawing
        - panel.h: height in characters
        - panel.w: width in characters
        """
        h, w = self.h, self.w

        # Draw title
        title = "Module Properties Demo"
        panel.win.addstr(1, 2, title, self.front.color_white)

        # Show panel dimensions (available as self.h, self.w)
        panel.win.addstr(2, 2, f"Panel size: {h}x{w}",
                        self.front.color_cyan)

        # Instructions
        y = 4
        panel.win.addstr(y, 2, "Controls:",
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, "SPACE - Add item",
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "D - Delete selected",
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "UP/DOWN - Navigate",
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "Q - Quit",
                        self.front.color_white)

        # Element scroller pattern - display list with selection
        y += 2
        panel.win.addstr(y, 2, "Items:", self.front.color_yellow)
        y += 1

        # Draw each item, highlight selected
        for i, item in enumerate(self.items):
            if i >= h - y - 2:  # Stop if we run out of space
                break

            # Selected item uses different color
            if i == self.selected:
                color = self.front.color_green
                prefix = "> "
            else:
                color = self.front.color_white
                prefix = "  "

            # Truncate if too long for panel
            max_len = w - 6
            display = item[:max_len] if len(item) > max_len else item
            panel.win.addstr(y + i, 4, f"{prefix}{display}", color)

    def PageInfo(self, panel):
        """Optional 3-line info panel."""
        panel.win.addstr(0, 2, f"Items: {len(self.items)}",
                        self.front.color_white)
        panel.win.addstr(1, 2, f"Selected: {self.selected + 1}",
                        self.front.color_green)
        panel.win.addstr(2, 2, f"Created: {self.item_count}",
                        self.front.color_cyan)

    @callback(CustomModID, Keys.SPACE)
    def add_item(self, *args, **kwargs):
        """
        Callback decorator usage:
        @callback(MODULE_ID, KEY_CONSTANT)

        The function is called when the key is pressed
        while this module is active.
        """
        self.item_count += 1
        new_item = f"Item {self.item_count}"
        self.items.append(new_item)

        # self.print() adds messages to the message panel
        self.print(f"Added: {new_item}")

    @callback(CustomModID, Keys.D)
    def delete_item(self, *args, **kwargs):
        """Delete the currently selected item."""
        if len(self.items) == 0:
            self.print("No items to delete")
            return

        deleted = self.items.pop(self.selected)
        self.print(f"Deleted: {deleted}")

        # Adjust selection if needed
        if self.selected >= len(self.items) and self.selected > 0:
            self.selected -= 1

    @callback(CustomModID, Keys.DOWN)
    def move_down(self, *args, **kwargs):
        """Navigate down in the list."""
        if self.selected < len(self.items) - 1:
            self.selected += 1

    @callback(CustomModID, Keys.UP)
    def move_up(self, *args, **kwargs):
        """Navigate up in the list."""
        if self.selected > 0:
            self.selected -= 1

    @callback(CustomModID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Exit the application."""
        # self.logic gives access to app logic controller
        self.logic.should_stop = True


if __name__ == "__main__":
    # Create app with our custom module
    app = App(
        modules=[CustomModule],
        title="Module Tutorial",
        show_info_panel=True,  # Show the info panel
    )
    # App runs automatically (autostart=True is default)
