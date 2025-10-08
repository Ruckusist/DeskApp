#!/usr/bin/env python3
"""
SideDesk Server Daemon
Runs the DeskApp server as a persistent background process
"""

import sys
import signal
import os
from deskapp.server import Server


def main():
    """Run the server daemon."""
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 28080

    # Create PID file
    pid_file = os.path.expanduser('~/.sidedesk_server.pid')
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

    # Setup signal handlers for clean shutdown
    def signal_handler(sig, frame):
        if server:
            server.end_safely()
        if os.path.exists(pid_file):
            os.remove(pid_file)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start server
    server = Server(
        ServerHost=host,
        ServerPort=port,
        Verbose=False,
        Sink=None,
        Quiet=True
    )
    server.Start()

    print(f"SideDesk server started on {host}:{port}")
    print(f"PID: {os.getpid()}")

    # Keep running
    try:
        server.Thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        server.end_safely()
        if os.path.exists(pid_file):
            os.remove(pid_file)


if __name__ == '__main__':
    main()
