"""Client manager helpers.

Updated 2025-10-06 by GitHub Copilot to defer subscriptions until the
server confirms login so modules (for example Users) receive data.
"""

import threading
from typing import Any, Callable, Dict, Optional

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
        self._pending_subs = set()
        self._active_subs = set()

    def init_app(self, sink: Callable[[str], None], data: Dict[str, Any]):
        self._app_sink = sink
        self._app_data = data
        # Seed shared stores
        data.setdefault('chat_log', [])
        data.setdefault('chat_colors', {})
        data.setdefault('users', [])

    def _on_message(self, client: ClientSession, session, message):
        login_flag = message.get('login')
        if login_flag is not None:
            if login_flag:
                self._subscribe_pending()
            else:
                self._last_error = "Login failed"

        # Update users subscription if present
        if message.get('sub') == 'users':
            try:
                if self._app_data is not None:
                    self._app_data['users'] = list(message.get('data') or [])
            except Exception:
                pass

    def _subscribe_pending(self) -> None:
        if not self._client:
            return
        for sub in list(self._pending_subs):
            try:
                self._client.add_sub(sub)
                self._pending_subs.remove(sub)
                self._active_subs.add(sub)
            except Exception:
                break

    def login(self, host: str, port: int, username: str, password: str = 'password'):
        with self._lock:
            if self._client and self._client.logged_in:
                return True, None
            self._host, self._port = host, port
            self._username = username
            self._pending_subs = {"users"}
            self._active_subs.clear()
            try:
                self._client = ClientSession(
                    SERVER_HOST=host,
                    SERVER_PORT=port,
                    VERBOSE=False
                )
                if not self._client.connect():
                    self._last_error = f"Unable to connect to {host}:{port}"
                    self._client = None
                    return False, self._last_error
                # Register a callback for incoming messages from server
                self._client.register_callback(self._on_message)
                # Send login message
                self._client.login(username=username, password=password)
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
                self._pending_subs.clear()
                self._active_subs.clear()
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
        with self._lock:
            self._pending_subs.add(sub)
            if self._client and self._client.logged_in:
                self._subscribe_pending()

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
