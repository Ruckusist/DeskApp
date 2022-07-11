from deskapp import App

def main() -> None:
    app = App(
        title = "Dude",
        header = "Sweet",
        demo_mode = True,
        splash_screen = True,  # SPLASH SCREEN
        v_split = .5,
        
    )
    # app.set_header("Welcome to Deskapp")
    # app.set_title("D.e.s.k. App")
    app.start()

if __name__ == "__main__":
    main()