import time
from types import SimpleNamespace
from termcolor import colored


def get_time():
    block_l = colored('[', 'red')
    block_r = colored(']', 'red')
    timed = colored(f'{int(time.time())}', 'blue') 
    return f'{block_l}{timed}{block_r}'


class Message(SimpleNamespace):
    type = 'basic'
    timestamp = int(time.time())
    avilable_types = [
        'chat',
        'game',
        'sys'
    ]
    broadcast = False
    reciever = None
    text = ''

    def __init__(self, message, username):
        super().__init__(
            message=message.message if not type(message) == type(b'!') else message.decode(),
            original=message.original if not type(message) == type(b'!') else message,
        )
        self.username = username

    def check(self):
        try:
            mess = self.message.split('|')
        except:
            mess = [0]
            return False

        msg_type = mess[0]
        if not msg_type or msg_type == '': return False
        # print(f"found message type: {msg_type}")
        if msg_type == 'chat':
            return Chat_Message(self, self.username)
        elif msg_type == 'game':
            return Game_Message(self, self.username)
        elif msg_type == 'sys':
            return System_Message(self, self.username)
        else:
            return False

    def parse(self) -> None: pass

    def __str__(self) -> str:
        return self.message


class Chat_Message(Message):
    """
        CHAT MESSAGING FORMAT 
        chat|open|hey guys whats up?  | global chat
        chat|ruckus|dude whats up?    | direct message

        should return an message back to sender if reciever
        is unavailable.
    """
    
    type = 'chat'
    
    def __init__(self, message, username):
        super().__init__(message, username)

    def parse(self) -> None:
        # print("parsing message!")
        try:
            _, reciever, message = self.message.split('|')
        except:
            _, reciever, message = (0,0,0)
        
        self.text = str(message)

        print(f"{get_time()} {self.username}@{reciever}: {message}")
        if reciever == 'open':
            self.broadcast = True
        else:
            self.reciever = reciever


class Game_Message(Message):
    type = 'game'
    def __init__(self, message, username):
        super().__init__(message, username)


class System_Message(Message):
    type = 'sys'
    def __init__(self, message, username):
        super().__init__(message, username)
