"""
07_events.py - Event System Tutorial

DeskApp's event system enables asynchronous communication between
modules and background workers. This is a simplified version of
ex_event_basic.py for tutorial purposes.

Event System Features:
- Emit events from any module with app.emit()
- Listen to events with app.on() or self.on_event()
- System events (init, resize, shutdown, fps_update, error)
- Thread-safe event queue
- Worker threads for background tasks

Press P to emit a "ping" event.
Press D to emit a "data" event with payload.
Press S to start a background worker.
Press X to stop the worker.
Press Q to quit.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
from deskapp.src.worker import BaseWorker
import random
import time

EventID = random.random()


class SimpleWorker(BaseWorker):
    """Background worker that counts and emits events."""
    
    def work(self):
        """Main work loop - runs in background thread."""
        counter = 0
        
        while not self.should_stop:
            counter += 1
            
            # Emit event from worker thread
            self.emit("worker.tick", {
                "count": counter,
                "timestamp": time.time()
            })
            
            # Wait 1 second
            time.sleep(1)
        
        # Emit stopped event
        self.emit("worker.stopped", {"final_count": counter})


class EventDemo(Module):
    """Demonstrates the event system."""
    name = "Event Demo"

    def __init__(self, app):
        super().__init__(app, EventID)
        
        # Event tracking
        self.ping_count = 0
        self.data_count = 0
        self.worker_ticks = 0
        self.last_data = None
        
        # Worker instance
        self.worker = None
        
        # Register event listeners using self.on_event()
        # This automatically tracks handlers for cleanup
        self.on_event("ping", self.on_ping)
        self.on_event("data", self.on_data)
        self.on_event("worker.tick", self.on_worker_tick)
        self.on_event("worker.stopped", self.on_worker_stopped)
        
        # System events
        self.on_event("system.init", self.on_system_init)
        self.on_event("system.resize", self.on_system_resize)

    def page(self, panel):
        """Display event system status."""
        h, w = panel.h, panel.w
        
        # Title
        panel.win.addstr(1, 2, "Event System Tutorial", 
                        self.front.color_white)
        
        # Event counts
        y = 3
        panel.win.addstr(y, 2, "Event Statistics:", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, f"Ping events: {self.ping_count}", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, f"Data events: {self.data_count}", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, f"Worker ticks: {self.worker_ticks}", 
                        self.front.color_white)
        
        # Last data
        if self.last_data:
            y += 2
            panel.win.addstr(y, 2, "Last Data Event:", 
                            self.front.color_yellow)
            y += 1
            panel.win.addstr(y, 4, str(self.last_data)[:w-6], 
                            self.front.color_cyan)
        
        # Worker status
        y += 2
        worker_running = (self.worker is not None and 
                         self.worker.is_running)
        status = "RUNNING" if worker_running else "STOPPED"
        color = (self.front.color_green if worker_running 
                else self.front.color_red)
        panel.win.addstr(y, 2, f"Worker Status: {status}", color)
        
        # Controls
        y += 2
        panel.win.addstr(y, 2, "Controls:", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, "P - Emit ping event", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "D - Emit data event", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "S - Start worker", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "X - Stop worker", 
                        self.front.color_white)

    def PageInfo(self, panel):
        """Show event queue metrics."""
        metrics = self.app.events.get_metrics()
        
        panel.win.addstr(0, 2, f"Events: {metrics['total_events']}", 
                        self.front.color_white)
        panel.win.addstr(1, 2, f"Queue: {metrics['queue_size']}", 
                        self.front.color_cyan)
        panel.win.addstr(2, 2, 
                        f"Listeners: {metrics['listener_count']}", 
                        self.front.color_green)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def on_ping(self, event_type, data, source):
        """Handler for ping events."""
        self.ping_count += 1

    def on_data(self, event_type, data, source):
        """Handler for data events."""
        self.data_count += 1
        self.last_data = data

    def on_worker_tick(self, event_type, data, source):
        """Handler for worker tick events."""
        self.worker_ticks = data.get("count", 0)

    def on_worker_stopped(self, event_type, data, source):
        """Handler for worker stopped event."""
        final = data.get("final_count", 0)
        self.print(f"Worker stopped at count {final}")

    def on_system_init(self, event_type, data, source):
        """Handler for system init event."""
        self.print("System initialized")

    def on_system_resize(self, event_type, data, source):
        """Handler for terminal resize."""
        h = data.get("height", 0)
        w = data.get("width", 0)
        self.print(f"Terminal resized: {h}x{w}")

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    @callback(EventID, Keys.P)
    def emit_ping(self, *args, **kwargs):
        """P emits a ping event."""
        # Using self.emit_event() automatically sets source
        self.emit_event("ping", {"timestamp": time.time()})
        self.print("Emitted ping event")

    @callback(EventID, Keys.D)
    def emit_data(self, *args, **kwargs):
        """D emits a data event with payload."""
        payload = {
            "message": "Hello from event system!",
            "count": self.data_count + 1,
            "random": random.randint(1, 100)
        }
        self.emit_event("data", payload)
        self.print("Emitted data event")

    @callback(EventID, Keys.S)
    def start_worker(self, *args, **kwargs):
        """S starts the background worker."""
        if self.worker and self.worker.is_running:
            self.print("Worker already running")
            return
        
        # Create and start worker
        self.worker = SimpleWorker(self.app.events)
        self.worker.start()
        self.print("Worker started")

    @callback(EventID, Keys.X)
    def stop_worker(self, *args, **kwargs):
        """X stops the background worker."""
        if not self.worker or not self.worker.is_running:
            self.print("No worker running")
            return
        
        self.worker.stop()
        self.worker = None
        self.print("Stopping worker...")

    @callback(EventID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q exits the app."""
        # Clean up worker
        if self.worker and self.worker.is_running:
            self.worker.stop()
        
        self.logic.should_stop = True


if __name__ == "__main__":
    app = App(
        modules=[EventDemo],
        title="Event System",
        show_info=True,
    )
