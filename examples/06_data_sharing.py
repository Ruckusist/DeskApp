"""
06_data_sharing.py - Module Communication

DeskApp provides several ways for modules to share data:
1. app.data dictionary - Global application state
2. Module switching - Navigate between modules
3. Message passing - self.print() for user feedback
4. Context dictionaries - Per-module persistent data

This example demonstrates a multi-module app where:
- Counter module tracks a number
- Display module shows that number
- Settings module controls behavior
- Data flows between all three

Press PgUp/PgDn to switch modules.
Press +/- in Counter to change value.
Press S in Settings to toggle auto-increment.
Press Q to quit.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
import random

CounterID = random.random()
DisplayID = random.random()
SettingsID = random.random()


class Counter(Module):
    """Module that maintains a counter value."""
    name = "Counter"

    def __init__(self, app):
        super().__init__(app, CounterID)

        # Initialize shared data if not present
        if "counter_value" not in self.app.data:
            self.app.data["counter_value"] = 0
        if "auto_increment" not in self.app.data:
            self.app.data["auto_increment"] = False

    def page(self, panel):
        """Display and control the counter."""
        # Read from shared data
        value = self.app.data["counter_value"]
        auto = self.app.data["auto_increment"]

        panel.win.addstr(1, 2, "Counter Module",
                        self.front.color_white)
        panel.win.addstr(3, 2, f"Current Value: {value}",
                        self.front.color_green)
        panel.win.addstr(5, 2, f"Auto-increment: "
                              f"{'ON' if auto else 'OFF'}",
                        self.front.color_yellow if auto
                        else self.front.color_white)

        panel.win.addstr(7, 2, "Controls:",
                        self.front.color_yellow)
        panel.win.addstr(8, 4, "+ - Increment",
                        self.front.color_white)
        panel.win.addstr(9, 4, "- - Decrement",
                        self.front.color_white)
        panel.win.addstr(10, 4, "R - Reset to 0",
                        self.front.color_white)

        panel.win.addstr(12, 2, "Switch to Display or Settings",
                        self.front.color_cyan)
        panel.win.addstr(13, 2, "with PgUp/PgDn",
                        self.front.color_cyan)

        # Auto-increment logic
        if auto:
            self.app.data["counter_value"] += 1

    @callback(CounterID, Keys.PLUS)
    def increment(self, *args, **kwargs):
        """+ increments the counter."""
        self.app.data["counter_value"] += 1
        self.print(f"Counter: {self.app.data['counter_value']}")

    @callback(CounterID, Keys.MINUS)
    def decrement(self, *args, **kwargs):
        """- decrements the counter."""
        self.app.data["counter_value"] -= 1
        self.print(f"Counter: {self.app.data['counter_value']}")

    @callback(CounterID, Keys.R)
    def reset(self, *args, **kwargs):
        """R resets to zero."""
        self.app.data["counter_value"] = 0
        self.print("Counter reset to 0")

    @callback(CounterID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        self.logic.should_stop = True


class Display(Module):
    """Module that displays the counter value in different ways."""
    name = "Display"

    def __init__(self, app):
        super().__init__(app, DisplayID)

    def page(self, panel):
        """Show the counter in various formats."""
        # Read shared data
        value = self.app.data.get("counter_value", 0)

        panel.win.addstr(1, 2, "Display Module",
                        self.front.color_white)
        panel.win.addstr(3, 2, "Value Representations:",
                        self.front.color_yellow)

        panel.win.addstr(5, 4, f"Decimal: {value}",
                        self.front.color_white)
        panel.win.addstr(6, 4, f"Hex: {hex(value)}",
                        self.front.color_cyan)
        panel.win.addstr(7, 4, f"Binary: {bin(value)}",
                        self.front.color_green)
        panel.win.addstr(8, 4, f"Squared: {value ** 2}",
                        self.front.color_magenta)

        # Visual bar
        panel.win.addstr(10, 2, "Visual Bar:",
                        self.front.color_yellow)
        bar_width = min(abs(value), 40)
        bar = "█" * bar_width
        color = (self.front.color_green if value >= 0
                else self.front.color_red)
        panel.win.addstr(11, 4, bar, color)

        panel.win.addstr(13, 2, "This module reads counter_value",
                        self.front.color_cyan)
        panel.win.addstr(14, 2, "from app.data",
                        self.front.color_cyan)

    @callback(DisplayID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        self.logic.should_stop = True


class Settings(Module):
    """Module that controls application behavior."""
    name = "Settings"

    def __init__(self, app):
        super().__init__(app, SettingsID)

    def page(self, panel):
        """Display and modify settings."""
        value = self.app.data.get("counter_value", 0)
        auto = self.app.data.get("auto_increment", False)

        panel.win.addstr(1, 2, "Settings Module",
                        self.front.color_white)
        panel.win.addstr(3, 2, "Application State:",
                        self.front.color_yellow)

        panel.win.addstr(5, 4, f"counter_value: {value}",
                        self.front.color_white)
        panel.win.addstr(6, 4, f"auto_increment: {auto}",
                        self.front.color_white)

        panel.win.addstr(8, 2, "Controls:",
                        self.front.color_yellow)
        panel.win.addstr(9, 4, "S - Toggle auto-increment",
                        self.front.color_white)
        panel.win.addstr(10, 4, "C - Clear counter",
                        self.front.color_white)

        panel.win.addstr(12, 2, "Data Sharing Pattern:",
                        self.front.color_cyan)
        panel.win.addstr(13, 2, "app.data is a shared dictionary",
                        self.front.color_white)
        panel.win.addstr(14, 2, "accessible from all modules",
                        self.front.color_white)

    @callback(SettingsID, Keys.S)
    def toggle_auto(self, *args, **kwargs):
        """S toggles auto-increment."""
        current = self.app.data.get("auto_increment", False)
        self.app.data["auto_increment"] = not current
        status = "ON" if not current else "OFF"
        self.print(f"Auto-increment: {status}")

    @callback(SettingsID, Keys.C)
    def clear_counter(self, *args, **kwargs):
        """C clears the counter."""
        self.app.data["counter_value"] = 0
        self.print("Counter cleared")

    @callback(SettingsID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        self.logic.should_stop = True


if __name__ == "__main__":
    app = App(
        modules=[Counter, Display, Settings],
        title="Data Sharing Demo",
        show_info_panel=True,
    )

    # app.data is available to all modules
    # Use it to share state between modules
