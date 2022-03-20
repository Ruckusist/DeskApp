import os, time, sys, datetime
import selectors, socket, threading
from types import SimpleNamespace
from timeit import default_timer as timer


class Message(SimpleNamespace):
    def __init__(self, message):
        super().__init__(message)



class Client_Session:
    def __init__(self, server, client, client_addr):
        self.server = server
        self.login_timer = timer()
        self.client = client
        self.client_addr = client_addr
        self.should_logout = False

    def logout(self):
        self.should_logout = True

    def send(self, message):
        self.client.send( message.encode() )

    def main_loop(self):
        while not self.should_logout:
            try:
                # get a message!
                message = self.client.recv(1024).decode()
                print(f"[{self.client_addr}]: {message}")
            except: 
                self.logout()

            if not message or message == '': continue

            try:
                # broadcast that message!
                self.server.broadcast(message)
            except Exception as e:
                print(e)


class Server:
    def __init__(self):
        # SOCKET SYSTEM
        self.host = 'localhost'
        self.port = 42068

        # self.selector = selectors.DefaultSelector()
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream.bind((self.host, self.port))
        self.stream.listen()
        print(f"Listening: {self.host}:{self.port} ")
        # self.stream.setblocking(False)
        # self.selector.register(self.stream, selectors.EVENT_READ, data=None)

        # LOGIN SYSTEM
        self.clients = []  # this is (Client Session, Client Thread)
        self.username_lookup = {}  # this is dict by Socket Client to find username? seems wrong...
        self.users = {}  # this is the User Database

    def accept_login(self, client, host_addr, username, password):
        # Add new User to Users Dict
        if username not in self.users:
            self.users[username] = {
                'password': password,
                'host_addr': host_addr,
                'client': client,
                'online': True
            }

        else:  # if username in Users Dict and The Password is no good
            if password != self.users[username]['password']:
                return False
            # if the user name is Good and the Password is good
            # user comes back online...
            self.users[username]['online'] = True
            self.users[username]['client'] = client
            self.users[username]['host_addr'] = host_addr
            
        # cross refrence the username and the client
        self.username_lookup[client] = username
        return True

    def run_server(self):
        """
        Run Server Takes a New Incoming Connection, Verifies the User, 
        Then Creates a User Session and Sends them away.
        """
        print("Starting Ruckus Server.")
        try:
            while True:

                # new incoming Connection:
                client, client_addr = self.stream.accept()
                result = client.recv(1024).decode()
                username, password = result.split(':')
                print(f"Recieveing Login Request from: {username}")

                # verify user credentials
                if self.accept_login(client, client_addr, username, password):
                    
                    # Create a user session
                    client.send('Good: Username'.encode())
                    print('New connection. Username: '+str(username))

                    client_session = Client_Session(self, client, client_addr)
                
                    client_thread = threading.Thread(target=client_session.main_loop)
                    client_thread.start()

                    self.clients.append((client_session, client_thread))

                else:
                    client.send('Err: Username'.encode())
                    print(f"This Guy failed to login properly?!?! --> {client_addr}")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            self.end_safely()

    def logged_out(self, client):
        username = self.username_lookup[client]
        user = self.users[username]
        user['online'] = False
        try:
            user['client'].shutdown(socket.SHUT_RDWR)
        except: pass
        return True

    def broadcast(self, msg):
        for connection in self.clients:
            client = connection[0]
            try:
                client.send(msg.encode())
                print(f"SENT->[{client.client_addr}]: {msg}")
            except Exception as e:
                self.clients.remove(connection)
                print(f"FAIL->[{client.client_addr}]: {msg} \n{msg}")

    def end_safely(self):
        for client, thread in self.clients:
            client.should_logout = True
            thread.join()
        print("Closed Ruckus Server Properly.")

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