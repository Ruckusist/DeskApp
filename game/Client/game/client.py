import socket
import threading
from types import SimpleNamespace


class Message(SimpleNamespace):
    def __init__(self, message) -> None:
        super().__init__(message)


class Chat_Message(Message):
    def __init__(self, message) -> None:
        super().__init__(message)


class Client:
    def __init__(self, parent):
        self.parent = parent
        # self.host_addr = 'localhost'
        self.host_addr = 'ruckusist.com'
        self.host_port = 42069
        self.username = None
        self.logged_in = False
        self.should_logout = False

    def try_login(self, username, password):
        self.stream = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.stream.connect((self.host_addr, self.host_port))
        self.stream.send(f'{username}:{password}'.encode())
        msg = self.stream.recv(1024)
        if msg.decode().split(':')[0] == 'Good':
            self.username = username
            self.logged_in = True
            message_handler = threading.Thread(target=self.handle_messages,args=())
            message_handler.start()
            return True
        return False

    def handle_messages(self):
        while not self.should_logout:
            try:
                incoming = self.stream.recv(1024).decode()
                self.parent.app.data['new_message'] = True
            except:
                self.parent.app.data.pop('client')
                self.end_safely()
                break
            try:
                data = incoming.split('|')
            except:
                continue
            
            msg_type = data.pop(0)

            # IF CHAT MESSAGE!
            if msg_type == 'chat':
                sender = data.pop(0)
                msg = ''.join(data)

                self.parent.app.data['messages'].append((sender,msg))
        
        self.logged_in = False

    def send(self, message, msg_type='chat'):
        if msg_type == 'chat':
            reciever = 'open'

            # DIRECT MESSAGING!
            if message.startswith('@'):
                message = message.split(' ')
                reciever = message.pop(0)[1:]
                message = ' '.join(message)

            if self.logged_in:
                broadcast = f"{msg_type}|{reciever}|{message}".encode()
                self.stream.send(broadcast)
        
        elif msg_type == 'sys':
            broadcast = f"{msg_type}|{message}".encode()
            self.stream.send(broadcast)

    def end_safely(self):
        if self.logged_in:
            self.send('LGOUT', 'sys')
            self.should_logout = True
            self.stream.shutdown(socket.SHUT_RDWR)