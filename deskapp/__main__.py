import random
import deskapp


HelloID = random.random()
class Hello(deskapp.Module):
    """The simplest module - just displays a message."""
    name = "Hello"  # Shows in menu

    def __init__(self, app):
        super().__init__(app, HelloID)

    def page(self, panel):
        self.write(panel, 2, 2, "Hello, World", 'cyan')

def main():
    deskapp.App(modules=[Hello], demo_mode=True)


if __name__ == "__main__":
    main()
