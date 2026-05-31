"""
widgets.py — Deskapp core rendering utilities
Proposal 09 — CoreWidgets — 053126

Four composable helpers available to every mod via:
    from deskapp import ScrollList, ResultGrid, ConfirmPrompt, JsonRegistry

All rendering goes through Module.write() — no curses imports here.
"""

import json
import os
import pathlib
import tempfile


# ================================================================== #
# ScrollList                                                           #
# ================================================================== #

class ScrollList:
    """Stateful scrollable list for any vertical item collection.

    Usage:
        self.List = ScrollList()
        self.List.SetItems(["alpha", "beta", "gamma"])

        # in page():
        self.List.Render(self, Panel, Row=4, Col=2,
                         Height=self.h - 6, Width=self.w - 4)

        # in callbacks:
        @callback(ID, Keys.UP)
        def OnUp(self, *a, **k): self.List.MoveUp()
    """

    def __init__(self, Items=None):
        self.Items     = list(Items) if Items else []
        self.Cursor    = 0
        self.ScrollTop = 0

    def SetItems(self, Items):
        """Replace the item list. Clamps cursor to new length."""
        self.Items     = list(Items)
        self.Cursor    = max(0, min(self.Cursor, len(self.Items) - 1))
        self._Clamp()

    def MoveUp(self):
        if self.Cursor > 0:
            self.Cursor -= 1
            self._Clamp()

    def MoveDown(self):
        if self.Cursor < len(self.Items) - 1:
            self.Cursor += 1
            self._Clamp()

    def JumpTop(self):
        self.Cursor    = 0
        self.ScrollTop = 0

    def JumpEnd(self):
        self.Cursor = max(0, len(self.Items) - 1)
        self._Clamp()

    def Selected(self):
        """Return the currently highlighted item, or None."""
        if not self.Items:
            return None
        return self.Items[self.Cursor]

    def SelectedIndex(self):
        """Return the cursor position as an integer."""
        return self.Cursor

    def Render(self, Mod, Panel, Row, Col, Height, Width,
               SelectedColor="yellow", NormalColor=None,
               Formatter=None):
        """Render the visible window of items into Panel.

        Args:
            Mod:           The calling Module instance (for write()).
            Panel:         The panel object passed to page().
            Row, Col:      Top-left position inside the panel.
            Height:        Number of rows available.
            Width:         Maximum character width per row.
            SelectedColor: Color name for the highlighted row.
            NormalColor:   Color name for non-highlighted rows (None=default).
            Formatter:     callable(item) -> str; defaults to str().
        """
        if not self.Items or Height <= 0 or Width <= 0:
            return

        Fmt = Formatter if Formatter else str
        self._Clamp(Height)

        for Offset in range(min(Height, len(self.Items) - self.ScrollTop)):
            Idx      = self.ScrollTop + Offset
            Item     = self.Items[Idx]
            Selected = (Idx == self.Cursor)
            Color    = SelectedColor if Selected else NormalColor
            Prefix   = "> " if Selected else "  "
            Line     = (Prefix + Fmt(Item))[:Width]
            Mod.write(Panel, Row + Offset, Col, Line, color=Color)

    # ---------------------------------------------------------------- #
    # Internal                                                           #
    # ---------------------------------------------------------------- #

    def _Clamp(self, Height=None):
        """Keep ScrollTop so cursor is always visible."""
        if not self.Items:
            return
        N = len(self.Items)
        self.Cursor = max(0, min(self.Cursor, N - 1))
        if Height is None:
            return
        if self.Cursor < self.ScrollTop:
            self.ScrollTop = self.Cursor
        elif self.Cursor >= self.ScrollTop + Height:
            self.ScrollTop = self.Cursor - Height + 1
        self.ScrollTop = max(0, min(self.ScrollTop, max(0, N - Height)))


# ================================================================== #
# ResultGrid                                                           #
# ================================================================== #

class ResultGrid:
    """Column-auto-sized tabular grid renderer.

    Handles: header row (cyan), selected row highlight (yellow),
    row-number gutter, vertical scroll, horizontal column panning.

    Works with any sequence of rows — tuples, lists, or sqlite3.Row.

    Usage:
        self.Grid = ResultGrid()
        self.Grid.SetData(["id", "name", "ts"], Rows)

        # in page():
        self.Grid.Render(self, Panel, Row=4, Col=1,
                         Height=self.h - 6, Width=self.w - 2)
    """

    def __init__(self, MaxColW=24, GutterW=5):
        self.MaxColW   = MaxColW
        self.GutterW   = GutterW
        self.Cols      = []
        self.Rows      = []
        self.ColWidths = []
        self.Cursor    = 0
        self.VScroll   = 0
        self.HScroll   = 0

    def SetData(self, Cols, Rows):
        """Load column headers and row data; recomputes column widths."""
        self.Cols    = list(Cols)
        self.Rows    = list(Rows)
        self.Cursor  = 0
        self.VScroll = 0
        self.HScroll = 0
        self._ComputeWidths()

    def MoveUp(self):
        if self.Cursor > 0:
            self.Cursor -= 1

    def MoveDown(self):
        if self.Cursor < len(self.Rows) - 1:
            self.Cursor += 1

    def ScrollLeft(self):
        if self.HScroll > 0:
            self.HScroll -= 1

    def ScrollRight(self):
        if self.HScroll < max(0, len(self.Cols) - 1):
            self.HScroll += 1

    def JumpTop(self):
        self.Cursor  = 0
        self.VScroll = 0

    def JumpEnd(self):
        self.Cursor = max(0, len(self.Rows) - 1)

    def Selected(self):
        """Return the highlighted row, or None."""
        if not self.Rows:
            return None
        return self.Rows[self.Cursor]

    def SelectedIndex(self):
        return self.Cursor

    def Render(self, Mod, Panel, Row, Col, Height, Width):
        """Render the grid into Panel.

        Args:
            Mod:          The calling Module instance.
            Panel:        Panel object from page().
            Row, Col:     Top-left position.
            Height:       Rows available (includes header row).
            Width:        Total character width available.
        """
        if Height <= 1 or Width <= 4:
            return

        self._AdjustVScroll(Height - 1)

        # Header
        HeaderParts = []
        Gutter      = " " * self.GutterW
        Remaining   = Width - self.GutterW
        VisibleCols = self._VisibleCols(Remaining)

        for CIdx in VisibleCols:
            W    = self.ColWidths[CIdx]
            Name = self.Cols[CIdx][:W].ljust(W)
            HeaderParts.append(Name)
        Header = Gutter + "  ".join(HeaderParts)
        Mod.write(Panel, Row, Col, Header[:Width], color="cyan")

        # Rows
        DataH = Height - 1
        for Offset in range(min(DataH, len(self.Rows) - self.VScroll)):
            AbsIdx   = self.VScroll + Offset
            RowData  = self.Rows[AbsIdx]
            Selected = (AbsIdx == self.Cursor)
            Color    = "yellow" if Selected else None
            GutterTx = str(AbsIdx + 1).rjust(self.GutterW - 1) + " "

            CellParts = []
            for CIdx in VisibleCols:
                W     = self.ColWidths[CIdx]
                try:
                    Val = str(RowData[CIdx]) if not isinstance(
                        RowData, dict) else str(RowData[self.Cols[CIdx]])
                except Exception:
                    Val = ""
                CellParts.append(Val[:W].ljust(W))

            Line = GutterTx + "  ".join(CellParts)
            Mod.write(Panel, Row + 1 + Offset, Col,
                      Line[:Width], color=Color)

    # ---------------------------------------------------------------- #
    # Internal                                                           #
    # ---------------------------------------------------------------- #

    def _ComputeWidths(self):
        """Compute per-column display widths."""
        self.ColWidths = []
        for I, Name in enumerate(self.Cols):
            W = len(Name)
            for RowData in self.Rows:
                try:
                    Val = str(RowData[I])
                except Exception:
                    Val = ""
                if len(Val) > W:
                    W = len(Val)
            self.ColWidths.append(min(W, self.MaxColW))

    def _VisibleCols(self, AvailW):
        """Return list of column indices visible given HScroll + width."""
        Visible = []
        Used    = 0
        for I in range(self.HScroll, len(self.Cols)):
            W = self.ColWidths[I] + 2  # 2 for separator
            if Used + W > AvailW and Visible:
                break
            Visible.append(I)
            Used += W
        return Visible

    def _AdjustVScroll(self, DataH):
        if not self.Rows:
            return
        N = len(self.Rows)
        self.Cursor = max(0, min(self.Cursor, N - 1))
        if self.Cursor < self.VScroll:
            self.VScroll = self.Cursor
        elif self.Cursor >= self.VScroll + DataH:
            self.VScroll = self.Cursor - DataH + 1
        self.VScroll = max(0, min(self.VScroll, max(0, N - DataH)))


# ================================================================== #
# ConfirmPrompt                                                        #
# ================================================================== #

class ConfirmPrompt:
    """Inline Y/N confirmation prompt.

    Holds one pending question at a time. Renders nothing when inactive.
    The mod calls Ask() to arm it, then Yes()/No() from key callbacks.

    Usage:
        self.Confirm = ConfirmPrompt()

        @callback(ID, Keys.D)
        def OnD(self, *a, **k):
            Name = self.List.Selected()
            self.Confirm.Ask(
                f"Delete {Name}? [Y/N]",
                OnYes=lambda: self.DoDelete(Name),
            )

        @callback(ID, Keys.Y)
        def OnY(self, *a, **k): self.Confirm.Yes()

        @callback(ID, Keys.N)
        def OnN(self, *a, **k): self.Confirm.No()

        # in page():
        self.Confirm.Render(self, Panel, Row=self.h - 3, Col=2,
                            Width=self.w - 4)
    """

    def __init__(self):
        self.Message = ""
        self.OnYes   = None
        self.OnNo    = None

    @property
    def Active(self):
        return self.OnYes is not None

    def Ask(self, Message, OnYes, OnNo=None):
        """Arm the prompt.

        Args:
            Message: String shown to the user.
            OnYes:   Zero-arg callable invoked on Y.
            OnNo:    Zero-arg callable invoked on N / ESC (optional).
        """
        self.Message = str(Message)
        self.OnYes   = OnYes
        self.OnNo    = OnNo

    def Yes(self):
        """Call from the Y key callback."""
        if not self.Active:
            return
        Fn = self.OnYes
        self._Clear()
        if Fn:
            Fn()

    def No(self):
        """Call from the N key callback or ESC."""
        if not self.Active:
            return
        Fn = self.OnNo
        self._Clear()
        if Fn:
            Fn()

    def Render(self, Mod, Panel, Row, Col, Width, Color="yellow"):
        """Render the prompt line. No-op when not Active."""
        if not self.Active:
            return
        Line = self.Message[:Width]
        Mod.write(Panel, Row, Col, Line, color=Color)

    def _Clear(self):
        self.Message = ""
        self.OnYes   = None
        self.OnNo    = None


# ================================================================== #
# JsonRegistry                                                         #
# ================================================================== #

class JsonRegistry:
    """Load/save a JSON list of path strings to a config file.

    Atomic writes (write-to-temp then rename). No state beyond the file
    path and JSON key — always reads fresh, always writes immediately.

    Usage:
        self.Reg = JsonRegistry(
            pathlib.Path.home() / ".config" / "deskapp" / "databases.json",
            Key="databases",
        )
        KnownDBs = self.Reg.Load()
        KnownDBs = self.Reg.Add("/path/to/new.db", KnownDBs)
        self.Reg.Save(KnownDBs)
    """

    def __init__(self, ConfigPath, Key="items"):
        self.ConfigPath = pathlib.Path(ConfigPath)
        self.Key        = Key

    def Load(self):
        """Read the registry. Returns a list of strings (empty on miss)."""
        try:
            Raw = json.loads(self.ConfigPath.read_text())
            return list(Raw.get(self.Key, []))
        except Exception:
            return []

    def Save(self, Items):
        """Write Items to the registry atomically.

        Args:
            Items: List of path strings to persist.

        Returns:
            True on success, False on error.
        """
        try:
            self.ConfigPath.parent.mkdir(parents=True, exist_ok=True)
            Payload = json.dumps({self.Key: list(Items)}, indent=2)
            Dir     = str(self.ConfigPath.parent)
            Fd, Tmp = tempfile.mkstemp(dir=Dir, suffix=".tmp")
            try:
                with os.fdopen(Fd, "w") as F:
                    F.write(Payload)
                os.replace(Tmp, str(self.ConfigPath))
            except Exception:
                try:
                    os.unlink(Tmp)
                except Exception:
                    pass
                raise
            return True
        except Exception as E:
            print(f"[JsonRegistry] Save error: {E}")
            return False

    def Add(self, Path, Items):
        """Return a new list with Path added (deduplicates).

        Args:
            Path:  String path to add.
            Items: Current list.

        Returns:
            New list with Path appended if not already present.
        """
        Result = list(Items)
        Norm   = str(pathlib.Path(Path).expanduser().resolve())
        if Norm not in [str(pathlib.Path(I).expanduser().resolve())
                        for I in Result]:
            Result.append(Norm)
        return Result

    def Remove(self, Path, Items):
        """Return a new list with Path removed.

        Args:
            Path:  String path to remove.
            Items: Current list.

        Returns:
            New list without Path.
        """
        Norm   = str(pathlib.Path(Path).expanduser().resolve())
        return [I for I in Items
                if str(pathlib.Path(I).expanduser().resolve()) != Norm]
