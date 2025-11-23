import random
import threading
import subprocess
import shlex
import time

try:
    import apt  # type: ignore
    import apt.progress.base as apt_progress
    HAS_PYTHON_APT = True
except Exception:
    HAS_PYTHON_APT = False
from deskapp import Module, callback, Keys
from deskapp.src.events import BaseWorker


APT_ID = random.random()


class AptWorker(BaseWorker):
    """Worker to execute a single APT command and stream output.

    Emits events:
        apt.command.start
        apt.command.output
        apt.command.done
        apt.command.error
    """

    def __init__(self, app, task_id, command):
        super().__init__(app, name="APT")
        self.task_id = task_id
        self.command = command
        self.process = None

    def work(self):
        self.emit(
            "apt.command.start",
            {"id": self.task_id, "command": self.command},
        )

        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except Exception as e:
            self.emit(
                "apt.command.error",
                {"id": self.task_id, "error": str(e)},
            )
            return

        def reader(stream, stream_name):
            try:
                for line in stream:
                    if self.should_stop:
                        break
                    self.emit(
                        "apt.command.output",
                        {
                            "id": self.task_id,
                            "stream": stream_name,
                            "line": line.rstrip("\n"),
                        },
                    )
            except Exception as e:
                self.emit(
                    "apt.command.error",
                    {"id": self.task_id, "error": str(e)},
                )

        threads = []
        if self.process.stdout is not None:
            t_out = threading.Thread(
                target=reader,
                args=(self.process.stdout, "stdout"),
                daemon=True,
            )
            t_out.start()
            threads.append(t_out)
        if self.process.stderr is not None:
            t_err = threading.Thread(
                target=reader,
                args=(self.process.stderr, "stderr"),
                daemon=True,
            )
            t_err.start()
            threads.append(t_err)

        rc = None
        try:
            rc = self.process.wait()
        except Exception as e:
            self.emit(
                "apt.command.error",
                {"id": self.task_id, "error": str(e)},
            )

        for t in threads:
            t.join(timeout=0.2)

        self.emit(
            "apt.command.done",
            {"id": self.task_id, "rc": rc},
        )


class AptApiWorker(BaseWorker):
    """Worker that uses python-apt API for update/upgrade.

    Emits:
        apt.progress.update  (progress: 0.0-1.0)
        apt.command.done     (rc: 0 on success, 1 on failure)
    """

    def __init__(self, app, task_id, action: str):
        super().__init__(app, name="APTAPI")
        self.task_id = task_id
        self.action = action  # 'update' or 'upgrade'

    def work(self):
        if not HAS_PYTHON_APT:
            # Fallback: nothing to do, signal error-like done.
            self.emit(
                "apt.command.done",
                {"id": self.task_id, "rc": 1},
            )
            return

        class Progress(apt_progress.OpProgress):
            def __init__(self, outer):
                super().__init__()
                self.outer = outer

            def update(self, percent=None):  # type: ignore[override]
                try:
                    if percent is None:
                        return
                    p = max(0.0, min(100.0, float(percent))) / 100.0
                    self.outer.emit(
                        "apt.progress.update",
                        {"id": self.outer.task_id, "progress": p},
                    )
                except Exception:
                    pass

        cache = apt.Cache()
        rc = 1
        try:
            if self.action == "update":
                self.emit(
                    "apt.command.output",
                    {
                        "id": self.task_id,
                        "stream": "stdout",
                        "line": "[APT] Updating package lists...",
                    },
                )
                cache.update(Progress(self))
                cache.open(None)
            elif self.action == "upgrade":
                self.emit(
                    "apt.command.output",
                    {
                        "id": self.task_id,
                        "stream": "stdout",
                        "line": "[APT] Updating package lists before upgrade...",
                    },
                )
                cache.update(Progress(self))
                cache.open(None)
                self.emit(
                    "apt.command.output",
                    {
                        "id": self.task_id,
                        "stream": "stdout",
                        "line": "[APT] Marking upgradable packages...",
                    },
                )
                cache.upgrade()
                self.emit(
                    "apt.command.output",
                    {
                        "id": self.task_id,
                        "stream": "stdout",
                        "line": "[APT] Committing upgrade; this may take a while...",
                    },
                )
                cache.commit(Progress(self), None)
                self.emit(
                    "apt.progress.update",
                    {"id": self.task_id, "progress": 1.0},
                )
                self.emit(
                    "apt.command.output",
                    {
                        "id": self.task_id,
                        "stream": "stdout",
                        "line": "[APT] Upgrade finished.",
                    },
                )
            rc = 0
        except Exception as e:
            self.emit(
                "apt.command.error",
                {"id": self.task_id, "error": str(e)},
            )
        finally:
            self.emit(
                "apt.command.done",
                {"id": self.task_id, "rc": rc},
            )


class APT(Module):
    name = "APT"

    def __init__(self, app):
        super().__init__(app, APT_ID)
        self.tasks = []
        self.next_task_id = 1
        self.selected = 0
        self.current_worker = None

        # Update-specific state
        self.update_output = []  # raw stdout lines from last APT task(s)
        self.update_scroll = 0   # vertical scroll for 3-line window
        self.update_packages = []  # full list of upgradable package names
        self.filtered_packages = []  # current filtered view for scroller
        self.pkg_index = 0       # selection in package list (including "Upgrade all")
        self.update_progress = 0.0  # 0.0 - 1.0 for info-panel progress bar
        self.update_last_time = 0.0  # last time we saw update activity
        # Which scroller ENTER should apply to: 'actions' or 'packages'
        self.focus = "actions"

        self.actions = [
            ("Update", "sudo apt update"),
            ("Upgrade", "sudo apt upgrade -y"),
            ("Search", "SEARCH"),
            ("Install", "INSTALL"),
        ]

        # Action bar shows high-level operations; selection is driven by
        # LEFT/RIGHT and fired with ENTER.
        self.action_bar_items = [label for (label, _cmd) in self.actions]

        self.on_event("apt.command.start", self._on_cmd_start)
        self.on_event("apt.command.output", self._on_cmd_output)
        self.on_event("apt.command.done", self._on_cmd_done)
        self.on_event("apt.command.error", self._on_cmd_error)
        self.on_event("apt.progress.update", self._on_progress_update)

    def end_safely(self):
        if self.current_worker is not None:
            self.current_worker.stop(timeout=1.0)
        super().end_safely()

    def _add_task(self, label, command):
        task_id = self.next_task_id
        self.next_task_id += 1
        task = {
            "id": task_id,
            "label": label,
            "command": command,
            "status": "pending",
            "rc": None,
            "stdout": [],
            "stderr": [],
        }
        self.tasks.append(task)
        self.scroll_elements = [t["label"] for t in self.tasks]
        if self.selected >= len(self.tasks):
            self.selected = max(0, len(self.tasks) - 1)
        return task

    def _find_task(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                return t
        return None

    def _start_task(self, task):
        if self.current_worker is not None and self.current_worker.is_alive():
            self.print("APT: A command is already running.")
            return
        task["status"] = "running"
        # Use python-apt API only for 'update' so we can still
        # get a clean package list without risking UI lockups.
        if (
            HAS_PYTHON_APT
            and task["command"].startswith("sudo apt ")
            and "update" in task["command"]
        ):
            self.current_worker = AptApiWorker(self.app, task["id"], "update")
        else:
            # All other commands (including Upgrade) run via subprocess.
            self.current_worker = AptWorker(self.app, task["id"], task["command"])
        self.current_worker.start()
        self.print(f"APT: Started '{task['label']}'")

    def _on_cmd_start(self, event):
        task = self._find_task(event["data"].get("id"))
        if task is not None:
            task["status"] = "running"

    def _on_cmd_output(self, event):
        data = event["data"]
        task = self._find_task(data.get("id"))
        if task is None:
            return
        line = data.get("line", "")
        if data.get("stream") == "stderr":
            task["stderr"].append(line)
        else:
            task["stdout"].append(line)
            # Track output for the most recent APT task in the page log.
            # We treat any task with a label ending in "(apt)" or starting
            # with "Install:" / "Upgrade all" as relevant to the log.
            label = task.get("label", "")
            if (
                label.endswith("(apt)")
                or label.startswith("Install:")
                or label.startswith("Upgrade all")
            ):
                self.update_output.append(line)
                # Always auto-scroll to the latest lines (5-line window
                # in page(), but we keep this local window size small).
                window = 5
                filtered = [
                    l for l in self.update_output
                    if "tty" not in l.lower() and "cli" not in l.lower()
                ]
                max_scroll = max(0, len(filtered) - window)
                self.update_scroll = max_scroll
                self.update_last_time = time.time()
                # Also mirror to messages area for full visibility.
                self.print(f"APT: {label}: {line}")

    def _on_cmd_done(self, event):
        data = event["data"]
        task = self._find_task(data.get("id"))
        if task is not None:
            task["status"] = "done"
            task["rc"] = data.get("rc")
            label = task.get("label", "")
            # When an update task finishes, refresh derived package list
            if label.startswith("Update (apt)"):
                self._refresh_update_state(task)
                self.update_progress = 1.0
                self.update_last_time = time.time()
            # For other APT tasks, just mark the bar as complete briefly
            elif (
                label.endswith("(apt)")
                or label.startswith("Install:")
                or label.startswith("Upgrade all")
            ):
                self.update_progress = 1.0
                self.update_last_time = time.time()
        self.current_worker = None

    def _on_progress_update(self, event):
        data = event["data"]
        task = self._find_task(data.get("id"))
        if task is None:
            return
        # Trust the real progress from python-apt
        self.update_progress = float(data.get("progress", 0.0))
        self.update_last_time = time.time()

    def _refresh_update_state(self, task):
        """Derive cleaned update output and package list from an update task."""
        # Reset scroll when a new update completes
        self.update_scroll = 0
        self.pkg_index = 0

        # Use stdout from the completed task as canonical update output
        self.update_output = list(task.get("stdout", []))

        # Prefer python-apt API to derive upgradable packages.
        self.update_packages = []
        if HAS_PYTHON_APT:
            try:
                cache = apt.Cache()
                cache.update()  # ensure cache is current
                cache.open(None)
                upgradable = [
                    pkg for pkg in cache
                    if pkg.is_installed and pkg.is_upgradable
                ]
                names = {pkg.name for pkg in upgradable}
                self.update_packages = sorted(names, key=str.lower)
            except Exception as e:
                self.print(f"APT python-apt error: {e}")
        # Fallback: keep filtered list in sync
        self.filtered_packages = list(self.update_packages)

    def PageInfo(self, panel):
        """Temporarily take over info panel to show update progress.

        While an Update (apt) task is running, or for 5 seconds after it
        completes, we draw a vertical progress bar and return a truthy
        value so the backend does NOT call default_page_info(). Once the
        5s window passes, we return None so the normal info content shows
        again.
        """
        now = time.time()

        # Determine if we are in an active "progress bar" window
        active_window = False
        running = any(
            t["status"] == "running" and (
                t["label"].endswith("(apt)")
                or t["label"].startswith("Install:")
                or t["label"].startswith("Upgrade all")
            )
            for t in self.tasks
        )
        if running:
            active_window = True
            # Cheap heuristic: map number of lines to a 0.0-1.0 range.
            # Cap at 200 lines for now.
            lines = len(self.update_output)
            self.update_progress = min(1.0, lines / 200.0)
        elif self.update_last_time and (now - self.update_last_time) <= 5.0:
            # Recently finished; keep bar visible for a few seconds
            active_window = True

        if not active_window:
            # Give control back to default info panel behavior
            return None

        # Clear inside of info panel, then draw bar
        try:
            panel.win.erase()
            if self.app.show_box:
                panel.win.box()
        except Exception:
            pass

        # Use a horizontal left-to-right progress bar across the panel.
        self.render_horizontal_progress(panel, self.update_progress,
                                        label="Update", row=2)
        # Non-None return tells backend that we handled the info panel.
        return True

    def _on_cmd_error(self, event):
        data = event["data"]
        task = self._find_task(data.get("id"))
        if task is not None:
            task["status"] = "error"
            task["stderr"].append(data.get("error", ""))
        self.current_worker = None

    def page(self, panel):
        h = self.h
        w = self.w

        self.write(panel, 1, 2, "APT Helper", color="cyan")
        self.render_action_bar(panel, row=2)
        # --- 5-line auto-scrolling update output ---
        out_start = 4
        # Header intentionally left blank per design

        # Filter out the CLI warning line (contains "This must be run as root"
        # or similar no-tty text) and take a tail slice for scrolling.
        filtered = [
            line for line in self.update_output
            if "tty" not in line.lower() and "cli" not in line.lower()
        ]
        window = 5
        if filtered:
            # Clamp scroll and render 3-line window
            max_scroll = max(0, len(filtered) - window)
            if self.update_scroll > max_scroll:
                self.update_scroll = max_scroll
            start = self.update_scroll
            end = start + window
            lines = filtered[start:end]
            for i, line in enumerate(lines):
                self.write(panel, out_start + i, 2, line[: w - 4])

        pkg_start = out_start + window + 1

        # --- 5-line scrolling package list ---
        self.write(panel, pkg_start, 2, "Packages:", color="blue")
        pkg_start += 1

        entries = ["Upgrade all"] + self.filtered_packages
        if entries:
            # Clamp selection
            if self.pkg_index < 0:
                self.pkg_index = 0
            if self.pkg_index >= len(entries):
                self.pkg_index = len(entries) - 1

            window = 5
            # Center selection within 5-line window when possible
            top = max(0, self.pkg_index - 2)
            max_top = max(0, len(entries) - window)
            if top > max_top:
                top = max_top
            visible = entries[top : top + window]

            for idx, name in enumerate(visible):
                y = pkg_start + idx
                cursor_index = top + idx
                cursor = ">> " if cursor_index == self.pkg_index else "   "
                color = "yellow" if cursor_index == self.pkg_index else None
                label = f"{cursor}{name}"
                self.write(panel, y, 2, label[: w - 4], color=color)

    def _queue_preset_action(self, index):
        if index < 0 or index >= len(self.actions):
            return
        label, command = self.actions[index]
        label = f"{label} (apt)"
        if command == "SEARCH":
            self.print("Tab, type search term, Enter, then use results.")
            return
        if command == "INSTALL":
            # Switch to text input mode so the user can type a package
            # name in the footer; APT.handle_text() will consume it.
            self.app.front.key_mode = True
            self.print("Type package name, press Enter to install.")
            return
        task = self._add_task(label, command)
        self._start_task(task)

    @callback(APT_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        # ENTER applies to whichever scroller was last moved.
        if self.focus == "packages":
            entries = ["Upgrade all"] + self.filtered_packages
            if not entries:
                return
            if self.pkg_index < 0 or self.pkg_index >= len(entries):
                return
            name = entries[self.pkg_index]
            if self.pkg_index == 0:
                label = "Upgrade all (apt)"
                cmd = "sudo apt upgrade"
            else:
                label = f"Install: {name}"
                cmd = f"sudo apt install {shlex.quote(name)}"
            task = self._add_task(label, cmd)
            self._start_task(task)
        else:
            # ENTER activates the highlighted action bar item (Update/Upgrade/...).
            if self.action_bar_items:
                self._queue_preset_action(self.action_bar_index)

    @callback(APT_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        # Scroll within the 5-line package list.
        self.focus = "packages"
        if self.pkg_index > 0:
            self.pkg_index -= 1

    @callback(APT_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        entries_len = 1 + len(self.filtered_packages)
        if entries_len == 0:
            return
        self.focus = "packages"
        if self.pkg_index < entries_len - 1:
            self.pkg_index += 1

    @callback(APT_ID, Keys.HOME)
    def on_home(self, *args, **kwargs):
        if not self.update_output:
            return
        # HOME no longer affects update_output auto-scroll; keep as no-op
        return

    @callback(APT_ID, Keys.END)
    def on_end(self, *args, **kwargs):
        if not self.update_output:
            return
        # END no longer affects update_output auto-scroll; keep as no-op
        return

    def handle_text(self, input_string: str):
        """Use text input for search/install depending on focused action.

        - If action bar is on Search: filter update_packages by substring.
        - If action bar is on Install: queue an install task for the name.
        """
        text = input_string.strip()
        if not text:
            return

        action_label = None
        if 0 <= self.action_bar_index < len(self.actions):
            action_label = self.actions[self.action_bar_index][0]

        if action_label == "Search":
            # Simple case-insensitive substring match over update_packages
            haystack = self.update_packages or []
            self.filtered_packages = [
                name for name in haystack
                if text.lower() in name.lower()
            ] or list(self.update_packages)
            self.pkg_index = 0
            self.focus = "packages"
            self.print(f"APT search: filtered to {len(self.filtered_packages)} packages")
        elif action_label == "Install":
            label = f"Install: {text}"
            cmd = f"sudo apt install {shlex.quote(text)}"
            task = self._add_task(label, cmd)
            self._start_task(task)
        else:
            # Fallback to base behavior
            super().handle_text(input_string)

    @callback(APT_ID, Keys.LEFT)
    def on_left(self, *args, **kwargs):
        if not self.action_bar_items:
            return
        self.focus = "actions"
        self.action_bar_index -= 1
        if self.action_bar_index < 0:
            self.action_bar_index = len(self.action_bar_items) - 1

    @callback(APT_ID, Keys.RIGHT)
    def on_right(self, *args, **kwargs):
        if not self.action_bar_items:
            return
        self.focus = "actions"
        self.action_bar_index += 1
        if self.action_bar_index >= len(self.action_bar_items):
            self.action_bar_index = 0