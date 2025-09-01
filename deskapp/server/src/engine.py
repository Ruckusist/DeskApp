import pickle, os, time, threading
from deskapp.server import Session, Message, User, Errors
from passlib.hash import bcrypt


class Engine:
    ## RENAME THIS TO LOGINDB
    def __init__(self, user_type:User=User, verbose=True):
        self.verbose = verbose
        self.print = Errors(logfile='log.txt', level=5, color=True, reporter="Eng")
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
        # self.thread = multiprocessing.Process(target=self.run, args=(), daemon=True)
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
        # TODO: SECURITY IMPROVEMENT NEEDED
        # Currently passwords are transmitted in plain text from client to server.
        # This should be changed to hash passwords client-side before transmission
        # for better security. Consider implementing secure password protocols
        # like SRP (Secure Remote Password) or at minimum use TLS encryption.
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
