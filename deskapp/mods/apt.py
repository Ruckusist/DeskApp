"""
APT Module for Deskapp
Proposal 06 — AptModule — 053126

Modal TUI frontend for the APT package manager.
Views: ACTIONS, LIST, DETAIL, LOG
"""

import collections
import random
import shlex
import subprocess

try:
    import apt as apt_lib
    HAS_APT = True
except ImportError:
    HAS_APT = False

from deskapp import Module, callback, Keys
from deskapp.src.events import BaseWorker


APT_ID = random.random()

VIEW_ACTIONS = "actions"
VIEW_LIST    = "list"
VIEW_DETAIL  = "detail"
VIEW_LOG     = "log"

LIST_INSTALLED  = "Installed"
LIST_UPGRADABLE = "Upgradable"
LIST_SEARCH     = "Search Results"

LOG_MAX = 500


# ------------------------------------------------------------------ #
# Workers                                                              #
# ------------------------------------------------------------------ #

class AptWorker(BaseWorker):
    """Stream a shell command line-by-line into the event bus.

    Emits:
        <prefix>.out.start  — command started
        <prefix>.out.line   — one output line
        <prefix>.out.done   — finished, includes rc
        <prefix>.out.error  — error during setup or read
    """

    def __init__(self, app, TaskId, Command, Prefix="apt"):
        super().__init__(app, name="APT")
        self.TaskId = TaskId
        self.Command = Command
        self.Prefix = Prefix
        self.Process = None

    def work(self):
        self.emit(
            f"{self.Prefix}.out.start",
            {"id": self.TaskId, "command": self.Command},
        )
        try:
            self.Process = subprocess.Popen(
                self.Command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as E:
            self.emit(
                f"{self.Prefix}.out.error",
                {"id": self.TaskId, "error": str(E)},
            )
            return
        try:
            for Line in self.Process.stdout:
                if self.should_stop:
                    try:
                        self.Process.kill()
                    except Exception:
                        pass
                    break
                self.emit(
                    f"{self.Prefix}.out.line",
                    {"id": self.TaskId, "line": Line.rstrip("\n")},
                )
        except Exception as E:
            self.emit(
                f"{self.Prefix}.out.error",
                {"id": self.TaskId, "error": str(E)},
            )
        finally:
            Rc = None
            try:
                Rc = self.Process.wait(timeout=2)
            except Exception:
                pass
            self.emit(
                f"{self.Prefix}.out.done",
                {"id": self.TaskId, "rc": Rc},
            )

    def Kill(self):
        """Signal stop and escalate: SIGTERM → wait → SIGKILL."""
        self.should_stop = True
        if self.Process is not None:
            try:
                self.Process.terminate()
                try:
                    self.Process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.Process.kill()
            except Exception:
                pass


class PackageListWorker(BaseWorker):
    """Load installed packages in the background.

    Emits:
        apt.packages.installed  — sorted list of package name strings
    """

    def __init__(self, app):
        super().__init__(app, name="PkgList")

    def work(self):
        Packages = []
        if HAS_APT:
            try:
                Cache = apt_lib.Cache()
                Cache.open(None)
                if self.should_stop:
                    return
                Packages = sorted(
                    [P.name for P in Cache if P.is_installed],
                    key=str.lower,
                )
            except Exception:
                Packages = self.FallbackDpkg()
        else:
            Packages = self.FallbackDpkg()
        if not self.should_stop:
            self.emit("apt.packages.installed", {"packages": Packages})

    def FallbackDpkg(self):
        """Parse dpkg -l when python-apt is unavailable."""
        try:
            Result = subprocess.run(
                ["dpkg", "-l"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            Names = []
            for Line in Result.stdout.splitlines():
                Parts = Line.split()
                if len(Parts) >= 2 and Parts[0] == "ii":
                    Names.append(Parts[1].split(":")[0])
            return sorted(Names, key=str.lower)
        except Exception:
            return []


class UpgradableWorker(BaseWorker):
    """Load upgradable package list in the background.

    Emits:
        apt.packages.upgradable  — sorted list of package name strings
    """

    def __init__(self, app):
        super().__init__(app, name="Upgradable")

    def work(self):
        Packages = []
        if HAS_APT:
            try:
                Cache = apt_lib.Cache()
                Cache.open(None)
                if self.should_stop:
                    return
                Packages = sorted(
                    [
                        P.name for P in Cache
                        if P.is_installed and P.is_upgradable
                    ],
                    key=str.lower,
                )
            except Exception:
                Packages = self.FallbackApt()
        else:
            Packages = self.FallbackApt()
        if not self.should_stop:
            self.emit("apt.packages.upgradable", {"packages": Packages})

    def FallbackApt(self):
        """Parse apt list --upgradable output."""
        try:
            Result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            Names = []
            for Line in Result.stdout.splitlines():
                if "/" in Line:
                    Names.append(Line.split("/")[0])
            return sorted(Names, key=str.lower)
        except Exception:
            return []



# ------------------------------------------------------------------ #
# Module                                                               #
# ------------------------------------------------------------------ #

class APT(Module):
    name = "APT"

    def __init__(self, app):
        super().__init__(app, APT_ID)

        # View state
        self.CurrentView = VIEW_ACTIONS
        self.PrevView    = VIEW_ACTIONS
        self.ListContext = LIST_INSTALLED

        # Package data
        self.InstalledPackages  = []
        self.UpgradablePackages = []
        self.SearchResults      = []

        # List navigation
        self.PkgIndex = 0

        # Log (capped deque)
        self.LogLines  = collections.deque(maxlen=LOG_MAX)
        self.LogScroll = 0

        # Detail view
        self.RawDetailLines = []   # raw apt show output lines
        self.DetailLines    = []   # formatted for display
        self.DetailPkg      = ""
        self.DetailScroll   = 0

        # Worker tracking (command workers only)
        self.CurrentWorker = None
        self.CurrentTaskId = 0
        self.ActiveCommand = ""

        # Confirmation overlay
        self.ConfirmMsg    = ""
        self.ConfirmAction = None

        # Status bar
        self.StatusMsg   = "Loading installed packages..."
        self.StatusColor = "cyan"

        # Action bar
        self.Actions = [
            ("Update",    "sudo apt update"),
            ("Upgrade",   "sudo apt upgrade -y"),
            ("Installed", LIST_INSTALLED),
            ("Upgradable",LIST_UPGRADABLE),
            ("Remove",    "REMOVE"),
            ("Autoremove","sudo apt autoremove -y"),
            ("Install",   "INSTALL"),
        ]
        self.action_bar_items = [
            Label for Label, _ in self.Actions
        ]

        # Wire events
        self.on_event("apt.out.start",  self.OnCmdStart)
        self.on_event("apt.out.line",   self.OnCmdLine)
        self.on_event("apt.out.done",   self.OnCmdDone)
        self.on_event("apt.out.error",  self.OnCmdError)
        self.on_event(
            "apt.detail.out.start", self.OnDetailStart
        )
        self.on_event(
            "apt.detail.out.line",  self.OnDetailLine
        )
        self.on_event(
            "apt.detail.out.done",  self.OnDetailDone
        )
        self.on_event(
            "apt.packages.installed",  self.OnInstalledLoaded
        )
        self.on_event(
            "apt.packages.upgradable", self.OnUpgradableLoaded
        )

        # Load installed packages immediately in background
        PackageListWorker(self.app).start()

    # -------------------------------------------------------------- #
    # Worker helpers                                                   #
    # -------------------------------------------------------------- #

    def StartCmdWorker(self, Worker):
        """Start a command worker, stopping any running one first."""
        if (
            self.CurrentWorker is not None
            and self.CurrentWorker.is_alive()
        ):
            if hasattr(self.CurrentWorker, "Kill"):
                self.CurrentWorker.Kill()
            else:
                self.CurrentWorker.should_stop = True
        self.CurrentWorker = Worker
        Worker.start()

    def CancelWorker(self):
        """Cancel the current running command worker."""
        if self.CurrentWorker is None:
            return
        if hasattr(self.CurrentWorker, "Kill"):
            self.CurrentWorker.Kill()
        else:
            self.CurrentWorker.should_stop = True
        self.CurrentWorker = None
        self.SetStatus("Cancelled", "yellow")

    def NextTaskId(self):
        self.CurrentTaskId += 1
        return self.CurrentTaskId

    # -------------------------------------------------------------- #
    # Status                                                           #
    # -------------------------------------------------------------- #

    def SetStatus(self, Msg, Color="cyan"):
        self.StatusMsg   = str(Msg)
        self.StatusColor = Color

    def _EnableFloat(self):
        """Size and show the backend floating panel for LOG overlay."""
        try:
            self.app.floating_height = max(10, self.h - 4)
            self.app.floating_width  = max(30, self.w - 6)
            self.app.backend.show_floating = True
        except Exception:
            pass

    def _DisableFloat(self):
        """Hide the backend floating panel."""
        try:
            self.app.backend.show_floating = False
        except Exception:
            pass

    # -------------------------------------------------------------- #
    # Event handlers                                                   #
    # -------------------------------------------------------------- #

    def OnCmdStart(self, Event):
        self.SetStatus(f"Running: {self.ActiveCommand}", "yellow")

    def OnCmdLine(self, Event):
        Line = Event["data"].get("line", "")
        self.LogLines.append(Line)
        ViewH  = max(1, self.h - 3)
        Bottom = max(0, len(self.LogLines) - ViewH)
        # Auto-scroll only when the user is already at or near the bottom
        if self.LogScroll >= Bottom - 1:
            self.LogScroll = Bottom

    def OnCmdDone(self, Event):
        Rc = Event["data"].get("rc", -1)
        Color = "green" if Rc == 0 else "red"
        self.SetStatus(
            f"Done (rc={Rc}): {self.ActiveCommand}", Color
        )
        self.CurrentWorker = None
        if "update" in self.ActiveCommand.lower():
            UpgradableWorker(self.app).start()

    def OnCmdError(self, Event):
        Err = Event["data"].get("error", "unknown error")
        self.LogLines.append(f"ERROR: {Err}")
        self.SetStatus(f"Error: {Err[:55]}", "red")
        self.CurrentWorker = None

    def OnDetailStart(self, Event):
        self.RawDetailLines = []
        self.DetailLines    = []

    def OnDetailLine(self, Event):
        Line = Event["data"].get("line", "")
        self.RawDetailLines.append(Line)

    def OnDetailDone(self, Event):
        Data = self.ParseAptShow(self.RawDetailLines)
        self.DetailLines = self.BuildDetailLines(Data, self.w)
        self.SetStatus(
            f"Details loaded: {self.DetailPkg}", "green"
        )

    def OnInstalledLoaded(self, Event):
        self.InstalledPackages = Event["data"].get("packages", [])
        Count = len(self.InstalledPackages)
        self.SetStatus(f"{Count} installed packages", "green")
        if self.ListContext == LIST_INSTALLED:
            self.PkgIndex = 0

    def OnUpgradableLoaded(self, Event):
        self.UpgradablePackages = Event["data"].get("packages", [])
        Count = len(self.UpgradablePackages)
        self.SetStatus(f"{Count} packages upgradable", "green")

    # -------------------------------------------------------------- #
    # List helpers                                                     #
    # -------------------------------------------------------------- #

    def CurrentList(self):
        if self.ListContext == LIST_INSTALLED:
            return self.InstalledPackages
        if self.ListContext == LIST_UPGRADABLE:
            return self.UpgradablePackages
        return self.SearchResults

    def SelectedPackage(self):
        Lst = self.CurrentList()
        if not Lst:
            return None
        return Lst[max(0, min(self.PkgIndex, len(Lst) - 1))]

    def ClampPkgIndex(self):
        Lst = self.CurrentList()
        if not Lst:
            self.PkgIndex = 0
        else:
            self.PkgIndex = max(
                0, min(self.PkgIndex, len(Lst) - 1)
            )

    def GoBack(self):
        """Back out one view level."""
        if self.CurrentView == VIEW_LOG:
            self._DisableFloat()
        if self.CurrentView in (VIEW_DETAIL, VIEW_LOG):
            self.CurrentView = self.PrevView
        elif self.CurrentView == VIEW_LIST:
            self.CurrentView = VIEW_ACTIONS
        self.ConfirmAction = None
        self.ConfirmMsg    = ""

    # -------------------------------------------------------------- #
    # Actions                                                          #
    # -------------------------------------------------------------- #

    def RunShellAction(self, Label, Command):
        """Launch an AptWorker and switch to LOG view."""
        TaskId = self.NextTaskId()
        self.ActiveCommand = Label
        Worker = AptWorker(self.app, TaskId, Command)
        self.StartCmdWorker(Worker)
        self.PrevView    = self.CurrentView
        self.CurrentView = VIEW_LOG
        self.LogScroll   = 0
        self._EnableFloat()

    def RunDetailFetch(self, PkgName):
        """Fetch package details and switch to DETAIL view."""
        TaskId = self.NextTaskId()
        self.DetailPkg      = PkgName
        self.RawDetailLines = []
        self.DetailLines    = []
        self.DetailScroll   = 0
        Worker = AptWorker(
            self.app,
            TaskId,
            f"apt show {shlex.quote(PkgName)}",
            Prefix="apt.detail",
        )
        self.StartCmdWorker(Worker)
        self.PrevView    = self.CurrentView
        self.CurrentView = VIEW_DETAIL

    def SetConfirm(self, Msg, Action):
        self.ConfirmMsg    = Msg
        self.ConfirmAction = Action

    def ActivateAction(self):
        """Execute the selected action bar item."""
        Idx = self.action_bar_index
        if Idx < 0 or Idx >= len(self.Actions):
            return
        Label, Command = self.Actions[Idx]

        if Command == LIST_INSTALLED:
            self.ListContext = LIST_INSTALLED
            self.CurrentView = VIEW_LIST
            self.PkgIndex    = 0
            self.SetStatus("Installed packages", "cyan")
            return

        if Command == LIST_UPGRADABLE:
            self.ListContext = LIST_UPGRADABLE
            self.CurrentView = VIEW_LIST
            self.PkgIndex    = 0
            self.SetStatus("Upgradable packages", "cyan")
            return

        if Command == "REMOVE":
            Pkg = self.SelectedPackage()
            if Pkg is None:
                self.SetStatus(
                    "Select a package first", "yellow"
                )
                return
            self.SetConfirm(
                f"Remove {Pkg}? (Y/N)",
                lambda P=Pkg: self.RunShellAction(
                    f"Remove {P}",
                    f"sudo apt remove -y {shlex.quote(P)}",
                ),
            )
            return

        if Command == "INSTALL":
            Pkg = self.SelectedPackage()
            if Pkg is None:
                self.SetStatus(
                    "Select a package first", "yellow"
                )
                return
            self.SetConfirm(
                f"Install {Pkg}? (Y/N)",
                lambda P=Pkg: self.RunShellAction(
                    f"Install {P}",
                    f"sudo apt install -y {shlex.quote(P)}",
                ),
            )
            return

        if Label == "Upgrade":
            self.SetConfirm(
                "Upgrade all packages? (Y/N)",
                lambda: self.RunShellAction(Label, Command),
            )
            return

        if Label == "Autoremove":
            self.SetConfirm(
                "Run autoremove? (Y/N)",
                lambda: self.RunShellAction(Label, Command),
            )
            return

        self.RunShellAction(Label, Command)

    def ActivateListItem(self):
        """Fetch details for the currently selected package."""
        Pkg = self.SelectedPackage()
        if Pkg:
            self.RunDetailFetch(Pkg)

    # -------------------------------------------------------------- #
    # Detail parsing helpers                                           #
    # -------------------------------------------------------------- #

    def ParseAptShow(self, RawLines):
        """Parse apt show RFC 822 output into an ordered dict.

        Handles:
          - Field: value lines
          - Continuation lines (leading whitespace)
          - Blank-line markers within a field (` .`)
        """
        Data = collections.OrderedDict()
        Current = None
        for Line in RawLines:
            if not Line.strip():
                Current = None
                continue
            if Line[0] in (" ", "\t") and Current is not None:
                Cont = Line.strip()
                if Cont == ".":
                    Data[Current] = Data[Current] + "\n"
                else:
                    Prev = Data[Current]
                    if Prev.endswith("\n"):
                        Data[Current] = Prev + Cont
                    else:
                        Data[Current] = Prev + " " + Cont
            elif ": " in Line or Line.endswith(":"):
                Key, _, Val = Line.partition(": ")
                Key = Key.strip()
                Data[Key] = Val.strip()
                Current = Key
        return Data

    def _WrapCommaList(self, Text, MaxW):
        """Wrap a comma-separated dependency string into lines."""
        Items = [I.strip() for I in Text.split(",")]
        Lines = []
        Row = ""
        for Item in Items:
            Candidate = (Row + ", " + Item) if Row else Item
            if len(Candidate) > MaxW and Row:
                Lines.append(Row)
                Row = Item
            else:
                Row = Candidate
        if Row:
            Lines.append(Row)
        return Lines

    def BuildDetailLines(self, Data, W):
        """Format a parsed apt show dict into display lines."""
        MaxW   = max(1, W - 4)
        Sep    = "\u2500" * min(MaxW, 60)
        Pkg    = Data.get("Package",        self.DetailPkg)
        Ver    = Data.get("Version",         "?")
        Arch   = Data.get("Architecture",    "?")
        Size   = Data.get("Installed-Size",  "?")
        Sec    = Data.get("Section",         "?")
        Prio   = Data.get("Priority",        "?")
        Maint  = Data.get("Maintainer",      "")
        Home   = Data.get("Homepage",        "")
        Dep    = Data.get("Depends",         "")
        Rec    = Data.get("Recommends",      "")
        Sug    = Data.get("Suggests",        "")
        Desc   = Data.get("Description",     "")

        Lines = []
        Lines.append(f"Package:   {Pkg}")
        Lines.append(f"Version:   {Ver}")
        Lines.append(
            f"Arch:      {Arch:<18}  Size:      {Size}"
        )
        Lines.append(
            f"Section:   {Sec:<18}  Priority:  {Prio}"
        )
        if Maint:
            Lines.append("")
            Lines.append(f"Maintainer:")
            Lines.append(f"  {Maint[:MaxW - 2]}")
        if Home:
            Lines.append(f"Homepage:")
            Lines.append(f"  {Home[:MaxW - 2]}")
        Lines.append("")
        Lines.append(Sep)

        def AddList(Label, Text):
            if not Text:
                return
            Lines.append(f"")
            Lines.append(f"{Label}:")
            for Chunk in self._WrapCommaList(Text, MaxW - 2):
                Lines.append(f"  {Chunk}")

        AddList("Depends",    Dep)
        AddList("Recommends", Rec)
        AddList("Suggests",   Sug)

        if Desc:
            Lines.append("")
            Lines.append("Description:")
            for Para in Desc.split("\n"):
                Para = Para.strip()
                if not Para:
                    Lines.append("")
                    continue
                Words = Para.split()
                Row = "  "
                for Word in Words:
                    if len(Row) + len(Word) + 1 > MaxW:
                        Lines.append(Row.rstrip())
                        Row = "  " + Word + " "
                    else:
                        Row += Word + " "
                if Row.strip():
                    Lines.append(Row.rstrip())

        return Lines

    # -------------------------------------------------------------- #
    # Text input hook (search)                                         #
    # -------------------------------------------------------------- #

    def handle_text(self, InputString):
        """Filter installed packages by search term."""
        Text = InputString.strip()
        if not Text:
            return
        Haystack = self.InstalledPackages or self.UpgradablePackages
        self.SearchResults = [
            N for N in Haystack if Text.lower() in N.lower()
        ]
        self.ListContext = LIST_SEARCH
        self.CurrentView = VIEW_LIST
        self.PkgIndex    = 0
        self.SetStatus(
            f"Search '{Text}': {len(self.SearchResults)} results",
            "green",
        )

    # -------------------------------------------------------------- #
    # Render entry point                                               #
    # -------------------------------------------------------------- #

    def page(self, Panel):
        H = self.h
        W = self.w
        try:
            Panel.win.erase()
        except Exception:
            pass

        if self.CurrentView == VIEW_LOG:
            # Show the previous view as a background; the float panel
            # renders the log as an overlay via PageFloat().
            if self.PrevView == VIEW_LIST:
                self.RenderList(Panel, H, W)
            else:
                self.RenderActions(Panel, H, W)
        elif self.CurrentView == VIEW_DETAIL:
            self.RenderDetail(Panel, H, W)
        elif self.CurrentView == VIEW_LIST:
            self.RenderList(Panel, H, W)
        else:
            self.RenderActions(Panel, H, W)

        if self.ConfirmAction is not None:
            self.RenderConfirm(Panel, H, W)

    # -------------------------------------------------------------- #
    # Render: ACTIONS view                                             #
    # -------------------------------------------------------------- #

    def RenderActions(self, Panel, H, W):
        self.write(Panel, 1, 2, "APT  Package Manager", color="cyan")
        self.render_action_bar(Panel, row=2)
        self.write(
            Panel, 3, 2,
            f"[ {self.ListContext} ]  "
            f"{len(self.CurrentList())} packages",
            color="blue",
        )
        ListH = max(0, H - 5)
        self.RenderPackageList(Panel, 4, ListH, W)
        self.RenderStatus(Panel, H, W)

    # -------------------------------------------------------------- #
    # Render: LIST view                                                #
    # -------------------------------------------------------------- #

    def RenderList(self, Panel, H, W):
        Header = (
            f"[ {self.ListContext} ]  "
            f"{len(self.CurrentList())} packages  "
            "(ENTER=detail  ESC=back)"
        )
        self.write(Panel, 1, 2, Header[:W - 2], color="cyan")
        self.render_action_bar(Panel, row=2)
        ListH = max(0, H - 4)
        self.RenderPackageList(Panel, 3, ListH, W)
        self.RenderStatus(Panel, H, W)

    # -------------------------------------------------------------- #
    # Render: shared package list                                      #
    # -------------------------------------------------------------- #

    def RenderPackageList(self, Panel, StartRow, ListH, W):
        Lst = self.CurrentList()
        if not Lst:
            self.write(
                Panel, StartRow, 2,
                "(empty — run Update or select a list)",
                color="yellow",
            )
            return
        self.ClampPkgIndex()
        Top    = max(0, self.PkgIndex - ListH // 2)
        MaxTop = max(0, len(Lst) - ListH)
        if Top > MaxTop:
            Top = MaxTop
        Visible = Lst[Top: Top + ListH]
        for Offset, Name in enumerate(Visible):
            Row = StartRow + Offset
            if Row >= StartRow + ListH:
                break
            AbsIdx   = Top + Offset
            Selected = (AbsIdx == self.PkgIndex)
            Cursor   = ">> " if Selected else "   "
            Color    = "yellow" if Selected else None
            Label    = (Cursor + Name)[: W - 4]
            self.write(Panel, Row, 2, Label, color=Color)

    # -------------------------------------------------------------- #
    # Render: status bar                                               #
    # -------------------------------------------------------------- #

    def RenderStatus(self, Panel, H, W):
        Msg = self.StatusMsg[: W - 14]
        self.write(Panel, H - 2, 2, Msg, color=self.StatusColor)
        Running = (
            self.CurrentWorker is not None
            and self.CurrentWorker.is_alive()
        )
        if Running:
            self.write(Panel, H - 2, W - 12, "[running]",
                       color="yellow")

    # -------------------------------------------------------------- #
    # Floating panel hook — LOG overlay                               #
    # -------------------------------------------------------------- #

    def PageFloat(self, Panel):
        """Render log content into the backend floating panel."""
        H, W = Panel.dims[0], Panel.dims[1]
        self.RenderLog(Panel, H, W)

    # -------------------------------------------------------------- #
    # Render: LOG view                                                 #
    # -------------------------------------------------------------- #

    def RenderLog(self, Panel, H, W):
        self.write(
            Panel, 1, 2,
            "LOG  (ESC=back  HOME=top  END=bottom  C=cancel)",
            color="cyan",
        )
        Lines = list(self.LogLines)
        ViewH  = max(0, H - 3)
        MaxScr = max(0, len(Lines) - ViewH)
        if self.LogScroll > MaxScr:
            self.LogScroll = MaxScr
        Visible = Lines[self.LogScroll: self.LogScroll + ViewH]
        for Offset, Line in enumerate(Visible):
            Row = 2 + Offset
            if Row >= H - 1:
                break
            Color = "red" if Line.startswith("ERROR") else None
            self.write(Panel, Row, 1, Line[: W - 2], color=Color)
        self.RenderStatus(Panel, H, W)

    # -------------------------------------------------------------- #
    # Render: DETAIL view                                              #
    # -------------------------------------------------------------- #

    def RenderDetail(self, Panel, H, W):
        Header = (
            f"DETAIL: {self.DetailPkg}"
            "  (ESC=back  HOME/END=scroll)"
        )
        self.write(Panel, 1, 2, Header[:W - 2], color="cyan")
        ViewH  = max(0, H - 3)
        Lines  = self.DetailLines
        MaxScr = max(0, len(Lines) - ViewH)
        if self.DetailScroll > MaxScr:
            self.DetailScroll = MaxScr
        Visible = Lines[
            self.DetailScroll: self.DetailScroll + ViewH
        ]
        FieldHeaders = (
            "Package:", "Version:", "Arch:", "Section:",
            "Maintainer:", "Homepage:",
        )
        SectionHeaders = (
            "Depends:", "Recommends:", "Suggests:", "Description:",
        )
        for Offset, Line in enumerate(Visible):
            Row = 2 + Offset
            if Row >= H - 1:
                break
            Stripped = Line.lstrip()
            if any(Stripped.startswith(F) for F in FieldHeaders):
                Color = "cyan"
            elif any(Stripped.startswith(S) for S in SectionHeaders):
                Color = "yellow"
            elif Stripped.startswith("\u2500"):
                Color = "blue"
            else:
                Color = None
            self.write(Panel, Row, 1, Line[:W - 2], color=Color)
        self.RenderStatus(Panel, H, W)

    # -------------------------------------------------------------- #
    # Render: confirmation overlay                                     #
    # -------------------------------------------------------------- #

    def RenderConfirm(self, Panel, H, W):
        Row  = H // 2
        Box  = f"  {self.ConfirmMsg}  "[: W - 4]
        Col  = max(2, (W - len(Box)) // 2)
        self.write(Panel, Row, Col, Box, color="red")

    # -------------------------------------------------------------- #
    # Key callbacks                                                    #
    # -------------------------------------------------------------- #

    @callback(APT_ID, Keys.UP)
    def OnUp(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            return
        if self.CurrentView == VIEW_LOG:
            if self.LogScroll > 0:
                self.LogScroll -= 1
            return
        if self.CurrentView == VIEW_DETAIL:
            if self.DetailScroll > 0:
                self.DetailScroll -= 1
            return
        if self.PkgIndex > 0:
            self.PkgIndex -= 1

    @callback(APT_ID, Keys.DOWN)
    def OnDown(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            return
        if self.CurrentView == VIEW_LOG:
            ViewH = max(1, self.h - 3)
            MaxScr = max(0, len(self.LogLines) - ViewH)
            if self.LogScroll < MaxScr:
                self.LogScroll += 1
            return
        if self.CurrentView == VIEW_DETAIL:
            ViewH = max(1, self.h - 3)
            MaxScr = max(0, len(self.DetailLines) - ViewH)
            if self.DetailScroll < MaxScr:
                self.DetailScroll += 1
            return
        Lst = self.CurrentList()
        if self.PkgIndex < len(Lst) - 1:
            self.PkgIndex += 1

    @callback(APT_ID, Keys.LEFT)
    def OnLeft(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            return
        if self.CurrentView in (VIEW_LOG, VIEW_DETAIL):
            return
        self.action_bar_index -= 1
        if self.action_bar_index < 0:
            self.action_bar_index = len(self.action_bar_items) - 1

    @callback(APT_ID, Keys.RIGHT)
    def OnRight(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            return
        if self.CurrentView in (VIEW_LOG, VIEW_DETAIL):
            return
        self.action_bar_index += 1
        if self.action_bar_index >= len(self.action_bar_items):
            self.action_bar_index = 0

    @callback(APT_ID, Keys.ENTER)
    def OnEnter(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            return
        if self.CurrentView in (VIEW_LOG, VIEW_DETAIL):
            return
        if self.CurrentView == VIEW_LIST:
            self.ActivateListItem()
        else:
            self.ActivateAction()

    @callback(APT_ID, Keys.ESC)
    def OnEsc(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            self.ConfirmAction = None
            self.ConfirmMsg    = ""
            self.SetStatus("Cancelled", "yellow")
            return
        self.GoBack()

    @callback(APT_ID, Keys.HOME)
    def OnHome(self, *args, **kwargs):
        if self.CurrentView == VIEW_LOG:
            self.LogScroll = 0
        elif self.CurrentView == VIEW_DETAIL:
            self.DetailScroll = 0
        else:
            self.PkgIndex = 0

    @callback(APT_ID, Keys.END)
    def OnEnd(self, *args, **kwargs):
        if self.CurrentView == VIEW_LOG:
            ViewH = max(1, self.h - 3)
            self.LogScroll = max(0, len(self.LogLines) - ViewH)
        elif self.CurrentView == VIEW_DETAIL:
            ViewH = max(1, self.h - 3)
            self.DetailScroll = max(
                0, len(self.DetailLines) - ViewH
            )
        else:
            Lst = self.CurrentList()
            if Lst:
                self.PkgIndex = len(Lst) - 1

    @callback(APT_ID, Keys.L)
    def OnL(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            return
        if self.CurrentView != VIEW_LOG:
            self.PrevView    = self.CurrentView
            self.CurrentView = VIEW_LOG
            self._EnableFloat()

    @callback(APT_ID, Keys.C)
    def OnC(self, *args, **kwargs):
        if self.ConfirmAction is not None:
            return
        self.CancelWorker()

    @callback(APT_ID, Keys.Y)
    def OnY(self, *args, **kwargs):
        if self.ConfirmAction is None:
            return
        Action = self.ConfirmAction
        self.ConfirmAction = None
        self.ConfirmMsg    = ""
        Action()

    @callback(APT_ID, Keys.N)
    def OnN(self, *args, **kwargs):
        if self.ConfirmAction is None:
            return
        self.ConfirmAction = None
        self.ConfirmMsg    = ""
        self.SetStatus("Cancelled", "yellow")

    # -------------------------------------------------------------- #
    # Cleanup                                                          #
    # -------------------------------------------------------------- #

    def end_safely(self):
        self.CancelWorker()
        super().end_safely()