import threading
import socket
import time
import subprocess
import os
import sys
import signal
from typing import Optional, Dict, Any

from deskapp.server import Server


class _ServerManager:
    """Manager for persistent SideDesk server daemon process."""

    def __init__(self):
        self._lock = threading.RLock()
        self._last_error: Optional[str] = None
        self._host = 'localhost'
        self._port = 28080
        self._pid_file = os.path.expanduser('~/.sidedesk_server.pid')

    def _get_pid(self) -> Optional[int]:
        """Get PID from PID file if exists."""
        try:
            if os.path.exists(self._pid_file):
                with open(self._pid_file, 'r') as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return None

    def _is_process_running(self, pid: int) -> bool:
        """Check if process with given PID is running."""
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
            return True
        except (OSError, ProcessLookupError):
            return False

    def _try_bind(self, host: str, port: int) -> Optional[str]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.close()
            return None
        except OSError as e:
            return str(e)

    def start(self, host: str = 'localhost', port: int = 28080,
              verbose: bool = True, sink=None, quiet: bool = True):
        """
        Start server as background daemon process.
        Returns (ok: bool, error: str|None)
        """
        with self._lock:
            # Check if already running
            pid = self._get_pid()
            if pid and self._is_process_running(pid):
                self._last_error = None
                return True, None

            # Clean up stale PID file
            if os.path.exists(self._pid_file):
                os.remove(self._pid_file)

            # Check if port is available
            bind_err = self._try_bind(host, port)
            if bind_err is not None:
                self._last_error = (
                    f"Port {port} unavailable on {host}: {bind_err}"
                )
                return False, self._last_error

            self._host, self._port = host, port

            try:
                # Get path to daemon script
                import sidedesk.server
                server_dir = os.path.dirname(
                    sidedesk.server.__file__
                )
                daemon_script = os.path.join(server_dir, 'daemon.py')

                # Use current Python interpreter
                python_exe = sys.executable

                # Start daemon process
                process = subprocess.Popen(
                    [python_exe, daemon_script, host, str(port)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True  # Detach from parent
                )

                # Wait a bit for server to start
                time.sleep(0.5)

                # Verify it started
                pid = self._get_pid()
                if pid and self._is_process_running(pid):
                    self._last_error = None
                    return True, None
                else:
                    self._last_error = "Server failed to start"
                    return False, self._last_error

            except Exception as e:
                self._last_error = str(e)
                return False, self._last_error

    def stop(self):
        """
        Stop the server daemon.
        Returns (ok: bool, error: str|None)
        """
        with self._lock:
            pid = self._get_pid()
            if not pid or not self._is_process_running(pid):
                # Clean up PID file if it exists
                if os.path.exists(self._pid_file):
                    os.remove(self._pid_file)
                self._last_error = None
                return True, None

            try:
                # Send SIGTERM for graceful shutdown
                os.kill(pid, signal.SIGTERM)

                # Wait for process to die
                for _ in range(20):
                    if not self._is_process_running(pid):
                        break
                    time.sleep(0.1)

                # Force kill if still running
                if self._is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(0.1)

                # Clean up PID file
                if os.path.exists(self._pid_file):
                    os.remove(self._pid_file)

                self._last_error = None
                return True, None

            except Exception as e:
                self._last_error = str(e)
                return False, self._last_error

    def restart(self):
        """
        Restart the server.
        Returns (ok: bool, error: str|None)
        """
        host, port = self._host, self._port
        ok, err = self.stop()
        if not ok:
            return False, err
        # Small delay to ensure socket release
        time.sleep(0.2)
        ok, err = self.start(host=host, port=port)
        return ok, err

    def is_running(self) -> bool:
        """Check if server is running."""
        pid = self._get_pid()
        return bool(pid and self._is_process_running(pid))

    def get_status(self) -> Dict[str, Any]:
        """Get server status."""
        with self._lock:
            running = self.is_running()

            # Check if we have a connected client
            clients = 0
            try:
                from sidedesk.client.manager import status as client_status
                client_info = client_status()
                if client_info.get('connected') or client_info.get('logged_in'):
                    clients = 1  # At least us
            except Exception:
                pass

            info: Dict[str, Any] = {
                'running': running,
                'host': self._host,
                'port': self._port,
                'error': self._last_error,
                'clients': clients,
            }
            if running:
                pid = self._get_pid()
                if pid:
                    info['pid'] = pid
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
