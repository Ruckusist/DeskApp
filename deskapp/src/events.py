"""
DeskApp Event + Worker System
Provides thread-safe event bus for inter-module communication and
background task coordination, plus standard background worker patterns.

Architecture:
- Queue-based event passing (thread-safe)
- Main thread processes events and updates UI
- Worker threads emit events, never touch curses directly
- Event handlers execute in main thread context

Event Structure:
    {
        'type': str,
        'source': str,
        'data': dict,
        'timestamp': float
    }

Worker Patterns:
- BaseWorker: lifecycle + event emission
- CounterWorker: periodic counter events
- TimerWorker: one-shot delayed events
- PeriodicWorker: callback-based periodic work

Created by: Claude Sonnet 4.5 on 10/10/25
Workers merged by: GitHub Copilot 11-15-25
"""

import queue
import threading
import time
from typing import Callable, Dict, List, Any, Optional


class EventBus:
    """Thread-safe event bus for DeskApp framework.

    Provides pub/sub event system with queued delivery.
    All event processing happens on main thread for curses safety.
    """

    def __init__(self, max_queue_size: int = 1000):
        """Initialize event bus.

        Args:
            max_queue_size: Maximum events in queue before dropping
        """
        # Thread-safe event queue
        self.event_queue = queue.Queue(maxsize=max_queue_size)

        # Event listeners: {event_type: [handler_fn, ...]}
        self.listeners: Dict[str, List[Callable]] = {}

        # Lock for listener dict modifications
        self.listener_lock = threading.Lock()

        # Metrics
        self.events_emitted = 0
        self.events_processed = 0
        self.events_dropped = 0
        self.handler_errors = 0

        # Performance tracking
        self.last_process_time = 0.0

    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None,
             source: str = "unknown") -> bool:
        """Emit an event to the queue.

        Args:
            event_type: Event identifier (e.g., 'data.update')
            data: Event payload (default: empty dict)
            source: Event source (module name or 'system')

        Returns:
            True if queued, False if queue full (dropped)
        """
        if data is None:
            data = {}

        event = {
            'type': event_type,
            'source': source,
            'data': data,
            'timestamp': time.time()
        }

        try:
            # Non-blocking put - drop if queue full
            self.event_queue.put_nowait(event)
            self.events_emitted += 1
            return True
        except queue.Full:
            # Queue overflow - drop event
            self.events_dropped += 1
            return False

    def on(self, event_type: str, handler: Callable) -> None:
        """Register event listener.

        Args:
            event_type: Event to listen for (e.g., 'data.update')
            handler: Callback function(event) -> None
        """
        with self.listener_lock:
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            if handler not in self.listeners[event_type]:
                self.listeners[event_type].append(handler)

    def off(self, event_type: str, handler: Callable) -> bool:
        """Unregister event listener.

        Args:
            event_type: Event type
            handler: Handler function to remove

        Returns:
            True if removed, False if not found
        """
        with self.listener_lock:
            if event_type in self.listeners:
                if handler in self.listeners[event_type]:
                    self.listeners[event_type].remove(handler)
                    # Clean up empty listener lists
                    if not self.listeners[event_type]:
                        del self.listeners[event_type]
                    return True
        return False

    def process_events(self, max_events: int = 10,
                      max_time_ms: float = 5.0) -> int:
        """Process queued events in main thread.

        Calls registered handlers for each event.
        Limits processing to prevent UI stutter.

        Args:
            max_events: Maximum events to process this call
            max_time_ms: Max processing time in milliseconds

        Returns:
            Number of events processed
        """
        start_time = time.perf_counter()
        processed = 0

        for _ in range(max_events):
            # Check time budget
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if elapsed_ms >= max_time_ms:
                break

            # Get next event (non-blocking)
            try:
                event = self.event_queue.get_nowait()
            except queue.Empty:
                break

            # Dispatch to handlers
            self._dispatch_event(event)
            processed += 1
            self.events_processed += 1

        # Track processing time
        self.last_process_time = (
            (time.perf_counter() - start_time) * 1000
        )

        return processed

    def _dispatch_event(self, event: Dict[str, Any]) -> None:
        """Dispatch event to registered handlers.

        Handles exceptions to prevent one bad handler crashing loop.

        Args:
            event: Event dict to dispatch
        """
        event_type = event['type']

        # Get handlers (with lock for thread safety)
        with self.listener_lock:
            handlers = self.listeners.get(event_type, []).copy()

        # Call each handler
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't crash
                self.handler_errors += 1
                # Emit error event (if not already in error handler)
                if event_type != 'system.error':
                    self.emit(
                        'system.error',
                        {
                            'error': str(e),
                            'handler': handler.__name__,
                            'event_type': event_type,
                            'original_event': event
                        },
                        source='event_bus'
                    )

    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics.

        Returns:
            Dict with emitted, processed, dropped counts, etc.
        """
        return {
            'events_emitted': self.events_emitted,
            'events_processed': self.events_processed,
            'events_dropped': self.events_dropped,
            'handler_errors': self.handler_errors,
            'queue_size': self.event_queue.qsize(),
            'last_process_time_ms': self.last_process_time,
            'listener_count': sum(
                len(handlers) for handlers in self.listeners.values()
            )
        }

    def clear(self) -> int:
        """Clear all pending events from queue.

        Returns:
            Number of events cleared
        """
        cleared = 0
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
                cleared += 1
            except queue.Empty:
                break
        return cleared

    def shutdown(self) -> None:
        """Clean shutdown - clear queue and listeners."""
        self.clear()
        with self.listener_lock:
            self.listeners.clear()


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
            time.sleep(0.1)


class PeriodicWorker(BaseWorker):
    """Worker that calls function periodically.

    Useful for polling, monitoring, or periodic updates.
    """

    def __init__(self, app, interval: float, callback,
                 name: str = "Periodic"):
        super().__init__(app, name=name)
        self.interval = interval
        self.callback = callback

    def work(self) -> None:
        """Call callback periodically."""
        while not self.should_stop:
            try:
                result = self.callback()
                if result is not None:
                    self.emit('periodic.result', {'result': result})
            except Exception as e:
                self.emit('periodic.error', {'error': str(e)})

            time.sleep(self.interval)
