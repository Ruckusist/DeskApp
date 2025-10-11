<p align="center">
  <img src="./logo.png" alt="Deskapp Logo" width="180">
</p>

<h1 align="center">Deskapp</h1>
<p align="center">
  An open-source, terminal-first app framework and multiplayer server.<br/>
  Build rich TUI apps, games, and services — locally or over the network.
</p>

<p align="center">
  <!-- Core status badges -->
  <a href="https://github.com/Ruckusist/DeskApp/actions/workflows/ci.yml">
    <img alt="CI" src="https://github.com/Ruckusist/DeskApp/actions/workflows/ci.yml/badge.svg?branch=master" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/actions/workflows/codeql.yml">
    <img alt="CodeQL" src="https://github.com/Ruckusist/DeskApp/actions/workflows/codeql.yml/badge.svg?branch=master" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/releases">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/Ruckusist/DeskApp?display_name=tag" />
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
  <a href="https://github.com/Ruckusist/DeskApp">
    <img alt="Platforms" src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey" />
  </a>
  <a href="https://pre-commit.com/">
    <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" />
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img alt="code style ruff" src="https://img.shields.io/badge/code%20style-ruff-46aef7" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/security/dependabot">
    <img alt="Dependabot" src="https://img.shields.io/badge/dependabot-enabled-brightgreen?logo=dependabot" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/issues">
    <img alt="Issues" src="https://img.shields.io/github/issues/Ruckusist/DeskApp" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/pulls">
    <img alt="PRs" src="https://img.shields.io/github/issues-pr/Ruckusist/DeskApp" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/graphs/contributors">
    <img alt="Contributors" src="https://img.shields.io/github/contributors/Ruckusist/DeskApp" />
  </a>
  <a href="https://github.com/Ruckusist/DeskApp/commits/master">
    <img alt="Last commit" src="https://img.shields.io/github/last-commit/Ruckusist/DeskApp" />
  </a>
</p>

---

- Website: https://deskapp.org
- PyPI: https://pypi.org/project/deskapp/ (when published)

<details>
  <summary><strong>Table of contents</strong></summary>

- Overview
- Features
- Installation
- Quickstart
- CLI entry points
- Examples
- Architecture
- Roadmap & ideas
- Known issues
- Contributing
- Security policy
- License

</details>

## Overview
Deskapp is a pythonic framework for building terminal user interfaces (TUIs) plus a lightweight multiplayer server for real-time, multi-user apps and games. Compose interfaces, connect clients over sockets, and ship cross-platform terminal apps.

> [!TIP]
> Looking for a starting point? Check the Quickstart below and the examples/ folder.

## Features
- Terminal-first UI framework with composable modules
- Multiplayer-friendly socket server (login, messaging, compression/encryption)
- Multiple CLI tools out of the box: `deskapp`, `sidedesk`, `deskchat`, `deskapp-aws`
- Works on Linux, macOS, and Windows (via modern terminals)
- Modern developer experience: pre-commit, Ruff lint/format, CI, CodeQL, Dependabot

## Installation
Install with pip:

```bash
pip install deskapp
```

Or install from source (editable):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

## Quickstart
Run the main app:

```bash
deskapp
```

**Try the tutorials!** Learn DeskApp in ~2 hours with our step-by-step
examples:

```python
# Your first DeskApp in 20 lines
from deskapp import App, Module, callback, Keys
import random

HelloID = random.random()

class Hello(Module):
    name = "Hello"
    
    def __init__(self, app):
        super().__init__(app, HelloID)
    
    def page(self, panel):
        panel.win.addstr(2, 2, "Hello, DeskApp!", 
                        self.front.color_white)
    
    @callback(HelloID, Keys.Q)
    def quit(self, *args, **kwargs):
        self.logic.should_stop = True

if __name__ == "__main__":
    app = App(modules=[Hello], title="Hello World")
```

**Next steps**: See [examples/README.md](examples/README.md) for the
complete tutorial series (00_hello.py through 08_complete_app.py).

## CLI entry points
- `deskapp` — launch the primary Deskapp runtime
- `sidedesk` — companion launcher/runtime for side modules
- `deskchat` — chat client/server utilities bundled with Deskapp
- `deskapp-aws` — AWS-related utilities and integration helpers

> [!NOTE]
> Entry points are defined in pyproject.toml and setup.py; install the package to make them available globally.

## Examples
Browse the examples folder for progressively more complex samples.

**📚 Tutorial Series** (Start here!):
- **00_hello.py** - Minimal "Hello World" (5 min)
- **01_panels.py** - Panel system tour (10 min)
- **02_module.py** - Module basics (15 min)
- **03_callbacks.py** - Event handling (15 min)
- **04_layouts.py** - Split ratios & resizing (10 min)
- **05_styling.py** - Colors & formatting (10 min)
- **06_data_sharing.py** - Module communication (15 min)
- **07_events.py** - Event system & workers (20 min)
- **08_complete_app.py** - Full application (30 min)

**Total**: ~2 hours from beginner to production-ready apps!

See [examples/README.md](examples/README.md) for the complete learning
path with detailed explanations.

**Additional Examples**:
- **ex_fps_test.py** - FPS tracking demo
- **ex_floating_test.py** - Floating panel overlay
- **ex_event_basic.py** - Event system basics
- **ex_async_fetch.py** - Advanced async patterns
- **deskhunter.py** - Complete game example
- **THREADING.md** - Threading guide

**Legacy Examples**:

```bash
python examples/ex_0.py   # sanity check
python examples/ex_1.py   # basic printing
python examples/ex_2.py   # horizontal scroller
python examples/ex_3.py   # Arduino-style event loop
python examples/ex_4.py   # minimal game (Math_Game)
```
python examples/ex_5.py   # server + deskapp user profile demo (WIP)
```

## Architecture
- Server: Python socket server that supports login, messaging, compression/encryption and multi-user sessions.
- Web connector: planned web server and JS client library to connect to the server.
- Client modules: desktop terminal apps built on the Deskapp framework.

## Roadmap & ideas
- Games: Desklike, DeskHunter, Desk2042, DeskType, DeskShip, DeskSnake (in progress), DeskFortress
- Apps: Linux Builder, Bitcoin Trader, MP3 Player/Organizer, RoboDog, Deskapt (apt frontend)
- New functionality: regex-based callbacks, robust interrupt/event system for server crashes, enhanced mouse support, streamlined redraw logic

### TODO
- [x] Unify the printing mechanism
- [ ] Refresh examples with a login-page-based example
- [ ] Add a web sub-module to render Deskapp in a browser
- [ ] Use pop-up warnings in a demo to evaluate usability
- [ ] Add functional shortcuts for all module features
- [ ] Improve mouse handling and screen redraw logic
- [ ] Reproduce Deskapp in other programming languages
- [ ] Stream development on Twitch and create tutorials for YouTube

## Known issues
- Starting a blank app with only demo mode turned off results in no modules being loaded, causing the decider to fail.

## Changelog
See GitHub Releases for human-friendly notes: https://github.com/Ruckusist/DeskApp/releases

<details>
  <summary>Historic notes</summary>

- 6.10.23 — Reassembling the onefile back into a One.0 version.
- 3.11.23 — Deskapp.org is now live.
- 3.11.23 — Lannocc v0.0.12: Live terminal resizing now works.
- 3.11.23 — Lannocc v0.0.11: Fixed sizing issues.
- 3.11.23 — Ruckusist v0.0.10: Stabilized onefile before transitioning to multifile for 1.0.
- 3.5.23 — Lannocc v0.0.9: Fixed a sizing anomaly.
- 11.11.22 — Added the server module.
- 11.11.22 — Added mouse support and refactored previous updates.
- 7.26.22 — Transition release with new functionality and bugs.
- 4.20.22 — Started working on version 4.
- 4.6.22 — Added `demo_mode` flag to the App object.

</details>

## Contributing
See CONTRIBUTING: .github/CONTRIBUTING.md

Set up dev tools and pre-commit hooks:

```bash
pip install -e .
pip install pre-commit ruff
pre-commit install
pre-commit run -a
```

## Security policy
Please report vulnerabilities responsibly. See SECURITY: .github/SECURITY.md

## License
MIT — see LICENSE.txt
