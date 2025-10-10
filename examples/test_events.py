"""
Unit tests for DeskApp Event System
Tests EventBus functionality in isolation.

Created by: Claude Sonnet 4.5 on 10/10/25
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import threading
from deskapp.src.events import EventBus


def test_basic_emit_and_listen():
    """Test basic event emission and listener."""
    print("\n=== Test: Basic Emit and Listen ===")
    
    bus = EventBus()
    received = []
    
    def handler(event):
        received.append(event)
    
    bus.on('test.event', handler)
    bus.emit('test.event', {'value': 42}, source='test')
    bus.process_events()
    
    assert len(received) == 1
    assert received[0]['type'] == 'test.event'
    assert received[0]['data']['value'] == 42
    assert received[0]['source'] == 'test'
    print("✓ Basic emit/listen works")


def test_multiple_handlers():
    """Test multiple handlers for same event."""
    print("\n=== Test: Multiple Handlers ===")
    
    bus = EventBus()
    calls = []
    
    def handler1(event):
        calls.append('h1')
    
    def handler2(event):
        calls.append('h2')
    
    bus.on('multi.event', handler1)
    bus.on('multi.event', handler2)
    bus.emit('multi.event', {}, source='test')
    bus.process_events()
    
    assert len(calls) == 2
    assert 'h1' in calls
    assert 'h2' in calls
    print("✓ Multiple handlers work")


def test_handler_removal():
    """Test removing event handlers."""
    print("\n=== Test: Handler Removal ===")
    
    bus = EventBus()
    calls = []
    
    def handler(event):
        calls.append(1)
    
    bus.on('remove.event', handler)
    bus.emit('remove.event', {}, source='test')
    bus.process_events()
    assert len(calls) == 1
    
    bus.off('remove.event', handler)
    bus.emit('remove.event', {}, source='test')
    bus.process_events()
    assert len(calls) == 1  # Should not increment
    
    print("✓ Handler removal works")


def test_event_batching():
    """Test max_events batching."""
    print("\n=== Test: Event Batching ===")
    
    bus = EventBus()
    received = []
    
    def handler(event):
        received.append(event)
    
    bus.on('batch.event', handler)
    
    # Emit 20 events
    for i in range(20):
        bus.emit('batch.event', {'index': i}, source='test')
    
    # Process only 10
    processed = bus.process_events(max_events=10)
    assert processed == 10
    assert len(received) == 10
    
    # Process rest
    processed = bus.process_events(max_events=10)
    assert processed == 10
    assert len(received) == 20
    
    print("✓ Event batching works")


def test_thread_safety():
    """Test thread-safe event emission."""
    print("\n=== Test: Thread Safety ===")
    
    bus = EventBus()
    received = []
    
    def handler(event):
        received.append(event)
    
    bus.on('thread.event', handler)
    
    # Emit from multiple threads
    def worker(worker_id):
        for i in range(10):
            bus.emit('thread.event', {'worker': worker_id, 'i': i},
                    source=f'worker_{worker_id}')
            time.sleep(0.001)
    
    threads = [threading.Thread(target=worker, args=(i,))
               for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Process all events
    while bus.event_queue.qsize() > 0:
        bus.process_events(max_events=100)
    
    assert len(received) == 30  # 3 workers * 10 events
    print("✓ Thread safety works")


def test_error_handling():
    """Test handler exception handling."""
    print("\n=== Test: Error Handling ===")
    
    bus = EventBus()
    calls = []
    errors = []
    
    def bad_handler(event):
        calls.append('bad')
        raise ValueError("Intentional error")
    
    def good_handler(event):
        calls.append('good')
    
    def error_handler(event):
        errors.append(event['data']['error'])
    
    bus.on('error.event', bad_handler)
    bus.on('error.event', good_handler)
    bus.on('system.error', error_handler)
    
    bus.emit('error.event', {}, source='test')
    bus.process_events()
    
    # Both handlers should be called
    assert 'bad' in calls
    assert 'good' in calls
    
    # Error event should be emitted
    bus.process_events()  # Process the error event
    assert len(errors) > 0
    assert 'Intentional error' in errors[0]
    
    print("✓ Error handling works")


def test_metrics():
    """Test event bus metrics."""
    print("\n=== Test: Metrics ===")
    
    bus = EventBus()
    
    def handler(event):
        pass
    
    bus.on('metric.event', handler)
    
    for i in range(5):
        bus.emit('metric.event', {'i': i}, source='test')
    
    bus.process_events(max_events=3)
    
    metrics = bus.get_metrics()
    assert metrics['events_emitted'] == 5
    assert metrics['events_processed'] == 3
    assert metrics['queue_size'] == 2
    assert metrics['listener_count'] == 1
    
    print("✓ Metrics tracking works")
    print(f"  Metrics: {metrics}")


def test_queue_overflow():
    """Test queue overflow behavior."""
    print("\n=== Test: Queue Overflow ===")
    
    bus = EventBus(max_queue_size=10)
    
    # Emit more than max
    for i in range(15):
        result = bus.emit('overflow.event', {'i': i}, source='test')
        if i < 10:
            assert result is True  # Should succeed
        else:
            assert result is False  # Should drop
    
    metrics = bus.get_metrics()
    assert metrics['events_dropped'] == 5
    
    print("✓ Queue overflow handling works")


def run_all_tests():
    """Run all event bus tests."""
    print("=" * 60)
    print("DeskApp Event System Unit Tests")
    print("=" * 60)
    
    tests = [
        test_basic_emit_and_listen,
        test_multiple_handlers,
        test_handler_removal,
        test_event_batching,
        test_thread_safety,
        test_error_handling,
        test_metrics,
        test_queue_overflow
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
