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

    @property
    def h(self):
        return self.app.logic.current_dims()[0]

    @property
    def w(self):
        return self.app.logic.current_dims()[1]

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

