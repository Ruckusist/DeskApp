import functools # , random, os, pkg_resources

callbacks = []
def callback(ID, keypress) -> ():
    """
    This callback system is an original design. @Ruckusist.
    """
    global callbacks
    def decorated_callback(func) -> ():
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
    return decorated_callback # Maybe it returns NOTHING... oooooohhh....