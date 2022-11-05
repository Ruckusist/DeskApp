import time, os
from deskapp import App

def main() -> None:
    app = App(
        title = "DeskApp",
        header = "Welcome to Deskapp",
        demo_mode = True,
        splash_screen = True,
        v_split = .5,
        h_split = .3,
        autostart = False,
    )
    print("Testing The Deskapp...")
    time.sleep(3)
    os.system('clear')
    time.sleep(1)
    app.start()

if __name__ == "__main__":
    main()