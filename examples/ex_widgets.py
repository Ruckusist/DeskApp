"""
ex_widgets.py — CoreWidgets demonstration example
Proposal 09 — CoreWidgets — 053126

Exercises all four widgets in one app:
    ScrollList    — left panel, 8 items, UP/DOWN move cursor
    ResultGrid    — main panel, tabular data, arrow keys + , / . pan cols
    ConfirmPrompt — D key arms a Y/N prompt at the bottom of main panel
    JsonRegistry  — status bar shows a round-trip write/read of a temp file

Run from the project root:
    python3 examples/ex_widgets.py

Controls:
    UP / DOWN       — move ScrollList cursor (left panel focused)
    ENTER           — move focus to grid
    , / .           — pan ResultGrid columns left / right
    D               — trigger ConfirmPrompt on selected grid row
    Y / N           — answer the confirm prompt
    ESC             — dismiss confirm prompt / go back to list
    Q / Ctrl-C      — quit
"""

import os
import sys
import random
import tempfile
import pathlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from deskapp import (
    App, Module, callback, Keys,
    ScrollList, ResultGrid, ConfirmPrompt, JsonRegistry,
)

DEMO_ID = random.random()

SAMPLE_ITEMS = [
    "Alpha dataset",
    "Beta dataset",
    "Gamma dataset",
    "Delta dataset",
    "Epsilon dataset",
    "Zeta dataset",
    "Eta dataset",
    "Theta dataset",
]

SAMPLE_COLS = ["id", "name", "category", "score", "active"]
SAMPLE_ROWS = [
    (1, "Widget Alpha",   "render",   "9.1",  "yes"),
    (2, "Widget Beta",    "input",    "8.7",  "yes"),
    (3, "Widget Gamma",   "data",     "7.4",  "no"),
    (4, "Widget Delta",   "render",   "9.9",  "yes"),
    (5, "Widget Epsilon", "input",    "6.2",  "yes"),
    (6, "Widget Zeta",    "data",     "8.0",  "no"),
    (7, "Widget Eta",     "render",   "7.7",  "yes"),
    (8, "Widget Theta",   "input",    "9.3",  "yes"),
]

# Focus modes
FOCUS_LIST = "list"
FOCUS_GRID = "grid"


class WidgetsDemo(Module):
    """Demonstrates ScrollList, ResultGrid, ConfirmPrompt, JsonRegistry."""

    name = "Widgets Demo"

    def __init__(self, App_):
        super().__init__(App_, DEMO_ID)

        self.Focus   = FOCUS_LIST
        self.Status  = ""
        self.StatusColor = "cyan"

        # ScrollList
        self.List = ScrollList(SAMPLE_ITEMS)

        # ResultGrid
        self.Grid = ResultGrid(MaxColW=20)
        self.Grid.SetData(SAMPLE_COLS, SAMPLE_ROWS)

        # ConfirmPrompt
        self.Confirm = ConfirmPrompt()

        # JsonRegistry round-trip on startup (temp file)
        self._RegistryDemo()

    # -------------------------------------------------------------- #
    # JsonRegistry demo                                               #
    # -------------------------------------------------------------- #

    def _RegistryDemo(self):
        """Write and read back a registry to prove the round-trip."""
        try:
            with tempfile.TemporaryDirectory() as Tmp:
                Reg   = JsonRegistry(
                    pathlib.Path(Tmp) / "demo.json",
                    Key="items",
                )
                Items = []
                Items = Reg.Add("/tmp/alpha.db", Items)
                Items = Reg.Add("/tmp/beta.db",  Items)
                Reg.Save(Items)
                Back  = Reg.Load()
                assert len(Back) == 2
                Items = Reg.Remove("/tmp/alpha.db", Back)
                Reg.Save(Items)
                Back2 = Reg.Load()
                assert len(Back2) == 1
            self.SetStatus(
                "JsonRegistry: write/read/remove round-trip OK", "green"
            )
        except Exception as E:
            self.SetStatus(f"JsonRegistry error: {E}", "red")

    # -------------------------------------------------------------- #
    # Helpers                                                         #
    # -------------------------------------------------------------- #

    def SetStatus(self, Msg, Color="cyan"):
        self.Status      = str(Msg)
        self.StatusColor = Color

    def DeleteRow(self, RowIdx):
        """Remove a row from the demo data and reload the grid."""
        Rows = list(SAMPLE_ROWS)
        if 0 <= RowIdx < len(Rows):
            Removed = Rows.pop(RowIdx)
            self.Grid.SetData(SAMPLE_COLS, Rows)
            self.SetStatus(
                f"Deleted row: {Removed[1]}", "yellow"
            )
        else:
            self.SetStatus("Nothing to delete", "yellow")

    # -------------------------------------------------------------- #
    # Render                                                          #
    # -------------------------------------------------------------- #

    def page(self, Panel):
        try:
            Panel.win.erase()
        except Exception:
            pass

        H = self.h
        W = self.w

        Title = (
            "Widgets Demo  "
            "UP/DOWN=list  ENTER=grid  ,/.=pan cols  D=delete  Y/N=confirm"
        )
        self.write(Panel, 1, 2, Title[:W - 3], color="cyan")

        # Divider between list area and grid area
        ListW = min(26, W // 3)
        GridX = ListW + 2
        GridW = W - GridX - 1

        # Focus indicator
        ListHeader = (
            "[LIST]" if self.Focus == FOCUS_LIST else " LIST "
        )
        GridHeader = (
            "[GRID]" if self.Focus == FOCUS_GRID else " GRID "
        )

        self.write(Panel, 2, 2, ListHeader, color="yellow")
        self.write(Panel, 2, GridX, GridHeader, color="yellow")

        # ScrollList
        ListH = H - 6
        self.List.Render(
            self, Panel, Row=3, Col=2,
            Height=ListH, Width=ListW - 2,
        )

        # ResultGrid
        self.Grid.Render(
            self, Panel, Row=3, Col=GridX,
            Height=H - 6, Width=GridW,
        )

        # ConfirmPrompt (only draws when Active)
        self.Confirm.Render(
            self, Panel, Row=H - 3, Col=2,
            Width=W - 4,
        )

        # Status bar
        self.write(Panel, H - 2, 2,
                   self.Status[:W - 4],
                   color=self.StatusColor)

    def PageInfo(self, Panel):
        """Show selected items in the info panel."""
        try:
            Pw = Panel.dims[1]
            self.write(Panel, 1, 2,
                       "Selected (list):"[:Pw - 4], color="cyan")
            Item = self.List.Selected() or "(none)"
            self.write(Panel, 2, 2, str(Item)[:Pw - 4], color="yellow")

            self.write(Panel, 4, 2,
                       "Selected (grid):"[:Pw - 4], color="cyan")
            Row = self.Grid.Selected()
            if Row:
                self.write(Panel, 5, 2,
                           str(Row[1])[:Pw - 4], color="yellow")
                self.write(Panel, 6, 2,
                           f"score: {Row[3]}"[:Pw - 4])
            else:
                self.write(Panel, 5, 2, "(none)")
        except Exception:
            pass
        return True

    # -------------------------------------------------------------- #
    # Key callbacks                                                   #
    # -------------------------------------------------------------- #

    @callback(DEMO_ID, Keys.UP)
    def OnUp(self, *a, **k):
        if self.Focus == FOCUS_LIST:
            self.List.MoveUp()
        else:
            self.Grid.MoveUp()

    @callback(DEMO_ID, Keys.DOWN)
    def OnDown(self, *a, **k):
        if self.Focus == FOCUS_LIST:
            self.List.MoveDown()
        else:
            self.Grid.MoveDown()

    @callback(DEMO_ID, Keys.HOME)
    def OnHome(self, *a, **k):
        if self.Focus == FOCUS_LIST:
            self.List.JumpTop()
        else:
            self.Grid.JumpTop()

    @callback(DEMO_ID, Keys.END)
    def OnEnd(self, *a, **k):
        if self.Focus == FOCUS_LIST:
            self.List.JumpEnd()
        else:
            self.Grid.JumpEnd()

    @callback(DEMO_ID, Keys.ENTER)
    def OnEnter(self, *a, **k):
        if self.Confirm.Active:
            return
        # toggle focus between list and grid
        self.Focus = (
            FOCUS_GRID if self.Focus == FOCUS_LIST else FOCUS_LIST
        )
        self.SetStatus(
            f"Focus: {self.Focus}", "cyan"
        )

    @callback(DEMO_ID, Keys.ESC)
    def OnEsc(self, *a, **k):
        if self.Confirm.Active:
            self.Confirm.No()
        else:
            self.Focus = FOCUS_LIST

    # , key  = raw 44  (pan columns left)
    @callback(DEMO_ID, 44)
    def OnPanLeft(self, *a, **k):
        self.Grid.ScrollLeft()

    # . key  = raw 46  (pan columns right)
    @callback(DEMO_ID, 46)
    def OnPanRight(self, *a, **k):
        self.Grid.ScrollRight()

    # D key  = raw 100
    @callback(DEMO_ID, 100)
    def OnD(self, *a, **k):
        if self.Confirm.Active:
            return
        Idx = self.Grid.SelectedIndex()
        Row = self.Grid.Selected()
        if Row is None:
            return
        self.Confirm.Ask(
            f"Delete row {Idx + 1}: '{Row[1]}'? [Y/N]",
            OnYes=lambda: self.DeleteRow(Idx),
            OnNo=lambda: self.SetStatus("Delete cancelled", "cyan"),
        )

    @callback(DEMO_ID, Keys.Y)
    def OnY(self, *a, **k):
        self.Confirm.Yes()

    @callback(DEMO_ID, Keys.N)
    def OnN(self, *a, **k):
        self.Confirm.No()


if __name__ == "__main__":
    App(
        modules=[WidgetsDemo],
        name="Widgets Demo",
        title="CoreWidgets Example",
        header="Proposal 09 — CoreWidgets",
        demo_mode=False,
        show_right_panel=False,
        show_info_panel=True,
    )
