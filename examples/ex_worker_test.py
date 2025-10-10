"""
Worker Thread Example
Demonstrates BaseWorker pattern for background tasks.

Shows:
- CounterWorker emitting periodic events
- TimerWorker for delayed actions
- Clean worker start/stop
- Event-based UI updates

Created by: Claude Sonnet 4.5 on 10/10/25
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from deskapp import App, Module, callback, Keys
from deskapp.src.worker import CounterWorker, TimerWorker
import random
import time

WorkerTest_ID = random.random()


class WorkerTest(Module):
    """Module demonstrating worker thread pattern."""

    name = "Worker Test"

    def __init__(self, app):
        super().__init__(app, WorkerTest_ID)
        self.counter_value = 0
        self.timer_fired = False
        self.worker_events = []
        self.counter_worker = None
        self.timer_worker = None
        
        # Register event listeners
        self.on_event('counter.tick', self.on_counter_tick)
        self.on_event('timer.done', self.on_timer_done)
        self.on_event('worker.started', self.on_worker_started)
        self.on_event('worker.stopped', self.on_worker_stopped)
        self.on_event('worker.error', self.on_worker_error)

    def on_counter_tick(self, event):
        """Handle counter tick events."""
        self.counter_value = event['data']['count']
        self.log_event(f"Counter: {self.counter_value}")

    def on_timer_done(self, event):
        """Handle timer expiration."""
        self.timer_fired = True
        self.log_event("Timer fired!")

    def on_worker_started(self, event):
        """Handle worker start."""
        name = event['data']['name']
        self.log_event(f"Worker '{name}' started")

    def on_worker_stopped(self, event):
        """Handle worker stop."""
        name = event['data']['name']
        self.log_event(f"Worker '{name}' stopped")

    def on_worker_error(self, event):
        """Handle worker errors."""
        error = event['data']['error']
        self.log_event(f"ERROR: {error}")

    def log_event(self, message):
        """Add to event log."""
        self.worker_events.append(message)
        if len(self.worker_events) > 15:
            self.worker_events.pop(0)

    def page(self, panel):
        """Render main content."""
        self.index = 1

        # Title
        self.write(panel, self.index, 2, "Worker Thread Demo", "yellow")
        self.index += 2

        # Instructions
        self.write(panel, self.index, 2, "Controls:", "cyan")
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  S: Start counter worker (1/sec)", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  X: Stop counter worker", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  T: Start 5-second timer", "white"
        )
        self.index += 2

        # Worker status
        counter_status = "RUNNING" if (
            self.counter_worker and self.counter_worker.is_running
        ) else "STOPPED"
        timer_status = "RUNNING" if (
            self.timer_worker and self.timer_worker.is_running
        ) else "STOPPED"
        
        self.write(panel, self.index, 2, "Worker Status:", "cyan")
        self.index += 1
        self.write(
            panel, self.index, 2,
            f"  Counter: {counter_status}", "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            f"  Timer: {timer_status}", "green"
        )
        self.index += 2

        # Counter value
        self.write(
            panel, self.index, 2,
            f"Counter Value: {self.counter_value}", "cyan"
        )
        self.index += 1
        timer_msg = "FIRED!" if self.timer_fired else "waiting..."
        self.write(
            panel, self.index, 2,
            f"Timer Status: {timer_msg}", "cyan"
        )
        self.index += 2

        # Event log
        self.write(panel, self.index, 2, "Event Log:", "cyan")
        self.index += 1
        if not self.worker_events:
            self.write(panel, self.index, 2, "  (no events)", "white")
        else:
            for event in self.worker_events[-12:]:
                if self.index >= self.h - 2:
                    break
                self.write(panel, self.index, 2, f"  {event}", "green")
                self.index += 1

    def PageInfo(self, panel):
        """Show threading info."""
        import threading
        active_count = threading.active_count()
        
        line1 = f"Active threads: {active_count}"
        line2 = f"Counter: {self.counter_value}"
        line3 = f"Events: {len(self.worker_events)}"
        
        try:
            maxw = max(0, panel.dims[1] - 4)
            panel.win.addstr(1, 2, line1[:maxw], self.front.color_cyan)
            panel.win.addstr(2, 2, line2[:maxw], self.front.color_green)
            panel.win.addstr(3, 2, line3[:maxw], self.front.color_yellow)
        except Exception:
            pass

    @callback(WorkerTest_ID, keypress=Keys.S)
    def on_s(self, *args, **kwargs):
        """Start counter worker."""
        if self.counter_worker and self.counter_worker.is_running:
            self.print("Counter already running")
            return
        
        self.counter_worker = CounterWorker(self.app, interval=1.0)
        self.counter_worker.start()
        self.print("Started counter worker")

    @callback(WorkerTest_ID, keypress=Keys.X)
    def on_x(self, *args, **kwargs):
        """Stop counter worker."""
        if not self.counter_worker or not self.counter_worker.is_running:
            self.print("Counter not running")
            return
        
        self.counter_worker.stop()
        self.print("Stopped counter worker")

    @callback(WorkerTest_ID, keypress=Keys.T)
    def on_t(self, *args, **kwargs):
        """Start timer."""
        if self.timer_worker and self.timer_worker.is_running:
            self.print("Timer already running")
            return
        
        self.timer_fired = False
        self.timer_worker = TimerWorker(
            self.app,
            delay=5.0,
            event_type='timer.done',
            event_data={'message': 'Timer expired'}
        )
        self.timer_worker.start()
        self.print("Started 5-second timer")

    def end_safely(self):
        """Clean up workers on shutdown."""
        if self.counter_worker:
            self.counter_worker.stop()
        if self.timer_worker:
            self.timer_worker.stop()
        super().end_safely()


if __name__ == "__main__":
    print("\n=== Worker Thread Example ===")
    print("Demonstrating background task pattern")
    print("\nControls:")
    print("  S - Start counter worker (counts every second)")
    print("  X - Stop counter worker")
    print("  T - Start 5-second timer")
    print("  Q - Quit\n")

    app = App(
        modules=[WorkerTest],
        demo_mode=False,
        title="Worker Demo",
        show_box=True,
        show_info_panel=True,
        autostart=False
    )
    app.start()

    print("\nWorker demo complete!")
