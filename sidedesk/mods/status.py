import random
from deskapp import Module, callback, Keys
from sidedesk.server import (
    start as server_start,
    stop as server_stop,
    restart as server_restart,
    get_status,
)


Status_ID = random.random()


class Status(Module):
    name = "Status"

    def __init__(self, app):
        super().__init__(app, Status_ID)
        self.elements = ["Start Server", "Stop Server", "Restart Server"]
        self.cur_el = 0
        self.last_action = ""

    def page(self, panel):
        self.index = 2
        # Heading
        try:
            panel.win.addstr(self.index, 2, " Status ", self.front.color_status_banner)
        except Exception:
            self.write(panel, self.index, 2, "Status", "blue")
        self.index += 2

        status = get_status() or {}
        running = status.get("running")
        host = status.get("host", "?")
        port = status.get("port", 0)
        clients = status.get("clients", 0)
        pid = status.get("pid")
        cpu = status.get("cpu_percent")
        rss = status.get("rss_bytes")
        uptime = status.get("uptime_sec")
        tx = status.get("net_bytes_sent")
        rx = status.get("net_bytes_recv")

        # Primary line
        try:
            color = self.front.color_status_ok if running else self.front.color_status_bad
            panel.win.addstr(self.index, 4, f"Server: {'RUNNING' if running else 'STOPPED'} @ {host}:{port} | clients: {clients}", color)
        except Exception:
            self.write(panel, self.index, 4, f"Server: {'RUNNING' if running else 'STOPPED'} @ {host}:{port} | clients: {clients}", "green" if running else "red")
        self.index += 2

        if running:
            if pid is not None:
                self.write(panel, self.index, 6, f"PID: {pid}", "white"); self.index += 1
            if cpu is not None:
                self.write(panel, self.index, 6, f"CPU: {cpu:.1f}%", "white"); self.index += 1
            if rss is not None:
                mb = rss / (1024*1024)
                self.write(panel, self.index, 6, f"Memory RSS: {mb:.1f} MiB", "white"); self.index += 1
            if uptime is not None:
                try:
                    total = int(float(uptime))
                    days, rem = divmod(total, 86400)
                    hours, rem = divmod(rem, 3600)
                    mins, secs = divmod(rem, 60)
                    parts = []
                    if days: parts.append(f"{days}d")
                    parts.append(f"{hours}h")
                    parts.append(f"{mins}m")
                    parts.append(f"{secs}s")
                    up_str = " ".join(parts)
                except Exception:
                    up_str = f"{uptime} s"
                self.write(panel, self.index, 6, f"Uptime: {up_str}", "white"); self.index += 1
            if rx is not None or tx is not None:
                try:
                    rx_mb = (rx or 0) / (1024*1024)
                    tx_mb = (tx or 0) / (1024*1024)
                    self.write(panel, self.index, 6, f"Net RX/TX: {rx_mb:.1f} / {tx_mb:.1f} MB", "white"); self.index += 1
                except Exception:
                    pass

        # Action buttons
        for i, el in enumerate(self.elements):
            color = "green" if self.cur_el == i else "white"
            self.write(panel, self.index, 4, el, color)
            self.index += 1
        self.index += 1
        try:
            panel.win.addstr(self.index, 4, "Use UP/DOWN to select, ENTER to activate", self.front.color_accent)
        except Exception:
            self.write(panel, self.index, 4, "Use UP/DOWN to select, ENTER to activate", "yellow")
        self.index += 1
        if self.last_action:
            self.write(panel, self.index, 4, f"Last: {self.last_action}", "blue")

    @callback(Status_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        action = self.elements[self.cur_el]
        ok = False
        error = None
        if action == "Start Server":
            ok, error = server_start(sink=self.print, quiet=True, verbose=False, detach=True)
        elif action == "Stop Server":
            ok, error = server_stop()
        elif action == "Restart Server":
            ok, error = server_restart()
        self.last_action = f"{action} -> {'OK' if ok else 'FAIL'}"
        if error:
            self.last_action += f" | Error: {error}"
        self.print(self.last_action)

    @callback(Status_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        self.cur_el = (self.cur_el - 1) % len(self.elements)

    @callback(Status_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        self.cur_el = (self.cur_el + 1) % len(self.elements)

    def on_open(self):
        status = get_status()
        self.print(
            f"[Server] {'RUNNING' if status.get('running') else 'STOPPED'} @ {status.get('host')}:{status.get('port')} clients={status.get('clients')}"
        )
