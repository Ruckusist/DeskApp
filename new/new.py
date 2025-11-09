import os, random, time, datetime, sys, threading
from queue import Queue, Empty
import deskapp
import ollama


class Comms:
	def __init__(self, model="gemma3", persona=None):
		self.model = model
		self.persona = persona

		if not persona:
			with open(f"./persona/{model}.txt", "r") as f:
				persona = f.readlines()
		else:
			with open(f"./persona/{persona}.txt", "r") as f:
				persona = f.readlines()
		with open(f"./persona/rules.txt", "r") as f:
			rules = f.readlines()

		persona = "".join(persona).strip()
		rules = "".join(rules).strip()
		self.setup = self.system_call(persona + "\n\n" + rules)


	def system_call(self, content):
		Res = ollama.chat(
			model=self.model,
			messages=[{
					'role': 'system',
					'content': content,
				}],
		 )

		return Res['message']['content']

	def user_call(self, content, images=None):
		Res = ollama.chat(
			model=self.model,
			messages=[{
					'role': 'user',
					'content': content,
					'images': images,
				}],
		 )

		return Res['message']['content']

	@staticmethod
	def Call(
			Model="gemma3",
			Role='user',
			Content="answer in as few words as possible. have you been given an image? if so what is this image?",
			Images=None,
			):

		Res = ollama.chat(
			model=Model,
			messages=[{
					'role': Role,
					'content': Content,
					'images': Images,
				}],
		)

		return Res['message']['content']

ChatID = random.random()
class ThreadedComms(threading.Thread):
	"""
	Threaded wrapper for Comms. Runs ollama API calls in a
	separate thread to prevent UI blocking.
	Implementation: Proposal 31 (Threaded Comms)
	"""
	def __init__(self, model="gemma3", persona=None):
		super().__init__(daemon=True)
		self.model = model
		self.persona = persona
		self.requestQueue = Queue()
		self.responses = {}
		self.responseId = 0
		self.shutdownEvent = threading.Event()
		self.comms = None
		self.start()

	def run(self):
		"""Worker thread main loop."""
		try:
			self.comms = Comms(
				model=self.model,
				persona=self.persona
			)
		except Exception as e:
			self.responses[-1] = {"error": str(e)}
			return

		while not self.shutdownEvent.is_set():
			try:
				reqId, method, args, kwargs = \
					self.requestQueue.get(timeout=0.1)

				try:
					if method == "system":
						res = \
						self.comms.system_call(*args, **kwargs)
					elif method == "user":
						res = \
						self.comms.user_call(*args, **kwargs)
					else:
						res = None

					self.responses[reqId] = {"result": res}
				except Exception as e:
					self.responses[reqId] = \
						{"error": str(e)}
			except Empty:
				continue

	def systemCall(self, content):
		"""Queue a system call. Returns request ID."""
		self.responseId += 1
		self.requestQueue.put(
			(self.responseId, "system", (content,), {})
		)
		return self.responseId

	def userCall(self, content, images=None):
		"""Queue a user call. Returns request ID."""
		self.responseId += 1
		self.requestQueue.put(
			(self.responseId, "user", (content,), {"images": images})
		)
		return self.responseId

	def getResponse(self, reqId, timeout=0.1):
		"""
		Get response for request ID.
		Returns (success, result) or (False, None) if not ready.
		"""
		if reqId in self.responses:
			resp = self.responses.pop(reqId)
			if "error" in resp:
				return False, resp["error"]
			return True, resp.get("result")
		return False, None

	def shutdown(self):
		"""Stop the worker thread."""
		self.shutdownEvent.set()
		self.join(timeout=2.0)

class Chat(deskapp.Module):
	"""A simple chat module."""
	name = "Ollama Chatter Box."

	def __init__(self, app):
		super().__init__(app, ChatID)
		self.user_has_inputed = False
		self.user_text = ""
		self.bots_online = []
		self.history_buffer = []
		self.prev_buff_len = 0
		self.pendingRequest = None
		self.thinkingMsg = "Wizbot: [thinking...]"

		# Initialize threaded Comms with persona
		self.wizbot = ThreadedComms(model="gemma3", persona="wizard")
		setupId = self.wizbot.systemCall("")
		self.pendingRequest = setupId


	def string_decider(self, input_string):
		self.user_has_inputed = True
		self.user_text = "USER: " + input_string

	def page_loop_logic(self):
		# Check for pending response
		if self.pendingRequest is not None:
			success, response = \
				self.wizbot.getResponse(self.pendingRequest)
			if success:
				if response:
					self.history_buffer.append(
						"Wizbot: " + response
					)
				self.pendingRequest = None

		# Queue new user input
		if self.user_has_inputed:
			self.history_buffer.append(self.user_text)
			self.pendingRequest = \
				self.wizbot.userCall(self.user_text)
			self.user_has_inputed = False
			self.user_text = ""

	def wrapText(self, text, maxWidth):
		"""
		Wrap text to max width, breaking on word boundaries.
		Returns list of wrapped lines.

		Implementation: Proposal 30 (Dynamic Chat Word Wrap)
		"""
		if maxWidth < 1:
			return [text]

		lines = []
		for paragraph in text.split("\n"):
			if not paragraph.strip():
				lines.append("")
				continue

			words = paragraph.split()
			currentLine = ""

			for word in words:
				testLine = currentLine + " " + word
				if not currentLine:
					testLine = word

				if len(testLine) <= maxWidth:
					currentLine = testLine
				else:
					if currentLine:
						lines.append(currentLine)
					currentLine = word

			if currentLine:
				lines.append(currentLine)

		return lines

	def page(self, panel):
		self.page_loop_logic()

		# BOT STATUS
		self.write(panel, 1, 1,
			"Bots: " + str(len(self.bots_online)), 'yellow')

		idx = 2
		maxWidth = max(10, self.w - 2)

		# CHAT HISTORY
		for line in self.history_buffer:
			wrappedLines = self.wrapText(line, maxWidth)
			isUserMsg = line.startswith("USER: ")
			color = 'red' if isUserMsg else "black"

			for i, wrappedLine in enumerate(wrappedLines):
				self.write(panel, idx, 1, wrappedLine, color)
				idx += 1
				if idx >= self.h - 1:
					return

	@deskapp.callback(ChatID, deskapp.Keys.C)
	def chat_callback(self, *args, **kwargs):
		"""C key triggers a chat call."""
		for line in self.history_buffer:
			self.print(line)

	def end_safely(self):
		"""Shutdown threaded comms on module cleanup."""
		super().end_safely()
		if self.wizbot:
			self.wizbot.shutdown()


def main():
	# print(Comms.Call())
	app = deskapp.App(
		modules=[Chat],
		title="Chat Example",
		autostart=True,
		demo_mode=False,
		show_box=False,
		show_header=False,
		show_menu=False,
		show_messages=False,
	)


if __name__ == "__main__":
	main()
