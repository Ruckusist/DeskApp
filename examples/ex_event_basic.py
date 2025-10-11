"""
Basic Event System Example
Demonstrates app.emit(), app.on() for simple event communication.

Created by: Claude Sonnet 4.5 on 10/10/25
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from deskapp import App, Module, callback, Keys
import random

EventBasic_ID = random.random()


class EventBasic(Module):
    """Module demonstrating basic event system usage."""

    name = "Event Basic"

    def __init__(self, app):
        super().__init__(app, EventBasic_ID)
        self.event_log = []
        self.counter = 0

        # Register event listeners using module helpers
        self.on_event('test.ping', self.on_ping)
        self.on_event('test.data', self.on_data)
        self.on_event('system.error', self.on_error)

    def on_ping(self, event):
        """Handle ping events."""
        self.event_log.append(f"PING from {event['source']}")
        if len(self.event_log) > 10:
            self.event_log.pop(0)

    def on_data(self, event):
        """Handle data events."""
        data = event['data']
        self.event_log.append(
            f"DATA: {data.get('message', 'no message')}"
        )
        if len(self.event_log) > 10:
            self.event_log.pop(0)

    def on_error(self, event):
        """Handle error events."""
        self.event_log.append(f"ERROR: {event['data'].get('error', '')}")
        if len(self.event_log) > 10:
            self.event_log.pop(0)

    def page(self, panel):
        """Render main content."""
        self.index = 1
        self.counter += 1

        # Title
        self.write(panel, self.index, 2, "Event System Demo", "yellow")
        self.index += 2

        # Instructions
        self.write(panel, self.index, 2, "Controls:", "cyan")
        self.index += 1
        self.write(panel, self.index, 2, "  P: Emit ping event", "white")
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  D: Emit data event", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            "  E: Emit error event (test)", "white"
        )
        self.index += 2

        # Event metrics from app.data
        event_count = self.app.data.get('event_count', 0)
        queue_size = self.app.data.get('event_queue_size', 0)
        process_time = self.app.data.get('event_process_time', 0.0)

        self.write(
            panel, self.index, 2,
            "Event Metrics:", "cyan"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            f"  Processed this frame: {event_count}", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            f"  Queue size: {queue_size}", "white"
        )
        self.index += 1
        self.write(
            panel, self.index, 2,
            f"  Process time: {process_time:.3f}ms", "white"
        )
        self.index += 2

        # Event log
        self.write(panel, self.index, 2, "Recent Events:", "cyan")
        self.index += 1
        if not self.event_log:
            self.write(
                panel, self.index, 2,
                "  (no events yet)", "white"
            )
        else:
            for log in self.event_log[-10:]:
                if self.index >= self.h - 2:
                    break
                self.write(panel, self.index, 2, f"  {log}", "green")
                self.index += 1

    def PageInfo(self, panel):
        """Show event bus metrics in info panel."""
        metrics = self.app.events.get_metrics()

        line1 = (
            f"Events: {metrics['events_emitted']} emitted, "
            f"{metrics['events_processed']} processed"
        )
        line2 = (
            f"Queue: {metrics['queue_size']} | "
            f"Dropped: {metrics['events_dropped']}"
        )
        line3 = (
            f"Errors: {metrics['handler_errors']} | "
            f"Listeners: {metrics['listener_count']}"
        )

        try:
            maxw = max(0, panel.dims[1] - 4)
            panel.win.addstr(1, 2, line1[:maxw], self.front.color_cyan)
            panel.win.addstr(2, 2, line2[:maxw], self.front.color_green)
            panel.win.addstr(3, 2, line3[:maxw], self.front.color_yellow)
        except Exception:
            pass

    @callback(EventBasic_ID, keypress=Keys.P)
    def on_p(self, *args, **kwargs):
        """Emit ping event."""
        self.emit_event('test.ping', {})
        self.print("Emitted ping event")

    @callback(EventBasic_ID, keypress=Keys.D)
    def on_d(self, *args, **kwargs):
        """Emit data event."""
        self.emit_event(
            'test.data',
            {'message': f'Hello from frame {self.counter}'}
        )
        self.print("Emitted data event")

    @callback(EventBasic_ID, keypress=Keys.E)
    def on_e(self, *args, **kwargs):
        """Emit test error event."""
        self.emit_event(
            'system.error',
            {'error': 'This is a test error'}
        )
        self.print("Emitted error event")


if __name__ == "__main__":
    print("\n=== Event System Basic Example ===")
    print("Demonstrating app.emit() and app.on() usage")
    print("\nControls:")
    print("  P - Emit ping event")
    print("  D - Emit data event with message")
    print("  E - Emit error event")
    print("  Q - Quit\n")

    app = App(
        modules=[EventBasic],
        demo_mode=False,
        title="Event System Demo",
        show_box=True,
        show_info_panel=True,
        autostart=False
    )
    app.start()

    print("\nEvent system demo complete!")
