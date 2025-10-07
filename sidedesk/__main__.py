


from deskapp import App
from sidedesk import Login, Status, Users, Chat, Log, Settings, Test, Ollama, Gemini, OpenAI, Hugface, client

def main():
	app = App([
		Login,
		Status,
		Users,
		Ollama,
		Gemini,
		OpenAI,
		Hugface,
		Chat,
		Log,
		Settings,
		Test
	], splash_screen=False, demo_mode=False, name="Sidedesk", title="Sidedesk", header="Welcome to Sidedesk!", autostart=False, show_messages=False)
	# Wire client manager to app data so local bots and chat can update UI
	client.init_app(app.print, app.data)
	app.start()

if __name__ == "__main__":
	main()
