# server.py
"""
This server is the main loop for grabbing incoming messages.
It should also server as controller for the subsystems.
It should also carry information about all the underlying
subsystems.
"""

import time, socket, threading
# import multiprocessing
from deskapp.server import Session, Message, Engine, User, Errors


class Server:
    def __init__(self,
                 # SERVER_HOST="0.0.0.0",
                 SERVER_HOST="localhost",
                 SERVER_PORT=28080,
                 BUFFER_SIZE=1024,
                 VERBOSE=True,
                 USER=User,
                 ):
        
        self.server_host = SERVER_HOST
        self.server_port = SERVER_PORT
        self.buffer_size = BUFFER_SIZE
        self.verbose     = VERBOSE
        self.user_type   = USER
        self.reporter    = "Srv"
        self.print       = Errors(logfile='log.txt', level=5, color=True, reporter=self.reporter)
        
        if self.verbose:
            self.print(f"Server Coming Online @ {SERVER_HOST} : {SERVER_PORT} % {BUFFER_SIZE}")
        
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # EXPIRMENTAL
        self.stream.bind((self.server_host, self.server_port))
        self.stream.listen()

        self.clients = []
        self.callbacks = []
        self.engine = Engine(self.user_type, VERBOSE)
        self.should_shutdown = False
        self.thread = threading.Thread(target=self.loop, daemon=True)
        # self.thread = multiprocessing.Process(target=self.loop, args=(), daemon=True)
        
    def start(self):
        self.thread.start()

    def stop(self):
        # OMG WTF IS THIS DOING.
        # IS IT PUNCHING ITSELF IN THE FACE?
        self.should_shutdown = True
        stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (self.server_host, self.server_port)
        stream.connect(addr)

    def getSessionbyUsername(self, username):
        for i in self.clients:
            if i.username == username:
                return i
        return False
    
    def loop(self):
        while not self.should_shutdown:
            try:
                client_socket, address = self.stream.accept()
                if self.should_shutdown: continue
                session = Session(
                    server=self, 
                    stream=client_socket, 
                    addr=address, 
                    verbose=self.verbose
                )
                self.clients.append(session)
            except KeyboardInterrupt:
                break
            
    def disconnect(self, session):
        if session in self.clients:
            self.clients.remove(session)
            if self.verbose: 
                self.print(f"Client Disconnected @ {session.address[0]} : {session.address[1]}")
        
    def end_safely(self):
        # SHUT DOWN ALL ONLINE CLIENTS
        for session in self.clients:
            session.should_shutdown = True
            try: session.stream.shutdown(socket.SHUT_RDWR)
            except OSError: pass  # [Errno 107] Transport endpoint is not connected
            session.stream.close()
            session.thread.join()

        # SAVE ALL USERS IN DATABASE
        self.engine.end_safely()

        # PRINT
        if self.verbose: 
            print(end='\r')
            self.print(f"Server Going Offline @ {self.server_host} : {self.server_port} % {self.buffer_size}")

    def update_publish(self, key, value):
        self.engine.publish_data[key] = value

    def register_callback(self, func):
        self.callbacks.append(func)
        
    def remove_callback(self, func):
        self.callbacks.remove(func)

    def callback(self, session:Session, message:Message) -> None:
        if message.login:
            self.engine.callback(session, message)
            # return

        if message.logout:
            # ENGINE.LOGOUT HAS ALREADY BEEN CALLED.
            self.disconnect(session)

        if message.sub:
            if self.verbose: 
                self.print(f"{session.username} ! Subing to channel {message.sub}")
            self.engine.sub(session, message)

        if message.test:
            if self.verbose: 
                self.print(f"PING PONG! @ {session.username} {session.address[0]} : {session.address[1]}", end='\r')
            time.sleep(.5)
            session.send_message(test=True)
            
        if self.callbacks:
            for callback in self.callbacks:
                callback(session, message)

