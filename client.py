import socket
import random
import onefile
import server


class ClientSession(server.Session):
    def __init__(self):
        stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = ("localhost", 8080)
        stream.connect(addr)
        super().__init__(stream, addr, 1024, verbose=True)


class_id = random.random()
class LoginApp(onefile.Module):
    name = "Login"
    def __init__(self, app):
        super().__init__(app, class_id)
        self.scroll = 4
        self.username = "Agent42"
        self.password = "flowers"
        self.server = "localhost"
        self.port = 8080
        self.print("Started LoginApp")
        self.client = None


    def string_decider(self, input_string):
        if self.scroll == 0:
            self.server = input_string
        elif self.scroll == 1:
            self.port = int(input_string) if input_string.isdigit() else self.port
        elif self.scroll == 2:
            self.username = input_string
        elif self.scroll == 3:
            self.password = input_string

    def page(self, panel):
        panel.win.addstr(0, 2, "| Client |")
        self.scroll_elements = [ f"Server: {self.server}",
                                 f"Port: {self.port}",
                                 f"Username: {self.username}",
                                 f"Password: {('*'*len(self.password))}", 
                                 "Login", "Register", "Forgot Password",
                                 "Exit" ]
        
        for i, e, in enumerate(self.scroll_elements):
            color = self.front.chess_white if i is not self.scroll else self.front.color_red
            buff = self.w - len(e) - 6
            mesg = e + " " * buff
            panel.win.addstr(i+1, 5, mesg, color)

    def login(self):
        self.client = ClientSession()
        self.client.send_message(message="Hello World!", type="test")

    def end_safely(self):
        if self.client:
            self.client.disconnect()
        return super().end_safely()

    @onefile.callback(class_id, onefile.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.scroll == 4:
            self.print("Login")
            self.login()
        elif self.scroll == 5:
            self.print("Register")
        elif self.scroll == 6:
            self.print("Forgot Password")
        elif self.scroll == 7:
            self.app.exit()

if __name__ == "__main__":
    # client = ClientSession()
    app = onefile.App(modules=[LoginApp],
                      splash_screen=False,
                    demo_mode=False,
                    title="GameClient",
                    show_footer=False,
                    show_header=False,
                    show_menu=False,
                    # show_messages=False,
                    v_split=.5,
                    h_split=.2,
                    show_box=True,
                    show_banner=False)