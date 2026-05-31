<p align="center">
  <img src="./logo.png" alt="Deskapp Logo" width="180">
</p>

<h1 align="center">Deskapp</h1>
<p align="center">
  An open-source terminal application framework for Python.<br/>
  Build composable TUI apps with a module system, event bus, and key binding.
</p>

<p align="center">
  <a href="https://github.com/Ruckusist/DeskApp/actions/workflows/ci.yml">
    <img alt="CI" src="https://github.com/Ruckusist/DeskApp/actions/workflows/ci.yml/badge.svg?branch=master" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/blob/master/LICENSE.txt">
    <img alt="License" src="https://img.shields.io/github/license/Ruckusist/DeskApp" />
  </a>
  <a href="https://pypi.org/project/deskapp/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/deskapp?logo=pypi" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp">
    <img alt="Python version" src="https://img.shields.io/badge/python-%3E%3D3.8-blue" />
  </a>
</p>

---

- Website: https://deskapp.org
- PyPI: https://pypi.org/project/deskapp/

## Overview

Deskapp is a Python TUI framework built on curses. It handles terminal
rendering, panel layout, input routing, and event dispatch. You write
modules; Deskapp runs them.

The core pattern is: subclass `Module`, implement `page(panel)` to draw,
use `@callback` to bind keys, pass your modules to `App`.

## Installation

```bash
pip install deskapp
```

Or install from source:

```bash
pip install -e .
```

## Quickstart

```bash
deskapp
```

```python
from deskapp import App, Module, callback, Keys
import random

HelloID = random.random()

class Hello(Module):
    name = "Hello"

    def __init__(self, app):
        super().__init__(app, HelloID)

    def page(self, panel):
        panel.win.addstr(2, 2, "Hello, DeskApp!", self.front.color_white)

    @callback(HelloID, Keys.Q)
    def quit(self, *args, **kwargs):
        self.logic.should_stop = True

if __name__ == "__main__":
    App(modules=[Hello], title="Hello World")
```

## Core API

- `App(modules, title, ...)` — initialize and run the framework
- `Module` — base class for all app content; implement `page(panel)`
- `@callback(module_id, key)` — bind a key to a method
- `Keys` — enum of key codes: `Keys.UP`, `Keys.ENTER`, `Keys.Q`, etc.
- `self.write(panel, row, col, text)` — bounds-safe text rendering
- `self.emit_event(type, data)` / `self.on_event(type, handler)` — event bus
- `self.app.data` — shared state dict across modules

## Examples

The `examples/` folder contains a tutorial series and additional demos.

Tutorial series (work through in order):
- `00_hello.py` — minimal app
- `01_panels.py` — panel layout
- `02_module.py` — module basics
- `03_callbacks.py` — key binding
- `04_layouts.py` — split ratios and resizing
- `05_styling.py` — colors
- `06_data_sharing.py` — module-to-module communication
- `07_events.py` — event system and background workers
- `08_complete_app.py` — full application

Additional:
- `ex_fps_test.py`, `ex_floating_test.py`, `ex_event_basic.py`
- `ex_async_fetch.py`, `deskhunter.py` (game example)
- `THREADING.md` — threading guide

## Known Issues

- Starting with demo mode off and no modules loaded causes the decider to fail.

## Contributing

```bash
pip install -e .
pip install pre-commit ruff
pre-commit install
pre-commit run -a
```

## License

MIT — see LICENSE.txt
