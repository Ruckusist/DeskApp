"""
Deskapp.
by: Ruckusist
"""

__author__      = "Eric Petersen @Ruckusist"
__copyright__   = "Copyright 2022, The Ruckusist Project"
__credits__     = ["Eric Petersen", "@alphagriffin"]
__license__     = "MIT"
__maintainer__  = "Eric Petersen"
__email__       = "ruckusist@outlook.com"
__status__      = "Beta"


name = "DeskApp"
from .app import App, Backend, Logic
from .module import Module
from .keys import Keys
from .callback import callback, callbacks
from .frontend import Frontend
from .mods import *
