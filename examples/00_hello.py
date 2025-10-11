"""
00_hello.py - The Absolute Minimum DeskApp Example

This is the simplest possible DeskApp application. It demonstrates:
- Creating a minimal module with one method
- Setting up an App with that module
- Adding a quit callback
- Running the application

Run with: python examples/00_hello.py

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
import random

# Every module needs a unique ID for its callbacks
HelloID = random.random()


class Hello(Module):
    """The simplest module - just displays a message."""
    name = "Hello"  # Shows in menu

    def __init__(self, app):
        super().__init__(app, HelloID)

    def page(self, panel):
        """Main rendering - called every frame."""
        # panel.win is the curses window object
        # self.front.color_white is a color pair
        panel.win.addstr(2, 2, "Hello, DeskApp!", 
                        self.front.color_white)
        panel.win.addstr(4, 2, "Press Q to quit", 
                        self.front.color_cyan)

    @callback(HelloID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q key exits the app."""
        self.logic.should_stop = True


# Create the app with our module and start it
if __name__ == "__main__":
    app = App(modules=[Hello], title="Hello World")
    # App starts automatically by default (autostart=True)
