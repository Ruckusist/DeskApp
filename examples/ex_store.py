"""
ex_store.py — DataStore demonstration example
Proposal 08 — DataStore — 053126

Exercises the full DataStore lifecycle:
    ensure_table, execute, executemany, fetch, fetchone, delete

Run from the project root:
    python3 examples/ex_store.py

Controls:
    Tab + type + Enter  — add a new note
    UP / DOWN           — move cursor
    D                   — delete selected note
    Q / Ctrl-C          — quit
"""

import os
import sys
import random
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from deskapp import App, Module, callback, Keys

DEMO_ID = random.random()

TABLE    = "demo_notes"
SCHEMA   = "id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, ts TEXT"
SEEDS    = [
    "Welcome to the DataStore demo.",
    "Press Tab, type a note, press Enter to add it.",
    "Press D to delete the selected note.",
]


class StoreDemo(Module):
    """Demonstrates the deskapp DataStore API."""

    name = "Store Demo"

    def __init__(self, App_):
        super().__init__(App_, DEMO_ID)

        self.Rows    = []
        self.Cursor  = 0
        self.Status  = ""
        self.StatusColor = "cyan"

        # Register our table
        Ok = self.app.store.ensure_table(TABLE, SCHEMA)
        if Ok:
            self._Seed()
            self._Load()
            self.SetStatus(
                f"Store OK — {self.app.store.DbPath}", "green"
            )
        else:
            self.SetStatus("Store unavailable (fallback mode)", "red")

    # -------------------------------------------------------------- #
    # Data helpers                                                     #
    # -------------------------------------------------------------- #

    def _Seed(self):
        """Insert seed rows if the table is empty."""
        Count = self.app.store.fetchone(
            f"SELECT COUNT(*) AS n FROM {TABLE}"
        )
        if Count and Count["n"] == 0:
            Now = datetime.datetime.now().isoformat(timespec="seconds")
            self.app.store.executemany(
                f"INSERT INTO {TABLE} (text, ts) VALUES (?, ?)",
                [(S, Now) for S in SEEDS],
            )

    def _Load(self):
        """Reload rows from the store."""
        self.Rows = list(
            self.app.store.fetch(
                f"SELECT id, text, ts FROM {TABLE} ORDER BY id"
            )
        )
        self.Cursor = max(0, min(self.Cursor, len(self.Rows) - 1))

    def SetStatus(self, Msg, Color="cyan"):
        self.Status      = str(Msg)
        self.StatusColor = Color

    def SelectedRow(self):
        if not self.Rows:
            return None
        return self.Rows[self.Cursor]

    def DeleteSelected(self):
        Row = self.SelectedRow()
        if Row is None:
            self.SetStatus("Nothing to delete", "yellow")
            return
        Ok = self.app.store.execute(
            f"DELETE FROM {TABLE} WHERE id = ?", (Row["id"],)
        )
        if Ok:
            self.SetStatus(f"Deleted: {Row['text'][:40]}", "yellow")
        else:
            self.SetStatus("Delete failed", "red")
        self._Load()

    # -------------------------------------------------------------- #
    # Text input hook                                                  #
    # -------------------------------------------------------------- #

    def handle_text(self, InputString):
        Text = InputString.strip()
        if not Text:
            return
        Now = datetime.datetime.now().isoformat(timespec="seconds")
        Ok  = self.app.store.execute(
            f"INSERT INTO {TABLE} (text, ts) VALUES (?, ?)",
            (Text, Now),
        )
        if Ok:
            self.SetStatus(f"Added: {Text[:50]}", "green")
        else:
            self.SetStatus("Insert failed", "red")
        self._Load()
        self.Cursor = len(self.Rows) - 1  # jump to new row

    # -------------------------------------------------------------- #
    # Render                                                           #
    # -------------------------------------------------------------- #

    def page(self, Panel):
        H = self.h
        W = self.w
        try:
            Panel.win.erase()
        except Exception:
            pass

        self.write(Panel, 1, 2,
                   "DataStore Demo  (Tab=add  D=delete  Q=quit)",
                   color="cyan")
        self.write(Panel, 2, 2,
                   f"Table: {TABLE}  |  Rows: {len(self.Rows)}",
                   color="blue")

        # Column headers
        self.write(Panel, 3, 2, f"{'ID':<6}{'Timestamp':<22}Note",
                   color="yellow")

        # Row list
        ListH   = max(0, H - 6)
        if self.Rows:
            self.Cursor = max(0, min(self.Cursor, len(self.Rows) - 1))
            Top    = max(0, self.Cursor - ListH // 2)
            MaxTop = max(0, len(self.Rows) - ListH)
            if Top > MaxTop:
                Top = MaxTop
            Visible = self.Rows[Top: Top + ListH]
            for Offset, Row in enumerate(Visible):
                AbsIdx   = Top + Offset
                Selected = (AbsIdx == self.Cursor)
                RRow     = 4 + Offset
                if RRow >= H - 2:
                    break
                Cursor   = ">> " if Selected else "   "
                Color    = "yellow" if Selected else None
                IdStr    = str(Row["id"])
                TsStr    = Row["ts"][:19]
                Text     = Row["text"]
                MaxText  = max(0, W - 33)
                Line     = (
                    f"{Cursor}{IdStr:<6}{TsStr:<22}"
                    f"{Text[:MaxText]}"
                )
                self.write(Panel, RRow, 1, Line[:W - 2], color=Color)
        else:
            self.write(Panel, 4, 2,
                       "(no rows — add one with Tab)",
                       color="yellow")

        # Status
        self.write(Panel, H - 2, 2,
                   self.Status[:W - 4],
                   color=self.StatusColor)

    def PageInfo(self, Panel):
        """Show store path and row count in the info panel."""
        try:
            Ph = Panel.dims[0]
            Pw = Panel.dims[1]
            Path  = str(self.app.store.DbPath)
            Count = len(self.Rows)
            Ok    = "OK" if self.app.store.Ok else "FALLBACK"
            self.write(Panel, 1, 2,
                       f"Store: {Ok}"[:Pw - 4], color="green")
            self.write(Panel, 2, 2,
                       f"Path:  {Path}"[:Pw - 4], color="cyan")
            self.write(Panel, 3, 2,
                       f"Rows in {TABLE}: {Count}"[:Pw - 4],
                       color="yellow")
        except Exception:
            pass
        return True

    # -------------------------------------------------------------- #
    # Key callbacks                                                    #
    # -------------------------------------------------------------- #

    @callback(DEMO_ID, Keys.UP)
    def OnUp(self, *args, **kwargs):
        if self.Cursor > 0:
            self.Cursor -= 1

    @callback(DEMO_ID, Keys.DOWN)
    def OnDown(self, *args, **kwargs):
        if self.Cursor < len(self.Rows) - 1:
            self.Cursor += 1

    @callback(DEMO_ID, Keys.HOME)
    def OnHome(self, *args, **kwargs):
        self.Cursor = 0

    @callback(DEMO_ID, Keys.END)
    def OnEnd(self, *args, **kwargs):
        if self.Rows:
            self.Cursor = len(self.Rows) - 1

    # D key — raw int 100 ('d')
    @callback(DEMO_ID, 100)
    def OnD(self, *args, **kwargs):
        self.DeleteSelected()


if __name__ == "__main__":
    App(
        modules=[StoreDemo],
        name="Store Demo",
        title="DataStore Example",
        header="Proposal 08 — DataStore",
        demo_mode=False,
        show_right_panel=False,
        show_info_panel=True,
    )
