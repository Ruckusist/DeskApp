from deskapp import App
from deskapp.deskchat import Login, Status, Users, Chat, Log, Settings, Test


def main():
    app = App([
        Login,
        Status,
        Users,
        Chat,
        Log,
        Settings,
        Test,
    ], splash_screen=False, demo_mode=False, name="Deskchat", title="Deskchat", header="Welcome to Deskchat!")
    app.start()


if __name__ == "__main__":
    main()
