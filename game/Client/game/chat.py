import random, threading
import deskapp

from .client import Client

ClassID = random.random()
class Global_Chat(deskapp.Module):
    name = "Global Chat"
    def __init__(self, app):
        super().__init__(app)
        self.classID = ClassID
        self.client = None
        self.index = 1  # Verticle Print Position
        self.app.data['messages'] = [
            ('Dude', 'this is awesome'), 
            ('guy', 'i know right?'), 
            ('Dude', 'order pizza?'), 
            ('guy', 'totally order pizza'),
            ('Dude', 'before we order a pizza, lets get in a super duper ultra long string that surely cant be printed into this window... surely...')
            ]
        # LAST THING!
        self.register_module()

    @property
    def messages(self):
        return self.app.data['messages']

    def string_decider(self, panel, string_input):
        if not self.client:
            self.context['text_output'] = f"Not logged in: {string_input}"
        else:
            if self.app.data.get('client', 0):
                self.client.send(f"{string_input}")
            else:
                self.context['text_output'] = f"logged out: {string_input}"
                self.client = None

    def page(self, panel):
        new_message = self.app.data.get('new_message', 0)
        if new_message:
            self.app.data['new_message'] = False
            panel.clear()
            panel.box()
            panel.addstr(0, 1, "| Global Chat |")
        max_rows = self.app.frontend.winright[3]['dims'][0]-2
        max_len = self.app.frontend.winright[3]['dims'][1]-8

        if not self.client:  # we are not logged in
            client_data = self.app.data.get('client', 0)
            if client_data:
                panel.addstr(self.index, 4, f"Logged in to Ruckusist.com\t\t", self.frontend.chess_white)
                self.client = client_data['client']
            else:
                panel.addstr(self.index, 4, f"This shouldnt happen: have client data but no client.", self.frontend.chess_white)

        for message in reversed(self.messages):
            if max_rows <= 2: break
            panel.addstr(max_rows,1,f"{message[0]}: {message[1][:max_len]}")
            max_rows -= 1

        return False