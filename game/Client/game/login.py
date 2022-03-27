import random, threading
import deskapp

from .client import Client

from .map import Game_Map

ClassID = random.random()
class Login(deskapp.Module):
    name = "Login"
    def __init__(self, app):
        super().__init__(app)
        self.classID = ClassID
        self.elements = ['Login', 'Sign-Up', 'Exit']
        self.index = 1  # Verticle Print Position
        self.result_message = "Result: Not yet Logged in..."
        self.username = ''
        self.password = ''
        self.pass_len = 0
        self.client = Client(self)
        # LAST THING!
        self.register_module()

    def string_decider(self, panel, string_input):
        if self.scroll == 0:  # on the username selection
                self.username = string_input
        elif self.scroll == 1:  # on the password selection
            self.pass_len = len(string_input)
            self.password = string_input
        else:
            self.context['text_input'] = string_input
   
    def page(self, panel):
        self.index = 1  # reset this to the top of the box every round
        panel.addstr(self.index, 4, "    Login To Ruckusist.com", self.frontend.chess_white); self.index+=2
        
        self.scroll_elements = [
            f"Username: {self.username}",
            f"Password: {'*'*self.pass_len}",
            "Login",
            "Exit",
        ]

        for index, element in enumerate(self.scroll_elements):
            color = self.frontend.chess_white if index is not self.scroll else self.frontend.color_rw
            panel.addstr(self.index, 4, element, color)
            self.index += 1

        self.index += 2  # increment the Verticle Print Position
        
        panel.addstr(self.index, 4, f"{self.context['text_output']}", self.frontend.chess_white); self.index+=1
        return False

    def send_login_request(self):
        self.context['text_output'] = "Sending Login Request."
        set_of_nogood_usernames = ['', 'dad', 'god']
        flag = False
        if self.username in set_of_nogood_usernames:
            self.context['text_output'] = "Username is No Good."
            flag = True
        set_of_nogood_passwords = ['', ' ', 'password']
        if self.password in set_of_nogood_passwords:
            self.context['text_output'] += "Password is No Good."
            flag = True
        if flag: return False
        self.context['text_output'] = "Sending Login Request Now."
        try:
            if self.client.try_login(self.username, self.password):
                # THIS IS A GOOD LOGIN!
                self.app.data['client'] = {
                    'client': self.client,
                    'username': self.username
                }
                self.context['text_output'] = "log in Successful."

                # LETS TRY TO AUTO LOGIN TO THE GAME!!
                self.app.logic.setup_panel(Game_Map(self.app))

                # lets TRY TO SPLIT THE MAIN SCREEN!!!
                self.app.frontend.dual_main_screen()
                return True
        except Exception as e:
            self.context['text_output'] = f"log in Failed... {e}"
        return False

    def end_safely(self):
        if self.client:
            self.client.end_safely()

    @deskapp.callback(ClassID, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.scroll == 2:  # on the login selection
            self.context['text_output'] = "logging in."
            if not self.send_login_request():
                self.context['text_output'] = "log in attempt failed."

        if self.scroll == 3:  # on the exit selection
            self.context['text_output'] = "Exitting App."
            self.app.close()
