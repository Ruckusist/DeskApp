import argparse
import os
import signal
import sys
import time
from deskapp.server import Server


def main(argv=None):
    parser = argparse.ArgumentParser(description='DeskApp Server')
    parser.add_argument('--host', default='localhost', help='Bind host (default: localhost)')
    parser.add_argument('--port', type=int, default=28080, help='Bind port (default: 28080)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--quiet', action='store_true', help='Reduce log noise')
    parser.add_argument('--pidfile', default=None, help='Write PID to this file')
    args = parser.parse_args(argv)

    srv = Server(SERVER_HOST=args.host, SERVER_PORT=args.port, VERBOSE=args.verbose and not args.quiet, SINK=None, QUIET=args.quiet)
    stop_flag = {'stop': False}

    def _signal_handler(signum, frame):
        stop_flag['stop'] = True
        try:
            srv.stop()
        except Exception:
            pass

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    # Write PID file if requested
    if args.pidfile:
        try:
            with open(args.pidfile, 'w') as f:
                f.write(str(os.getpid()))
        except Exception:
            pass

    srv.start()
    try:
        while not stop_flag['stop']:
            time.sleep(0.2)
    finally:
        try:
            srv.end_safely()
        finally:
            # Cleanup pidfile
            if args.pidfile:
                try:
                    if os.path.exists(args.pidfile):
                        os.remove(args.pidfile)
                except Exception:
                    pass


if __name__ == "__main__":
    sys.exit(main())
