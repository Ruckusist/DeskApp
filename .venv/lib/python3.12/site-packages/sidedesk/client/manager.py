import threading
from typing import Optional, Callable, Dict, Any

from deskapp.server import ClientSession


class _ClientManager:
    def __init__(self):
        self._client: Optional[ClientSession] = None
        self._lock = threading.RLock()
        self._last_error: Optional[str] = None
        self._host = 'localhost'
        self._port = 28080
        self._username: Optional[str] = None
        self._app_sink: Optional[Callable[[str], None]] = None
        self._app_data: Optional[Dict[str, Any]] = None

    def init_app(self, sink: Callable[[str], None], data: Dict[str, Any]):
        self._app_sink = sink
        self._app_data = data
        # Seed shared stores
        data.setdefault('chat_log', [])
        data.setdefault('chat_colors', {})
        data.setdefault('users', [])

    def _on_message(self, client: ClientSession, session, message):
        # Update users subscription if present
        if message.get('sub') == 'users':
            try:
                if self._app_data is not None:
                    self._app_data['users'] = list(message.get('data') or [])
            except Exception:
                pass

    def login(self, host: str, port: int, username: str, password: str = 'password'):
        with self._lock:
            if self._client and self._client.logged_in:
                return True, None
            self._host, self._port = host, port
            self._username = username
            try:
                self._client = ClientSession(SERVER_HOST=host, SERVER_PORT=port, VERBOSE=False)
                if not self._client.connect():
                    self._last_error = f"Unable to connect to {host}:{port}"
                    self._client = None
                    return False, self._last_error
                # Register a callback for incoming messages from server
                self._client.register_callback(self._on_message)
                # Send login message
                self._client.login(username=username, password=password)
                # Subscribe to users list to drive Users module
                self._client.add_sub('users')
                return True, None
            except Exception as e:
                self._last_error = str(e)
                self._client = None
                return False, self._last_error

    def logout(self):
        with self._lock:
            if not self._client:
                return True, None
            try:
                self._client.end_safely()
                self._client = None
                return True, None
            except Exception as e:
                self._last_error = str(e)
                self._client = None
                return False, self._last_error

    def is_connected(self) -> bool:
        return bool(self._client and self._client.connected)

    def is_logged_in(self) -> bool:
        return bool(self._client and self._client.logged_in)

    def get_status(self) -> Dict[str, Any]:
        return {
            'connected': self.is_connected(),
            'logged_in': self.is_logged_in(),
            'host': self._host,
            'port': self._port,
            'username': self._username,
            'error': self._last_error,
        }

    def add_sub(self, sub: str):
        if self._client:
            try:
                self._client.add_sub(sub)
            except Exception:
                pass

    def send_chat_local(self, username: str, text: str):
        # Local-only chat log entry
        if self._app_data is None:
            return
        self._app_data.setdefault('chat_log', []).append({'user': username, 'text': text})


_manager = _ClientManager()


def init_app(sink: Callable[[str], None], data: Dict[str, Any]):
    _manager.init_app(sink, data)


def login(host: str, port: int, username: str, password: str = 'password'):
    return _manager.login(host, port, username, password)


def logout():
    return _manager.logout()


def status() -> Dict[str, Any]:
    return _manager.get_status()


def add_sub(sub: str):
    return _manager.add_sub(sub)


def chat_local(username: str, text: str):
    return _manager.send_chat_local(username, text)
