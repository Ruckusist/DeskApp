# session.py
# last updated: 10-5-25
# credit: Claude Sonnet 4.5 - code quality improvements

import time
import threading
import io
from deskapp.server import Message, Errors


class Session:
    def __init__(self, server, stream, addr, verbose):
        self.Server = server
        self.BufferSize = self.Server.BufferSize
        self.Stream = stream
        self.Address = addr
        self.Verbose = verbose
        self.Username = None
        self.ShouldShutdown = False
        self.Print = Errors(
            logfile="client.txt",
            level=5,
            color=True,
            reporter="ses",
            sink=getattr(self.Server.Print, "sink", None),
            quiet=getattr(self.Server.Print, "quiet", False)
        )
        if self.Verbose:
            self.Print(f"Client Coming Online @ {addr[0]} : {addr[1]}")
        self.Thread = threading.Thread(
            target=self.MainLoop,
            daemon=True
        )
        self.Thread.start()

    def Disconnect(self):
        self.ShouldShutdown = True
        self.Stream.close()

    def SendMessage(self, **flags):
        sending = Message(flags, created=time.time())
        message = sending.serialize()
        try:
            self.Stream.send(message)
        except OSError:
            self.Disconnect()
        except KeyboardInterrupt:
            self.Disconnect()

    def ReceiveMessage(self) -> bytes:
        data = io.BytesIO()
        while True:
            try:
                packet = self.Stream.recv(self.BufferSize)
            except ConnectionResetError:
                self.Disconnect()
                return 0
            except KeyboardInterrupt:
                self.Disconnect()
                return 0
            packetSize = len(packet)
            if not packetSize:
                break
            data.write(packet)

            if packetSize < self.BufferSize:
                break
            if packetSize == self.BufferSize:
                continue
        return data.getvalue()

    def MainLoop(self):
        while True:
            if self.ShouldShutdown:
                break
            data = self.ReceiveMessage()
            if not data:
                break
            if not len(data):
                break

            try:
                message = Message.deserialize(data)
            except Exception as e:
                try:
                    if self.Verbose and self.Print:
                        self.Print.error(f"Bad Message Error: {e}")
                except Exception:
                    pass
                continue
            message.file_size = len(data)
            if self.Server is not self:
                if getattr(self.Server, "ShouldShutdown", False):
                    pass
                else:
                    self.Server.Callback(self, message)
            else:
                try:
                    self.Callback(self, message)
                except Exception:
                    pass

            del message
        self.Disconnect()
        try:
            self.Server.Disconnect(self)
        except TypeError:
            pass
