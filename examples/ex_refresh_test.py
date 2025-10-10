"""
Example demonstrating clean panel refresh without artifacts.
Tests erase() implementation with fast-updating content.

Created by: Claude Sonnet 4.5 on 10/09/25
"""

from deskapp import App, Module, callback, Keys
import random
import time

RefreshTest_ID = random.random()


class RefreshTest(Module):
    """Module that rapidly updates to test refresh behavior."""

    name = "RefreshTest"

    def __init__(self, app):
        super().__init__(app, RefreshTest_ID)
        self.counter = 0
        self.start_time = time.time()
        self.dialog_dismissed = False

    def page(self, panel):
        """Render constantly changing content."""
        self.index = 1
        self.counter += 1
        elapsed = time.time() - self.start_time

        # Title
        self.write(
            panel, self.index, 2,
            "Panel Refresh Test", "yellow"
        )
        self.index += 2

        # Counter - changes every frame
        self.write(
            panel, self.index, 2,
            f"Frame: {self.counter}", "white"
        )
        self.index += 1

        # FPS estimate
        fps = self.counter / elapsed if elapsed > 0 else 0
        self.write(
            panel, self.index, 2,
            f"FPS: {fps:.1f}", "cyan"
        )
        self.index += 2

        # Instructions
        self.write(
            panel, self.index, 2,
            "Watch for ghosting or artifacts", "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "Toggle panels (NUM1-8) to test", "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "Resize window to test refresh", "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "NUM9: Toggle floating confirmation", "green"
        )
        self.index += 2

        # Moving indicator
        indicator_pos = (self.counter % 40) + 2
        if self.index < self.h - 2:
            self.write(
                panel, self.index, indicator_pos,
                ">>", "red"
            )

    def PageRight(self, panel):
        """Right panel with fast updates."""
        self.write(panel, 1, 1, "RIGHT", "yellow")
        self.write(panel, 2, 1, str(self.counter % 100), "white")

    def PageInfo(self, panel):
        """Info panel content."""
        self.write(
            panel, 1, 2,
            f"Clean refresh - Frame {self.counter}", "cyan"
        )

    def PageFloat(self, panel):
        """Render floating confirmation dialog."""
        # Title
        self.write(panel, 1, 2, "Confirmation Dialog", "yellow")

        # Message
        self.write(panel, 3, 2, "This is a test floating panel", "white")
        self.write(panel, 4, 2, "demonstrating overlay dialogs.", "white")

        # Status
        if self.dialog_dismissed:
            self.write(panel, 6, 2, "Dialog accepted!", "green")
        else:
            self.write(panel, 6, 2, "Press ENTER to accept", "cyan")

    @callback(RefreshTest_ID, keypress=Keys.ENTER)
    def on_enter_accept(self, *args, **kwargs):
        """Accept and dismiss the floating dialog."""
        if self.app.back.show_floating:
            self.dialog_dismissed = True
            self.print("Floating dialog accepted!")


if __name__ == "__main__":
    print("\nTesting panel refresh behavior...")
    print("Watch for:")
    print("  - No ghosting of previous text")
    print("  - Clean borders")
    print("  - Smooth updates")
    print("  - Proper clearing on panel toggle\n")

    app = App(
        modules=[RefreshTest],
        demo_mode=False,
        title="Refresh Test",
        show_box=True,
        show_right_panel=True,
        show_info_panel=True,
        show_floating=False,
        floating_height=10,
        floating_width=40,
        autostart=False
    )
    app.start()

    print("\nRefresh test complete!")
