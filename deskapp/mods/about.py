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
        self.register_module()
        

    def page(self, panel=None):
        page = """
### About ###
    _ \             |              _)      |   
   |   | |   |  __| |  / |   |  __| |  __| __|
   __ <  |   | (      <  |   |\__ \ |\__ \ |  
  _| \_\\__,_|\___|_|\_\\__,_|____/_|____/\__|
* Created by Ruckusist @ Ruckusist.com
* Clone  @ Ruckusist.com/ruckusTUI.git
    or   @ github.com/ruckusist/ruckusTUI.git

TUI in python is still harder than it should be.
Hopefully this helps someone get their data on
their screen faster than doing this all over from
scratch everytime.
        """
        # template = self.templates_stock.get_template("about.j2")
        template = Environment().from_string(page)
        return template.render(context=self.context)

    @callback(ID=aboutID, keypress=10)
    def on_enter(self, *args, **kwargs):
        self.visible = False