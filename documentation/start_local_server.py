#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import signal
import http.server
import socketserver

os.chdir(os.path.join('..', 'docs'))
port = 8000

server = socketserver.ThreadingTCPServer(('', port), http.server.SimpleHTTPRequestHandler)
server.daemon_threads = True
server.allow_reuse_address = True


def signal_handler(signal, frame):
    print('Exiting')
    try:
        if server:
            server.server_close()

    finally:
        sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print('Starting local server...')
print('Open URL http://localhost:8000/')

try:
    while True:
        sys.stdout.flush()
        server.serve_forever()

except KeyboardInterrupt:
    pass

server.server_close()
