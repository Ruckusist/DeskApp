import onefile
import server


class_id = onefile.random_class_id()
class Game(onefile.Module):
    name = "Game"
    def __init__(self, app):
        super().__init__(app, class_id)
        self.server = server.Server()
        self.server.register_callback("test", self.test)
        self.server.start()
        self.print("Started Game")

    def test(self, client, message):
        self.print(f"Test: {message}")

    def page(self, panel):
        panel.win.addstr(0, 2, "| Game Server |")
        blanks = self.h - 4
        if self.server.clients:
            panel.win.addstr(1, 3, f"Online Clients: {len(self.server.clients)}")
            for i, e in enumerate(self.server.clients.copy()):
                mesg = f"{e.addr} {e.should_shutdown}"
                panel.win.addstr(i+2, 5, mesg)
                blanks -= 1
                if e.should_shutdown:
                    self.server.clients.remove(e)
        else:
            panel.win.addstr(1, 1, (" " * (self.w-6)))
            panel.win.addstr(2, 5, "No Clients Online"+(" " * (self.w-23)))
            blanks -= 1

        for i in range(blanks):
            panel.win.addstr(i+len(self.server.clients)+3, 1, (" " * (self.w-6)))

    @onefile.callback(class_id, onefile.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        pass

if __name__ == "__main__":
    app = onefile.App(modules=[Game], demo_mode=False)
    app.start()