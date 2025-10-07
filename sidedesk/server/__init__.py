"""
Sidedesk server controller package.

Delegates to the shared deskapp deskchat server manager so Sidedesk does not
implement unique server behavior. This ensures all features (detach, metrics)
live under deskapp.
"""

from deskapp.deskchat.server import start, stop, restart, is_running, get_status
