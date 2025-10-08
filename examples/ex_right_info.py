# examples/ex_right_info.py
# last updated: 10-07-25
# added by: GPT5
# Minimal example showcasing new Right Panel (NUM7) and Info Panel (NUM8)

try:
    import deskapp
except ImportError:
    print("#==? [ERR] You must install Deskapp first.")
    print("#==> [COPY] pip install -U deskapp")
    exit(1)

class Demo(deskapp.Module):
    name = "Demo"
    def __init__(self, app):
        super().__init__(app, "Demo")

    def page(self, panel):
        # main panel content
        self.write(panel, 2, 2, "Main Panel")
        self.write(panel, 4, 2, "Press NUM7 toggle Right")
        self.write(panel, 5, 2, "Press NUM8 toggle Info")
        return False

    def PageRight(self, panel):  # optional right panel content
        try:
            self.write(panel, 1, 2, "Right Panel", color="green")
            self.write(panel, 2, 2, "Extra data...", color="blue")
            self.write(panel, 3, 2, "Hello World", color="yellow")
        except Exception:
            pass

    def PageInfo(self, panel):  # custom info panel (3 lines)
        try:
            self.write(panel, 1, 2, "Info: Demo Module", color="cyan")
            self.write(panel, 2, 2, "NUM7 Right | NUM8 Info", color="yellow")
            self.write(panel, 3, 2, "PgUp/Dn Switch Mods", color="green")
            return True
        except Exception:
            return None


def main():
    app = deskapp.App(
        modules=[Demo],
        demo_mode=False,
        show_menu=False,
        show_messages=False,
        show_right_panel=True,   # start with right panel visible
        show_info_panel=True,    # info panel on by default
        show_header=False,
        show_footer=True,
        show_box=True,
        show_banner=True,
    )
    app.start()

if __name__ == "__main__":
    main()
