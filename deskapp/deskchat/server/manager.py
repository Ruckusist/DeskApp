import os
import signal
import sys
import threading
import socket
import time
from typing import Optional, Dict, Any

try:
    import psutil  # type: ignore
except Exception:  # psutil optional at import; status will degrade gracefully
    psutil = None  # type: ignore

from deskapp.server import Server


class _ServerManager:
    def __init__(self):
        # Runtime objects
        self._server = None  # type: Optional[Server]
        self._thread = None  # type: Optional[threading.Thread]
        self._lock = threading.RLock()
        self._last_error = None  # type: Optional[str]
        # Bind info
        self._host = 'localhost'
        self._port = 28080
        # Detached process support
        self._pid = None  # type: Optional[int]
        self._pidfile = os.path.join(os.getcwd(), '.deskapp_server.pid')

    def _try_bind(self, host: str, port: int) -> Optional[str]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.close()
            return None
        except OSError as e:
            return str(e)

    def _read_pidfile(self) -> Optional[int]:
        try:
            if os.path.exists(self._pidfile):
                with open(self._pidfile, 'r') as f:
                    pid_str = f.read().strip()
                    if pid_str:
                        return int(pid_str)
        except Exception:
            return None
        return None

    def _write_pidfile(self, pid: int) -> None:
        try:
            with open(self._pidfile, 'w') as f:
                f.write(str(pid))
        except Exception:
            pass

    def _clear_pidfile(self) -> None:
        try:
            if os.path.exists(self._pidfile):
                os.remove(self._pidfile)
        except Exception:
            pass

    def start(self, host: str = 'localhost', port: int = 28080, verbose: bool = True, sink=None, quiet: bool = True, detach: bool = True):
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
                if detach:
                    # Spawn a detached child python process running the server __main__
                    # Use sys.executable to match current venv
                    import subprocess
                    python = sys.executable or 'python3'
                    # Write PID within manager; __main__ can also accept --pidfile but we manage one here
                    cmd = [python, '-m', 'deskapp.server', '--host', str(host), '--port', str(port), '--quiet']
                    # Start new session to detach from this controlling terminal
                    proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True,
                        close_fds=True,
                    )
                    self._pid = proc.pid
                    self._write_pidfile(self._pid)
                    self._server = None
                    self._thread = None
                    # Wait briefly for bind to succeed
                    start_deadline = time.time() + 2.5
                    ok = False
                    while time.time() < start_deadline:
                        err = self._try_bind(host, port)
                        if err is None:
                            # If bind still succeeds, server not yet listening; wait
                            time.sleep(0.1)
                        else:
                            # bind failed now -> likely because server bound it
                            ok = True
                            break
                    if not ok:
                        self._last_error = 'Server process did not bind the port in time.'
                        return False, self._last_error
                    self._last_error = None
                    return True, None
                else:
                    # In-process thread mode (legacy)
                    self._server = Server(SERVER_HOST=host, SERVER_PORT=port, VERBOSE=verbose, SINK=sink, QUIET=quiet)
                    self._server.start()
                    self._thread = self._server.thread
                    self._pid = os.getpid()
                    self._last_error = None
                    return True, None
            except Exception as e:
                self._server = None
                self._thread = None
                self._last_error = str(e)
                return False, self._last_error

    def stop(self):
        with self._lock:
            # Prefer PID-based termination if present
            pid = self._pid or self._read_pidfile()
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    # Wait briefly for it to die
                    deadline = time.time() + 3.0
                    while time.time() < deadline:
                        try:
                            os.kill(pid, 0)
                        except OSError:
                            break  # no such process
                        time.sleep(0.1)
                    self._last_error = None
                except Exception as e:
                    self._last_error = str(e)
                    return False, self._last_error
                finally:
                    self._clear_pidfile()
                    self._pid = None
                return True, None

            # Fallback to in-process thread shutdown
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
        # If we have a pid file, prefer checking the process
        pid = self._pid or self._read_pidfile()
        if pid:
            try:
                if psutil:
                    return psutil.pid_exists(pid)
                # Fallback: signal 0
                os.kill(pid, 0)
                return True
            except Exception:
                return False
        return bool(self._thread and self._thread.is_alive())

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            info: Dict[str, Any] = {
                'running': self.is_running(),
                'host': self._host,
                'port': self._port,
                'error': self._last_error,
                'clients': 0,
                'pid': None,
            }
            # Gather metrics for detached process if possible
            pid = self._pid or self._read_pidfile()
            if pid:
                info['pid'] = pid
                if psutil:
                    try:
                        p = psutil.Process(pid)
                        with p.oneshot():
                            cpu = p.cpu_percent(interval=0.0)
                            mem = p.memory_info().rss
                            create_time = p.create_time()
                        info['cpu_percent'] = cpu
                        info['rss_bytes'] = mem
                        info['uptime_sec'] = max(0.0, time.time() - create_time)
                    except Exception:
                        pass
            # In-thread server metrics
            if self._server:
                try:
                    info['clients'] = len(self._server.clients)
                except Exception:
                    pass
            # System-wide network IO (rx/tx) as a coarse proxy
            if psutil:
                try:
                    net = psutil.net_io_counters(pernic=False)
                    info['net_bytes_sent'] = getattr(net, 'bytes_sent', None)
                    info['net_bytes_recv'] = getattr(net, 'bytes_recv', None)
                except Exception:
                    pass
            return info


_manager = _ServerManager()


def start(host: str = 'localhost', port: int = 28080, verbose: bool = True, sink=None, quiet: bool = True, detach: bool = True):
    return _manager.start(host=host, port=port, verbose=verbose, sink=sink, quiet=quiet, detach=detach)

def stop():
    return _manager.stop()


def restart():
    return _manager.restart()


def is_running() -> bool:
    return _manager.is_running()


def get_status() -> Dict[str, Any]:
    return _manager.get_status()
