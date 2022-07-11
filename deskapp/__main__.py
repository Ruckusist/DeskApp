from deskapp import App

def main() -> None:
    app = App(
        title = "DeskApp",
        header = "Welcome to Deskapp",
        demo_mode = True,
        splash_screen = True,
        v_split = .5,
    )
    app.start()

if __name__ == "__main__":
    main()