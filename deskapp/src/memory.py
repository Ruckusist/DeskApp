"""
Memory tracking utility for DeskApp.
Created by: Claude Sonnet 4.5 on 10/10/25
Proposal: 11_MemoryMonitoring_101025
Session 1 Step 2
"""

import psutil
import os
import time


class MemoryTracker:
    """Track application memory usage over time."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.baseline = self.get_current_raw()
        self.history = []
        self.last_update = time.time()

    def get_current_raw(self):
        """Get raw memory info dict."""
        mem = self.process.memory_info()
        return {
            "rss": mem.rss,  # Resident Set Size (actual RAM)
            "vms": mem.vms,  # Virtual Memory Size
            "percent": self.process.memory_percent()
        }

    def get_current(self):
        """Get current memory and update history."""
        current = self.get_current_raw()

        # Update history (max 60 samples)
        now = time.time()
        if now - self.last_update >= 1.0:  # Sample every second
            self.history.append(current["rss"])
            if len(self.history) > 60:
                self.history.pop(0)
            self.last_update = now

        return current

    def get_formatted(self):
        """Get formatted memory string for display."""
        mem = self.get_current()
        mb = mem["rss"] / (1024 * 1024)
        return f"{mb:.1f}MB ({mem['percent']:.1f}%)"

    def get_growth_mb(self):
        """Get memory growth since baseline in MB."""
        current = self.get_current()
        growth = (current["rss"] - self.baseline["rss"]) / (1024 * 1024)
        return growth

    def check_leak(self):
        """
        Check for potential memory leak.
        Returns: (is_leak: bool, growth_mb: float)
        """
        if len(self.history) < 60:
            return False, 0.0

        # Check growth over last 60 samples (60 seconds)
        oldest = self.history[0]
        newest = self.history[-1]
        growth = (newest - oldest) / (1024 * 1024)

        # Threshold: 10 MB growth in 60 seconds
        is_leak = growth > 10.0
        return is_leak, growth
