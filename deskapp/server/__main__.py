import time
from deskapp import Module, Keys, callback, App
from deskapp.server import Server


def main():
    srv = Server()
    srv.start()
    while True:
        try:
            time.sleep(.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
    srv.end_safely()



if __name__ == "__main__":
    main()