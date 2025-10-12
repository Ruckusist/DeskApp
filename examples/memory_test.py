"""
Memory Monitoring Test - Proposal 11 Session 1 Verification
Created by: Claude Sonnet 4.5 10-10-25

Simple test to verify memory tracking displays in info panel.
Should show memory usage updating every 2 seconds.
"""

from deskapp import App, Module, Keys, callback
import random

TestMod_ID = random.random()


class MemoryTest(Module):
    """Simple module to test memory monitoring."""

    name = "Memory Test"

    def __init__(self, app):
        super().__init__(app, TestMod_ID)
        self.counter = 0

    def page(self, panel):
        """Display memory test info."""
        h, w = panel.dims[0], panel.dims[1]

        self.counter += 1

        # Get memory info
        mem = self.app.memory.get_current()
        baseline = self.app.memory.baseline
        growth = self.app.memory.get_growth_mb()

        y = 1
        panel.win.addstr(y, 2, "Memory Monitoring Test",
                        self.front.color_cyan)
        y += 2

        panel.win.addstr(y, 2, f"Frame: {self.counter}",
                        self.front.color_white)
        y += 1

        panel.win.addstr(y, 2,
                        f"Current: {mem['rss']/(1024*1024):.1f} MB",
                        self.front.color_green)
        y += 1

        panel.win.addstr(y, 2,
                        f"Baseline: {baseline['rss']/(1024*1024):.1f} MB",
                        self.front.color_white)
        y += 1

        panel.win.addstr(y, 2, f"Growth: {growth:+.1f} MB",
                        self.front.color_yellow)
        y += 2

        panel.win.addstr(y, 2,
                        "Check info panel (bottom) for memory display",
                        self.front.color_cyan)
        y += 1

        panel.win.addstr(y, 2, "Memory updates every 2 seconds",
                        self.front.color_green)


if __name__ == "__main__":
    app = App(
        modules=[MemoryTest],
        title="Memory Monitoring Test",
        show_demo=False
    )
