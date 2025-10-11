"""
DeskApp Event System
Provides thread-safe event bus for inter-module communication and
background task coordination.

Architecture:
- Queue-based event passing (thread-safe)
- Main thread processes events and updates UI
- Worker threads emit events, never touch curses directly
- Event handlers execute in main thread context

Event Structure:
    {
        'type': str,        # Event identifier (e.g., 'data.update')
        'source': str,      # Originating module or 'system'
        'data': dict,       # Arbitrary payload
        'timestamp': float  # time.time() when emitted
    }

System Events:
    'system.init'        - App initialization complete
                          data: {'module_count': int, 'terminal_size': (w,h)}
    'system.shutdown'    - App shutting down
                          data: {}
    'system.resize'      - Terminal resized
                          data: {'width': int, 'height': int}
    'system.fps_update'  - FPS stats updated (emitted every second)
                          data: {'fps': float, 'frame_time': float}
    'system.error'       - Error in event handler
                          data: {'error': str, 'handler': str, ...}

Usage:
    # In app initialization
    app.events = EventBus()

    # Emit an event
    app.events.emit('data.update', {'value': 42}, source='MyModule')

    # Register listener
    def on_data_update(event):
        print(f"Got data: {event['data']}")
    app.events.on('data.update', on_data_update)

    # Process events (in main loop)
    app.events.process_events(max_events=10)

Created by: Claude Sonnet 4.5 on 10/10/25
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
