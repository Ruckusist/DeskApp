"""SideDesk login module.

Updated 2025-10-06 by GitHub Copilot to default post-login modules when
needed so the additional panels appear immediately after authentication.
"""

import random

from deskapp import Module, callback, Keys
from sidedesk.server import (
    get_status as server_status,
    start as server_start,
)
from sidedesk.client.manager import (
    init_app as client_init,
    login as client_login,
)

Login_ID = random.random()
class Login(Module):
    name = "Login"
    def __init__(self, app):
        super().__init__(app, Login_ID)
        self.username = "dude"
        self.password = "pass"
        self.server = "localhost"
        # Initialize client manager with app sink and shared data store
        try:
            client_init(self.print, self.app.data)
        except Exception:
            pass
        self.cur_el = 0
        self.elements = ["Username", "Password", "Server", "Log In"]
        self.input_string = ""

    def page(self, panel):
        self.index = 2
        self.write(
            panel, self.index, 2, "Sidedesk Chat Login", "yellow"
        )
        self.index += 2
        self.write(
            panel, self.index, 4,
            f"Username: {self.username}",
            "white" if self.cur_el != 0 else "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 4,
            f"Password: {'*' * len(self.password)}",
            "white" if self.cur_el != 1 else "green"
        )
        self.index += 1
        # Reflect the actual server port from Status manager
        try:
            port = server_status().get('port', 28080)
        except Exception:
            port = 28080
        self.write(
            panel, self.index, 4,
            f"Server:   {self.server}:{port}",
            "white" if self.cur_el != 2 else "green"
        )
        self.index += 1
        self.write(
            panel, self.index, 4,
            "[ Log In ]" if self.cur_el == 3 else "Log In",
            "green" if self.cur_el == 3 else "white"
        )
        self.index += 2
        self.write(
            panel, self.index, 4,
            "Use UP/DOWN to move, ENTER to log in", "yellow"
        )

    def string_decider(self, input_string):
        if self.cur_el == 0:
            self.username = input_string or self.username
        elif self.cur_el == 1:
            self.password = input_string or self.password
        elif self.cur_el == 2:
            # Accept host or host:port
            value = (input_string or self.server).strip()
            self.server = value
        self.input_string = ""
        if self.cur_el < 3:
            self.print(
                f"Set {self.elements[self.cur_el]} to {input_string}"
            )


    @callback(Login_ID, Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.cur_el == 3:
            self.print("=== LOGIN ATTEMPT ===")
            status = server_status()
            self.print(f"Server status: {status.get('running')}")
            if not status.get('running'):
                self.print("Starting server...")
                ok, err = server_start(
                    sink=self.print, quiet=True, verbose=False
                )
                self.print(
                    f"Server start: {'OK' if ok else 'FAIL'}"
                    f"{f' ({err})' if err else ''}"
                )
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
            # Use configured username and password
            username = self.username or 'dude'
            password = self.password or 'pass'
            self.print(
                f"Attempting login: {username} @ {host}:{port}"
            )
            ok, err = client_login(
                host=host, port=port, username=username,
                password=password
            )
            self.print(f"Login result: ok={ok}, err={err}")
            if ok:
                self.print(f">>> Logged in as {username} @ {host}:{port}")
                # Add post-login modules to menu
                post_login_mod_classes = self.app.data.get(
                    "post_login_modules", []
                )
                if not post_login_mod_classes:
                    from sidedesk import (
                        AI,
                        Chat,
                        Log,
                        Settings,
                        Test,
                        Users,
                    )

                    post_login_mod_classes = [
                        Users,
                        Chat,
                        AI,
                        Log,
                        Settings,
                        Test,
                    ]
                    self.app.data["post_login_modules"] = (
                        post_login_mod_classes
                    )
                self.print(
                    f">>> Adding {len(post_login_mod_classes)} modules"
                )
                self.print(
                    f">>> Current menu has {len(self.app.menu)} items"
                )
                self.print(
                    f">>> Available panels before: "
                    f"{list(self.app.logic.available_panels.keys())}"
                )
                added_count = 0
                for ModClass in post_login_mod_classes:
                    # Check if this module class is already in menu
                    if ModClass not in self.app.menu:
                        # Add class to menu
                        self.app.menu.append(ModClass)
                        self.print(
                            f">>> Appended {ModClass.name} to menu"
                        )
                        # Setup the module (this will instantiate it)
                        try:
                            self.print(
                                f">>> Calling setup_mod({ModClass.name})..."
                            )
                            self.app.back.setup_mod(ModClass)
                            self.print(
                                f">>> Setup {ModClass.name} complete"
                            )
                            added_count += 1
                        except Exception as e:
                            self.print(
                                f"!!! Error adding {ModClass.__name__}: {e}"
                            )
                            import traceback
                            self.print(f"!!! {traceback.format_exc()}")
                    else:
                        self.print(
                            f">>> Skipped {ModClass.name} (already in menu)"
                        )
                self.print(
                    f">>> Total modules added: {added_count}"
                )
                unique_menu = []
                for mod_class in self.app.menu:
                    if mod_class not in unique_menu:
                        unique_menu.append(mod_class)
                self.app.menu[:] = unique_menu
                self.print(
                    f">>> Menu normalized: {len(self.app.menu)} items"
                )
                self.app.logic.available_panels.clear()
                self.app.logic.current = 0
                self.print(
                    ">>> Cleared existing panels"
                )
                self.app.back.setup_mods()
                self.print(
                    f">>> Panels rebuilt: "
                    f"{list(self.app.logic.available_panels.keys())}"
                )
                self.app.back.update_menu()
                self.app.back.redraw_mods()
                self.print(
                    f">>> Menu now has {len(self.app.menu)} items: "
                    f"{[M.name for M in self.app.menu]}"
                )
                self.print(
                    f">>> Available panels after: "
                    f"{list(self.app.logic.available_panels.keys())}"
                )
                # Mark that we've logged in
                self.app.data['logged_in'] = True
            else:
                self.print(f"!!! Login failed: {err}")
        # Otherwise, ENTER does nothing
    @callback(Login_ID, Keys.UP)
    def on_up(self, *args, **kwargs):
        self.cur_el = (self.cur_el - 1) % len(self.elements)

    @callback(Login_ID, Keys.DOWN)
    def on_down(self, *args, **kwargs):
        self.cur_el = (self.cur_el + 1) % len(self.elements)

