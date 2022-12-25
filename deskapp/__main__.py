import time, os
# from deskapp import App
# from deskapp import Draw
from .src.frontend import Frontend_TEST, Frontend

def main() -> None:
    # app = App(
    #     title = "DeskApp",
    #     header = "Welcome to Deskapp",
    #     demo_mode = True,
    #     splash_screen = True,
    #     v_split = .4,
    #     h_split = .16,
    #     autostart = False,
    # )
    # app.start()
    # Draw()
    
    x = Frontend()
    x()

if __name__ == "__main__":
    main()
