# server.py
# last updated: 10-5-25
# credit: Claude Sonnet 4.5 - code quality improvements
"""
This server is the main loop for grabbing incoming messages.
It should also server as controller for the subsystems.
It should also carry information about all the underlying subsystems.
"""

import time
import socket
import threading
from deskapp.server import Session, Message, Engine, User, Errors


class Server:
    def __init__(
        self,
        ServerHost="localhost",
        ServerPort=28080,
        BufferSize=1024,
        Verbose=True,
        UserType=User,
        Sink=None,
        Quiet=False,
    ):
        self.ServerHost = ServerHost
        self.ServerPort = ServerPort
        self.BufferSize = BufferSize
        self.Verbose = Verbose
        self.UserType = UserType
        self.Reporter = "Srv"
        self.Print = Errors(
            logfile="log.txt",
            level=5,
            color=True,
            reporter=self.Reporter,
            sink=Sink,
            quiet=Quiet
        )

        self.Print = Errors(
            logfile="log.txt",
            level=5,
            color=True,
            reporter=self.Reporter,
            sink=Sink,
            quiet=Quiet
        )

        if self.Verbose:
            msg = (
                f"Server Coming Online @ {ServerHost} : "
                f"{ServerPort} % {BufferSize}"
            )
            self.Print(msg)

        self.Stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Stream.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )
        self.Stream.bind((self.ServerHost, self.ServerPort))
        self.Stream.listen()

        self.Clients = []
        self.Callbacks = []
        self.Engine = Engine(
            self.UserType,
            self.Verbose,
            sink=Sink,
            quiet=Quiet
        )
        self.ShouldShutdown = False
        self.Thread = threading.Thread(target=self.Loop, daemon=True)

        self.Thread = threading.Thread(target=self.Loop, daemon=True)

    def Start(self):
        self.Thread.start()

    def Stop(self):
        self.ShouldShutdown = True
        try:
            self.Stream.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.Stream.close()
        except OSError:
            pass
        try:
            stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            stream.settimeout(0.2)
            addr = (self.ServerHost, self.ServerPort)
            stream.connect(addr)
        except OSError:
            pass
        finally:
            try:
                stream.close()
            except Exception:
                pass

    def GetSessionByUsername(self, username):
        for client in self.Clients:
            if client.Username == username:
                return client
        return False

    def Loop(self):
        while not self.ShouldShutdown:
            try:
                clientSocket, address = self.Stream.accept()
                if self.ShouldShutdown:
                    try:
                        clientSocket.close()
                    except Exception:
                        pass
                    continue
                session = Session(
                    server=self,
                    stream=clientSocket,
                    addr=address,
                    verbose=self.Verbose
                )
                self.Clients.append(session)
            except KeyboardInterrupt:
                break
            except OSError:
                if self.ShouldShutdown:
                    break
                else:
                    continue

    def Disconnect(self, session):
        if session in self.Clients:
            self.Clients.remove(session)
            if self.Verbose:
                msg = (
                    f"Client Disconnected @ {session.Address[0]} : "
                    f"{session.Address[1]}"
                )
                self.Print(msg)

    def EndSafely(self):
        for session in self.Clients:
            session.ShouldShutdown = True
            try:
                session.Stream.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            session.Stream.close()
            session.Thread.join()

        self.Engine.EndSafely()

        if self.Verbose:
            msg = (
                f"Server Going Offline @ {self.ServerHost} : "
                f"{self.ServerPort} % {self.BufferSize}"
            )
            self.Print(msg)

    def UpdatePublish(self, key, value):
        self.Engine.PublishData[key] = value

    def RegisterCallback(self, func):
        self.Callbacks.append(func)

    def RemoveCallback(self, func):
        self.Callbacks.remove(func)

    def Callback(self, session: Session, message: Message) -> None:
        if message.login:
            self.Engine.Callback(session, message)

        if message.logout:
            self.Disconnect(session)

        if message.sub:
            if self.Verbose:
                msg = f"{session.Username} ! Subing to channel {message.sub}"
                self.Print(msg)
            self.Engine.Sub(session, message)

        if message.test:
            if self.Verbose:
                msg = (
                    f"PING PONG! @ {session.Username} "
                    f"{session.Address[0]} : {session.Address[1]}"
                )
                self.Print(msg)
            time.sleep(.5)
            session.SendMessage(test=True)

        if self.Callbacks:
            for callback in self.Callbacks:
                callback(session, message)
