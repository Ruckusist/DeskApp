import time, threading, random
from timeit import default_timer as timer
import deskapp

classIDEx3 = random.random()

class Ex3(deskapp.Module):
    name = "Example 3"
    
    def __init__(self, app):
        super().__init__(app, classIDEx3)
        self.elements = ['this', 'that', 'other']
        self.index = 1  # Vertical Print Position
        
        self.should_loop = False  # <-- this is example 3
        self.context = {'looptime': 0.0}  # Initialize context dictionary
        
        self.register_module()
        self.context['looptime'] = 0.0
        
        self.register_module()

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
        panel.win.addstr(1, 1, "Example Three.")
        self.index = 3  # reset this to the top of the box every round

        # HORIZONTAL SCROLLER
        h_index = 0  # HORIZONTAL index
        for index, element in enumerate(self.elements):
            color = self.front.chess_white if index is not self.cur_el else self.front.color_red
            panel.win.addstr(self.index, 2+h_index, element, color)
            h_index += 1 + len(element)

        self.index += 1  # increment the Vertical Print Position
        if self.should_loop:
            msg = f"Looping... Sleeping for {self.context['looptime']:.2f} secs"
        else: 
            msg = "Press Enter to Start Looping."
        panel.win.addstr(self.index, 4, msg, self.front.chess_white)
        return False

    def end_safely(self):
        self.should_loop = False

    @deskapp.callback(classIDEx3, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.should_loop: 
            self.should_loop = False
        else:
            self.should_loop = True
            threading.Thread(target=self.loop).start()

if __name__ == "__main__":
    app = deskapp.App([Ex3])
    app.start()