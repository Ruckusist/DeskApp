# engine.py
# last updated: 10-5-25
# credit: Claude Sonnet 4.5 - code quality improvements

import pickle
import os
import time
import threading
import bcrypt
from deskapp.server import Session, Message, User, Errors


class Engine:
    def __init__(
        self,
        UserType: User = User,
        Verbose=True,
        sink=None,
        quiet=False
    ):
        self.Verbose = Verbose
        self.Print = Errors(
            logfile="log.txt",
            level=5,
            color=True,
            reporter="Eng",
            sink=sink,
            quiet=quiet
        )
        if os.path.exists("users.data"):
            self.Load()
        else:
            self.Users = {}

        self.UserType = UserType

        # Create default admin user if no users exist
        self.CreateDefaultAdmin()

        self.PublishData = {"users": []}
        self.Thread = threading.Thread(target=self.Run, daemon=True)
        self.Thread.start()

    def Save(self):
        if not self.Users:
            if self.Verbose:
                self.Print("No users to save.")
            return
        for user in self.Users:
            self.Users[user].session = False

        pickle.dump(self.Users, open("users.data", "wb"))
        if self.Verbose:
            self.Print("Saved User Database.")

    def Load(self):
        self.Users = pickle.load(open("users.data", "rb"))
        if self.Verbose:
            self.Print(f"Loaded User Database. {len(self.Users)}")

    def CreateDefaultAdmin(self):
        """Create default admin user if no users exist."""
        if not self.Users or len(self.Users) == 0:
            username = "dude"
            password = "pass"
            hashedPassword = self.HashPassword(password)
            adminUser = self.UserType(
                username=username,
                password=hashedPassword,
                session=None
            )
            self.Users[username] = adminUser
            self.Save()
            if self.Verbose:
                self.Print(
                    f"Created default admin user: {username}"
                )

    def HashPassword(self, password):
        """Hash password using bcrypt directly."""
        # Bcrypt has a 72 byte limit
        passwordBytes = password.encode("utf-8")
        if len(passwordBytes) > 72:
            passwordBytes = passwordBytes[:72]
        salt = bcrypt.gensalt(rounds=13)
        return bcrypt.hashpw(passwordBytes, salt).decode("utf-8")

    def CheckPassword(self, username, password):
        """Verify password against stored hash."""
        # Bcrypt has a 72 byte limit
        passwordBytes = password.encode("utf-8")
        if len(passwordBytes) > 72:
            passwordBytes = passwordBytes[:72]
        savedPassword = self.Users[username].password
        savedPasswordBytes = savedPassword.encode("utf-8")
        return bcrypt.checkpw(passwordBytes, savedPasswordBytes)

    @Errors.protected
    def Login(self, session: Session, message: Message) -> bool:
        username = message.username
        password = message.password

        if self.Verbose:
            self.Print(f"Logging in {username}, {'*'*len(password)}")

        if self.Users.get(username, False):
            if self.Users[username].online:
                return True

        if not self.Users.get(username, False):
            hashedPassword = self.HashPassword(password)
            session.Username = username
            newUser = self.UserType(
                username=username,
                password=hashedPassword,
                session=session
            )
            newUser.session.user = newUser

            self.Users[username] = newUser
            return True

        else:
            if self.CheckPassword(username, password):
                session.Username = username
                session.user = self.Users[username]
                self.Users[username].session = session
                self.Users[username].subscriptions = []
                return True
        return False

    def Logout(self, session):
        username = session.Username
        if self.Verbose:
            self.Print(f"engine:logout -- {username}")
        if self.Users.get(username, False):
            self.Users[username].session = False

    def Callback(self, session: Session, message: Message):
        if message.logout:
            self.Logout(session)
            return
        if message.login:
            goodLogin = self.Login(session, message)
            if not goodLogin:
                session.SendMessage(login=False)
            else:
                session.SendMessage(login=True)
            return

    def EndSafely(self):
        self.Save()

    def Sub(self, session: Session, message: Message):
        user = self.Users[session.Username]
        if not message.remove:
            user.subscriptions.append(message.sub)
        else:
            user.subscriptions.remove(message.sub)

    def Run(self):
        if self.Verbose:
            self.Print("Starting Pub/Sub Server")
        while True:
            try:
                time.sleep(.15)
                usersOnline = [
                    self.Users[x]
                    for x in self.Users
                    if self.Users[x].online
                ]
                self.PublishData["users"] = [
                    x for x in self.Users if self.Users[x].online
                ]
                for user in usersOnline:
                    for sub in user.subscriptions:
                        if self.PublishData.get(sub, False):
                            user.session.SendMessage(
                                sub=sub,
                                data=self.PublishData[sub]
                            )
                        elif sub == "self":
                            user.session.SendMessage(
                                sub=sub,
                                data=user.data
                            )
                        else:
                            if self.Verbose:
                                self.Print("sub data does not exist.")
            except KeyboardInterrupt:
                break
