"""
Example demonstrating floating panel overlay system.
Shows modal dialog, popup menu, and notification use cases.

Created by: Claude Sonnet 4.5 on 10/09/25
"""

from deskapp import App, Module, callback, Keys
import random

FloatingTest_ID = random.random()


class FloatingTest(Module):
    """Module demonstrating floating panel capabilities."""

    name = "Floating Test"

    def __init__(self, app):
        super().__init__(app, FloatingTest_ID)
        self.menu_items = [
            "Option 1: Save",
            "Option 2: Load",
            "Option 3: Settings",
            "Option 4: Exit"
        ]
        self.selected_item = 0
        self.notification_text = "Press NUM9 to toggle floating panel"
        self.dialog_mode = "menu"  # menu, dialog, notification

    def page(self, panel):
        """Main panel content with instructions."""
        self.index = 1

        # Title
        self.write(panel, self.index, 2, "Floating Panel Demo", "yellow")
        self.index += 2

        # Instructions
        self.write(
            panel, self.index, 2,
            "Controls:", "cyan"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  NUM9: Toggle floating panel", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  M: Switch to menu mode", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  D: Switch to dialog mode", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  N: Switch to notification mode", "white"
        )
        self.index += 2

        # Current mode
        self.write(
            panel, self.index, 2,
            f"Current mode: {self.dialog_mode}", "green"
        )
        self.index += 1
        status = "VISIBLE" if self.app.back.show_floating else "HIDDEN"
        self.write(
            panel, self.index, 2,
            f"Floating panel: {status}", "green"
        )
        self.index += 2

        # Demo info
        self.write(
            panel, self.index, 2,
            "The floating panel overlays all other panels", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "and stays centered even on resize.", "white"
        )
        self.index += 2

        # Use cases
        self.write(panel, self.index, 2, "Use cases:", "cyan")
        self.index += 1
        self.write(panel, self.index, 2, "  - Modal dialogs", "white")
        self.index += 1
        self.write(panel, self.index, 2, "  - Popup menus", "white")
        self.index += 1
        self.write(panel, self.index, 2, "  - Notifications", "white")
        self.index += 1
        self.write(panel, self.index, 2, "  - Help overlays", "white")

    def PageFloat(self, panel):
        """Render floating panel content based on mode."""
        if self.dialog_mode == "menu":
            self.render_menu(panel)
        elif self.dialog_mode == "dialog":
            self.render_dialog(panel)
        elif self.dialog_mode == "notification":
            self.render_notification(panel)

    def render_menu(self, panel):
        """Render popup menu in floating panel."""
        self.write(panel, 1, 2, "Popup Menu", "yellow")
        self.write(panel, 2, 2, "Use UP/DOWN to navigate:", "white")

        for idx, item in enumerate(self.menu_items):
            y = idx + 4
            if y >= panel.dims[0] - 1:
                break
            color = "green" if idx == self.selected_item else "white"
            cursor = ">" if idx == self.selected_item else " "
            self.write(panel, y, 2, f"{cursor} {item}", color)

    def render_dialog(self, panel):
        """Render modal dialog in floating panel."""
        self.write(panel, 1, 2, "Confirm Action", "yellow")
        self.write(panel, 3, 2, "Are you sure you want to", "white")
        self.write(panel, 4, 2, "proceed with this action?", "white")
        self.write(panel, 6, 2, "[Y]es    [N]o", "green")

    def render_notification(self, panel):
        """Render notification in floating panel."""
        self.write(panel, 1, 2, "Notification", "yellow")
        self.write(panel, 3, 2, self.notification_text, "cyan")
        self.write(panel, 5, 2, "Press any key to dismiss", "white")

    def PageRight(self, panel):
        """Right panel with mode info."""
        self.write(panel, 1, 1, "Mode Info", "yellow")
        self.write(panel, 2, 1, f"Current:", "white")
        self.write(panel, 3, 1, self.dialog_mode, "green")

    @callback(FloatingTest_ID, keypress=Keys.M)
    def on_m(self, *args, **kwargs):
        """Switch to menu mode."""
        self.dialog_mode = "menu"
        self.print("Switched to menu mode")

    @callback(FloatingTest_ID, keypress=Keys.D)
    def on_d(self, *args, **kwargs):
        """Switch to dialog mode."""
        self.dialog_mode = "dialog"
        self.print("Switched to dialog mode")

    @callback(FloatingTest_ID, keypress=Keys.N)
    def on_n(self, *args, **kwargs):
        """Switch to notification mode."""
        self.dialog_mode = "notification"
        self.print("Switched to notification mode")

    @callback(FloatingTest_ID, keypress=Keys.UP)
    def on_up_menu(self, *args, **kwargs):
        """Navigate menu up."""
        if self.dialog_mode == "menu":
            self.selected_item = max(0, self.selected_item - 1)

    @callback(FloatingTest_ID, keypress=Keys.DOWN)
    def on_down_menu(self, *args, **kwargs):
        """Navigate menu down."""
        if self.dialog_mode == "menu":
            self.selected_item = min(
                len(self.menu_items) - 1,
                self.selected_item + 1
            )

    @callback(FloatingTest_ID, keypress=Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        """Select menu item."""
        if self.dialog_mode == "menu":
            item = self.menu_items[self.selected_item]
            self.print(f"Selected: {item}")


if __name__ == "__main__":
    print("\n=== Floating Panel Test ===")
    print("Demonstrating overlay/dialog system...")
    print("\nStarting app with floating panel enabled...\n")

    app = App(
        modules=[FloatingTest],
        demo_mode=False,
        title="Floating Panel Test",
        show_box=True,
        show_right_panel=True,
        show_info_panel=True,
        show_floating=True,
        floating_height=12,
        floating_width=45,
        autostart=False
    )
    app.start()

    print("\nFloating panel test complete!")
    print("Features demonstrated:")
    print("  - Centered overlay positioning")
    print("  - Multiple dialog modes")
    print("  - Z-order stacking (always on top)")
    print("  - Resize handling")

