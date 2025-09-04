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
        self.write(panel, self.index, 2, "Status Window", "yellow")
        self.index += 2
        status = get_status()
        running = status.get("running")
        host = status.get("host")
        port = status.get("port")
        clients = status.get("clients")
        self.write(
            panel,
            self.index,
            4,
            f"Server: {'RUNNING' if running else 'STOPPED'} @ {host}:{port} | clients: {clients}",
            "green" if running else "red",
        )
        self.index += 2
        for i, el in enumerate(self.elements):
            color = "green" if self.cur_el == i else "white"
            self.write(panel, self.index, 4, el, color)
            self.index += 1
        self.index += 1
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
            ok, error = server_start(sink=self.print, quiet=True, verbose=False)
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
