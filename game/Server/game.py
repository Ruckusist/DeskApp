import socket
import threading

class Server:
    def __init__(self):
        self.stream = None
        self.clients = []
        self.username_lookup = {}
        self.start_server()

    def start_server(self):
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        host = socket.gethostbyname(socket.gethostname())
        port = 42069

        self.stream.bind((host, port))
        self.stream.listen(100)  # ?? why do we listen for 100 right off the bat?

    def run_server(self):
        while True:
            client, client_addr = self.stream.accept()

            username = client.recv(1024).decode()  # username is first 1024 of bitstream?
            
            # print('New connection. Username: '+str(username))
            self.broadcast('New User joined. --> ' + username)

            self.username_lookup[client] = username

            self.clients.append(client)
             
            threading.Thread(
                target=self.handle_client,
                args=(client, client_addr,)).start()

    def broadcast(self,msg):
        for connection in self.clients:
            connection.send(msg.encode())

    def handle_client(self,client, client_addr):
        while True:
            try:
                msg = client.recv(1024)  # we are always recieving 1024?
            except:
                client.shutdown(socket.SHUT_RDWR)
                self.clients.remove(client)
                
                # print(str(self.username_lookup[c])+' left the room.')
                self.broadcast(str(self.username_lookup[client])+' logged out.')
                break

            if msg.decode() != '':  # is not... lol
                # print('New message: '+str(msg.decode()))
                for connection in self.clients:
                    if connection != client:  # this client has already been removed i think...
                        connection.send(msg)

server = Server()
server.run_server()