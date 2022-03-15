from timeit import default_timer as timer
import socket
import threading

class Server:
    def __init__(self):
        self.stream = None
        self.clients = []
        self.username_lookup = {}
        self.client_lookup = {}
        self.users = {}
        self.start_server()

    def start_server(self):
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # host = socket.gethostbyname(socket.gethostname())
        host = 'localhost'
        port = 42069

        self.stream.bind((host, port))
        self.stream.listen(100)  # ?? why do we listen for 100 right off the bat?

    def accept_login(self, client, host_addr, username, password):
        if username not in self.users:
            self.users[username] = {
                'password': password,
                'host_addr': host_addr,
                'client': client,
                'online': True
            }

        else:  # if username in self.users:
            if password != self.users[username]['password']:
                return False
            self.users[username]['online'] = True
        self.username_lookup[username] = client
        self.client_lookup[client] = username
        self.clients.append(client)
        print("Users Online:")
        print("-"*25)
        for i in self.users:
            if self.users[i]['online'] == True:
                print(f"\t{i}") 
        return True

    def log_out(self, client): 
        username = self.client_lookup[client]
        self.users[username]['online'] = False
        try:
            client.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print(e)
        self.clients.remove(client)
        self.broadcast(f'! {username} logged out.')
        print(f'! {username} logged out.')

    def run_server(self):
        print("Starting Server.")
        while True:
            client, client_addr = self.stream.accept()
            result = client.recv(1024).decode()  # username is first 1024 of bitstream?
            username, password = result.split(':')
            print(f"recieveing: {username}  --  {password}")
            if self.accept_login(client, client_addr, username, password):
                client.send('Good: Username'.encode())
                print('New connection. Username: '+str(username))
                self.broadcast(f'LGN| {username} - New User joined. - ')
             
                threading.Thread(
                    target=self.handle_client,
                    args=(client, client_addr,)).start()
            else:
                client.send('Err: Username'.encode())
                print(f"This Guy failed to login properly?!?! --> {client_addr}")

    def broadcast(self, msg, msg_type='msg'):
        broadcast = f"{msg_type}|{msg}".encode()
        for connection in self.clients:
            try:
                connection.send(broadcast)
            except:
                self.clients.remove(connection)

    def handle_client(self,client, client_addr):
        start_time = timer()
        flag = False
        while True:
            try:
                incoming = client.recv(1024).decode()
            except:
                self.log_out(client)
                break

            if incoming != '':
                print(f"incoming Message: {incoming}")
                try:
                    incoming = incoming.split('|')
                    msg_type = incoming.pop(0)
                except:
                    print("Cant break down message!")

                # GLOBAL CHAT FUNCTION - msg
                if msg_type == 'msg':
                    broadcast = f"{msg_type}|{incoming[0]}".encode()
                    # print(f"broadcasting:\n\t{broadcast.decode()}\nto {len(self.clients)} clients")
                    for connection in self.clients:
                        # if connection != client:
                        try:
                            connection.send(broadcast)
                        except:
                            print(f"{connection} failed to broadcast")
                            self.clients.remove(connection)
                if msg_type == 'LGOUT':
                    self.log_out(client)

server = Server()
server.run_server()