"""
Example demonstrating FPS tracking and cap functionality.
Tests FPS calculation, display, and optional limiter.

Created by: Claude Sonnet 4.5 on 10/09/25
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from deskapp import App, Module, callback, Keys
import random
import time

FPSTest_ID = random.random()


class FPSTest(Module):
    """Module that tests FPS tracking and display."""

    name = "FPS Test"

    def __init__(self, app):
        super().__init__(app, FPSTest_ID)
        self.counter = 0
        self.start_time = time.time()

    def page(self, panel):
        """Render FPS metrics."""
        self.index = 1

        # Title
        self.write(
            panel, self.index, 2,
            "FPS Tracking Test", "yellow"
        )
        self.index += 2

        # Get FPS data from app.data
        fps = self.app.data.get('fps', 0.0)
        frame_time = self.app.data.get('frame_time', 0.0)
        fps_cap = self.app.fps_cap

        # FPS display
        self.write(
            panel, self.index, 2,
            f"Current FPS: {fps}", "cyan"
        )
        self.index += 1

        # Frame time
        self.write(
            panel, self.index, 2,
            f"Frame Time: {frame_time}ms", "white"
        )
        self.index += 1

        # FPS cap status
        cap_status = f"{fps_cap}" if fps_cap else "Unlimited"
        self.write(
            panel, self.index, 2,
            f"FPS Cap: {cap_status}", "green"
        )
        self.index += 2

        # Instructions
        self.write(
            panel, self.index, 2,
            "Info panel shows FPS in default view", "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "FPS updates every second (rolling avg)", "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "Toggle NUM7 to see default PageInfo", "green"
        )
        self.index += 2

        # Frame counter
        self.counter += 1
        elapsed = time.time() - self.start_time
        local_fps = self.counter / elapsed if elapsed > 0 else 0
        self.write(
            panel, self.index, 2,
            f"Local frame count: {self.counter}", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            f"Local FPS estimate: {local_fps:.1f}", "white"
        )

    def PageRight(self, panel):
        """Right panel with FPS summary."""
        fps = self.app.data.get('fps', 0.0)
        frame_time = self.app.data.get('frame_time', 0.0)

        self.write(panel, 1, 1, "FPS Stats", "yellow")
        self.write(panel, 2, 1, f"FPS: {fps}", "cyan")
        self.write(panel, 3, 1, f"Frame: {frame_time}ms", "white")


if __name__ == "__main__":
    print("\n=== FPS Tracking Test ===")
    print("\nTest 1: Unlimited FPS (default)")
    print("Starting app with no FPS cap...")

    app1 = App(
        modules=[FPSTest],
        demo_mode=False,
        title="FPS Test (Unlimited)",
        show_box=True,
        show_right_panel=True,
        show_info_panel=True,
        autostart=False
    )
    # Note: Run this and observe FPS, then quit to try capped version
    # app1.start()

    print("\nTest 2: Capped at 30 FPS")
    print("Starting app with fps_cap=30...")

    app2 = App(
        modules=[FPSTest],
        demo_mode=False,
        title="FPS Test (Capped 30)",
        show_box=True,
        show_right_panel=True,
        show_info_panel=True,
        fps_cap=30,
        autostart=False
    )
    app2.start()

    print("\nFPS test complete!")
    print("Check that:")
    print("  - FPS displayed in info panel (NUM7)")
    print("  - FPS cap enforces limit when set")
    print("  - Frame time reported accurately")

