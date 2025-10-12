"""
Memory Leak Detection Demo - Proposal 11 Session 3 Test
Created by: Claude Sonnet 4.5 10-10-25

Demonstrates memory leak detection by intentionally creating
a memory leak. Watch the warning appear after 60 seconds.

Controls:
- L: Toggle leak (start/stop creating memory leak)
- G: Force garbage collection (in Memory Viewer module)
- PgUp/PgDn: Switch modules
- Q: Quit

The leak creates ~1MB per second. After 60 seconds, you should
see a warning in the message panel.
"""

from deskapp import App, Module, Keys, callback
from deskapp.mods.memory_viewer import MemoryViewer
import random

LeakTest_ID = random.random()


class LeakTest(Module):
    """Module to test memory leak detection."""

    name = "Leak Tester"

    def __init__(self, app):
        super().__init__(app, LeakTest_ID)
        self.leak_active = False
        self.leak_data = []
        self.leak_rate = 1024 * 1024  # 1MB per frame

    def page(self, panel):
        """Display leak test controls."""
        h, w = panel.dims[0], panel.dims[1]

        # Intentionally leak memory if active
        if self.leak_active:
            # Create 1MB of data per render
            chunk = bytearray(self.leak_rate)
            self.leak_data.append(chunk)

        y = 1
        panel.win.addstr(y, 2, "MEMORY LEAK DETECTOR TEST",
                        self.front.color_cyan)
        y += 2

        # Status
        status = "ACTIVE" if self.leak_active else "STOPPED"
        color = self.front.color_red if self.leak_active else (
            self.front.color_green
        )
        panel.win.addstr(y, 2, f"Leak Status: {status}", color)
        y += 1

        # Leaked amount
        leaked_mb = (sum(len(c) for c in self.leak_data) /
                    (1024 * 1024))
        panel.win.addstr(y, 2, f"Leaked: {leaked_mb:.1f} MB",
                        self.front.color_yellow)
        y += 2

        # Instructions
        panel.win.addstr(y, 2, "Press 'L' to toggle leak",
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 2, "Press 'C' to clear leaked data",
                        self.front.color_white)
        y += 2

        panel.win.addstr(y, 2, "After 60s of leaking, watch for",
                        self.front.color_cyan)
        y += 1
        panel.win.addstr(y, 2, "warning in message panel",
                        self.front.color_cyan)

    @callback(LeakTest_ID, Keys.L)
    def toggle_leak(self, *args, **kwargs):
        """Toggle memory leak on 'L' key."""
        self.leak_active = not self.leak_active
        status = "started" if self.leak_active else "stopped"
        self.print(f"Memory leak {status}")

    @callback(LeakTest_ID, Keys.C)
    def clear_leak(self, *args, **kwargs):
        """Clear leaked data on 'C' key."""
        freed = sum(len(c) for c in self.leak_data) / (1024 * 1024)
        self.leak_data = []
        self.print(f"Cleared {freed:.1f}MB of leaked data")


if __name__ == "__main__":
    app = App(
        modules=[LeakTest, MemoryViewer],
        title="Memory Leak Detection Demo",
        demo_mode=False
    )
