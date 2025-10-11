# DeskApp Examples - Learning Path

Welcome to the DeskApp tutorial series! These examples will teach you
everything you need to build powerful terminal applications.

## What is DeskApp?

DeskApp is a terminal-first framework for building rich TUI (Text User
Interface) applications with composable modules. Think of it as a
framework for creating interactive command-line tools with multiple
screens, background tasks, and real-time updates.

## What You'll Learn

By following these tutorials in order, you'll master:

- **Module system** - Creating reusable UI components
- **Panel layouts** - Managing multiple display areas
- **Event handling** - Responding to keyboard and mouse input
- **Styling** - Using colors and formatting
- **Data sharing** - Communication between modules
- **Event system** - Async operations with workers
- **Production patterns** - Building complete applications

## Learning Path

### Beginner (Start Here!)

**00_hello.py** - The Absolute Minimum (5 minutes)
- Your first DeskApp in 20 lines
- Basic module structure
- Single callback (Q to quit)
- **Run**: `python examples/00_hello.py`

**01_panels.py** - Panel System Tour (10 minutes)
- All 8 panel types explained
- Panel toggling (NUM1-9)
- PageRight() and PageInfo() hooks
- Panel visibility controls
- **Run**: `python examples/01_panels.py`

**02_module.py** - Creating Custom Modules (15 minutes)
- Module base class deep-dive
- The page() rendering hook
- @callback decorator usage
- Module properties (h, w, name)
- Element scroller pattern
- **Run**: `python examples/02_module.py`

### Intermediate (Core Skills)

**03_callbacks.py** - Event Handling Deep-Dive (15 minutes)
- Keyboard callbacks (all key types)
- Multiple handlers per key
- String input mode (TAB key)
- Callback argument passing
- **Run**: `python examples/03_callbacks.py`

**04_layouts.py** - Split Ratios & Resizing (10 minutes)
- v_split, h_split, r_split explained
- Dynamic layout changes
- Terminal resize handling
- Responsive design patterns
- **Run**: `python examples/04_layouts.py`

**05_styling.py** - Colors & Formatting (10 minutes)
- Color system (9 colors)
- Text formatting with colors
- Border and banner options
- Panel clearing and refresh
- **Run**: `python examples/05_styling.py`

### Advanced (Professional Patterns)

**06_data_sharing.py** - Module Communication (15 minutes)
- app.data dictionary usage
- Sharing state between modules
- Module switching (PgUp/PgDn)
- Message passing patterns
- **Run**: `python examples/06_data_sharing.py`

**07_events.py** - Event System Tutorial (20 minutes)
- Event emission with app.emit()
- Event listeners with app.on()
- System events (resize, fps_update, etc.)
- Worker thread pattern
- Error handling
- **Run**: `python examples/07_events.py`

**08_complete_app.py** - Full Application (30 minutes)
- Multi-module navigation
- Background data fetching
- Progress updates
- Interactive task list
- Professional error handling
- Clean shutdown
- **Run**: `python examples/08_complete_app.py`

## Quick Reference Table

| Example | Concepts Covered | Difficulty | Time |
|---------|-----------------|------------|------|
| 00_hello.py | Module, Callback, Minimal app | Beginner | 5m |
| 01_panels.py | Panels, Layout, Toggling | Beginner | 10m |
| 02_module.py | Module API, Rendering, State | Beginner | 15m |
| 03_callbacks.py | Events, Input, String mode | Medium | 15m |
| 04_layouts.py | Splits, Resize, Responsive | Medium | 10m |
| 05_styling.py | Colors, Formatting, Visual | Medium | 10m |
| 06_data_sharing.py | Data flow, Multi-module | Advanced | 15m |
| 07_events.py | Event system, Workers, Async | Advanced | 20m |
| 08_complete_app.py | Full app, Production patterns | Advanced | 30m |

**Total Learning Time**: ~2 hours for complete mastery

## Running Examples

All examples are standalone and can be run directly:

```bash
# From DeskApp root directory
python examples/00_hello.py

# Or with module syntax
python -m examples.00_hello
```

## Additional Examples

Beyond the tutorial series, the `examples/` folder contains:

**Feature Demonstrations**:
- **ex_fps_test.py** - FPS tracking demonstration
- **ex_floating_test.py** - Floating panel overlay
- **ex_refresh_test.py** - Panel refresh testing
- **ex_event_basic.py** - Basic event system (alternative)
- **ex_worker_test.py** - Worker thread patterns
- **ex_async_fetch.py** - Advanced async operations
- **deskhunter.py** - Complete game example
- **THREADING.md** - Comprehensive threading guide

**Legacy Examples** (older format):
- **ex_0.py** - Sanity check / minimal example
- **ex_1.py** - Basic screen printing
- **ex_2.py** - Horizontal scroller
- **ex_3.py** - Arduino-style event loop pattern
- **ex_4.py** - Math game (class-based architecture)
- **ex_right_info.py** - Panel demonstration

## Common Issues & Solutions

### "Module not found" error
Make sure you're in the DeskApp root directory and the package is
installed:
```bash
pip install -e .
```

### Terminal too small warning
DeskApp needs at least 24 lines x 80 columns. Resize your terminal
window or use a smaller font.

### Colors not showing
Your terminal must support ANSI color codes. Most modern terminals do.
Try a different terminal emulator if colors don't work.

### Background workers not stopping
Always call `worker.stop()` in your quit callback to ensure clean
shutdown. See 07_events.py and 08_complete_app.py for examples.

## Next Steps

After completing the tutorials:

1. **Read THREADING.md** - Deep-dive into worker patterns
2. **Study deskapp/mods/** - Real production modules
3. **Build your own app** - Start with 00_hello.py as template
4. **Check main README.md** - Installation and deployment guides

## Contributing Examples

Have a great example to share? Add it to `examples/` following the
pattern:
- Clear docstring explaining the concept
- Inline comments for every non-obvious line
- < 150 lines for focused teaching
- Follows 79-character line limit
- Uses double quotes for strings

## Need Help?

- Check the main README.md for installation help
- Read THREADING.md for event system details
- Look at existing modules in deskapp/mods/
- Study the source code in deskapp/src/

Happy coding! 🚀

---
Updated: 10/10/25 by Claude Sonnet 4.5