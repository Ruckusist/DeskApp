import socket, threading, time, io, json


class Message(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def serialize(self):
        return json.dumps(self).encode()
    
    def deserialize(self):
        return json.loads(self)


class Session:
    def __init__(self, stream, addr, buff, verbose):
        self.stream = stream
        self.addr = addr
        self.buff = buff
        self.verbose = verbose
        self.should_shutdown = False
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def send_message(self, **flags):
        sending = Message(flags, created=time.time())
        try:
            self.stream.send(sending.serialize())
        except (OSError, KeyboardInterrupt):
            self.disconnect()

    def recv_message(self) -> bytes:
        data = io.BytesIO()
        while True:
            try:
                packet = self.stream.recv(self.buff)
            except ConnectionResetError:
                self.disconnect()
                return 0
            except KeyboardInterrupt:
                self.disconnect()
                return 0
            packet_size = len(packet)
            if not packet_size:
                break
            data.write(packet)
            if packet_size < self.buff:
                break
            if packet_size == self.buff:
                pass
        return data.getvalue()

    def disconnect(self):
        # print(f"Disconnecting: {self.addr}")
        self.should_shutdown = True
        self.stream.close()

    def loop(self):
        while not self.should_shutdown:
            try:
                data = self.recv_message()
                if data:
                    # print(data.decode())
                    # print(f"Recieved {len(data)} bytes from {self.addr}")
                    message = Message.deserialize(data)

                else:
                    # print(f"Connection Closed: {self.addr}")
                    self.should_shutdown = True
            except KeyboardInterrupt:
                self.should_shutdown = True
            except Exception as e:
                print(e)
                self.should_shutdown = True


class Server:
    def __init__(self, host='localhost', port=8080, buff=1024, profile=None):
        self.host = host
        self.port = port
        self.buff = buff
        self.profile = profile
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.stream.bind((self.host, self.port))
        self.stream.listen(5)
        self.clients = []
        self.callbacks = []
        self.should_shutdown = False

    def start(self):
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while not self.should_shutdown:
            try:
                # Accept new connections
                client, addr = self.stream.accept()
                client = Session(client, addr, self.buff, True)
                self.clients.append(client)

                # remove bad connections
                for client in self.clients.copy():
                    if client.should_shutdown:
                        self.clients.remove(client)

            except KeyboardInterrupt:
                self.should_shutdown = True

            except Exception as e:
                pass

    def callback(self, session:Session, message:Message):
        for callback in self.callbacks:
            if callback[0] == message['type']:
                callback[1](session, message)

    def register_callback(self, type, func):
        self.callbacks.append((type, func))

    def stop(self):
        self.should_shutdown = True
        self.stream.close()
        # print("Server Stopped")

    
if __name__ == "__main__":
    server = Server("localhost", 8080, 1024)
    server.start()

