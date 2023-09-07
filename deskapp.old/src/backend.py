import os
import sys, inspect     # tracebacks
import time, datetime   # time
import socket, getpass  # for user information


class OLD_Backend:
    """This is the Main_Loop"""
    def __init__(self, parent):
        self.app = parent
        self.running = True
        self.error_log = self.app.error_log
        
    def logger(self, message:list, message_type:str):       
        # for line in message:
        #     print(f"[{message_type}]\t{line}")
        #  TODO
        self.error_log.append((message, message_type))

    def get_user(self): return f"{getpass.getuser()}@{socket.gethostname()}"

    def get_time(self): return time.strftime("%b %d, %Y|%I:%M%p", time.localtime())

    def error_handler(self, exception, outer_err, offender, logfile="", verbose=True):
        try:
            outer_off = ''.join([x.strip(' ').strip('\n') for x in outer_err[4]])
            off = ''.join([x.strip(' ').strip('\n') for x in offender[4]])
            error_msg = []
            error_msg.append(f"╔══| Errors® |═[{self.get_time()}]═[{self.get_user()}]═[{os.getcwd(), 'green'}]═══>>\n")
            error_msg.append(f"║ {outer_err[1]} :: {'__main__' if outer_err[3] == '<module>' else outer_err[3]}\n")
            error_msg.append(f"║ \t{outer_err[2]}: {outer_off}  -->\n")
            error_msg.append(f"║ ++ {offender[1]} :: Func: {offender[3]}()\n")
            error_msg.append(f"║ -->\t{offender[2]}: {off}\n")
            error_msg.append(f"║ [ERR] {exception[0]}: {exception[1]}\n")
            error_msg.append(f"╚══════════════════════════>>\n\n")
            msg = "".join(error_msg)
            log_print(msg)
            # return msg
            return msg
        except: print("There has been Immeasureable damage. Good day.")

    def print_error(self, err):
        error_mesg = err[0]
        print(err[1])
        for line in error_mesg:
            print(line)

    @property
    def is_running(self):
        return self.running

    async def main(self):
        while self.is_running:
            self.app.frontend.refresh()
            keypress = 0
            keypress = self.app.frontend.get_input()
            # if keypress:
            self.app.logic.decider(keypress)
            self.app.logic.all_page_update()
  
    def start(self):
        try:
            # print("Starting main loop.")
            asyncio.run(self.main())
        except KeyboardInterrupt:
            # so it should never end this way.
            print("Keyboard Interrupt: Ending Safely.")
        except Exception:
            exception = sys.exc_info()
            outer_err = inspect.stack()[-1]
            offender = inspect.trace()[-1]
            error = self.error_handler(
                exception, 
                outer_err, 
                offender
            )
            # The error isnt working because its not printing.
            print(error)

        finally:
            self.exit_program()

    def exit_program(self):
        self.app.logic.end_safely()


class Backend:
    """
    Backend.
    This should be the main running thread. This should be the 
    main exception catcher. 
    
    TODO: fork the process and hold on to it as a tray icon(w/e).
    Then come back to the running instance, there should be a 
    exit/shutdown difference.
    TODO: do the error handling and make a nice text file out 
    of it.
    TODO: The profiler should begin to grow here but eventually 
    move out it its own class.
    TODO: Should modules use a thread that has already been 
    modified by the backend?
    """
    def __init__(self, app):
        self.app = app
        self.running = True
        self.print = app.print

    def main(self):
        while self.running:
            try:
                self.app.frontend.refresh()  # just calls some curses funcs.
                # CAPTURE KEYBOARD
                keypress = self.app.frontend.get_input()
                if keypress and keypress != -1 and keypress != 0:
                    self.app.logic.decider(keypress)

                # Capture Mouse
                if keypress == 0:
                    mouseclick = self.app.frontend.get_click()  # ((x,y), btn)
                    self.app.logic.decider(mouseclick)
                
                self.app.logic.all_page_update()

            except KeyboardInterrupt:
                self.running = False
            except Exception as ex:
                self.print("ERR: Loop Error in Input. Try Again.")
                if ex: self.print(ex)
        
        self.exit_program()

    def start(self):
        self.main()

    def exit_program(self):
        self.app.logic.end_safely()
