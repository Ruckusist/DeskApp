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

from .src.callback import callback, callbacks
from .src.frontend import Frontend
from .src.backend import Backend
from .src.logic import Logic
from .src.keys import Keys
from .src.module import Module
from .src.app import App

