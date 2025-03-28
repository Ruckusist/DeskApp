from deskapp import SubClass, Keys, callback, callbacks



class Module(SubClass):
    name = "Basic Module"
    def __init__(self, app, class_id):
        super().__init__(app)
        self.class_id = class_id
        self.cur_el = 0
        self.elements = []
        self.scroll = 0
        self.scroll_elements = []
        self.input_string = ""
        self.mouse_input = None

    @property
    def h(self):
        return self.app.logic.current_dims()[0]

    @property
    def w(self):
        return self.app.logic.current_dims()[1]
    
    def write(self, panel, x, y, string, color=None):
        if color == "yellow":
            c = self.front.color_yellow
        elif color == "red":
            c = self.front.color_red
        elif color == "green":
            c = self.front.color_green
        elif color == "blue":
            c = self.front.color_blue
        elif color == "black":
            c = self.front.color_black        
        else: 
            c = self.front.color_white
        if x >= self.h: 
            self.print("printed too many rows (x)")
            return
        if y >= self.w:
            self.print("printed off screen (y)")
            return
        if len(string) > self.w-y:
            self.print("string is too long")
            return
        panel.win.addstr(x, y, string,c)

    def element_scroller(self, panel):
        # self.index = 3
        for index, element in enumerate(self.scroll_elements):
            color = self.front.chess_white if index is not self.scroll else self.front.color_black
            cursor = ">> " if index is self.scroll else "   "
            panel.win.addstr(index+self.index, 2, cursor+element, color)
        self.index += len(self.scroll_elements)

    def register_module(self):
        self.app.menu.append(self)

    def page(self, panel):
        panel.win.addstr(2,2,"This is working!")

    def mouse_decider(self, mouse): pass

    def string_decider(self, input_string):
        self.input_string = input_string
        self.print(f"text input: {input_string}")

    def end_safely(self): pass

    @callback(0, keypress=Keys.UP)
    def on_up(self, *args, **kwargs):
        if self.scroll < 1:
            self.scroll = len(self.scroll_elements)-1
        else: self.scroll -= 1

    @callback(0, keypress=Keys.DOWN)
    def on_down(self, *args, **kwargs):
        """scroll down"""
        if self.scroll < len(self.scroll_elements)-1:
            self.scroll += 1
        else: self.scroll = 0

    @callback(0, keypress=Keys.RIGHT)
    def on_left(self, *args, **kwargs):
        """rotate clickable elements"""
        if self.cur_el < len(self.elements)-1:
            self.cur_el += 1
        else: self.cur_el = 0

    @callback(0, keypress=Keys.LEFT)
    def on_right(self, *args, **kwargs):
        """rotate clickable elements"""
        if self.cur_el > 0:
            self.cur_el -= 1
        else: self.cur_el = len(self.elements)-1

