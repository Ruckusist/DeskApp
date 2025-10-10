# Floating Panel Testing Guide

## CRITICAL FIX - 10/10/25
**Z-Order Issue Resolved**: Floating panel now correctly displays on top of ALL panels including main module panels. The `.top()` call was moved to the END of the render sequence to ensure proper overlay behavior.

## Updated Examples

### ex_refresh_test.py
**Updated by: Claude Sonnet 4.5 on 10/10/25**

Now includes floating confirmation dialog:
- Press `NUM9` to toggle floating panel
- When floating panel is visible, press `ENTER` to accept
- Dialog shows confirmation message and acceptance status

**Test Steps:**
1. Run: `python examples/ex_refresh_test.py`
2. Press `NUM9` to show floating panel (centered overlay)
3. Press `ENTER` to accept dialog
4. Press `NUM9` again to hide panel
5. Verify panel stays centered on resize

### ex_floating_test.py
**Created by: Claude Sonnet 4.5 on 10/09/25**

Comprehensive floating panel demo with three modes:
- **Menu Mode (M)**: Navigable popup menu with UP/DOWN/ENTER
- **Dialog Mode (D)**: Modal confirmation with Yes/No
- **Notification Mode (N)**: Simple notification overlay

**Test Steps:**
1. Run: `python examples/ex_floating_test.py`
2. Press `NUM9` to toggle floating panel
3. Press `M`, `D`, or `N` to switch modes
4. In menu mode: use UP/DOWN arrows to navigate
5. Press `ENTER` to select menu items
6. Verify overlay stays on top of all other panels

## Common Issues & Fixes

### Issue: Floating panel not showing
**Fix:** Make sure `show_floating=True` in App initialization, or press `NUM9` to toggle

### Issue: Panel not centered
**Fix:** The `make_floating_panel()` centers automatically. Check terminal size is sufficient (minimum 10x40)

### Issue: Content not rendering in PageFloat
**Fix:** Ensure module has `PageFloat(self, panel)` method defined and returns content

## How It Works

1. **curse.py**: `make_floating_panel()` creates centered overlay with boundary clamping
2. **backend.py**: `update_floating()` renders content, `.top()` ensures z-order
3. **module.py**: `PageFloat()` hook allows modules to provide custom content
4. **app.py**: NUM9 callback toggles `show_floating` state

## Key Bindings

- `NUM9`: Toggle floating panel visibility
- `NUM1-8`: Toggle other panels (header, footer, menu, etc.)
- `Q`: Quit application
- `Tab`: Enter text input mode

