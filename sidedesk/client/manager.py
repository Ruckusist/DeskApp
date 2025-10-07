import threading
import time

from deskapp.server import ClientSession


class _ClientManager:
    """Lightweight client manager for Sidedesk.

    Intent: keep code simple (no attr type annotations) because the runtime
    loader used by the TUI raises errors on annotated assignment lines.
    """

    def __init__(self):
        # Connection / identity
        self._client = None          # ClientSession or None
        self._host = 'localhost'
        self._port = 28080
        self._username = None

        # App integration
        self._app_sink = None        # callable(str) for logging to UI
        self._app_data = None        # shared dict for modules

        # State / errors
        self._last_error = None
        self._lock = threading.RLock()

        # Subscription deferral until login ack
        self._pending_subs = []
        self._subscribed = False

        # Monitor thread
        self._monitor_thread = None
        self._stop_monitor = threading.Event()

    # ---------------- App wiring ----------------
    def init_app(self, sink, data):
        self._app_sink = sink
        self._app_data = data
        data.setdefault('chat_log', [])
        data.setdefault('users', [])
        data.setdefault('bots', {})

    # ---------------- Internal callbacks ----------------
    def _on_message(self, client, session, message):
        # Login acknowledgement -> perform deferred subscriptions
        try:
            if getattr(message, 'login', False) and not self._subscribed:
                for sub in list(self._pending_subs):
                    try:
                        client.add_sub(sub)
                    except Exception:
                        pass
                self._pending_subs.clear()
                self._subscribed = True
        except Exception:
            pass

        # Subscription payload handling
        sub = getattr(message, 'sub', None)
        if sub is None and hasattr(message, 'get'):
            try:
                sub = message.get('sub')
            except Exception:
                sub = None
        if self._app_data is None or sub is None:
            return
        try:
            data = getattr(message, 'data', None)
            if data is None and hasattr(message, 'get'):
                data = message.get('data')
            if sub == 'users':
                self._app_data['users'] = list(data or [])
            elif sub == 'chat' and isinstance(data, list):
                self._app_data['chat_log'] = data
            elif sub == 'bots' and isinstance(data, dict):
                self._app_data['bots'] = data
        except Exception:
            pass

    # ---------------- Login / Logout ----------------
    def login(self, host, port, username, password='password'):
        with self._lock:
            if self._client and getattr(self._client, 'logged_in', False):
                return True, None
            self._host, self._port, self._username = host, port, username
            try:
                cli = ClientSession(SERVER_HOST=host, SERVER_PORT=port, VERBOSE=False)
                if not cli.connect():
                    self._last_error = f"Unable to connect to {host}:{port}"
                    return False, self._last_error
                self._client = cli
                cli.register_callback(self._on_message)
                cli.login(username=username, password=password)
                # Defer subs until login ack so server has username bound
                self._pending_subs = ['users', 'chat', 'bots']
                self._subscribed = False
                self._start_monitor()
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
                self._stop_monitor.set()
                self._client.end_safely()
            except Exception:
                pass
            self._client = None
            self._pending_subs.clear()
            self._subscribed = False
            return True, None

    # ---------------- Monitor ----------------
    def _start_monitor(self):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._stop_monitor.clear()

        def loop():
            while not self._stop_monitor.is_set():
                cli = self._client
                if not cli:
                    break
                if not getattr(cli, 'connected', False):
                    if getattr(cli, 'logged_in', False):
                        cli.logged_in = False
                        if self._app_sink:
                            try:
                                self._app_sink("Disconnected from server. Logged out.")
                            except Exception:
                                pass
                    break
                time.sleep(0.5)

        self._monitor_thread = threading.Thread(target=loop, daemon=True)
        self._monitor_thread.start()

    # ---------------- Status helpers ----------------
    def is_connected(self):
        return bool(self._client and getattr(self._client, 'connected', False))

    def is_logged_in(self):
        return bool(self._client and getattr(self._client, 'logged_in', False))

    def get_status(self):
        return dict(
            connected=self.is_connected(),
            logged_in=self.is_logged_in(),
            host=self._host,
            port=self._port,
            username=self._username,
            error=self._last_error,
        )

    # ---------------- Subscriptions ----------------
    def add_sub(self, sub):
        if self._client:
            try:
                self._client.add_sub(sub)
            except Exception:
                pass

    # ---------------- Actions ----------------
    def send_chat(self, username, text):
        if not text:
            return False
        if self._client and getattr(self._client, 'logged_in', False):
            try:
                self._client.send_message(chat_user=username, chat_text=text)
                return True
            except Exception:
                pass
        if self._app_data is not None:
            self._app_data.setdefault('chat_log', []).append({'user': username, 'text': text})
        return False

    def request_bot(self, provider, model=None):
        if self._client and getattr(self._client, 'logged_in', False):
            try:
                self._client.send_message(bot_add=True, provider=provider, model=model or '')
                return True
            except Exception as e:
                if self._app_sink:
                    self._app_sink(f"Bot request error: {e}")
                return False
        if self._app_sink:
            self._app_sink(f"(offline) queued bot: {provider}:{model or '*'} (no server)")
        if self._app_data is not None and model:
            bots = self._app_data.setdefault('bots', {})
            bots.setdefault(model, {'provider': provider, 'kind': 'standard'})
        return False

    # Transitional local bot helpers
    def add_bot(self, name, kind='standard', provider=None):
        if self._client and getattr(self._client, 'logged_in', False):
            try:
                self._client.send_message(bot_add=True, provider=provider or 'unknown', model=name, kind=kind)
                return
            except Exception:
                pass
        if not self._app_data:
            return
        bots = self._app_data.setdefault('bots', {})
        bots.setdefault(name, {'kind': kind, 'provider': provider or 'unknown'})
        users = self._app_data.setdefault('users', [])
        label = f"{name} : '{kind}'"
        if label not in users:
            users.append(label)

    def bot_say(self, name, text):
        if not self._app_data:
            return
        self._app_data.setdefault('chat_log', []).append({'user': name, 'text': text})


_manager = _ClientManager()


def init_app(sink, data):
    _manager.init_app(sink, data)


def login(host, port, username, password='password'):
    return _manager.login(host, port, username, password)


def logout():
    return _manager.logout()


def status():
    return _manager.get_status()


def add_sub(sub):
    return _manager.add_sub(sub)


def send_chat(username, text):
    return _manager.send_chat(username, text)


def request_bot(provider, model=None):
    return _manager.request_bot(provider, model)


def add_bot(name, kind='standard', provider=None):
    return _manager.add_bot(name, kind, provider)


def bot_say(name, text):
    return _manager.bot_say(name, text)
