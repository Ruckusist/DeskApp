# GitHub Copilot Instructions for DeskApp

## Project Overview

DeskApp is an open-source, terminal-first app framework and multiplayer server for building rich TUI (Terminal User Interface) applications, games, and services. The project enables developers to create cross-platform terminal applications that can run locally or over the network with real-time multiplayer capabilities.

### Key Architecture Components

- **Framework Core**: Terminal UI framework with composable modules (`deskapp/src/`)
- **Server System**: Socket-based multiplayer server with authentication (`deskapp/server/`)
- **Chat System**: Real-time messaging capabilities (`deskapp/deskchat/`)
- **AWS Integration**: Cloud deployment utilities (`deskapp/aws/`)
- **SideDesk**: Companion runtime system (`sidedesk/`)
- **Web Interface**: Planned web connectivity (`deskapp/webapp/`)

## Code Style and Standards

### Python Standards
- **Python Version**: Minimum Python 3.8+ (target compatibility)
- **Formatter**: Use Ruff for code formatting (configured in `pyproject.toml`)
- **Linting**: Follow Ruff rules: E, F, I, B, UP, S (pycodestyle, pyflakes, isort, bugbear, pyupgrade, bandit)
- **Line Length**: Maximum 100 characters
- **Quote Style**: Double quotes preferred
- **Imports**: Use isort-compliant import ordering

### Naming Conventions
- **Classes**: PascalCase (e.g., `App`, `Backend`, `Module`)
- **Functions/Methods**: snake_case (e.g., `setup_mod`, `should_stop`)
- **Variables**: snake_case (e.g., `show_header`, `user_modules`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `COMMAND_KEYS`)
- **Files**: snake_case.py (e.g., `app.py`, `backend.py`)

### File Organization
```
deskapp/
├── __init__.py           # Package initialization
├── __main__.py           # CLI entry point
├── src/                  # Core framework code
│   ├── app.py           # Main App class
│   ├── backend.py       # Backend logic
│   ├── curse.py         # Terminal interface
│   ├── logic.py         # Business logic
│   └── module.py        # Module base class
├── mods/                # Built-in modules
├── server/              # Multiplayer server
├── deskchat/           # Chat system
├── aws/                # AWS integrations
└── webapp/             # Web interface
```

## Framework Patterns

### App Initialization Pattern
```python
class App:
    def __init__(self,
                 modules: list = [],
                 demo_mode: bool = True,
                 title: str = "Deskapp",
                 # ... panel controls
                 show_header: bool = True,
                 disable_header: bool = False,
                 # ... other options
                ):
        # Initialize with sensible defaults
        # Setup core modules: Curse, Logic, Backend
        # Auto-start if configured
```

### Module Development Pattern
- All modules should inherit from the base `Module` class
- Modules are self-contained with their own logic and rendering
- Use the callback decorator system for key bindings
- Follow the composable architecture pattern

### Callback System Pattern
```python
@callback(ID=1, keypress=Keys.TAB)
def on_tab(self, *args, **kwargs):
    # Handle key events
    self.print("Tab pressed")
```

## Development Guidelines

### When Adding New Features
1. **Maintain Backward Compatibility**: Don't break existing module APIs
2. **Terminal-First Design**: Prioritize terminal UX over other interfaces
3. **Modular Architecture**: New features should be modular and composable
4. **Cross-Platform**: Ensure compatibility with Linux, macOS, and Windows terminals
5. **Performance**: Keep the main rendering loop responsive

### Error Handling
- Use the built-in `app.error()` and `app.print()` methods for user feedback
- Graceful degradation for optional features
- Proper exception handling in network operations
- Log errors to the message system for user visibility

### Testing Considerations
- Test terminal rendering across different terminal emulators
- Verify keyboard input handling works correctly
- Test multiplayer functionality with multiple clients
- Ensure AWS integration doesn't break without credentials

## CLI Entry Points
Maintain these CLI commands as defined in `pyproject.toml`:
- `deskapp` → `deskapp.__main__:main`
- `sidedesk` → `sidedesk.__main__:main`
- `deskchat` → `deskapp.deskchat.__main__:main`
- `deskapp-aws` → `deskapp.aws.__main__:main`

## Dependencies and Imports
### Core Dependencies
- `passlib` - Password hashing for authentication
- `boto3` - AWS services integration
- `flask` - Web server capabilities

### Internal Import Structure
```python
from deskapp import Curse, Logic, Backend, Module, Keys, callback
from deskapp.mods import About, Buttons, Fire  # Built-in modules
```

## Security Considerations
- Always use proper password hashing (passlib)
- Validate user inputs in network operations
- Secure socket communications
- Follow bandit security linting recommendations
- Be cautious with AWS credentials and permissions

## Performance Guidelines
- Keep the main rendering loop under 60fps for smooth experience
- Minimize I/O operations in the render cycle
- Use efficient terminal drawing techniques
- Cache computed values when possible
- Limit message history to prevent memory leaks (current limit: 300 messages)

## Documentation Standards
- Include docstrings for all public methods and classes
- Document complex algorithms and business logic
- Keep README.md updated with new features
- Use type hints where beneficial for clarity
- Comment keyboard shortcuts and their purposes

## Common Patterns to Follow

### Panel Management
```python
# Standard panel visibility toggles
self.app.back.show_header = not self.app.back.show_header
self.print(f"show_header = {self.app.back.show_header}")
```

### Message Handling
```python
# Prevent message spam
prev_message = self.data['messages'][-1] if len(self.data['messages']) > 0 else ""
if message != prev_message:
    self.data['messages'].append(message)
```

### Module Integration
```python
# Adding new modules
if self.show_demo:
    self.menu.extend([About, Buttons, Fire])
```

## Roadmap Awareness
Be aware of planned features when making changes:
- **Games**: DeskSnake, Desk2042, DeskType, etc.
- **Web Integration**: Browser-based client connectivity
- **Enhanced Mouse Support**: Improved mouse handling
- **Regex Callbacks**: Pattern-based event handling
- **Cross-Language Ports**: Maintaining API compatibility

## Common Gotchas
- **Demo Mode**: When `demo_mode=False` and no modules provided, the app may fail to start
- **Terminal Resizing**: Handle terminal resize events properly
- **Key Mode**: Tab key toggles special input mode - handle this state carefully
- **Message Limits**: Messages are capped at 300 to prevent memory issues
- **Panel Dependencies**: Some panels depend on others being visible

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

