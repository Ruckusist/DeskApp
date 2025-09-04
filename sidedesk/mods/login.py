
import random
from deskapp import Module, callback, Keys
from sidedesk.server import get_status as server_status, start as server_start
from sidedesk.client.manager import init_app as client_init, login as client_login

Login_ID = random.random()
class Login(Module):
    name = "Login"
    def __init__(self, app):
        super().__init__(app, Login_ID)
        self.username = "test"
        self.server = "localhost"
        # Initialize client manager with app sink and shared data store
        try:
            client_init(self.print, self.app.data)
        except Exception:
            pass
        self.cur_el = 0
        self.elements = ["Username", "Server", "Log In"]
        self.input_string = ""

    def page(self, panel):
        self.index = 2
        self.write(panel, self.index, 2, "Sidedesk Chat Login", "yellow")
        self.index += 2
        self.write(panel, self.index, 4, f"Username: {self.username}", "white" if self.cur_el != 0 else "green")
        self.index += 1
        # Reflect the actual server port from Status manager
        try:
            port = server_status().get('port', 28080)
        except Exception:
            port = 28080
        self.write(panel, self.index, 4, f"Server:   {self.server}:{port}", "white" if self.cur_el != 1 else "green")
        self.index += 1
        self.write(panel, self.index, 4, "[ Log In ]" if self.cur_el == 2 else "Log In", "green" if self.cur_el == 2 else "white")
        self.index += 2
        self.write(panel, self.index, 4, "Use UP/DOWN to move, ENTER to log in", "yellow")

    def string_decider(self, input_string):
        if self.cur_el == 0:
            self.username = input_string or self.username
        elif self.cur_el == 1:
            # Accept host or host:port
            value = (input_string or self.server).strip()
            self.server = value
        self.input_string = ""
        if self.cur_el < 2:
            self.print(f"Set {self.elements[self.cur_el]} to {input_string}")


    @callback(Login_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.cur_el == 2:
            status = server_status()
            if not status.get('running'):
                ok, err = server_start(sink=self.print, quiet=True, verbose=False)
                self.print(f"Server start: {'OK' if ok else 'FAIL'}{f' ({err})' if err else ''}")
                status = server_status()
            host = self.server or status.get('host', 'localhost')
            port = status.get('port', 28080)
            # If server entry includes :port, honor it
            if ':' in host:
                try:
                    h, p = host.split(':', 1)
                    host = h
                    port = int(p)
                except Exception:
                    pass
            ok, err = client_login(host=host, port=port, username=self.username)
            if ok:
                self.print(f"Logged in as {self.username} @ {host}:{port}")
            else:
                self.print(f"Login failed: {err}")
        # Otherwise, ENTER does nothing
    @callback(Login_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        self.cur_el = (self.cur_el - 1) % len(self.elements)

    @callback(Login_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        self.cur_el = (self.cur_el + 1) % len(self.elements)

