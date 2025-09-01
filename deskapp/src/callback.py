"""
Deskapp 1.0
callback.py
last updated: 6-10-23
updated by: Ruckusist
State: Good. Stable.
"""

import functools
from typing import Any, Callable, Dict, List, Optional

callbacks: List[Dict[str, Any]] = []

def callback(ID: int, keypress: int) -> Callable:
    """
    A decorator for registering callback functions for key events.
    
    This callback system is an original design by @Ruckusist that allows
    modules to register functions to be called when specific keys are pressed.
    
    Args:
        ID (int): Class identifier for the callback
        keypress (int): The key code that triggers this callback
        
    Returns:
        Callable: The decorated function
    """
    global callbacks
    
    def decorated_callback(func: Callable) -> Callable:
        @functools.wraps(func)
        def register_callback(*args: Any, **kwargs: Any) -> Any:
            kwargs['keypress'] = keypress
            return func(*args, **kwargs)
            
        callbacks.append({
            'key': keypress,
            'docs': func.__doc__,
            'func': register_callback,
            'classID': ID,
        })
        return register_callback
        
    return decorated_callback
