import time
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
    print("This is working!")
    time.sleep(3)
    app.setup()
    app.start()

if __name__ == "__main__":
    main()