import deskapp
from .game import Login, Global_Chat, Game_Map

def main() -> None:
    app = deskapp.App([Login, Global_Chat, Game_Map])
    app.start()

main()