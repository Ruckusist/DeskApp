# DeskApp Threading & Event System Guide

## Overview

DeskApp v0.1.22+ includes a robust event system and threading model for background tasks. This guide explains the architecture, patterns, and best practices.

## Architecture

### Event-Driven Model

```
┌─────────────┐
│   Workers   │ (Background Threads)
│   Threads   │
└──────┬──────┘
       │ emit events
       │ (thread-safe queue)
       ▼
┌─────────────┐
│  EventBus   │ (Queue + Listeners)
└──────┬──────┘
       │ process_events()
       │ (main thread only!)
       ▼
┌─────────────┐
│   Modules   │ (Event Handlers)
│   + UI      │
└─────────────┘
```

### Critical Rules

1. **ALL curses operations MUST happen on main thread**
   - Drawing, panels, windows, colors, input
   - Workers NEVER touch curses directly

2. **Workers communicate via events ONLY**
   - Use `worker.emit(event_type, data)`
   - Main loop calls `app.events.process_events()`
   - Event handlers update UI safely

3. **Event processing is bounded**
   - Max 10 events/frame (prevents UI stutter)
   - Max 5ms processing time/frame
   - Overflow protection (1000 event queue)

## Event System API

### Emitting Events

```python
# From app or module
app.emit('custom.event', {'key': 'value'}, source='MyModule')

# From module (auto-source)
self.emit_event('data.update', {'value': 42})

# From worker thread (thread-safe)
worker.emit('task.complete', {'result': data})
```

### Listening to Events

```python
# In module __init__
self.on_event('custom.event', self.handle_event)

def handle_event(self, event):
    data = event['data']
    source = event['source']
    timestamp = event['timestamp']
    # Update UI here (we're in main thread!)
```

### Event Structure

```python
{
    'type': 'custom.event',     # Event identifier
    'source': 'MyModule',        # Originating module/worker
    'data': {'key': 'value'},    # Arbitrary payload
    'timestamp': 1633024800.0    # time.time()
}
```

## System Events

DeskApp emits standard system events:

| Event | When | Data |
|-------|------|------|
| `system.init` | After module setup | `{'module_count', 'terminal_size'}` |
| `system.shutdown` | Before app exit | `{}` |
| `system.resize` | Terminal resized | `{'width', 'height'}` |
| `system.fps_update` | Every second | `{'fps', 'frame_time'}` |
| `system.error` | Handler exception | `{'error', 'handler', ...}` |

## Worker Thread Pattern

### Basic Worker

```python
from deskapp.src.worker import BaseWorker

class MyWorker(BaseWorker):
    def work(self):
        while not self.should_stop:
            # Do background work
            result = expensive_operation()

            # Emit event for UI update
            self.emit('work.done', {'result': result})

            # Sleep to avoid busy-wait
            time.sleep(1.0)

# In module
worker = MyWorker(app, name="MyWorker")
worker.start()

# Later, clean shutdown
worker.stop(timeout=2.0)
```

### Built-In Workers

**CounterWorker** - Periodic counter
```python
from deskapp.src.worker import CounterWorker

counter = CounterWorker(app, interval=1.0)
counter.start()
# Emits 'counter.tick' every second
```

**TimerWorker** - One-shot timer
```python
from deskapp.src.worker import TimerWorker

timer = TimerWorker(app, delay=5.0, event_type='timer.done')
timer.start()
# Emits 'timer.done' after 5 seconds
```

**PeriodicWorker** - Periodic callback
```python
from deskapp.src.worker import PeriodicWorker

def poll_data():
    return check_server_status()

poller = PeriodicWorker(app, interval=10.0, callback=poll_data)
poller.start()
# Calls poll_data() every 10 seconds
```

## Complete Example

### Module with Worker

```python
from deskapp import App, Module, callback, Keys
from deskapp.src.worker import BaseWorker
import random

class DataWorker(BaseWorker):
    def work(self):
        count = 0
        while not self.should_stop:
            count += 1
            self.emit('data.ready', {'count': count})
            time.sleep(2.0)

class MyModule(Module):
    name = "Worker Demo"

    def __init__(self, app):
        super().__init__(app, random.random())
        self.data_count = 0
        self.worker = None

        # Listen for events
        self.on_event('data.ready', self.on_data)

    def on_data(self, event):
        # This runs in MAIN thread - safe to update UI vars
        self.data_count = event['data']['count']

    def page(self, panel):
        # Render UI using worker data
        self.write(panel, 1, 2, f"Count: {self.data_count}", "cyan")

    @callback(ID, keypress=Keys.S)
    def on_s(self, *args, **kwargs):
        # Start worker
        if not self.worker:
            self.worker = DataWorker(self.app, name="DataWorker")
            self.worker.start()

    def end_safely(self):
        # Clean shutdown
        if self.worker:
            self.worker.stop()
        super().end_safely()
```

## Performance Considerations

### Event Queue Limits

- **Queue Size**: 1000 events max
- **Processing**: 10 events/frame, 5ms max
- **Overflow**: Drops oldest events with warning

### Monitoring

```python
# In your module
metrics = self.app.events.get_metrics()
print(f"Queue size: {metrics['queue_size']}")
print(f"Events dropped: {metrics['events_dropped']}")
print(f"Process time: {metrics['last_process_time_ms']}ms")
```

### Best Practices

1. **Keep event handlers fast** (< 1ms each)
2. **Batch updates** (don't emit per-byte, emit per-chunk)
3. **Use worker sleep** (avoid busy-waiting)
4. **Clean shutdown** (call `worker.stop()` in `end_safely()`)

## Common Patterns

### Progress Updates

```python
# Worker
for i in range(100):
    progress = (i + 1) / 100 * 100
    self.emit('task.progress', {'progress': progress})
    do_work(i)

# Module handler
def on_progress(self, event):
    self.progress_pct = event['data']['progress']
```

### Error Handling

```python
# Worker
try:
    result = risky_operation()
    self.emit('task.complete', {'result': result})
except Exception as e:
    self.emit('task.error', {'error': str(e)})

# Module handler
def on_error(self, event):
    error_msg = event['data']['error']
    self.print(f"Error: {error_msg}")
```

### Multi-Step Process

```python
# Worker
self.emit('process.started', {})
step1_result = do_step1()
self.emit('process.step', {'step': 1, 'result': step1_result})
step2_result = do_step2(step1_result)
self.emit('process.step', {'step': 2, 'result': step2_result})
self.emit('process.complete', {'final': step2_result})
```

## Debugging

### Event Debug Mode

```python
# Enable event logging
app.emit('debug.event', {'message': 'checkpoint'})

# Monitor event flow
def debug_handler(event):
    print(f"Event: {event['type']} from {event['source']}")
app.on('*', debug_handler)  # Not yet implemented, but planned
```

### Common Issues

**Issue**: UI not updating from worker
- **Cause**: Worker touching curses directly
- **Fix**: Emit event, update UI in handler

**Issue**: Events getting dropped
- **Cause**: Queue overflow (>1000 events)
- **Fix**: Reduce event emission rate or batch

**Issue**: UI stuttering
- **Cause**: Event handlers taking too long
- **Fix**: Move heavy work to worker, keep handlers light

## Backward Compatibility

The event system is **100% optional**. Existing modules work without changes:
- Don't use events? No problem.
- No worker threads? Nothing changes.
- Pure rendering modules? Still work perfectly.

Only opt-in when you need background tasks or inter-module communication.

## Examples

See these examples for complete patterns:

- `examples/test_events.py` - Event bus unit tests
- `examples/ex_event_basic.py` - Basic event emission/listening
- `examples/ex_worker_test.py` - Worker thread basics
- `examples/ex_async_fetch.py` - Advanced async pattern

## Summary

**Event System** = Thread-safe communication bus
**Workers** = Background threads that emit events
**Main Loop** = Processes events, updates UI (single-threaded)
**Result** = Non-blocking, responsive, safe TUI apps

---

*Created by: Claude Sonnet 4.5 on 10/10/25*
*Updated for DeskApp v0.1.22+*
