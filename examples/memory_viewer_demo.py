"""
Memory Viewer Demo - Proposal 11 Session 2 Test
Created by: Claude Sonnet 4.5 10-10-25

Demonstrates the MemoryViewer module with live memory tracking,
history graph, and leak detection capabilities.

Run this and watch the memory display update in real-time.
Press PgUp/PgDn to switch between About and MemoryViewer.
"""

from deskapp import App
from deskapp.mods.about import About
from deskapp.mods.memory_viewer import MemoryViewer


if __name__ == "__main__":
    app = App(
        modules=[About, MemoryViewer],
        title="Memory Viewer Demo",
        demo_mode=False,
        show_info_panel=True
    )
