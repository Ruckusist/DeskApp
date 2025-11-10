# test.py
# A comprehensive test and demonstration file for the DeskApp framework.
# This file consolidates features from the `examples/` directory to showcase
# the full capabilities of DeskApp in a single, multi-module application.

import random
import time
from deskapp import App, Module, callback, Keys
from deskapp.src.worker import BaseWorker
from deskapp.mods import MemoryViewer

# --- Worker Definition (from 07_events.py, ex_worker_test.py) ---
# Workers run background tasks and communicate with the UI via events.
# They should NEVER directly interact with curses/UI elements.

class TestWorker(BaseWorker):
    """A simple worker that emits a 'tick' event every second with a counter."""

    def work(self):
        """The main loop for the worker thread."""
        count = 0
        while not self.should_stop:
            count += 1
            # Emit an event for the main thread to process.
            # This is the primary way workers send data to the UI.
            self.emit("test.tick", {"count": count})
            time.sleep(1)

# --- Module Definitions ---

# Module-specific callback IDs to prevent conflicts
MainTest_ID = random.random()
DataDisplay_ID = random.random()

class MainTestModule(Module):
    """
    The main module demonstrating most of DeskApp's features.
    Corresponds to concepts from almost all examples.
    """
    name = "Main Test"

    def __init__(self, app):
        super().__init__(app, MainTest_ID)

        # --- Data Sharing (from 06_data_sharing.py) ---
        # Initialize a shared counter in the global app.data dictionary.
        if 'shared_counter' not in self.app.data:
            self.app.data['shared_counter'] = 0

        # --- Worker & Event System (from 07_events.py) ---
        self.worker = None
        self.worker_count = 0
        self.submitted_text = ""

        # --- Mouse Events (from ex_mouse_events.py) ---
        self.mouse_events = []

        # Register event listeners. self.on_event handles cleanup automatically.
        self.on_event("test.tick", self.on_worker_tick)
        self.on_event("input.mouse", self.on_mouse_event)
        self.on_event("ui.menu.select", self.on_menu_select)

    # --- Event Handlers (run in the main thread) ---
    def on_worker_tick(self, event):
        """Handles the 'test.tick' event from our worker."""
        self.worker_count = event['data'].get('count', 0)

    def on_mouse_event(self, event):
        """Handles raw mouse input events."""
        data = event['data']
        log = (f"Click | Region: {data['region']}, "
               f"Coords: ({data['row']}, {data['col']})")
        self.mouse_events.append(log)
        if len(self.mouse_events) > 5:
            self.mouse_events.pop(0)

    def on_menu_select(self, event):
        """Handles menu item selection events (from mouse clicks)."""
        self.print(f"Menu clicked: {event['data']['name']}")

    # --- Panel Rendering (from 01_panels.py, 02_module.py) ---
    def page(self, panel):
        """Renders the content for the main panel."""
        self.write(panel, 1, 2, "DeskApp Comprehensive Test", "yellow")

        y = 3
        self.write(panel, y, 2, "Press PgUp/PgDn to switch modules.", "cyan")
        y += 2

        # Worker Demo
        worker_status = "RUNNING" if self.worker and self.worker.is_running else "STOPPED"
        self.write(panel, y, 2, f"Worker Status: {worker_status}", "white")
        self.write(panel, y+1, 4, f"Worker Tick Count: {self.worker_count}", "green")
        y += 3

        # Data Sharing Demo
        shared_val = self.app.data['shared_counter']
        self.write(panel, y, 2, f"Shared Counter: {shared_val}", "white")
        y += 2

        # Text Input Demo (from 03_callbacks.py)
        self.write(panel, y, 2, "Last Submitted Text:", "white")
        self.write(panel, y+1, 4, f"'{self.submitted_text}'", "green")
        y += 3

        # Mouse Demo
        self.write(panel, y, 2, "Recent Mouse Events:", "white")
        for i, event_log in enumerate(self.mouse_events):
            self.write(panel, y+1+i, 4, event_log, "green")

    def PageRight(self, panel):
        """Renders content for the optional right-side panel."""
        self.write(panel, 1, 2, "Controls", "yellow")
        self.write(panel, 3, 2, "S - Start Worker", "white")
        self.write(panel, 4, 2, "X - Stop Worker", "white")
        self.write(panel, 5, 2, "SPACE - Inc Counter", "white")
        self.write(panel, 6, 2, "TAB - Text Input", "white")
        self.write(panel, 7, 2, "Q - Quit", "white")
        self.write(panel, 9, 2, "NUM1-9 Toggle Panels", "cyan")

    def PageInfo(self, panel):
        """Renders content for the 3-line info panel at the bottom."""
        worker_status = "ON" if self.worker and self.worker.is_running else "OFF"
        self.write(panel, 1, 2, f"Shared Counter: {self.app.data['shared_counter']}", "cyan")
        self.write(panel, 2, 2, f"Worker: {worker_status} | Ticks: {self.worker_count}", "green")
        # Line 3 is used by the default memory/fps display.

    # --- Input Handling (from 03_callbacks.py) ---
    def handle_text(self, input_string: str):
        """Hook for processing submitted text from input mode."""
        self.submitted_text = input_string
        self.print(f"Text submitted: '{input_string}'")

    @callback(MainTest_ID, Keys.S)
    def start_worker(self, *args, **kwargs):
        """Starts the background worker."""
        if not self.worker or not self.worker.is_running:
            self.worker = TestWorker(self.app, name="TestWorker")
            self.worker.start()
            self.print("Worker started.")
        else:
            self.print("Worker is already running.")

    @callback(MainTest_ID, Keys.X)
    def stop_worker(self, *args, **kwargs):
        """Stops the background worker."""
        if self.worker and self.worker.is_running:
            self.worker.stop()
            self.worker = None
            self.print("Worker stopped.")
        else:
            self.print("Worker is not running.")

    @callback(MainTest_ID, Keys.SPACE)
    def increment_counter(self, *args, **kwargs):
        """Increments the shared counter."""
        self.app.data['shared_counter'] += 1
        self.print(f"Shared counter incremented to {self.app.data['shared_counter']}")

    def end_safely(self):
        """Cleanly shuts down the module, including stopping any workers."""
        self.print("MainTestModule shutting down...")
        if self.worker:
            self.worker.stop()
        super().end_safely()

class DataDisplayModule(Module):
    """
    A second module to demonstrate data sharing and module switching.
    Corresponds to concepts from 06_data_sharing.py.
    """
    name = "Data Display"

    def __init__(self, app):
        super().__init__(app, DataDisplay_ID)

    def page(self, panel):
        """Displays the shared counter value in different formats."""
        self.write(panel, 1, 2, "Data Sharing Demonstration", "yellow")
        self.write(panel, 3, 2, "This module reads from 'app.data' set by 'Main Test'.", "cyan")

        # Read from the shared data dictionary
        value = self.app.data.get('shared_counter', 0)
        y = 5
        self.write(panel, y, 2, f"Decimal: {value}", "white")
        self.write(panel, y+1, 2, f"Hex: {hex(value)}", "green")
        self.write(panel, y+2, 2, f"Binary: {bin(value)}", "green")

        y += 4
        self.write(panel, y, 2, "Switch back to 'Main Test' with PgUp/PgDn.", "cyan")

# --- App Initialization and Execution ---
if __name__ == "__main__":
    app = App(
        # --- Modules ---
        modules=[
            MainTestModule,
            DataDisplayModule,
            MemoryViewer  # From deskapp.mods, demonstrates memory tracking
        ],
        # --- Basic Config ---
        title="Comprehensive DeskApp Test",
        demo_mode=False, # We are providing our own modules

        # --- Panel Visibility (from 01_panels.py) ---
        show_right_panel=True,
        show_info_panel=True,

        # --- Layouts (from 04_layouts.py) ---
        v_split=0.4,   # Ratio of Main vs Messages panel height
        h_split=0.18,  # Ratio of Menu vs Main panel width
        
        # --- Styling (from 05_styling.py) ---
        show_box=True,
        show_banner=True,

        # --- Input/Performance (from ex_mouse_events.py, ex_fps_test.py) ---
        use_mouse=True, # Enable mouse support
        fps_cap=60      # Limit framerate to 60 FPS
    )
    # The app starts automatically because autostart=True by default.