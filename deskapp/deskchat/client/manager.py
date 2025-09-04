from typing import Optional, Dict, Any, Callable, List, Tuple

from deskapp.server import ClientSession


class _ClientManager:
    def __init__(self):
        self._client: Optional[ClientSession] = None
        self._app_sink: Optional[Callable[[str], None]] = None
        self._app_data: Optional[Dict[str, Any]] = None
        self._host = 'localhost'
        self._port = 28080
        self._username: Optional[str] = None

    def init_app(self, sink: Optional[Callable[[str], None]] = None, data: Optional[Dict[str, Any]] = None):
        self._app_sink = sink
        self._app_data = data if data is not None else {}
        # Seed shared stores used by mods
        self._app_data.setdefault('users', [])
        self._app_data.setdefault('chat_log', [])  # list[{'user': str, 'text': str}]

    def _on_message(self, client: ClientSession, session, message):
        try:
            sub = message.get('sub')
        except Exception:
            sub = None
        if sub == 'users':
            try:
                users = list(message.get('data') or [])
                if self._app_data is not None:
                    self._app_data['users'] = users
            except Exception:
                pass

    def login(self, host: str, port: int, username: str, password: str = 'password') -> tuple[bool, Optional[str]]:
        try:
            # Close any previous client
            if self._client:
                try:
                    self._client.end_safely()
                except Exception:
                    pass
                self._client = None

            self._host, self._port, self._username = host, port, username
            client = ClientSession(SERVER_HOST=host, SERVER_PORT=port, VERBOSE=False)
            if not client.connect():
                return False, f"Unable to connect to {host}:{port}"
            # Register callback and login
            try:
                client.register_callback(self._on_message)
            except Exception:
                pass
            client.login(username=username, password=password)
            # Subscribe to users list
            try:
                client.add_sub('users')
            except Exception:
                pass
            self._client = client
            return True, None
        except Exception as e:
            self._client = None
            return False, str(e)

    def logout(self):
        if not self._client:
            return True, None
        try:
            self._client.end_safely()
            self._client = None
            return True, None
        except Exception as e:
            self._client = None
            return False, str(e)

    def add_sub(self, topic: str):
        if not self._client:
            return False
        try:
            self._client.add_sub(topic)
            return True
        except Exception:
            return False

    # Status helpers used by UI
    def is_connected(self) -> bool:
        return bool(self._client and self._client.connected)

    def get_username(self) -> Optional[str]:
        return self._client.username if self._client else None

    def get_status(self) -> Dict[str, Any]:
        if not self._client:
            return {'connected': False, 'logged_in': False, 'username': None, 'host': self._host, 'port': self._port}
        return {
            'connected': bool(self._client.connected),
            'logged_in': bool(getattr(self._client, 'logged_in', False)),
            'username': self._client.username,
            'host': getattr(self._client, 'host', self._host),
            'port': getattr(self._client, 'port', self._port),
        }

    # Local echo chat used by Chat and Log panels
    def chat_local(self, user: str, text: str):
        if self._app_data is None:
            return
        log: List[Dict[str, str]] = self._app_data.setdefault('chat_log', [])
        log.append({'user': user, 'text': text})
        # Keep log bounded
        if len(log) > 5000:
            del log[:len(log) - 5000]


_manager = _ClientManager()


def init_app(sink: Optional[Callable[[str], None]] = None, data: Optional[Dict[str, Any]] = None):
    return _manager.init_app(sink=sink, data=data)


def login(host: str, port: int, username: str, password: str = 'password'):
    return _manager.login(host=host, port=port, username=username, password=password)


def logout():
    return _manager.logout()


def add_sub(topic: str):
    return _manager.add_sub(topic)


def is_connected() -> bool:
    return _manager.is_connected()


def get_username() -> Optional[str]:
    return _manager.get_username()


def get_status() -> Dict[str, Any]:
    return _manager.get_status()


def status() -> Dict[str, Any]:
    # Alias to match prior sidedesk API, includes 'logged_in'
    return _manager.get_status()


def chat_local(user: str, text: str):
    return _manager.chat_local(user, text)
