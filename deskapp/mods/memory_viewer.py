"""
Memory Viewer Module for DeskApp.
Created by: Claude Sonnet 4.5 on 10/10/25
Proposal: 11_MemoryMonitoring_101025
Session 2 Step 1
Updated Session 3: Added GC trigger
"""

import random
import gc
from deskapp import Module, callback, Keys

MemoryViewer_ID = random.random()


class MemoryViewer(Module):
    """Display detailed memory usage statistics."""

    name = "Memory Viewer"

    def __init__(self, app):
        super().__init__(app, MemoryViewer_ID)
        self.refresh_rate = 1.0  # Update every second
        self.last_refresh = 0
        self.gc_message = ""  # For displaying GC results

    def page(self, panel):
        """Render memory statistics."""
        h, w = panel.dims[0], panel.dims[1]

        mem = self.app.memory.get_current()
        baseline = self.app.memory.baseline
        growth = self.app.memory.get_growth_mb()

        # Calculate MB values
        current_mb = mem["rss"] / (1024 * 1024)
        baseline_mb = baseline["rss"] / (1024 * 1024)

        # Color based on percentage
        if mem["percent"] < 50:
            color = self.front.color_green
        elif mem["percent"] < 80:
            color = self.front.color_yellow
        else:
            color = self.front.color_red

        # Display header
        y = 1
        if y < h - 1:
            panel.win.addstr(y, 2, "MEMORY USAGE",
                            self.front.color_cyan)
        y += 2

        # Current memory
        if y < h - 1:
            panel.win.addstr(y, 2, f"Current: {current_mb:.1f} MB",
                            color)
        y += 1

        # Baseline
        if y < h - 1:
            panel.win.addstr(y, 2, f"Baseline: {baseline_mb:.1f} MB",
                            self.front.color_white)
        y += 1

        # Growth
        if y < h - 1:
            growth_color = (self.front.color_green if growth < 5
                           else self.front.color_yellow if growth < 20
                           else self.front.color_red)
            panel.win.addstr(y, 2, f"Growth: {growth:+.1f} MB",
                            growth_color)
        y += 1

        # Percentage
        if y < h - 1:
            panel.win.addstr(y, 2, f"Percent: {mem['percent']:.1f}%",
                            color)
        y += 2

        # History graph (if available)
        if len(self.app.memory.history) > 1 and y < h - 2:
            panel.win.addstr(y, 2, "History (last 60s):",
                            self.front.color_cyan)
            y += 1
            self._render_graph(panel, y, 2, w - 4)
            y += 2

        # Additional stats
        if y < h - 1:
            panel.win.addstr(y, 2, "VMS: "
                            f"{mem['vms']/(1024*1024):.1f} MB",
                            self.front.color_white)
            y += 1

        # Samples collected
        if y < h - 1:
            samples = len(self.app.memory.history)
            panel.win.addstr(y, 2, f"Samples: {samples}/60",
                            self.front.color_white)
            y += 1

        # GC message if present
        if self.gc_message and y < h - 1:
            panel.win.addstr(y, 2, self.gc_message,
                            self.front.color_green)
            y += 1

        # Help text
        if y < h - 1:
            panel.win.addstr(y, 2, "Press 'G' to force GC",
                            self.front.color_cyan)

    def _render_graph(self, panel, y, x, width):
        """Render ASCII graph of memory history."""
        history = self.app.memory.history
        if len(history) < 2:
            return

        # Normalize to 0-10 range for display
        min_mem = min(history)
        max_mem = max(history)

        if max_mem == min_mem:
            return  # No variation

        # Sample history to fit width
        samples = min(len(history), width)
        step = len(history) / samples

        graph_line = ""
        for i in range(samples):
            idx = int(i * step)
            value = history[idx]
            normalized = (value - min_mem) / (max_mem - min_mem)
            height = int(normalized * 10)

            # Simple bar chart using characters
            if height < 3:
                graph_line += "▁"
            elif height < 5:
                graph_line += "▃"
            elif height < 7:
                graph_line += "▅"
            else:
                graph_line += "▇"

        try:
            panel.win.addstr(y, x, graph_line, self.front.color_cyan)
        except:
            pass

    def PageInfo(self, panel):
        """Display info panel."""
        mem = self.app.memory.get_current()
        is_leak, growth = self.app.memory.check_leak()

        h, w = panel.dims[0], panel.dims[1]

        # Line 1: Current memory
        line1 = f"Mem: {mem['rss']/(1024*1024):.1f}MB"
        panel.win.addstr(0, 1, line1[:w-2], self.front.color_white)

        # Line 2: Leak warning if detected
        if is_leak:
            line2 = f"LEAK: +{growth:.1f}MB/60s"
            panel.win.addstr(1, 1, line2[:w-2], self.front.color_red)

    @callback(MemoryViewer_ID, Keys.G)
    def force_gc(self, *args, **kwargs):
        """Force garbage collection on 'G' key."""
        # Get memory before GC
        mem_before = self.app.memory.get_current()['rss'] / (1024*1024)

        # Run garbage collection
        collected = gc.collect()

        # Get memory after GC
        mem_after = self.app.memory.get_current()['rss'] / (1024*1024)
        freed = mem_before - mem_after

        # Update message
        self.gc_message = (f"GC: Collected {collected} objects, "
                          f"freed {freed:.1f}MB")
        self.print(f"Garbage collection: {collected} objects, "
                  f"{freed:.1f}MB freed")
