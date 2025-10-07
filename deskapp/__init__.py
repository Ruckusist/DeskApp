"""
Deskapp 1.0
app.py
last updated: 6-10-23
updated by: Ruckusist
State: Good. Stable.
"""
class SubClass:
    def __init__(self, app):
        self.app   = app
        self.print = app.print
        self.front = app.front

# from .src.test import Test
from .src.callback import callback, callbacks
from .src.keys import Keys
from .src.curse import Curse
from .src.module import Module
from .src.backend import Backend

from .src.logic import Logic

from .src.app import App

from . import apis
