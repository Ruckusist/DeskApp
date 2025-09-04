"""
Sidedesk server controller package.
Provides a simple manager API to start/stop/restart the DeskApp server
from inside the Sidedesk UI.
"""

from .manager import start, stop, restart, is_running, get_status
