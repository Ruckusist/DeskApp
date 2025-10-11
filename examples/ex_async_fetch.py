"""
Advanced Worker Example: Async Data Fetcher
Demonstrates realistic background task pattern with progress updates.

Shows:
- Custom worker with multi-step process
- Progress events during long-running task
- Error handling and retry logic
- Multiple concurrent workers
- Clean UI updates from worker events

Created by: Claude Sonnet 4.5 on 10/10/25
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from deskapp import App, Module, callback, Keys
from deskapp.src.worker import BaseWorker
import random
import time

AsyncFetch_ID = random.random()


class DataFetchWorker(BaseWorker):
    """Worker that simulates async data fetching with progress."""

    def __init__(self, app, fetch_id: int, duration: float = 3.0):
        super().__init__(app, name=f"Fetch{fetch_id}")
        self.fetch_id = fetch_id
        self.duration = duration
        self.steps = 5

    def work(self):
        """Simulate multi-step data fetch process."""
        step_duration = self.duration / self.steps

        for step in range(self.steps):
            if self.should_stop:
                self.emit('fetch.cancelled', {
                    'fetch_id': self.fetch_id,
                    'step': step
                })
                return

            # Emit progress
            progress = ((step + 1) / self.steps) * 100
            self.emit('fetch.progress', {
                'fetch_id': self.fetch_id,
                'step': step + 1,
                'total_steps': self.steps,
                'progress': progress
            })

            # Simulate work
            time.sleep(step_duration)

        # Simulate success/failure (90% success rate)
        if random.random() < 0.9:
            self.emit('fetch.complete', {
                'fetch_id': self.fetch_id,
                'data': f'Result_{self.fetch_id}_{random.randint(100,999)}',
                'duration': self.duration
            })
        else:
            self.emit('fetch.error', {
                'fetch_id': self.fetch_id,
                'error': 'Simulated network error'
            })


class AsyncFetch(Module):
    """Module demonstrating async data fetching."""

    name = "Async Fetch"

    def __init__(self, app):
        super().__init__(app, AsyncFetch_ID)
        self.workers = {}  # {fetch_id: worker}
        self.fetch_status = {}  # {fetch_id: {'status': ..., 'progress': ...}}
        self.next_fetch_id = 1
        self.completed_fetches = []

        # Register event listeners
        self.on_event('fetch.progress', self.on_progress)
        self.on_event('fetch.complete', self.on_complete)
        self.on_event('fetch.error', self.on_error)
        self.on_event('fetch.cancelled', self.on_cancelled)
        self.on_event('system.init', self.on_init)

    def on_init(self, event):
        """Handle system init event."""
        self.print(f"System initialized with {event['data']['module_count']} modules")

    def on_progress(self, event):
        """Handle fetch progress updates."""
        data = event['data']
        fetch_id = data['fetch_id']
        self.fetch_status[fetch_id] = {
            'status': 'fetching',
            'progress': data['progress'],
            'step': data['step'],
            'total_steps': data['total_steps']
        }

    def on_complete(self, event):
        """Handle fetch completion."""
        data = event['data']
        fetch_id = data['fetch_id']
        self.fetch_status[fetch_id] = {
            'status': 'complete',
            'progress': 100,
            'data': data['data']
        }
        self.completed_fetches.append(f"#{fetch_id}: {data['data']}")
        if len(self.completed_fetches) > 10:
            self.completed_fetches.pop(0)
        self.print(f"Fetch #{fetch_id} complete: {data['data']}")

    def on_error(self, event):
        """Handle fetch errors."""
        data = event['data']
        fetch_id = data['fetch_id']
        self.fetch_status[fetch_id] = {
            'status': 'error',
            'progress': 0,
            'error': data['error']
        }
        self.print(f"Fetch #{fetch_id} error: {data['error']}")

    def on_cancelled(self, event):
        """Handle cancelled fetches."""
        data = event['data']
        fetch_id = data['fetch_id']
        self.fetch_status[fetch_id] = {
            'status': 'cancelled',
            'progress': 0
        }

    def page(self, panel):
        """Render main content."""
        self.index = 1

        # Title
        self.write(panel, self.index, 2, "Async Data Fetcher", "yellow")
        self.index += 2

        # Instructions
        self.write(panel, self.index, 2, "Controls:", "cyan")
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  F: Start new fetch (3s duration)", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  R: Start 5 fetches simultaneously", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  C: Cancel all active fetches", "white"
        )
        self.index += 2

        # Active fetches
        active_count = sum(
            1 for status in self.fetch_status.values()
            if status['status'] == 'fetching'
        )
        self.write(
            panel, self.index, 2,
            f"Active Fetches: {active_count}", "cyan"
        )
        self.index += 2

        # Progress bars
        if self.fetch_status:
            self.write(panel, self.index, 2, "Fetch Progress:", "cyan")
            self.index += 1

            # Show last 8 fetches
            for fetch_id in sorted(self.fetch_status.keys())[-8:]:
                if self.index >= self.h - 6:
                    break

                status = self.fetch_status[fetch_id]
                status_text = status['status']
                progress = status.get('progress', 0)

                # Progress bar
                bar_width = 20
                filled = int((progress / 100) * bar_width)
                bar = '█' * filled + '░' * (bar_width - filled)

                # Color based on status
                if status_text == 'complete':
                    color = "green"
                elif status_text == 'error':
                    color = "red"
                elif status_text == 'cancelled':
                    color = "yellow"
                else:
                    color = "cyan"

                line = f"  #{fetch_id}: [{bar}] {progress:.0f}% {status_text}"
                self.write(panel, self.index, 2, line, color)
                self.index += 1
        else:
            self.write(panel, self.index, 2, "  (no fetches yet)", "white")
            self.index += 1

        self.index += 1

        # Completed fetches
        if self.completed_fetches:
            self.write(
                panel, self.index, 2,
                "Recent Completions:", "cyan"
            )
            self.index += 1
            for item in self.completed_fetches[-5:]:
                if self.index >= self.h - 2:
                    break
                self.write(panel, self.index, 2, f"  {item}", "green")
                self.index += 1

    def PageInfo(self, panel):
        """Show fetch statistics."""
        total = len(self.fetch_status)
        complete = sum(
            1 for s in self.fetch_status.values()
            if s['status'] == 'complete'
        )
        errors = sum(
            1 for s in self.fetch_status.values()
            if s['status'] == 'error'
        )

        line1 = f"Total: {total} | Complete: {complete} | Errors: {errors}"
        line2 = f"Active workers: {len(self.workers)}"
        line3 = "Event-driven async pattern"

        try:
            maxw = max(0, panel.dims[1] - 4)
            panel.win.addstr(1, 2, line1[:maxw], self.front.color_cyan)
            panel.win.addstr(2, 2, line2[:maxw], self.front.color_green)
            panel.win.addstr(3, 2, line3[:maxw], self.front.color_yellow)
        except Exception:
            pass

    @callback(AsyncFetch_ID, keypress=Keys.F)
    def on_f(self, *args, **kwargs):
        """Start new fetch."""
        fetch_id = self.next_fetch_id
        self.next_fetch_id += 1

        worker = DataFetchWorker(self.app, fetch_id, duration=3.0)
        self.workers[fetch_id] = worker
        worker.start()

        self.fetch_status[fetch_id] = {
            'status': 'starting',
            'progress': 0
        }
        self.print(f"Started fetch #{fetch_id}")

    @callback(AsyncFetch_ID, keypress=Keys.R)
    def on_r(self, *args, **kwargs):
        """Start 5 fetches simultaneously."""
        for _ in range(5):
            self.on_f()
        self.print("Started 5 simultaneous fetches")

    @callback(AsyncFetch_ID, keypress=Keys.C)
    def on_c(self, *args, **kwargs):
        """Cancel all active fetches."""
        count = 0
        for worker in self.workers.values():
            if worker.is_running:
                worker.stop(timeout=0.5)
                count += 1
        self.print(f"Cancelled {count} fetches")

    def end_safely(self):
        """Clean up all workers."""
        for worker in self.workers.values():
            worker.stop(timeout=0.5)
        super().end_safely()


if __name__ == "__main__":
    print("\n=== Async Data Fetcher Example ===")
    print("Demonstrates realistic background task pattern")
    print("\nControls:")
    print("  F - Start new 3-second fetch")
    print("  R - Start 5 fetches simultaneously")
    print("  C - Cancel all active fetches")
    print("  Q - Quit\n")

    app = App(
        modules=[AsyncFetch],
        demo_mode=False,
        title="Async Fetch Demo",
        show_box=True,
        show_info_panel=True,
        autostart=False
    )
    app.start()

    print("\nAsync fetch demo complete!")
