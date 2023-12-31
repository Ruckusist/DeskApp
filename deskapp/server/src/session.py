import time, threading, io
from deskapp.server import Message, Errors


class Session:
    def __init__(self, server, stream, addr, verbose):
        self.server = server
        self.buffer_size = self.server.buffer_size
        self.stream = stream
        self.address = addr
        self.verbose = verbose
        self.username = None
        self.should_shutdown = False
        self.print = Errors(logfile='client.txt', level=5, color=True, reporter="ses")
        if self.verbose: 
            self.print(f"Client Coming Online @ {addr[0]} : {addr[1]}")
        self.thread = threading.Thread(target=self.main_loop, daemon=True)
        self.thread.start()

    def disconnect(self):
        self.should_shutdown = True
        self.stream.close()
        
    def send_message(self, **flags):
        sending = Message(flags, created=time.time())
        message = sending.serialize()  # this is wrong. is either. message.serialize()
                                       # or sending.serialize. but for serialize to return
                                       # an instance of Message is not right is it?
        try:
            self.stream.send(message)
        except OSError:  # [Errno 9] Bad file descriptor
            self.disconnect()
        except KeyboardInterrupt:
            self.disconnect()

    def recieve_message(self) -> bytes:
        data = io.BytesIO()
        while True:
            try:
                packet = self.stream.recv(self.buffer_size)
            except ConnectionResetError:  # Errno 104 Connection reset by peer.
                self.disconnect()
                return 0
            except KeyboardInterrupt:
                self.disconnect()
                return 0
            packet_size = len(packet)
            if not packet_size:
                break
            data.write(packet)

            if packet_size < self.buffer_size: break
            if packet_size == self.buffer_size:
            # this message is still coming and we need to keep going.

            # NOTE: This will have unexpected results if the packet size
            # is any multiple of the packetsize.

            # NOTE SOLUTION : send packet file size first then you know 
            # shit about the total size to expect.
                continue
        return data.getvalue()

    def main_loop(self):
        while True:
            if self.should_shutdown: break
            data = self.recieve_message()
            if not data: break  # this happens on broken pipes
            # print(data)
            if not len(data): break  # disconnect

            ## SECURITY FLAW! - dont deserialize unknown content!
            try:
                message = Message.deserialize(data)
            except:
                # these kinds of things happen.
                print("Bad Message Error")
                continue
            message.file_size = len(data)
            if self.server is not self:
                self.server.callback(self, message)
            else:  # there is no server.
                self.callback(self, message)

            del message
        self.disconnect()
        try:
            self.server.disconnect(self)
        except TypeError:  # there is no server
            pass