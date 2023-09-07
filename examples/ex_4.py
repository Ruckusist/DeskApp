import time, threading, random
from timeit import default_timer as timer
import onefile
# from deskapp.frontend import main

classID = random.random()
class Math_Game(onefile.Module):
    name = "Math Game"
    def __init__(self, app):
        super().__init__(app)
        self.classID = classID
        self.elements = ['this', 'that', 'other']
        self.index = 1  # Verticle Print Position

        self.should_loop = False  # <-- this is example 3
        self.screen_flag = False
        self.username = 'GerttysGarden'
        self.score = 0
        self.high_score = 0

        self.round = 1
        self.round_time = timer()

        self.min_number = 1
        self.max_number = 10
        # self.other = 1
        self.digit_1 = self.get_digit()
        self.digit_2 = self.get_digit()
        self.context['answer_box'] = ''
        self.register_module()

    def get_digit(self):
        if self.min_number >= self.max_number:
            self.min_number = int(self.max_number/2)
        return random.randint(self.min_number, self.max_number)

    def answer(self):
        return self.digit_1 + self.digit_2

    def loop(self):
        while True:
            if not self.should_loop: break
            start_loop_timer = timer()
            time.sleep(random.randrange(3))
            ## MY AWESOME ARDUINO STYLE CODE GOES HERE

            pass

            ## AND NOW MY RASPI IS A SUPERDUINO... 
            loop_time = timer() - start_loop_timer
            self.context['looptime'] = loop_time

    def page(self, panel):
        if self.screen_flag:
            panel.clear()
            panel.box()
            panel.addstr(0, 1, "| Math Game |")
            self.screen_flag = False
        max_h = self.app.frontend.winright_upper_dims[0]
        max_w = self.app.frontend.winright_upper_dims[1]
        v_line = 1
        
        upperlaneMath = max_w - (9 + len(self.username) + 2)
        # number of used squares - len of username - 2 for border
        top_line = f"╔═══| {self.username} |{'═'*upperlaneMath}╗"
        main_line = f"Score: {self.score} | hScore: {self.high_score}"
        second_line = f"Round: {self.round} | Round_time = {timer()-self.round_time:.2f}"
        bottom_line = f"╚{'═'*(max_w-4)}╝"
        # panel.addstr(v_line, 4, f"╔════════════════════════════════════╗"); v_line += 1
        panel.addstr(v_line, 1, top_line); v_line += 1
        panel.addstr(v_line, 1, f"║{main_line[:max_w-2]:{max_w-4}s}║"); v_line += 1
        # panel.addstr(v_line, 1, f"║{max_h}, {max_w}║"); v_line += 1
        # panel.addstr(v_line, 4, f"╚════════════════════════════════════╝"); v_line += 1
        panel.addstr(v_line, 1, bottom_line); v_line += 2
        panel.addstr(v_line, 4, f"{self.digit_1}"); v_line += 1
        panel.addstr(v_line, 2, f"+ {self.digit_2}"); v_line += 1
        panel.addstr(v_line, 1, f"------"); v_line += 1
        panel.addstr(v_line,4,f"{self.context['text_input']}"); v_line += 2
        panel.addstr(v_line,4,f"{self.context['answer_box']}"); v_line += 1

        return False

    def end_safely(self):
        self.should_loop = False

    def correct_answer(self):
        # time.sleep(2)
        self.screen_flag = True
        self.score += int(self.get_digit()/min(int(timer()-self.round_time), 10))
        self.round_time = timer()
        self.context['answer_box'] = ''
        self.context['text_input'] = ''
        try:
            self.min_number += int(self.get_digit()/4)
            self.max_number += int(self.get_digit()/4)
        except Exception as e:
            self.context['answer_box'] = f'{e}'
        self.digit_1 = self.get_digit()
        self.digit_2 = self.get_digit()

    def wrong_answer(self):
        self.screen_flag = True
        if self.score > self.high_score:
            self.high_score = self.score
            self.context['answer_box'] += 'You set a High Score!'
        self.context['text_input'] = ''
        self.score = 0
        self.min_number = 1
        self.max_number = 10
        self.digit_1 = self.get_digit()
        self.digit_2 = self.get_digit()

    def string_decider(self, panel, string_input):
        try:
            x = int(string_input)
        except:
            x = ''
        self.context["text_input"] = str(x)

    @onefile.callback(classID, onefile.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        
        try:
            player_input = int(self.context['text_input'])
        except:
            self.context['answer_box'] = 'Make sure your answer is a number!'
            return
        if player_input == self.answer():
            self.context['answer_box'] = 'Correct!'
            self.correct_answer()
        else:
            self.context['answer_box'] = 'False!'
            self.wrong_answer()

        pass

if __name__ == "__main__":
    app = onefile.App([Math_Game], demo_mode=False)
    app.start()