"""
09_multiline_input.py - Growing Input Field Demo

This example demonstrates the dynamically growing text input field.

- Press TAB to enter input mode.
- Type or paste a long string of text into the input field.
- Observe how the field grows up to 3 lines high.
- With more than 3 lines of text, observe how the input field scrolls.
- Press ENTER to submit the text.
- The submitted text will be displayed in the main panel.

Created by: AI Assistant on behalf of user request
"""

from deskapp import App, Module, callback, Keys
import random
import textwrap

MultilineInput_ID = random.random()

class MultilineInputDemo(Module):
    name = "Multiline Input"

    def __init__(self, app):
        super().__init__(app, MultilineInput_ID)
        self.submitted_text = "Nothing submitted yet."

    def page(self, panel):
        """Display instructions and submitted text."""
        self.write(panel, 1, 2, "Multiline Input Field Demo", "yellow")

        y = 3
        self.write(panel, y, 2, "1. Press TAB to focus the input field below.", "cyan")
        self.write(panel, y+1, 2, "2. Type or paste a long text.", "cyan")
        self.write(panel, y+2, 2, "3. Watch the input field grow and scroll.", "cyan")
        self.write(panel, y+3, 2, "4. Press ENTER to submit.", "cyan")
        y += 5

        self.write(panel, y, 2, "Submitted Text:", "yellow")
        
        # Display submitted text, wrapped
        text_lines = textwrap.wrap(self.submitted_text, width=self.w - 6)
        
        for i, line in enumerate(text_lines):
            if y + 1 + i >= self.h - 1:
                break
            self.write(panel, y + 1 + i, 4, line, "white")
            
    # Override the base `handle_text` to process submitted input.
    def handle_text(self, input_string: str):
        """This method is called when text is submitted from the input field."""
        self.submitted_text = input_string
        self.print(f"Received {len(input_string)} characters.")

    @callback(MultilineInput_ID, Keys.Q)
    def quit_app(self, *args, **kwargs):
        """Quit the application."""
        self.app.close()


if __name__ == "__main__":
    app = App(
        modules=[MultilineInputDemo],
        title="Multiline Input Demo",
        demo_mode=False,
    )