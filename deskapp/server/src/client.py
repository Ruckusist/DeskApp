import socket, time
from deskapp.server import Session, Errors


class ClientSession(Session):
    def __init__(self,
                 SERVER_HOST="localhost",
                 SERVER_PORT=28080,
                 BUFFER_SIZE=1024,
                 VERBOSE=True
                 ):

        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.buffer_size = BUFFER_SIZE
        self.BufferSize = BUFFER_SIZE  # For Session compatibility
        self.verbose = VERBOSE
        self.should_shutdown = False
        self.logged_in = False
        self.connected = False
        self.username = None
        self.print = Errors('client.log', 2, color=True, reporter=' C ')
        self.Print = self.print  # For Session compatibility

        # PUBSUB data
        self.data = {}

        # Callbacks data
        self.callbacks = []

    def connect(self):
        if self.connected: return True
        try:
            self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.addr = (self.host, self.port)
            self.stream.connect(self.addr)
            super().__init__(
                server=self,
                stream=self.stream,
                addr=self.addr,
                verbose=self.verbose
            )
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            self.print(e)
            return False

    def register_callback(self, func):
        self.callbacks.append(func)

    def add_sub(self, sub):
        self.data[sub] = {}
        self.send_message(sub=sub)

    def remove_sub(self, sub):
        del self.data[sub]
        self.send_message(sub=sub, remove=True)

    def callback(self, session, message):
        # LOGIN PROTOCOL.
        if message.get('login',0):
            if message.login == True:
                self.logged_in = True
                if self.verbose:
                    self.print(f"Properly logged in as {self.username}")
            else:
                if self.verbose:
                    self.print(f"{self.username} !! Bad Password. Kicked out.")

        if message.sub:
            if not self.data.get(message.sub, False):
                self.data[message.sub] = message.data
            else:
                self.data[message.sub] = message.data

        # TEST PROTOCOL.
        counter = 0
        if message.test:
            if counter < 2:
                counter += 1
                if self.verbose: self.print(f"PING PONG!", end='\r')
                if self.verbose: time.sleep(.5)
                session.send_message(test=True)
            else:
                counter = 0

        # APP Callbacks
        for callback in self.callbacks:
            callback(self, session, message)

    def login(self, username='Agent42', password='password'):
        self.username = username
        self.send_message(
            login=True,
            username=username,
            password=password
        )

    def logout(self):
        self.print(f"Logging out as {self.username}")
        self.logged_in = False
        self.send_message(
            login=True,
            logout=True
        )

    def end_safely(self):
        if self.logged_in:
            self.logout()
        if self.connected:
            self.disconnect()
        if self.verbose:
            self.print("Client Session ended Safely.")

    @Errors.protected
    def test(self):
        self.print(f"Lets Go! Client Session Started.")
        failed = 0
        flag = False
        while True:
            time.sleep(.5)
            if failed >= 4:
                if self.verbose:
                    self.print(f"Can't reach target server: {self.host}:{self.port}")
                break

            if not self.connected:
                if self.verbose:
                    self.print(f"Connecting to {self.host}:{self.port}")
                connected = self.connect()
                if not connected:
                    self.print(f"Failed to connect to {self.host}:{self.port}")
                    failed += 1
                continue

            if not self.logged_in:
                if self.verbose:
                    self.print(f"Trying to login as Agent42")

                self.login()
                failed += 1
                continue

            if not self.logged_in:
                if not self.connected:
                    if self.verbose:
                        self.print(f"Login attempt {failed+1} failed, trying again in 5 secs.")
                time.sleep(5)
                failed += 1
                continue

            if not flag:
                self.print("this is working")
                flag = True

        # if self.logged_in and self.connected:
        #     self.logout()
        #     self.disconnect()
        self.end_safely()


def main():
    (
        ClientSession()
        .test()
    )

if __name__ == "__main__":
    main()
