import deskapp

class Login(deskapp.Module):
    name = "Login"
    def __init__(self, app):
        super().__init__(app)

        self.elements = ['Login', 'Sign-Up', 'Exit']
        self.index = 1  # Verticle Print Position

    def page(self, panel):
        # panel.addstr(1,1,"Example Two.")
        self.index = 1  # reset this to the top of the box every round

        # HORIZONTAL SCROLLER
        h_index = 0  # HORIZONTAL index
        for index, element in enumerate(self.elements):
            color = self.frontend.chess_white if index is not self.cur_el else self.frontend.color_rw
            panel.addstr(self.index, 2+h_index, element, color)
            h_index += 1 + len(element)

        self.index += 2  # increment the Verticle Print Position
        panel.addstr(self.index, 4, "Username: Thrall", self.frontend.chess_white); self.index+=1
        panel.addstr(self.index, 4, "Password: ******", self.frontend.chess_white); self.index+=2
        panel.addstr(self.index, 4, "Result: Login Successful", self.frontend.chess_white); self.index+=1

        return False