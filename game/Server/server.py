import os, time, sys, datetime
import socket, threading
from timeit import default_timer as timer
import messages
from termcolor import colored


def get_time():
    block_l = colored('[', 'red')
    block_r = colored(']', 'red')
    timed = colored(f'{int(time.time())}', 'blue') 
    return f'{block_l}{timed}{block_r}'


class Client_Session:
    def __init__(self, server, client, client_addr, username):
        self.server = server
        self.client = client
        self.client_addr = client_addr
        self.username = username

        self.login_timer = timer()
        self.should_logout = False

    def logout(self):
        self.should_logout = True
        self.server.logged_out(self.client)

    def send(self, message):
        try:
            self.client.send( message.encode() )
        except:
            self.client.send( message )

    def handle_chat(self, message):
        message.parse()

        if message.broadcast:
            self.server.broadcast(self.username, message)

        # DIRECT MESSAGING!
        if message.reciever:
            if message.reciever in self.server.users:
                reciever = self.server.users[message.reciever]
                # self.server.users[message.reciever]['client'].send(f'DM->{self.username}: {message.text}'.encode())
                if reciever['online']:
                    mesg = f'chat|{self.username}|DM-> {message.text}'.encode()
                    reciever['client'].send(mesg)
                else:
                    self.send('chat|sys|DM FAILED: user offline.'.encode())

    def handle_sys(self, message):
        message.parse()
        if message.command == 'LGOUT':
            # LOG THIS PERSON OUT!
            print(f"{get_time()} USER LOGOUT - {self.username}")
            self.server.logged_out(self.client)
        else:
            print(f"{get_time()} Bad Command: @{self.username} | {message.command}")
    
    def handle_message(self, message):
        if message.type == 'chat':
            return self.handle_chat(message)
        elif message.type == 'sys':
            return self.handle_sys(message)
            pass
        else:
            print(f"{get_time()} got message type: {message.type} -- disregarding.")

    def main_loop(self):
        print(f"{get_time()} Starting Client Session: {self.username}")
        while not self.should_logout:
            try:
                # get a message!
                message = messages.Message(self.client.recv(1024), self.username).check()
            except Exception as e:
                print(f"{get_time()} OH NO! bad message error! {e}")
                self.logout()
                self.send("OH NO! bad message error!")
                # break
                continue

            if not message: continue

            self.handle_message(message)
        self.server.logged_out(self.client)


class Server:
    version = '0.0.2'

    def __init__(self):
        # SOCKET SYSTEM
        self.host = '0.0.0.0'
        self.port = 42069

        # self.selector = selectors.DefaultSelector()
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream.bind((self.host, self.port))
        self.stream.listen()
        

        # LOGIN SYSTEM
        self.clients = []  # this is (Client Session, Client Thread)
        self.username_lookup = {}  # this is dict by Socket Client to find username? seems wrong...
        self.users = {}  # this is the User Database
        self.print_startup()

    @property
    def is_online(self) -> int:
        counter = 0
        for user in self.users:
            if self.users[user]['online']: counter += 1
        return counter

    def print_startup(self):
        logo = """
    ---------------------------------
        __________
       |   ____   |
       |  |   /  /
       |  |  /  /
       |  | /  /
       |  |/  / uckusist.com
       |      \     (c) 2022
       |       \          __  _____
       |   |\   \        / / |     |
       |   | \   \      / /  |  0  |
       |   |  \   \    / /   |  0  |
       |   |   \   \  /_/    |_____|
       |___|    \___\        
    ---------------------------------
        """
        print(logo)
        print(f"{get_time()} Connected to {self.host}:{self.port}")
        print(f"{get_time()} Starting Ruckus Server v. {self.version}")

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
        try:
            while True:

                # new incoming Connection:
                client, client_addr = self.stream.accept()
                result = client.recv(1024).decode()
                username, password = result.split(':')
                print(f"{get_time()} Recieveing Login Request from User: {username}")

                # verify user credentials
                if self.accept_login(client, client_addr, username, password):
                    
                    # Create a user session
                    client.send('Good: Username'.encode())
                    # print('New connection. Username: '+str(username))

                    client_session = Client_Session(self, client, client_addr, username)
                
                    client_thread = threading.Thread(target=client_session.main_loop)
                    client_thread.start()

                    self.clients.append((client_session, client_thread))

                else:
                    client.send('Err: Username'.encode())
                    print(f"{get_time()} This Guy failed to login properly?!?! --> {client_addr}")

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

    def broadcast(self, username, message):
        bad_connections = []
        if message.type == 'chat':
            print(f"{get_time()} cast@{self.is_online}: {message.text}")
            for connection in self.clients:
                client = connection[0]
                try:
                    client.send(f"chat|{username}|{message.text}")
                except Exception as e:
                    bad_connections.append(connection)
        
        if bad_connections:
            for connection in bad_connections:
                self.clients.remove(connection)

    def end_safely(self):
        for client, thread in self.clients:
            client.should_logout = True
            thread.join()
        print("Closed Ruckus Server Properly.")


server = Server()
server.run_server()