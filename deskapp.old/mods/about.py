import random
from jinja2 import Environment
from onefile import Module, callback, Keys


classID = random.random()
class About(Module):
    name = "About"
    def __init__(self, app):
        super().__init__(app)
        self.classID = classID
        self.register_module()
        

    def page(self, panel=None):
        page = """
### About ###
    _ \             |              _)      |   
   |   | |   |  __| |  / |   |  __| |  __| __|
   __ <  |   | (      <  |   |\__ \ |\__ \ |  
  _| \_\\__,_|\___|_|\_\\__,_|____/_|____/\__|
* Created by Ruckusist @ Ruckusist.com
* Clone  @ Ruckusist.com/deskapp.git
    or   @ github.com/ruckusist/deskapp.git

Deskapp is a Curses Based UX for easily implementing
a new Python app without a desktop. Stream data on a
Raspberrypi, build a log viewer, capture and display
stock/crypto prices... Build a math game for kids.
Originally conceived to display Tensorflow training
statistics while training. Intended to run in a tmux
window in the background for long sessions.
        """
        # template = self.templates_stock.get_template("about.j2")
        template = Environment().from_string(page)
        return template.render(context=self.context)

    @callback(classID, keypress=Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.print("About: pressed enter")
        # self.visible = False