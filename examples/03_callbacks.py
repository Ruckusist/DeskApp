"""
03_callbacks.py - Event Handling Deep-Dive

This tutorial demonstrates DeskApp's callback system in detail:
- Keyboard callbacks (letters, numbers, special keys)
- Multiple callbacks per key (global vs module-specific)
- Callback argument passing
- String input mode (TAB key)
- Callback ID system

Press letters A-Z to trigger callbacks.
Press TAB to enter string input mode.
Press ENTER to process input (in input mode).
Press ESC to cancel input (in input mode).
Press Q to quit.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
import random

CallbackID = random.random()


class CallbackDemo(Module):
    """Demonstrates the callback system in detail."""
    name = "Callback Demo"

    def __init__(self, app):
        super().__init__(app, CallbackID)
        
        # Track keypresses
        self.last_key = "None"
        self.key_count = 0
        self.input_text = ""
        self.submitted_text = ""

    def page(self, panel):
        """Display callback information and status."""
        h, w = panel.h, panel.w
        
        # Title
        panel.win.addstr(1, 2, "Callback System Tutorial", 
                        self.front.color_white)
        
        # Status
        y = 3
        panel.win.addstr(y, 2, f"Last key: {self.last_key}", 
                        self.front.color_green)
        y += 1
        panel.win.addstr(y, 2, f"Total keys pressed: {self.key_count}", 
                        self.front.color_cyan)
        
        # Instructions
        y += 2
        panel.win.addstr(y, 2, "Keyboard Callbacks:", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, "A - Trigger callback A", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "B - Trigger callback B", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "H - Say hello", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "SPACE - Increment counter", 
                        self.front.color_white)
        
        # String input mode
        y += 2
        panel.win.addstr(y, 2, "String Input Mode:", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, "TAB - Enter input mode", 
                        self.front.color_white)
        y += 1
        
        # Show input mode status
        if self.front.key_mode:
            panel.win.addstr(y, 4, "Status: INPUT MODE ACTIVE", 
                            self.front.color_green)
            y += 1
            panel.win.addstr(y, 4, f"Current: {self.input_text}", 
                            self.front.color_cyan)
            y += 1
            panel.win.addstr(y, 4, "ENTER - Submit | ESC - Cancel", 
                            self.front.color_yellow)
        else:
            panel.win.addstr(y, 4, "Status: Normal mode", 
                            self.front.color_white)
        
        # Last submitted text
        if self.submitted_text:
            y += 2
            panel.win.addstr(y, 2, "Last submitted:", 
                            self.front.color_yellow)
            y += 1
            max_len = w - 6
            display = self.submitted_text[:max_len]
            panel.win.addstr(y, 4, display, 
                            self.front.color_green)

    def PageInfo(self, panel):
        """Show callback system info."""
        panel.win.addstr(0, 2, "Callback System", 
                        self.front.color_white)
        panel.win.addstr(1, 2, f"Module ID: {CallbackID:.6f}", 
                        self.front.color_cyan)
        panel.win.addstr(2, 2, f"Keys: {self.key_count}", 
                        self.front.color_green)

    # =========================================================================
    # CALLBACK EXAMPLES - Different patterns
    # =========================================================================

    @callback(CallbackID, Keys.A)
    def on_a(self, *args, **kwargs):
        """Simple callback - just logs a message."""
        self.last_key = "A"
        self.key_count += 1
        self.print("Callback A triggered!")

    @callback(CallbackID, Keys.B)
    def on_b(self, *args, **kwargs):
        """Another callback - shows multiple handlers work."""
        self.last_key = "B"
        self.key_count += 1
        self.print("Callback B is different from A")

    @callback(CallbackID, Keys.H)
    def say_hello(self, *args, **kwargs):
        """Callback with more logic."""
        self.last_key = "H"
        self.key_count += 1
        self.print("Hello from the callback system!")
        self.print("You can have multiple print() calls")

    @callback(CallbackID, Keys.SPACE)
    def increment(self, *args, **kwargs):
        """Callback that modifies state."""
        self.last_key = "SPACE"
        self.key_count += 1
        # No message - just increment counter

    @callback(CallbackID, Keys.TAB)
    def enter_input_mode(self, *args, **kwargs):
        """
        TAB toggles string input mode.
        
        In input mode:
        - Footer panel appears for typing
        - Regular callbacks are disabled
        - Type text and press ENTER to submit
        - Press ESC to cancel
        """
        self.last_key = "TAB"
        self.key_count += 1
        
        if not self.front.key_mode:
            # Enter input mode
            self.front.key_mode = True
            self.input_text = ""
            self.print("Input mode activated - type and press ENTER")
        else:
            # Exit input mode
            self.front.key_mode = False
            self.print("Input mode canceled")

    @callback(CallbackID, Keys.ENTER)
    def submit_input(self, *args, **kwargs):
        """
        ENTER in input mode processes the text.
        
        The input string is available in:
        self.logic.data["str_to_use"]
        """
        self.last_key = "ENTER"
        self.key_count += 1
        
        if self.front.key_mode:
            # Get the input string
            text = self.logic.data.get("str_to_use", "")
            self.submitted_text = text
            self.input_text = ""
            
            # Exit input mode
            self.front.key_mode = False
            
            if text:
                self.print(f"Submitted: {text}")
            else:
                self.print("Empty input submitted")

    @callback(CallbackID, Keys.ESC)
    def cancel_input(self, *args, **kwargs):
        """ESC cancels input mode."""
        self.last_key = "ESC"
        self.key_count += 1
        
        if self.front.key_mode:
            self.front.key_mode = False
            self.input_text = ""
            self.print("Input canceled")

    @callback(CallbackID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        self.logic.should_stop = True


if __name__ == "__main__":
    app = App(
        modules=[CallbackDemo],
        title="Callback System",
        show_info=True,
    )
