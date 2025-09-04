


from deskapp import App
from sidedesk import Login, Status, Users, Chat, Log, Settings, Test

def main():
	app = App([
		Login,
		Status,
		Users,
		Chat,
		Log,
		Settings,
		Test
	], splash_screen=False, demo_mode=False, name="Sidedesk", title="Sidedesk", header="Welcome to Sidedesk!")
	app.start()

if __name__ == "__main__":
	main()
