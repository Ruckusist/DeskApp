"""
character_motion.py — Deskapp CharacterMotion effects
Proposal 10 — CharacterMotion — 083126

Inspired by TerminalTextEffects (github.com/ChrisBuilds/terminaltexteffects)
by ChrisBuilds, specifically its "rain" effect: each character of the
input text falls from above the canvas and lands in its home position,
revealing the text over time. No code from that project is used here —
this is an original, dependency-free reimplementation of the concept,
sized for Deskapp's Module.write() rendering model (no bezier/easing,
no color gradients — those are left for a future proposal).

All rendering goes through Module.write() — no curses imports here.
"""

import random
import time


# ================================================================== #
# RainReveal                                                           #
# ================================================================== #

class RainReveal:
    """Animates a block of text falling into place, character by character.

    Each non-space character starts above the text block at a random
    height and falls straight down at a constant speed until it reaches
    its home row, where it lands and is drawn as the resolved character.
    Falling characters are drawn as a random "drop" glyph in DropColor;
    landed characters are drawn as themselves in Color.

    Usage:
        self.Rain = RainReveal()
        self.Rain.SetText(["HELLO WORLD", "DESKAPP"])
        self.Rain.Start()

        # in page(), every frame:
        self.Rain.Update()
        self.Rain.Render(self, Panel, Row=4, Col=2)

        # to replay from a key callback:
        self.Rain.Start()
    """

    DropGlyphs = "!@#$%^&*()-_=+[]{}<>/\\|;:.,~"

    def __init__(self, Lines=None, FallSpeed=28.0, Color="green",
                 DropColor="cyan"):
        self.FallSpeed = FallSpeed   # rows per second
        self.Color     = Color
        self.DropColor = DropColor
        self.Drops     = []
        self.Width     = 0
        self.Height    = 0
        self.Running   = False
        self._LastTick = None
        if Lines:
            self.SetText(Lines)

    def SetText(self, Lines):
        """Build one Drop per non-space character in Lines.

        Args:
            Lines: iterable of strings, the text to reveal.
        """
        Lines       = list(Lines)
        self.Height = len(Lines)
        self.Width  = max((len(L) for L in Lines), default=0)
        self.Drops  = []
        for RowIdx, Line in enumerate(Lines):
            for ColIdx, Ch in enumerate(Line):
                if Ch == " ":
                    continue
                self.Drops.append({
                    "Char":    Ch,
                    "HomeRow": RowIdx,
                    "Col":     ColIdx,
                    "CurRow":  self._SpawnRow(),
                    "Landed":  False,
                })
        self.Running   = False
        self._LastTick = None

    def _SpawnRow(self):
        """A random row above the canvas to start a drop falling from."""
        return float(-random.randint(1, max(1, self.Height * 2)))

    def Start(self):
        """(Re)start the fall from the top for all characters."""
        for Drop in self.Drops:
            Drop["CurRow"] = self._SpawnRow()
            Drop["Landed"] = False
        self.Running   = True
        self._LastTick = time.time()

    def IsDone(self):
        """True once every character has landed (False if never started)."""
        return bool(self.Drops) and all(D["Landed"] for D in self.Drops)

    def Update(self):
        """Advance the fall by elapsed wall-clock time. Call once per frame."""
        if not self.Running:
            return
        Now = time.time()
        if self._LastTick is None:
            self._LastTick = Now
        Dt   = Now - self._LastTick
        self._LastTick = Now
        Step = self.FallSpeed * Dt

        StillFalling = False
        for Drop in self.Drops:
            if Drop["Landed"]:
                continue
            Drop["CurRow"] += Step
            if Drop["CurRow"] >= Drop["HomeRow"]:
                Drop["CurRow"] = float(Drop["HomeRow"])
                Drop["Landed"] = True
            else:
                StillFalling = True

        if not StillFalling:
            self.Running = False

    def Render(self, Mod, Panel, Row, Col, Height=None, Width=None):
        """Draw all drops into Panel.

        Args:
            Mod:      The calling Module instance (for write()).
            Panel:    The panel object passed to page().
            Row, Col: Top-left position inside the panel.
            Height:   Rows available (defaults to text height).
            Width:    Columns available (defaults to text width).
        """
        MaxRow = Height if Height is not None else self.Height
        MaxCol = Width if Width is not None else self.Width

        for Drop in self.Drops:
            R = int(Drop["CurRow"])
            C = Drop["Col"]
            if R < 0 or R >= MaxRow or C >= MaxCol:
                continue
            if Drop["Landed"]:
                Ch, Color = Drop["Char"], self.Color
            else:
                Ch, Color = random.choice(self.DropGlyphs), self.DropColor
            Mod.write(Panel, Row + R, Col + C, Ch, color=Color)
