import functools, sys, inspect, getpass, time, socket, os
import logging, datetime


"""Console colors that work."""
HEADER     = '\033[95m'
OKBLUE     = '\033[94m'
OKGREEN    = '\033[92m'
WARNING    = '\033[93m'
FAIL       = '\033[91m'
ENDC       = '\033[0m'
BOLD       = '\033[1m'
UNDERLINE  = '\033[4m'

MAGENTA = '\u001b[35m'
YELLOW = '\u001b[33m'
BRIGHT_YELLOW = '\u001b[33;1m'
BRIGHT_WHITE = '\u001b[37;1m'
BRIGHT_GREEN = '\u001b[32;1m'
CYAN = '\u001b[36m'
# CURSOR
# all cursor movements require a .format(num of places to move)
UP          = '\u001b[{n}A'
DOWN        = '\u001b[{n}B'
LEFT        = '\u001b[{n}C'
RIGHT       = '\u001b[{n}D'
ROW_DOWN    = '\u001b[{n}E'
ROW_UP      = '\u001b[{n}F'
CLEARSCREEN = '\u001b[{n}J'.format(n=2)
# shapes
SQUARE = '█'  # '\033[219m'
SQR = u'\u2588'

class Errors:
    def __init__(self, logfile='error.log', level=5, color=False, reporter='?'):
        self.logfile = logfile
        self.level = level
        self.color = color
        self.reporter = reporter
    
    def report(self, mesg:str, level:int, end="\n"):
        report = f"{self.reporter[:3]:3s} {Errors.get_time()}| {mesg}"
        with open(self.logfile, 'a') as f:
            f.write(report+end)
        if level > self.level: return
        if not self.color:
            print(report, end=end)
        if not self.color: return
        
        reporter = f"{BRIGHT_YELLOW}{self.reporter[:3]:<3s}{ENDC}"
        tme_day = time.strftime("%m/%d/%y", time.localtime())
        tme_time = time.strftime("%I:%M%p", time.localtime())
        tme = f"{BRIGHT_GREEN}{tme_day}{ENDC} {YELLOW}{tme_time}{ENDC}"
        color = [BRIGHT_WHITE,MAGENTA,OKBLUE,WARNING][level]
        message = f"{color}{mesg}{ENDC}"
        report = f"{reporter} {tme}| {message}"
        print(report, end=end)
        
    def info(self, message, end="\n"):
        self.report(message, 0, end)
        
    def debug(self, message, end="\n"):
        self.report(message, 1, end)
        
    def error(self, message, end="\n"):
        self.report(message, 2, end)
        
    def junk(self, message, end="\r"):
        self.report(message, 3, end)

    def __call__(self, message, end="\n"):
        self.info(message, end)

    @staticmethod
    def get_user(): 
        # return colored(f"{getpass.getuser()}@{socket.gethostname()}", "cyan")
        return f"{getpass.getuser()}@{socket.gethostname()}"

    @staticmethod
    def get_time(): 
        # return colored(time.strftime("%b %d, %Y|%I:%M%p", time.localtime()), "yellow")
        return time.strftime("%m/%d/%y %I:%M%p", time.localtime())

    @staticmethod
    def error_handler(exception, outer_err, offender, logfile="", verbose=True):
        try:
            outer_off = ''.join([x.strip(' ').strip('\n') for x in outer_err[4]])
            off = ''.join([x.strip(' ').strip('\n') for x in offender[4]])
            error_msg = []
            error_msg.append(f"╔══| Errors® |═[{Errors.get_time()}]═[{Errors.get_user()}]═[{os.getcwd()}]═══>>")
            error_msg.append(f"║ {outer_err[1]} :: {'__main__' if outer_err[3] == '<module>' else outer_err[3]}")
            error_msg.append(f"║ \t{outer_err[2]}: {outer_off}  -->")
            error_msg.append(f"║ ++ {offender[1]} :: Func: {offender[3]}()")
            error_msg.append(f"║ -->\t{offender[2]}: {off}")
            error_msg.append(f"║ [ERR] {exception[0]}: {exception[1]}")
            error_msg.append(f"╚══════════════════════════>>")
            msg = "\n".join(error_msg)
            if logfile:
                with open(logfile, 'a') as f:
                    f.write(msg)
            return msg
        except: print("There has been Immeasureable damage. Good day.")

    @staticmethod
    def protected(func, logfile="", verbose=True):
        """Allows a function to die without killing the app."""
        @functools.wraps(func)
        def p_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                # this is a bad fix... i dont know WTF
                # its been too long since i worked in this
                # area. TODO the Exception should catch
                # all the errors including keyboard, but
                # doesnt. grrrrrrrr.
                print("Keyboard Interrupt: Ending Safely.")
                pass
            except Exception:
                exception = sys.exc_info()
                print(f"Num of Errors: {len(inspect.stack())}")
                for outer_err, offender in zip(inspect.stack(), inspect.trace()):
                    err = Errors.error_handler(
                        exception, 
                        outer_err, 
                        offender, 
                        logfile, 
                        verbose
                    )
                    print(err)
        return p_func
  
  
@Errors.protected  
def main():
    print(f"{UNDERLINE}Starting Errors Tests.{ENDC}")
    # while True:
    x = [1]
    print(x[len(x)])
    
    x = Errors('errors.txt', level=3, color=True, reporter="Srv")
    x.info("test")
    x.debug("That")
    x.error("errors: stuff")
    x.junk("JUNK")
    print("finished")
    
    
if __name__ == "__main__":
    main()