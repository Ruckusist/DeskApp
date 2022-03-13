import deskapp

class Global_Chat(deskapp.Module):
    name = "Global Chat"
    def __init__(self, app):
        super().__init__(app)
        self.messages = [
            ('Dude', 'this is awesome'), 
            ('guy', 'i know right?'), 
            ('Dude', 'order pizza?'), 
            ('guy', 'totally order pizza'),
            ('Dude', 'before we order a pizza, lets get in a super duper ultra long string that surely cant be printed into this window... surely...')
            ]
        self.index = 1  # Verticle Print Position

    def page(self, panel):
        max_rows = self.app.frontend.winright[3]['dims'][0]-2
        max_len = self.app.frontend.winright[3]['dims'][1]-8
        for message in reversed(self.messages):
            if max_rows <= 2: break
            panel.addstr(max_rows,1,f"{message[0]}: {message[1][:max_len]}")
            max_rows -= 1

        return False