# GitHub Copilot Instructions for DeskApp

## Project Overview

DeskApp is a terminal-first app framework for building rich TUI applications with composable modules. The framework includes multiplayer capabilities, chat systems, AWS integration, and a companion SideDesk runtime system.

### Core Architecture

- **`deskapp/src/`**: Framework core (App, Module, Backend, Curse, Logic)
- **`deskapp/mods/`**: Built-in modules (About, Buttons, Fire, etc.)
- **`deskapp/server/`**: Socket-based multiplayer server
- **`deskapp/deskchat/`**: Chat system with client/server components
- **`sidedesk/`**: AI-enabled companion runtime with Ollama integration
- **`deskapp/aws/`**: Cloud deployment utilities

## Critical Conventions ⚠️

### Code Style (STRICTLY ENFORCED)
- **79 character line limit** - absolutely enforced, fix violations immediately
- **4 spaces indentation** - never tabs
- **Double quotes** for strings - never single quotes
- **CamelCase** for functions and variables (NOT snake_case despite some existing code)
- **No leading underscores** on functions/variables
- **PascalCase** for classes

- Functions: `setup_mod()`, `should_stop`, `current_mod()`
- Variables: `show_header`, `user_modules`, `class_id`
- Files: `app.py`, `backend.py`, `module.py`

## Essential Architecture Patterns

### 1. App Initialization Pattern
```python
# Actual pattern from deskapp/src/app.py
app = App(
    modules=[Login, Status],
    demo_mode=False,  # True shows About/Buttons/Fire
    title="MyApp",
    show_header=True,
    disable_header=False,  # Prevents toggle
    v_split=0.4,  # Menu width ratio
    h_split=0.16,  # Message height ratio
    autostart=True  # False requires app.start()
)
```

### 2. Module System (CRITICAL PATTERN)
```python
# All modules inherit from Module and use random ID
import random
from deskapp import Module, callback, Keys

MyModule_ID = random.random()  # Unique callback namespace

class MyModule(Module):
    name = "Module Name"  # Required for UI

    def __init__(self, app):
        super().__init__(app, MyModule_ID)

    def page(self, panel):  # Main content rendering
        panel.win.addstr(1, 1, "Content", self.front.color_white)

    def PageRight(self, panel):  # Optional right panel
        panel.win.addstr(1, 1, "Right content")

    def PageInfo(self, panel):  # Optional info panel (3 lines)
        panel.win.addstr(1, 1, "Info line 1")

    @callback(MyModule_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("Module-specific handler")
```

### 3. Panel Management System
**Panel States**: All panels have `show_*` and `disable_*` flags
- `NUM1-8`: Toggle specific panels (header, footer, menu, main, messages, etc.)
- `NUM6`: Show all / hide all toggle
- Each panel respects its `disable_*` flag to prevent toggling

### 4. Callback Architecture
- Global callbacks use `ID=1` (app-level)
- Module callbacks use unique random IDs
- Callbacks stored in global `callbacks` list, processed by Backend.loop()

```python
@callback(ID=1, keypress=Keys.Q)  # Global quit
@callback(ModuleID, keypress=Keys.ENTER)  # Module-specific
```

## Development Workflow

### Project Focus & Boundaries
- **Work within**: `deskapp/` directory only
- **Never modify**: `.venv/` folder contents
- **Always credit**: Changes in file headers and `.github/changelog.ai`

### Proposal-Driven Development
1. **Create proposal** in `.github/proposals/` using pattern `IdeaTitle_MMDDYY.proposal`
2. **Start from clean state** - commit proposals before implementing
3. **Execute with checkboxes** - mark progress as you go
4. **Implementation follows** - update changelog and version

### Proposal File Format
```
IdeaTitle_MMDDYY
Last Updated: MM/DD/YY

Originating Prompt:
[user request here]

Interpretation:
[AI understanding of the request]

Full Proposal:
[ ] Actionable item 1
[ ] Actionable item 2
...
```

## Common Patterns to Follow

### Version Management
```python
# In pyproject.toml - always bump patch version
version = "0.1.12"  # Format: major.minor.patch
# Add comment explaining change:
# bumped to 0.1.13 by [AI] [date] [description]
```

### Message System
```python
# Prevent spam in app.print()
prev_message = self.data['messages'][-1] if len(self.data['messages']) > 0 else ""
if message != prev_message:
    self.data['messages'].append(message)
# Messages capped at 300 to prevent memory leaks
```

### Panel Bounds Checking
```python
# Always check bounds in drawing code
if x >= panel_height or y >= panel_width:
    return False
max_len = panel_width - y
text = string[:max_len] if len(string) > max_len else string
```

## CLI Entry Points & Configuration
```toml
# pyproject.toml defines these commands:
deskapp = "deskapp.__main__:main"
sidedesk = "sidedesk.__main__:main"
deskchat = "deskapp.deskchat.__main__:main"
deskapp-aws = "deskapp.aws.__main__:main"
```

### Key Dependencies
- `bcrypt` - Password hashing
- `boto3` - AWS integration
- `flask` - Web server
- `ollama` - AI integration (SideDesk)
- `chromadb` - Vector storage
- `mcp` - Model Context Protocol

## Critical Implementation Details

### Drawing Safety
- Use bounds checking: `if x >= h or y >= w: return`
- Truncate strings: `text = string[:max_width]`
- Wrap in try/except for terminal edge cases

### Module Integration
```python
# Adding modules to demo mode (app.py)
if self.show_demo:
    self.menu.extend([About, Buttons, Fire])

# SideDesk post-login pattern
app.data["post_login_modules"] = [Users, Chat, Ollama]
```

### Panel Layout Math
- Menu width: `app.v_split * total_width`
- Message height: `app.h_split * total_height`
- Right panel: `app.r_split * total_width`
- Always subtract panel widths from available space

## Debugging & Common Issues

### Demo Mode Gotcha
- `demo_mode=False` with empty `modules=[]` causes app failure
- Always provide at least one module or use demo_mode

### Terminal Compatibility
- Test across Linux, macOS, Windows terminals
- Handle resize events in Backend.loop()
- Mouse support optional (`use_mouse=True`)

### Key Mode System
- `TAB` toggles special input mode (`front.key_mode = True`)
- Footer shows when in key mode for text input
- `ENTER` processes input and exits key mode

# Instructions for GitHub Copilot
# copilot-instructions.md
# last updated: 10-5-25

Project Focus: Deskapp
Root folder: /home/ruckus/code/Deskapp
changelog: /home/ruckus/code/deskapp/.github/changelog.ai
proposals: /home/ruckus/code/deskapp/.github/proposals/
virtual environment: source .venv/bin/activate

-) Always credit your changes in the file and in the changelog.
-) we are focused on the hworld folder, do not suggest, or make changes outside of it.
-) we dont like _ at the beginning of function or variable names.
-) we use 4 spaces for indentation, never tabs.
-) we use CamelCase for function and variable names.
-) we keep everything to 79 characters per line.
-) we use double quotes for strings, never single quotes.
-) we prefer python classses.
-) we keep functions small and files small.
-) we think in a unix way.
-) we prefer building our own tools.
-) we work in complete sections. Do not leave half done code.
-) we always work from a plan.
-) keep all notes here in the .github folder, make new files if needed.

** RESPECT THE 80 CHARACTER LIMIT ** in all files. if you see it broken, fix it.

# Project Conventions
-) current workflow:
   1. create a proposal in .github/proposals/
   2. implement changes following project conventions
   3. update the changelog

-) Guidelines for Proposals
    - proposals should be numbered sequentially (Proposal 8, 10, 11, 12, etc.)
    - proposal numbers should match the feature/idea being implemented
    - keep a running list of proposal numbers to avoid conflicts
    - proposals should start every section with a checkbox.
    - proposals should be execututed using the checkboxes. mark them as you go.
    - proposals should be general and architectural.
    - proposals should not be about specific code changes.

-) Guidelines for Github
    - maintain all new proposals in commit. 1 commit per proposal.
    - always start to execute a proposal from an unchanged committed state.

-) new guidelines for .proposal files type.
    - should start every actionable item with a checkbox.
    - should be written with the intent to be executed by an AI agent.
    - filename pattern should be IdeaTitle_MMDDYY.proposal
    - first line should be IdeaTitle_MMDDYY
    - next should be the last updated review date.
    - skip a line.
    - next should be the originating prompt.
    - next should be the interpretation of the prompt.
    - skip a line
    - next should be the full proposal.

-) Guidelines for implementations
    - always credit your changes in the file and in the changelog.
    - always keep functions small and files small.
    - always use classes.
    - always use 4 spaces for indentation, never tabs.
    - always use double quotes for strings, never single quotes.
    - always use CamelCase for function and variable names.
    - never use _ at the beginning of function or variable names.
    - always keep everything to 79 characters per line.
    - always think in a unix way.
    - always prefer building our own tools.
    - always work in complete sections. Do not leave half done code.

-) Guidelines in general
    - always follow the above conventions.
    - leave the documentation to another bot. dont do it. just keep working.
    - always roll the version.
    - DONT EVER change a file in the venv folder. wtf.

