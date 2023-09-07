from deskapp import SubClass, Keys

class Logic(SubClass):
    def __init__(self, app):
        super().__init__(app)
        self.current = 0
        self.available_panels = {}

    def current_mod(self):
        name = list(self.available_panels)[self.current]
        return self.available_panels[name][0]

    def current_panel(self):
        name = list(self.available_panels)[self.current]
        return self.available_panels[name][1]
    
    def current_dims(self):
        name = list(self.available_panels)[self.current]
        return self.available_panels[name][2]

    def string_decider(self, input_string):
        mod = self.current_mod()
        mod.string_decider(input_string)

    def decider(self, keypress):
        """Callback decider system."""
        # Do we have a good keypress?
        if isinstance(keypress, int):
            if 0 >= keypress: return

        mod_name = list(self.available_panels)[self.current]
        cur_mod = self.available_panels[mod_name]

        mod_class = cur_mod[0]
        mod_panel = cur_mod[1]

        if isinstance(keypress, str):
            mod_class.string_decider(self.front.key_buffer)
            self.front.key_buffer = ""

        elif isinstance(keypress, tuple):
            mod_class.mouse_decider(keypress)

        elif isinstance(keypress, int):
            try:
                global callbacks
                all_calls_for_button = list(filter(lambda callback: callback['key'] in [int(keypress)], callbacks))
                if not all_calls_for_button:
                    self.print(f"{keypress} has no function")
                    return
                call_for_button = list(filter(lambda callback: callback['classID'] in [mod_class.class_id,0,1], all_calls_for_button))  # [0]
                callback = call_for_button[0]['func']  # TODO: come back for this 0, cant be right.
                callback(mod_class, mod_panel)

            except Exception as e:
                self.print(e)
