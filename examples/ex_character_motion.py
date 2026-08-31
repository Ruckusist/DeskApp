"""
ex_character_motion.py — CharacterMotion RainReveal demonstration
Proposal 10 — CharacterMotion — 083126

Inspired by TerminalTextEffects (github.com/ChrisBuilds/terminaltexteffects)
"rain" effect: each character of a banner falls from above the canvas
and lands into place, revealing the text.

Run from the project root:
    python3 examples/ex_character_motion.py

Controls:
    R / ENTER   — replay the rain effect
    Q / Ctrl-C  — quit
"""

import os
import sys
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from deskapp import App, Module, callback, Keys, RainReveal

DEMO_ID = random.random()

BANNER = [
    " ____             _    _              ",
    "|  _ \\  ___  ___ | | _/ \\   _ __  _ __ ",
    "| | | |/ _ \\/ __|| |/ / _ \\ | '_ \\| '_ \\",
    "| |_| |  __/\\__ \\|   / ___ \\| |_) | |_) |",
    "|____/ \\___||___/|_|_/_/   \\_\\ .__/| .__/",
    "                              |_|   |_|  ",
    "",
    "     CharacterMotion :: RainReveal demo",
]


class CharacterMotionDemo(Module):
    """Demonstrates the RainReveal character-motion effect."""

    name = "CharacterMotion Demo"

    def __init__(self, App_):
        super().__init__(App_, DEMO_ID)

        self.Rain = RainReveal(BANNER, FallSpeed=22.0,
                               Color="green", DropColor="cyan")
        self.Rain.Start()

    def page(self, Panel):
        try:
            Panel.win.erase()
        except Exception:
            pass

        H = self.h
        W = self.w

        Title = "CharacterMotion Demo   R/ENTER = replay   Q = quit"
        self.write(Panel, 1, 2, Title[:W - 3], color="cyan")

        self.Rain.Update()
        RowOffset = max(3, (H - self.Rain.Height) // 2)
        ColOffset = max(2, (W - self.Rain.Width) // 2)
        self.Rain.Render(
            self, Panel, Row=RowOffset, Col=ColOffset,
            Height=H - RowOffset - 1, Width=W - ColOffset - 1,
        )

        Status = "Falling..." if self.Rain.Running else "Landed."
        self.write(Panel, H - 2, 2, Status, color="yellow")

    def PageInfo(self, Panel):
        try:
            Pw = Panel.dims[1]
            self.write(Panel, 1, 2, "Effect: RainReveal"[:Pw - 4],
                       color="cyan")
            State = "falling" if self.Rain.Running else "landed"
            self.write(Panel, 2, 2, f"State: {State}"[:Pw - 4],
                       color="yellow")
        except Exception:
            pass
        return True

    # -------------------------------------------------------------- #
    # Key callbacks                                                   #
    # -------------------------------------------------------------- #

    @callback(DEMO_ID, Keys.R)
    def OnReplay(self, *a, **k):
        self.Rain.Start()

    @callback(DEMO_ID, Keys.ENTER)
    def OnEnter(self, *a, **k):
        self.Rain.Start()


if __name__ == "__main__":
    App(
        modules=[CharacterMotionDemo],
        name="CharacterMotion Demo",
        title="CharacterMotion Example",
        header="Proposal 10 — CharacterMotion (RainReveal)",
        demo_mode=False,
        show_right_panel=False,
        show_info_panel=True,
    )
