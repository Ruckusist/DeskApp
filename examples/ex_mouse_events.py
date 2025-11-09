"""
DeskApp Mouse Events Example
Demonstrates mouse input integration with EventBus and menu clicking.

Features:
- Shows how to listen for 'input.mouse' events
- Displays mouse click regions and coordinates
- Menu selection via mouse click (click menu items to switch)
- Event-driven architecture example

Updated by: Claude Sonnet 4.5 10-12-25
Created for Proposal 13 - Mouse Events Integration
"""

import random
from deskapp import App, Module, callback, Keys


MouseDemo_ID = random.random()


class MouseDemo(Module):
    name = "Mouse Demo"

    def __init__(self, app):
        super().__init__(app, MouseDemo_ID)
        self.mouse_events = []
        self.max_events = 20

        # Listen for mouse events
        self.on_event('input.mouse', self.handle_mouse_event)
        self.on_event('ui.menu.select', self.handle_menu_select)

    def handle_mouse_event(self, event):
        """Handle incoming mouse events."""
        data = event['data']
        msg = (
            f"Mouse: region={data['region']} "
            f"row={data['row']} col={data['col']} btn={data['button']}"
        )
        self.mouse_events.append(msg)
        if len(self.mouse_events) > self.max_events:
            self.mouse_events.pop(0)

    def handle_menu_select(self, event):
        """Handle menu selection events."""
        data = event['data']
        msg = f"Menu Selected: {data['name']} (index {data['index']})"
        self.print(msg)

    def page(self, panel):
        """Main panel rendering."""
        self.write(panel, 1, 2, "Mouse Events Demo", "cyan")
        self.write(panel, 2, 2, "=" * (self.w - 4), "cyan")

        self.write(panel, 4, 2, "Try clicking:", "yellow")
        self.write(panel, 5, 2, "  - Menu items on the left", "white")
        self.write(panel, 6, 2, "  - Different panels", "white")
        self.write(panel, 7, 2, "  - This main area", "white")

        self.write(panel, 9, 2, "Recent mouse events:", "green")

        start_row = 10
        available_rows = self.h - start_row - 1
        display_events = self.mouse_events[-available_rows:]

        for idx, event in enumerate(display_events):
            row = start_row + idx
            if row >= self.h - 1:
                break
            text = event[:self.w - 4]
            self.write(panel, row, 2, text, "white")

    def PageInfo(self, panel):
        """Info panel with instructions."""
        self.write(panel, 1, 2, "Mouse: ENABLED | Click menu to switch",
                   "green")
        self.write(panel, 2, 2, "Events logged in main panel", "yellow")
        self.write(
            panel, 3, 2, f"Total events: {len(self.mouse_events)}",
            "cyan"
        )
        return True

    @callback(MouseDemo_ID, keypress=Keys.C)
    def clear_events(self, *args, **kwargs):
        """Clear event log (press 'C')."""
        self.mouse_events.clear()
        self.print("Cleared mouse event log")


About_ID = random.random()


class About(Module):
    name = "About"

    def __init__(self, app):
        super().__init__(app, About_ID)

    def page(self, panel):
        self.write(panel, 1, 2, "DeskApp Mouse Events Example", "cyan")
        self.write(panel, 3, 2, "This example demonstrates:", "white")
        self.write(panel, 4, 2, "  1. Mouse event capture", "yellow")
        self.write(panel, 5, 2, "  2. EventBus integration", "yellow")
        self.write(panel, 6, 2, "  3. Menu click selection", "yellow")
        self.write(panel, 8, 2, "Click the 'Mouse Demo' menu item",
                   "green")
        self.write(panel, 9, 2, "to see mouse events in action.",
                   "green")


if __name__ == "__main__":
    app = App(
        modules=[About, MouseDemo],
        demo_mode=False,
        title="Mouse Events Example",
        use_mouse=True,  # CRITICAL: Enable mouse support
        show_header=True,
        show_footer=True,
        show_menu=True,
        show_messages=True,
        show_info_panel=True,
        show_right_panel=False,
        autostart=True
    )
