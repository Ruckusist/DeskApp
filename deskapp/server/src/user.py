# user.py
# last updated: 10-18-22
""" 
desc: A base for making server-side saved data.
features:
* a password will always be saved as a hash
* online returns True if there is currently a session
   in the user data, else, this user is not online.
   this is better than a flag.
* print of class has been overridden, but just for 
   ease of debugging. no useful information given.
"""

import time


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

    # def __getstate__(self):
    #     state = {}
    #     for x in self.__dict__:
    #         if x in ['password', 'session']:
    #             continue
    #         state[x] = self.__dict__[x]
    #     return state

    # def __setstate__(self, d):
    #     self.__dict__.update(d)
