import socket
import threading


class Client:
    def __init__(self, parent):
        self.parent = parent
        self.host_addr = 'localhost'
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
                incoming = incoming.split('|')
                try:
                    msg = tuple(incoming[-1].split(' - '))
                except:
                    msg = ('wrk', incoming[-1])
                # incoming = incoming.split('|')
                # msg_type = incoming.pop(0)
                # if msg_type == 'msg':
                #     self.parent.app.data['messages'].append((incoming[0].split(' - ')))
                self.parent.app.data['messages'].append(msg)
            except:
                self.parent.app.data['messages'].append(('ERR', incoming))
        
        self.logged_in = False

    def send(self, message, msg_type='msg'):
        if self.logged_in:
            if msg_type == 'msg':
                message = f"{self.username} - {message}"
            broadcast = f"{msg_type}|{message}".encode()
            self.stream.send(broadcast)

    def end_safely(self):
        if self.logged_in:
            self.send('logging out!', 'LGOUT')
            self.should_logout = True
            self.stream.shutdown(socket.SHUT_RDWR)