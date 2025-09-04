import threading
import socket
import time
from typing import Optional, Dict, Any

from deskapp.server import Server


class _ServerManager:
    def __init__(self):
        self._server: Optional[Server] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._last_error: Optional[str] = None
        self._host = 'localhost'
        self._port = 28080

    def _try_bind(self, host: str, port: int) -> Optional[str]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.close()
            return None
        except OSError as e:
            return str(e)

    def start(self, host: str = 'localhost', port: int = 28080, verbose: bool = True, sink=None, quiet: bool = True):
        with self._lock:
            if self.is_running():
                self._last_error = None
                return True, None
            bind_err = self._try_bind(host, port)
            if bind_err is not None:
                self._last_error = f"Port {port} unavailable on {host}: {bind_err}"
                return False, self._last_error

            self._host, self._port = host, port
            try:
                self._server = Server(SERVER_HOST=host, SERVER_PORT=port, VERBOSE=verbose, SINK=sink, QUIET=quiet)
                self._server.start()
                self._thread = self._server.thread
                self._last_error = None
                return True, None
            except Exception as e:
                self._server = None
                self._thread = None
                self._last_error = str(e)
                return False, self._last_error

    def stop(self):
        with self._lock:
            if not self._server:
                self._last_error = None
                return True, None
            try:
                self._server.stop()
                for _ in range(20):
                    if not self._thread or not self._thread.is_alive():
                        break
                    time.sleep(0.1)
                self._server.end_safely()
                self._last_error = None
            except Exception as e:
                self._last_error = str(e)
                self._server = None
                self._thread = None
                return False, self._last_error
            self._server = None
            self._thread = None
            return True, None

    def restart(self):
        host, port = self._host, self._port
        ok, err = self.stop()
        if not ok:
            return False, err
        time.sleep(0.2)
        return self.start(host=host, port=port)

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            info: Dict[str, Any] = {
                'running': self.is_running(),
                'host': self._host,
                'port': self._port,
                'error': self._last_error,
                'clients': 0,
            }
            if self._server:
                try:
                    info['clients'] = len(self._server.clients)
                except Exception:
                    pass
            return info


_manager = _ServerManager()


def start(host: str = 'localhost', port: int = 28080, verbose: bool = True, sink=None, quiet: bool = True):
    return _manager.start(host=host, port=port, verbose=verbose, sink=sink, quiet=quiet)

def stop():
    return _manager.stop()


def restart():
    return _manager.restart()


def is_running() -> bool:
    return _manager.is_running()


def get_status() -> Dict[str, Any]:
    return _manager.get_status()
