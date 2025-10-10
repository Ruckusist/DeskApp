import random
from deskapp import Module, callback, Keys
from sidedesk.client.manager import status as client_status

Users_ID = random.random()
class Users(Module):
    name = "Users"
    def __init__(self, app):
        super().__init__(app, Users_ID)


    # TODO: fetch user list periodically
    # TODO: fetch user list on chat login/logout
    # NOTE: make sure to handle real users and bots the same way.

    def page(self, panel):
        self.index = 2
        st = client_status()
        heading = f"Users ({'logged in' if st.get('logged_in') else 'not logged in'})"
        self.write(panel, self.index, 2, heading, "yellow")
        self.index += 2
        users = self.app.data.get('users', [])
        if not users:
            msg = "No users online."
            if st.get('logged_in'):
                msg = "Logged in, waiting for user list…"
            self.write(panel, self.index, 4, msg, "blue")
            return
        for u in users:
            self.write(panel, self.index, 4, f"• {u}", "white")
            self.index += 1
