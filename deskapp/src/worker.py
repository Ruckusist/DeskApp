"""
DeskApp Worker Thread Pattern
Provides base class for background task workers that safely emit events.

Architecture:
- Workers run in background threads
- Workers NEVER touch curses (main thread only!)
- Workers emit events for data updates
- Main loop processes events and updates UI

Usage:
    class MyWorker(BaseWorker):
        def work(self):
            while not self.should_stop:
                # Do background work
                result = expensive_operation()
                # Emit event for main thread
                self.emit('data.ready', {'result': result})
                time.sleep(1)

    # In module
    worker = MyWorker(app)
    worker.start()
    # ... later
    worker.stop()

Created by: Claude Sonnet 4.5 on 10/10/25
"""

import threading
import time
from typing import Optional, Dict, Any


class BaseWorker(threading.Thread):
    """Base class for background worker threads.

    Provides:
    - Clean start/stop lifecycle
    - Event emission to main thread
    - Error handling and reporting
    - Standard worker patterns
    """

    def __init__(self, app, name: str = "Worker"):
        """Initialize worker.

        Args:
            app: DeskApp App instance
            name: Worker name for identification
        """
        super().__init__(daemon=True)
        self.app = app
        self.worker_name = name
        self.should_stop = False
        self.is_running = False
        self.error = None

    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None
            ) -> bool:
        """Emit event from worker thread.

        Thread-safe wrapper for app.emit().

        Args:
            event_type: Event identifier
            data: Event payload

        Returns:
            True if queued, False if dropped
        """
        if data is None:
            data = {}
        return self.app.emit(event_type, data,
                            source=f"worker.{self.worker_name}")

    def run(self) -> None:
        """Thread entry point.

        DO NOT OVERRIDE - override work() instead.
        """
        self.is_running = True
        self.emit('worker.started', {'name': self.worker_name})

        try:
            self.work()
        except Exception as e:
            self.error = str(e)
            self.emit('worker.error', {
                'name': self.worker_name,
                'error': str(e)
            })
        finally:
            self.is_running = False
            self.emit('worker.stopped', {'name': self.worker_name})

    def work(self) -> None:
        """Worker main loop - OVERRIDE THIS.

        Check self.should_stop periodically and return to exit cleanly.

        Example:
            def work(self):
                while not self.should_stop:
                    result = do_work()
                    self.emit('work.done', {'result': result})
                    time.sleep(1)
        """
        raise NotImplementedError("Override work() in subclass")

    def stop(self, timeout: float = 2.0) -> bool:
        """Signal worker to stop and wait.

        Args:
            timeout: Max seconds to wait for clean shutdown

        Returns:
            True if stopped cleanly, False if timeout
        """
        self.should_stop = True
        self.join(timeout)
        return not self.is_alive()


class CounterWorker(BaseWorker):
    """Example worker that counts in background.

    Demonstrates basic worker pattern with periodic events.
    """

    def __init__(self, app, interval: float = 1.0):
        super().__init__(app, name="Counter")
        self.interval = interval
        self.count = 0

    def work(self) -> None:
        """Count and emit events periodically."""
        while not self.should_stop:
            self.count += 1
            self.emit('counter.tick', {
                'count': self.count,
                'interval': self.interval
            })
            time.sleep(self.interval)


class TimerWorker(BaseWorker):
    """Worker that triggers event after delay.

    One-shot timer that emits event when time expires.
    """

    def __init__(self, app, delay: float, event_type: str,
                 event_data: Optional[Dict] = None):
        super().__init__(app, name="Timer")
        self.delay = delay
        self.event_type = event_type
        self.event_data = event_data or {}

    def work(self) -> None:
        """Wait for delay then emit event."""
        start = time.time()
        while not self.should_stop:
            elapsed = time.time() - start
            if elapsed >= self.delay:
                self.emit(self.event_type, self.event_data)
                break
            # Check every 100ms
            time.sleep(0.1)


class PeriodicWorker(BaseWorker):
    """Worker that calls function periodically.

    Useful for polling, monitoring, or periodic updates.
    """

    def __init__(self, app, interval: float, callback, name: str = "Periodic"):
        super().__init__(app, name=name)
        self.interval = interval
        self.callback = callback

    def work(self) -> None:
        """Call callback periodically."""
        while not self.should_stop:
            try:
                # Callback can emit events or just do work
                result = self.callback()
                if result is not None:
                    self.emit('periodic.result', {'result': result})
            except Exception as e:
                self.emit('periodic.error', {'error': str(e)})

            time.sleep(self.interval)
