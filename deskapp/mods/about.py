import random
from ..module import Module
from ..callback import callback

from jinja2 import Environment

aboutID = random.random()
class About(Module):
    name = "About"
    def __init__(self, app):
        self.classID = aboutID
        super().__init__(app)
        

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
a new python app without a desktop. Stream Data on a
Raspberrypi, build a log viewer, capture and display
stock/crypto prices... Build a math game for kids.
Originally concieved to display tensorflow training
statistics while training. intended to run in a tmux
window in the background for long sessions.
        """
        # template = self.templates_stock.get_template("about.j2")
        template = Environment().from_string(page)
        return template.render(context=self.context)

    @callback(ID=aboutID, keypress=10)
    def on_enter(self, *args, **kwargs):
        self.visible = False