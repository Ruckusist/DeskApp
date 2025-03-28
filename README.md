<p align="center">
  <img src="./logo.png" alt="Deskapp Logo">
</p>

<h1 align="center">Deskapp.org</h1>

## Installation

Install Deskapp using pip:

```bash
pip install deskapp
```

## Running Deskapp

Run the application from the console:

```bash
deskapp
```

## Ideas for Games

- Desklike
- DeskHunter
- Desk2042
- DeskType
- DeskShip
- DeskSnake (in progress)
- DeskFortress

## Ideas for Applications

- **Linux Builder**: A user-friendly Linux configuration builder with cross-compiling support for remote systems.
- **Bitcoin Trader**: A cryptocurrency trading tool.
- **MP3 Player/Organizer**: A terminal-based music player and organizer.
- **RoboDog**: A robotics control interface.
- **Deskapt**: A terminal-based frontend for the `apt` package manager.

## Ideas for New Functionality

- Implement a callback system using regular expressions to trigger defined functions.
- Develop an interrupt/event system to handle socket server crashes gracefully.
- Enhance mouse support and streamline screen redraw functionality.

## TODO

- [x] Unify the printing mechanism.
- [ ] Refresh the examples folder with a new example based on a login page.
- [ ] Add a web sub-module to render Deskapp in a browser.
- [ ] Use pop-up warnings in a demo to evaluate their usability.
- [ ] Add functional shortcuts for all module features.
- [ ] Improve mouse handling and screen redraw logic.
- [ ] Reproduce Deskapp in other programming languages.
- [ ] Stream development on Twitch and create tutorials for YouTube.

## Sub-Modules

- **The Server**: A Python socket server with login, messaging, compression/encryption, and multiplayer app support.
- **Web Server**: A web server with a JavaScript library for connecting to "The Server" and a login page.

## Known Bugs

- Starting a blank app with only demo mode turned off results in no modules being loaded, causing the decider to fail.

## Changelog

- **6.10.23** - Ruckusist: Reassembling the onefile back into a One.0 version.
- **3.11.23** - Ruckusist: Deskapp.org is now live.
- **3.11.23** - Lannocc v0.0.12: Live terminal resizing now works.
- **3.11.23** - Lannocc v0.0.11: Fixed sizing issues.
- **3.11.23** - Ruckusist v0.0.10: Stabilized onefile for final bug fixes before transitioning to multifile for 1.0 release.
- **3.5.23** - Lannocc v0.0.9: Fixed a sizing anomaly.
- **11.11.22** - Ruckusist v0.0.8: Added the server module.
- **11.11.22** - Ruckusist v0.0.7: Added mouse support and refactored previous updates.
- **7.26.22** - Ruckusist v0.0.4: Transition release with new functionality and bugs.
- **4.20.22** - Ruckusist v0.0.4: Started working on version 4.
- **4.6.22** - Ruckusist v0.0.3: Added `demo_mode` flag to the App object.
