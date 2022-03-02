import random, os, threading, time
from deskapp.module import Module
from deskapp.callback import callback
from deskapp.keys import Keys

from jinja2 import Environment, FileSystemLoader
import pkg_resources


classID = random.random()
class Fire(Module):
    """My Cool Fire Animation."""

    name = "Fire"

    def __init__(self, app):
        super().__init__(app)
        self.started = False
        self.start_flag = 0
        self.background_process = True
        self.classID = classID
        
    def get_dims(self):
        self.context['w'] = int(self.app.frontend.winright_dims[1] - 2)
        self.context['h'] = int(self.app.frontend.winright_dims[0] - 5)
        self.context['size'] = self.context['h'] * self.context['w']
        self.context['char'] = [" ", ",", "^", "~", "*", "|", "H", "$", "#", "@"]

    @callback(classID, Keys.ENTER)   
    def on_enter(self, *args, **kwargs):
        """Ascii Fire, for demonstation purpose."""
        self.started = True
        if self.start_flag:
            if self.background_process:
                self.background_process = False
            else:
                self.background_process = True
                self.background_thread = threading.Thread(target=self.multipass)
                self.background_thread.start()

    def end_safely(self):
        self.background_process = False

    def one_pass(self):
        # credit : https://medium.com/sweetmeat/python-curses-based-ascii-art-fire-animation-259e9e007767
        w = self.context['w']
        h = self.context['h']
        b = self.context['b']
        size = self.context['size']
        c = self.context['char']
        for i in range(int(w/9)):
            b[int((random.random()*w)+w*(h-1))] = 105 # WTF?

        # for each pixel cube.
        for i in range(size):
            ## average over a pixel cube...
            # i think this is fire resolution... maybe adding b[i+w*2] + b[i+w*2+1]
            # but then you would also have to add this row to the size of b
            # plus you would want to add b[i+2], b[i+w+2], b[i+w*2+2], for a full 3x3
            # then divide over 9 obviously
            #  2x2
            # b[i] = int((
            #     b[i] + b[i+1] + b[i+w] + b[i+w+1]
            # )/4)
            #  3x3
            b[i] = int((
                b[i] + b[i+1] + b[i+2] + b[i+w] + b[i+w+1] + b[i+w+2] + b[i+w*2] + b[i+w*2+1] + b[i+w*2+2]
            )/9)
            #  4x4
            #b[i] = int((
            #    b[i] + b[i+1] + b[i+2] + b[i+3] +\
            #    b[i+w] + b[i+w+1] + b[i+w+2] + b[i+w+3] +\
            #    b[i+w*2] + b[i+w*2+1] + b[i+w*2+2] + b[i+w*2+2] +\
            #    b[i+w*3] + b[i+w*3+1] + b[i+w*3+2] + b[i+w*3+3]
            #    )/16)

            color = 0

            if i < size-1:
                self.context['gameboard'][int(i/w)][i%w] = c[(9 if b[i] > 9 else b[i])]

    def multipass(self):
        while True:
            if not self.background_process:
                break
            try:
                self.one_pass()
                # time.sleep(.005)
            except Exception as e:
                self.app.ERROR(e)
                break

    def page(self, panel=None):
        self.get_dims()
        if self.started:
            if not self.start_flag:
                self.start_flag = 1
                # build a blank set of zeros... np.zeros(w,h)??
                self.context['b'] = []
                for _ in range(self.context['size']+self.context['w']*5+3):
                    self.context['b'].append(0)
                self.context['blen'] = len(self.context['b'])
                self.context["gameboard"] = []
                for _ in range(self.context['h']):
                    row = []
                    for _ in range(self.context['w']):
                        row.append(' ')
                    self.context['gameboard'].append(row)
                self.background_thread = threading.Thread(target=self.multipass)
                self.background_thread.start()
                
        # template = self.templates_stock.get_template("fire.j2")
# This panel size is W: {{context.w}} H: {{context.h}}
# Using Char Set of: {% for x in context.char %}{{ x }} {% endfor %}
# Fire Grid: {{ context.blen }}

        page = """
{% for x in context.gameboard %}{% for y in x %}{{y}}{% endfor %}
{% endfor %}
        """
        template = Environment().from_string(page)
        if not self.background_process: self.context["gameboard"] = []
        return template.render(context=self.context)
