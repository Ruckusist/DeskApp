# server.py
"""
This server is the main loop for grabbing incoming messages.
It should also server as controller for the subsystems.
It should also carry information about all the underlying
subsystems.
"""

import functools, sys, inspect, getpass, time, socket, os
import logging, datetime
import math, lzma, base64, pickle
import threading, io
import _pickle as cPickle
from passlib.hash import bcrypt

import deskapp


class Errors:
    def __init__(self, logfile='error.log', level=5, color=False, reporter='?', printer=print):
        self.logfile = logfile
        self.level = level
        self.color = color
        self.reporter = reporter
        self.print = printer
    
    def report(self, mesg:str, level:int, end="\n"):
        report = f"{self.reporter[:3]:3s} {Errors.get_time()}| {mesg}"
        with open(self.logfile, 'a') as f:
            f.write(report+end)
        if level > self.level: return
        if not self.color:
            self.print(report, end=end)
        if not self.color: return
        
        reporter = f"{BRIGHT_YELLOW}{self.reporter[:3]:<3s}{ENDC}"
        tme_day = time.strftime("%m/%d/%y", time.localtime())
        tme_time = time.strftime("%I:%M%p", time.localtime())
        tme = f"{BRIGHT_GREEN}{tme_day}{ENDC} {YELLOW}{tme_time}{ENDC}"
        color = [BRIGHT_WHITE,MAGENTA,OKBLUE,WARNING][level]
        message = f"{color}{mesg}{ENDC}"
        report = f"{reporter} {tme}| {message}"
        self.print(report, end=end)
        
    def info(self, message, end="\n"):
        self.report(message, 0, end)
        
    def debug(self, message, end="\n"):
        self.report(message, 1, end)
        
    def error(self, message, end="\n"):
        self.report(message, 2, end)
        
    def junk(self, message, end="\r"):
        self.report(message, 3, end)

    def __call__(self, message, end="\n"):
        self.info(message, end)

    @staticmethod
    def get_user(): 
        # return colored(f"{getpass.getuser()}@{socket.gethostname()}", "cyan")
        return f"{getpass.getuser()}@{socket.gethostname()}"

    @staticmethod
    def get_time(): 
        # return colored(time.strftime("%b %d, %Y|%I:%M%p", time.localtime()), "yellow")
        return time.strftime("%m/%d/%y %I:%M%p", time.localtime())

    @staticmethod
    def error_handler(exception, outer_err, offender, logfile="", verbose=True):
        try:
            outer_off = ''.join([x.strip(' ').strip('\n') for x in outer_err[4]])
            off = ''.join([x.strip(' ').strip('\n') for x in offender[4]])
            error_msg = []
            error_msg.append(f"╔══| Errors® |═[{Errors.get_time()}]═[{Errors.get_user()}]═[{os.getcwd()}]═══>>")
            error_msg.append(f"║ {outer_err[1]} :: {'__main__' if outer_err[3] == '<module>' else outer_err[3]}")
            error_msg.append(f"║ \t{outer_err[2]}: {outer_off}  -->")
            error_msg.append(f"║ ++ {offender[1]} :: Func: {offender[3]}()")
            error_msg.append(f"║ -->\t{offender[2]}: {off}")
            error_msg.append(f"║ [ERR] {exception[0]}: {exception[1]}")
            error_msg.append(f"╚══════════════════════════>>")
            msg = "\n".join(error_msg)
            if logfile:
                with open(logfile, 'a') as f:
                    f.write(msg)
            return msg
        except: print("There has been Immeasureable damage. Good day.")

    @staticmethod
    def protected(func, logfile="", verbose=True):
        """Allows a function to die without killing the app."""
        @functools.wraps(func)
        def p_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                # this is a bad fix... i dont know WTF
                # its been too long since i worked in this
                # area. TODO the Exception should catch
                # all the errors including keyboard, but
                # doesnt. grrrrrrrr.
                print("Keyboard Interrupt: Ending Safely.")
                pass
            except Exception:
                exception = sys.exc_info()
                print(f"Num of Errors: {len(inspect.stack())}")
                for outer_err, offender in zip(inspect.stack(), inspect.trace()):
                    err = Errors.error_handler(
                        exception, 
                        outer_err, 
                        offender, 
                        logfile, 
                        verbose
                    )
                    print(err)
        return p_func


class User:
    def __init__(self, username, password, session):
        self.created:str = time.ctime()
        self.username = username
        self.name = username
        self.password = password
        self.session = session
        self.subscriptions = []
        self.data = {}

    @property
    def online(self):
        return True if self.session else False

    def __repr__(self):
        return "DeskServer User Profile"
    

class Message(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Message, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delitem__(self, key):
        super(Message, self).__delitem__(key)
        del self.__dict__[key]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)
 
    def pad(self):
        pad = "$"
        org_size = (sys.getsizeof(self.file) / 1024) / 1024
        needed_size = ((math.ceil(org_size) - org_size)*1024)*1024
        single_pad_size = sys.getsizeof(pad)
        print(f"single_pad_size: {single_pad_size} needed_size: {needed_size}")
        self.pad = pad * (int(needed_size / single_pad_size))
        pad_size = sys.getsizeof(self.pad)
        print(f"added {pad_size:.1f}")
        
    def serialize(self):
        org_size = (sys.getsizeof(self.file) / 1024) / 1024
        # print(f"Data Size: {org_size:.3f} mb")
        # PICKLE
        pdata = cPickle.dumps(self)
        p_size = (sys.getsizeof(pdata) / 1024) / 1024
        # print(f"Pickle Size: {p_size:.3f} mb")
        # lzma
        cdata = lzma.compress(pdata)
        c_size = (sys.getsizeof(cdata) / 1024) / 1024
        saved = ((org_size / c_size)-1)*100
        # print(f"Compressed Size: {c_size:.3f} mb  saved: {saved:.2f}%")
        # base 64 encode
        b64data = base64.b64encode(cdata)
        b64_size = (sys.getsizeof(b64data) / 1024) / 1024
        # print(f"B64 Size: {b64_size:.3f} mb | base 64 should be 33% larger filesize. actual: {(b64_size/c_size)-1:.2f}")
        # encrypt
        if not self.get('key', 0):
            return b64data
        obj = Fernet(self.key)
        edata = obj.encrypt(b64data)
        edata_size = (sys.getsizeof(edata) / 1024) / 1024
        # print(f"Encrypted Size: {edata_size:.3f} mb")
        return edata
        
    @staticmethod
    def deserialize(edata, key=None):
        # decrypt
        if key:
            edata_size = (sys.getsizeof(edata) / 1024) / 1024
            # print(f"Encrypted Size: {edata_size:.3f} mb")
            obj = Fernet(key)
            b64data = obj.decrypt(edata)
        else:
            b64data = edata
        b64data_size = (sys.getsizeof(b64data) / 1024) / 1024
        # print(f"B64 Size: {b64data_size:.3f} mb")
        cdata = base64.b64decode(b64data)
        c_size = (sys.getsizeof(cdata) / 1024) / 1024
        # print(f"Compressed Size: {c_size:.3f} mb")
        pdata = lzma.decompress(cdata)
        pdata_size = (sys.getsizeof(pdata) / 1024) / 1024
        # print(f"Pickle Size: {pdata_size:.3f} mb")
        data = cPickle.loads(pdata)
        data_size = (sys.getsizeof(data.file) / 1024) / 1024
        # print(f"Actual Size: {data_size:.3f} mb")
        return data


class Session:
    def __init__(self, server, stream, addr, verbose, PRINTER=print,
                 PRINT_COLOR=False):
        self.server = server
        self.buffer_size = self.server.buffer_size
        self.stream = stream
        self.address = addr
        self.verbose = verbose
        self.username = None
        self.should_shutdown = False
        self.print = Errors(logfile='client.txt', level=5, color=PRINT_COLOR, reporter="ses", printer=PRINTER)
        if self.verbose: 
            self.print(f"Client Coming Online @ {addr[0]} : {addr[1]}")
        self.thread = threading.Thread(target=self.main_loop, daemon=True)
        self.thread.start()

    def disconnect(self):
        self.should_shutdown = True
        self.stream.close()
        self.thread.join( )
        
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


class ClientSession(Session):
    name = "Client"
    def __init__(self, 
                 SERVER_HOST="localhost",
                 SERVER_PORT=28080,
                 BUFFER_SIZE=1024,
                 VERBOSE=True,
                 PRINTER=print,
                 PRINT_COLOR=False
                 ):
        
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.buffer_size = BUFFER_SIZE
        self.verbose = VERBOSE
        self.should_shutdown = False
        self.logged_in = False
        self.connected = False
        self.username = None
        self.printer = PRINTER
        self.print_color = PRINT_COLOR
        self.print = Errors('client.log', 2, color=PRINT_COLOR, reporter=' C ', printer=PRINTER, )
        
        # PUBSUB data
        self.data = {}

        # Callbacks data
        self.callbacks = []
    
    def connect(self):
        if self.connected: return True
        try:
            self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
            self.addr = (self.host, self.port)
            self.stream.connect(self.addr)
            super().__init__(
                server=self,
                stream=self.stream,
                addr=self.addr,
                verbose=self.verbose,
                PRINT_COLOR=self.print_color,
                PRINTER=self.printer
            )
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            self.print(e)
            return False
        
    def disconnect(self):
        return super().disconnect()

    def register_callback(self, func):
        self.callbacks.append(func)

    def add_sub(self, sub):
        self.data[sub] = {}
        self.send_message(sub=sub)

    def remove_sub(self, sub):
        del self.data[sub]
        self.send_message(sub=sub, remove=True)

    def callback(self, session, message):
        # LOGIN PROTOCOL.
        if message.get('login',0):
            if message.login == True:
                self.logged_in = True
                if self.verbose: 
                    self.print(f"Properly logged in as {self.username}")
            else:
                if self.verbose: 
                    self.print(f"{self.username} !! Bad Password. Kicked out.")
                    
        if message.sub:
            if not self.data.get(message.sub, False):
                self.data[message.sub] = message.data
            else:
                self.data[message.sub] = message.data

        # TEST PROTOCOL.
        counter = 0
        if message.test:
            if counter < 2: 
                counter += 1    
                if self.verbose: self.print(f"PING PONG!", end='\r')
                if self.verbose: time.sleep(.5)
                session.send_message(test=True)
            else:
                counter = 0

        # APP Callbacks
        for callback in self.callbacks:
            callback(self, session, message)

    def login(self, username='Agent42', password='password'):
        self.username = username
        self.send_message(
            login=True,
            username=username,
            password=password
        )

    def logout(self):
        self.print(f"Logging out as {self.username}")
        self.logged_in = False
        self.send_message(
            login=True,
            logout=True
        )

    def end_safely(self):
        if self.logged_in:
            self.logout()
        if self.connected:
            self.disconnect()
        if self.verbose:
            self.print("Client Session ended Safely.")
        
    @Errors.protected
    def test(self):
        self.print(f"Lets Go! Client Session Started.")
        failed = 0
        flag = False
        while True:
            time.sleep(.5)
            if failed >= 4: 
                if self.verbose: 
                    self.print(f"Can't reach target server: {self.host}:{self.port}")
                break
            
            if not self.connected:
                if self.verbose: 
                    self.print(f"Connecting to {self.host}:{self.port}")
                connected = self.connect()
                if not connected:
                    self.print(f"Failed to connect to {self.host}:{self.port}")
                    failed += 1
                continue
            
            if not self.logged_in:
                if self.verbose: 
                    self.print(f"Trying to login as Agent42")
                
                self.login()
                failed += 1
                continue
                
            if not self.logged_in:
                if not self.connected:
                    if self.verbose: 
                        self.print(f"Login attempt {failed+1} failed, trying again in 5 secs.")
                time.sleep(5)
                failed += 1
                continue
            
            if not flag:
                self.print("this is working")
                flag = True
            
        # if self.logged_in and self.connected:
        #     self.logout()
        #     self.disconnect()
        self.end_safely()


class Engine:
    ## RENAME THIS TO LOGINDB
    def __init__(self, user_type:User=User, verbose=True, 
                 color=False, printer=print):
        self.verbose = verbose
        self.print = Errors(logfile='log.txt', level=5, 
                            color=color, reporter="Eng",
                            printer=printer)
        if os.path.exists('users.data'):
            self.load()
        else:
            self.users = {}
        
        self.user_type = user_type
        self.hasher = bcrypt.using(rounds=13, relaxed=True)  # default is 12 rounds.
        
        # publish data is furnished by the app.
        # I dont like that an app has to reach all the way here
        # and write directly to this. that seems wrong. TODO::
        self.publish_data = {'users': []}
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def save(self):
        if not self.users:
            print("No users to save.")
            return
        for user in self.users:
            self.users[user].session = False

        pickle.dump(self.users, open('users.data', 'wb'))
        if self.verbose:
            self.print("Saved User Database.")

    def load(self):
        self.users = pickle.load(open('users.data', 'rb'))
        if self.verbose:
            self.print(f"Loaded User Database. {len(self.users)}")

    def hash_password(self, password):
        # YEAH I KNOW. THIS SHOULD HAPPEN CLIENT SIDE AND ONLY TRANSMIT
        # A HASHED PASSWORD AND NOT PLAIN TEXT. TODO::
        # CAUSE SOMETHING SOMETHING... windows...
        return self.hasher.hash(password)

    def check_password(self, username, password):
        saved_password = self.users[username].password
        return self.hasher.verify(password, saved_password)

    @Errors.protected
    def login(self, session:Session, message:Message) -> bool:
        # self.print("ENGINE:Login")
        username = message.username
        password = message.password

        if self.verbose: 
            self.print(f"Logging in {username}, {'*'*len(password)}")
        
        if self.users.get(username, False):  # already logged in
            if self.users[username].online:
                return True

        if not self.users.get(username, False):  # new user    
            hashed_password = self.hash_password(password)
            session.username = username  # dubious again... but its working.
            NewUser = self.user_type(
                username=username,
                password=hashed_password,
                session=session
                )
            NewUser.session.user = NewUser  # assign this userdata back to the session. 

            self.users[username] = NewUser
            return True

        else:
            if self.check_password(username, password):  # returning user
                session.username = username  # dubious at best.
                session.user = self.users[username]  # this feels wrong too...
                self.users[username].session = session
                self.users[username].subscriptions = [] # reset all previous subs?
                return True
        return False

    def logout(self, session):
        username = session.username
        if self.verbose:
            self.print(f"engine:logout -- {username}")
        if self.users.get(username, False):
            self.users[username].session = False
   
    def callback(self, session:Session, message:Message):
        # if self.verbose: self.print("ENGINE::Callback")
        if message.logout:
                self.logout(session)
                return
        if message.login:
            good_login = self.login(session, message)
            if not good_login: session.send_message(login=False)
            else:              session.send_message(login=True)
            return

    def end_safely(self):
        self.save()

    def sub(self, session: Session, message:Message):
        user = self.users[session.username]
        if not message.remove:
            user.subscriptions.append(message.sub)
        else:
            user.subscriptions.remove(message.sub)

    def run(self):
        if self.verbose: 
            self.print(f"Starting Pub/Sub Server")
        while True:
            try:
                time.sleep(.15)
                # get a list of users to talk to.
                usersOnline = [self.users[x] for x in self.users if self.users[x].online]
                self.publish_data['users'] = [x for x in self.users if self.users[x].online]
                for user in usersOnline:
                    for sub in user.subscriptions:
                        if self.publish_data.get(sub,False):  # does this server have this data?
                            user.session.send_message(sub=sub,data=self.publish_data[sub])
                        elif sub == 'self':
                            user.session.send_message(sub=sub,data=user.data)
                        else:
                            self.print("sub data does not exist.")
            except KeyboardInterrupt:
                break


class Server:
    def __init__(self,
                 SERVER_HOST="localhost",
                 SERVER_PORT=28080,
                 BUFFER_SIZE=1024,
                 VERBOSE=True,
                 USER=User,
                 PRINTER=print,
                 PRINT_COLOR=False,
                 ):
        
        self.server_host = SERVER_HOST
        self.server_port = SERVER_PORT
        self.buffer_size = BUFFER_SIZE
        self.verbose     = VERBOSE
        self.user_type   = USER
        self.reporter    = "Srv"
        self.print       = Errors(logfile='log.txt', level=5, color=PRINT_COLOR, reporter=self.reporter, printer=PRINTER)
        
        if self.verbose:
            self.print(f"Server Coming Online @ {SERVER_HOST} : {SERVER_PORT} % {BUFFER_SIZE}")
        
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # EXPIRMENTAL
        self.stream.bind((self.server_host, self.server_port))
        self.stream.listen()

        self.clients = []
        self.callbacks = []
        self.engine = Engine(self.user_type, VERBOSE, color=PRINT_COLOR, printer=PRINTER)
        self.should_shutdown = False
        self.thread = threading.Thread(target=self.loop, daemon=True)
        
    def start(self):
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def stop(self):
        # OMG WTF IS THIS DOING.
        # IS IT PUNCHING ITSELF IN THE FACE?
        self.should_shutdown = True
        stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (self.server_host, self.server_port)
        stream.connect(addr)
        self.print("Attempting to shutdown server.")

    def status(self):
        self.print(f"Server Status | {self.server_host}:{self.server_port} % {self.buffer_size}")
        self.print(f"Connected: {'online' if self.thread.is_alive() else 'offline'}")
        self.print(f"Connections: {len(self.clients)}")

    def getSessionbyUsername(self, username):
        for i in self.clients:
            if i.username == username:
                return i
        return False
    
    def loop(self):
        self.print("Server Loop Started.")
        while not self.should_shutdown:
            try:
                client_socket, address = self.stream.accept()
                if self.should_shutdown: continue
                session = Session(
                    server=self,
                    stream=client_socket,
                    addr=address,
                    verbose=self.verbose,
                    PRINTER=self.print,
                    PRINT_COLOR=False
                )
                self.clients.append(session)
            except KeyboardInterrupt:
                break
        self.print("Server Loop Ended.")
            
    def disconnect(self, session):
        if session in self.clients:
            self.clients.remove(session)
            if self.verbose: 
                self.print(f"Client Disconnected @ {session.address[0]} : {session.address[1]}")
        
    def end_safely(self):
        # SHUT DOWN ALL ONLINE CLIENTS
        for session in self.clients:
            session.should_shutdown = True
            try: session.stream.shutdown(socket.SHUT_RDWR)
            except OSError: pass  # [Errno 107] Transport endpoint is not connected
            session.stream.close()
            session.thread.join()

        # SAVE ALL USERS IN DATABASE
        self.engine.end_safely()

        # PRINT
        if self.verbose: 
            print(end='\r')
            self.print(f"Server Going Offline @ {self.server_host} : {self.server_port} % {self.buffer_size}")

    def update_publish(self, key, value):
        self.engine.publish_data[key] = value

    def register_callback(self, func):
        self.callbacks.append(func)
        
    def remove_callback(self, func):
        self.callbacks.remove(func)

    def callback(self, session:Session, message:Message) -> None:
        if message.login:
            self.engine.callback(session, message)
            # return

        if message.logout:
            # ENGINE.LOGOUT HAS ALREADY BEEN CALLED.
            self.disconnect(session)

        if message.sub:
            if self.verbose: 
                self.print(f"{session.username} ! Subing to channel {message.sub}")
            self.engine.sub(session, message)

        if message.test:
            if self.verbose: 
                self.print(f"PING PONG! @ {session.username} {session.address[0]} : {session.address[1]}", end='\r')
            time.sleep(.5)
            session.send_message(test=True)
            
        if self.callbacks:
            for callback in self.callbacks:
                callback(session, message)


@Errors.protected  
def Err_test():
    print(f"{UNDERLINE}Starting Errors Tests.{ENDC}")
    # while True:
    # x = [1]
    # print(x[len(x)])
    
    x = Errors('errors.txt', level=3, color=True, reporter=f"{SQR}!{SQR}")
    x.info("test")
    x.debug("That")
    x.error("errors: stuff")
    x.junk("JUNK")
    print("finished")
    x("testing")


@Errors.protected
def Server_Dry():
    server = Server(SERVER_HOST="localhost", SERVER_PORT=28080, BUFFER_SIZE=1024, VERBOSE=True)
    server.start()
    server.thread.join()


class DeskServer(deskapp.Module):
    name = "Deskserver"
    def __init__(self, app, **kwargs):
        super().__init__(app, "Server")
        self.server = Server(
            SERVER_HOST="localhost", SERVER_PORT=28080, 
            BUFFER_SIZE=1024, VERBOSE=True, 
            PRINTER=self.print, PRINT_COLOR=False)
        
        self.server.start()


    def string_decider(self, input_string):
        self.print(f"got input: {input_string}")
        if input_string == "start":
            self.server.start()
        elif input_string == "stop":
            self.server.stop()
            self.server.thread.join()
            self.print("Server Stopped.")
        elif input_string == "status":
            self.server.status()
    

class DeskClient(deskapp.Module):
    name = "DeskClient"
    def __init__(self, app, **kwargs):
        super().__init__(app, "Server")
        self.client = ClientSession(
            SERVER_HOST="localhost", SERVER_PORT=28080, 
            BUFFER_SIZE=1024, VERBOSE=True, 
            PRINTER=self.print, PRINT_COLOR=False)
        
    def string_decider(self, input_string):
        self.print(f"got input: {input_string}")
        if input_string == "connect":
            self.client.connect()
        elif input_string == "disconnect":
            self.client.disconnect()
        elif input_string == "login":
            self.client.login()
        elif input_string == "logout":
            self.client.logout()
        

def main():
    mod = DeskServer
    try:
        if sys.argv[1] == 'server':
            mod = DeskServer
            
        elif sys.argv[1] == 'client':
            mod = DeskClient

    except Exception as e:
        print(e)

    deskapp.App(
        modules=[mod],
        show_menu=False,
        show_main=False,
        show_header=False,
        show_banner=False,
        demo_mode=False,
        use_mouse=False,
        use_focus=False,
        )
        
    
if __name__ == "__main__":
    main()

