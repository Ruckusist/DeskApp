"""
Example demonstrating box parameter behavior.
Tests both box=True and box=False modes.

Created by: Claude Sonnet 4.5 on 10/09/25
"""

from deskapp import App, Module, callback, Keys
import random

TestBox_ID = random.random()


class TestBox(Module):
    """Simple module to test box rendering."""

    name = "BoxTest"

    def __init__(self, app):
        super().__init__(app, TestBox_ID)

    def page(self, panel):
        """Render test content."""
        self.index = 1
        self.write(panel, self.index, 2, "Box Parameter Test", "yellow")
        self.index += 2
        self.write(
            panel, self.index, 2,
            f"App box setting: {self.app.show_box}", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "All panels should respect this setting.", "cyan"
        )
        self.index += 2
        self.write(
            panel, self.index, 2,
            "Press <q> to quit", "green"
        )

    def PageInfo(self, panel):
        """Info panel content."""
        self.write(panel, 1, 2, f"Borders: {self.app.show_box}", "white")


if __name__ == "__main__":
    print("\nTesting box=True (with borders)...")
    print("Close the app, then we'll test box=False\n")

    app_with_box = App(
        modules=[TestBox],
        demo_mode=False,
        title="DeskApp - Box Test (borders ON)",
        show_box=True,
        autostart=False
    )
    app_with_box.start()

    print("\nNow testing box=False (borderless)...")
    print("All panels should render without borders.\n")

    app_no_box = App(
        modules=[TestBox],
        demo_mode=False,
        title="DeskApp - Box Test (borders OFF)",
        show_box=False,
        autostart=False
    )
    app_no_box.start()

    print("\nBox parameter test complete!")
