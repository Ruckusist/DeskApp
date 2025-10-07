# hworld/client/__main__.py
# last updated: 10-6-25

"""Hworld terminal client entry point"""

import sys
import deskapp
import random
# from login import LoginModule

HworldId = random.random()
class Hworld(deskapp.Module):
    name = "Hworld"
    def __init__(self, app):
        super().__init__(app, "Hworld")
        self.classID = HworldId

    def page(self, panel):
        self.write(panel, int(self.h)//2, int(self.w)//2, f"Hworld.")
        return False

def Main():
    app = deskapp.App(
            name="Deskapp - DeskHunter",
            title="DeskHunter",
            splash_screen=False,
            demo_mode=False,

            show_footer=True,
            show_header=False,
            show_messages=False,
            show_menu=False,
            show_banner=False,
            show_box=False,

            disable_footer=False,
            disable_header=True,
            disable_menu=False,
            disable_messages=True,

            # modules=[Hworld, LoginModule]
            modules=[Hworld]
        )
    app.start()

if __name__ == "__main__":
    Main()
