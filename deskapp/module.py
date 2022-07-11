from deskapp.callback import callback, callbacks
from deskapp.keys import Keys

import functools, random, os, pkg_resources
from jinja2 import Environment, FileSystemLoader


classID = lambda x: random.random()
class Module:
    """This is the Module Factory"""

    name = "BasicModule"

    def __init__(self, app):
        self.app = app
        self.backend = app.backend
        self.logic = app.logic
        self.frontend = app.frontend
        self.menu = app.menu
        # depricated -->
        self.context = {
            "text_input": "",
            "text_output": "",
        }
        # RESIZE WILL BREAK THIS.
        self.max_h = self.app.frontend.winright_upper_dims[0]
        self.max_w = self.app.frontend.winright_upper_dims[1]
        self.callbacks = []
        self.cur_el = 0
        self.elements = []
        self.scroll_elements = []
        self.scroll = 0
        self.classID = 0
        self.visible = True

    def register_module(self):
        # DEPRICATING THIS!
        # self.app.menu.append((self.name, self.page, self.string_decider, self))
        self.menu.append(self)  # boom.

    def __setup__(self):
        # creates a variable to get at the hard to find stock templates
        TEMPLATE_PATH = pkg_resources.resource_filename(
            'deskapp', 'mods/templates')
        self.templates_stock = Environment(loader=FileSystemLoader(
            TEMPLATE_PATH, followlinks=True))
        
        # add module to the active list.
        self.register_module()

    def page(self, panel=None):
        template = self.templates_stock.get_template(f"{self.name}.j2")
        return template.render(context=self.context)

    def string_decider(self, panel, string_input):
        # panel.addstr(1, 3, f"[{name}] {string_input}"))
        self.context["text_input"] = string_input

    def on_enter(self, *args, **kwargs):
        """Basic Enter Key Press."""
        pass

    def end_safely(self):
        pass

    @callback(0, keypress=Keys.UP)
    def on_up(self, *args, **kwargs): 
        """scroll up"""
        if self.scroll > 0:
            self.scroll -= 1
        else: self.scroll = len(self.scroll_elements)-1

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
