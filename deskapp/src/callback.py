"""
Deskapp 1.0
callback.py
last updated: 6-10-23
updated by: Ruckusist
State: Good. Stable.
"""

import functools

callbacks = []
def callback(ID, keypress):
    """
    This callback system is an original design. @Ruckusist.
    """
    global callbacks
    # global messages
    def decorated_callback(func):
        @functools.wraps(func)
        def register_callback(*args, **kwargs):
            kwargs['keypress'] = keypress
            return func(*args, **kwargs)
        callbacks.append({
                'key': keypress,
                'docs': func.__doc__,
                'func': register_callback,
                'classID': ID,
            })
        # print(f"registered callback function {func.__name__}() at keypress: {keypress}")
        # messages.append(f"registered callback function {func.__name__}() at keypress: {keypress} by classID: {ID}")
    return decorated_callback # Maybe it returns NOTHING... oooooohhh....
