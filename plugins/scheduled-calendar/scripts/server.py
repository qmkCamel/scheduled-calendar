"""Loopback-only, read-only calendar. Static files and task data; no mutation API."""
from __future__ import annotations

import argparse
import json
import os
import secrets
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from calendar_data import ROOT, calendar_payload, stamp

VERSION = json.loads((ROOT / '.codex-plugin' / 'plugin.json').read_text())['version']


class CalendarServer(ThreadingHTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send_data(self, code, data, content_type='application/json; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)

    def json(self, code, value):
        self.send_data(code, json.dumps(value, ensure_ascii=False).encode())

    def do_GET(self):
        port = self.server.server_port
        allowed = {f'127.0.0.1:{port}', f'localhost:{port}'}
        if self.headers.get('Host') not in allowed:
            return self.json(403, {'error': 'Invalid host'})
        origin = self.headers.get('Origin')
        if origin and origin not in {f'http://{host}' for host in allowed}:
            return self.json(403, {'error': 'Invalid origin'})
        url = urlsplit(self.path)
        if url.path == '/health':
            return self.json(200, {'service': 'scheduled-calendar', 'version': VERSION,
                                   'root': str(ROOT), 'home': str(self.server.home),
                                   'pid': os.getpid(), 'instance': self.server.instance})
        if url.path == '/api/calendar':
            if not secrets.compare_digest(self.headers.get('X-Calendar-Token', ''), self.server.token):
                return self.json(403, {'error': 'Missing calendar token'})
            try:
                params = parse_qs(url.query)
                payload = calendar_payload(self.server.home, stamp(params['start'][0]), stamp(params['end'][0]))
                payload['demo'] = self.server.demo
                return self.json(200, payload)
            except (KeyError, ValueError, TypeError) as exc:
                return self.json(400, {'error': str(exc)})
            except Exception:
                return self.json(500, {'error': '读取任务失败，请稍后刷新。'})
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/i18n.js': ('i18n.js', 'text/javascript; charset=utf-8'),
                 '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if url.path not in files:
            return self.json(404, {'error': 'Not found'})
        name, kind = files[url.path]
        data = (ROOT / 'web' / name).read_bytes()
        if name == 'index.html':
            data = data.replace(b'__CALENDAR_TOKEN__', self.server.token.encode())
        self.send_data(200, data, kind)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home()/'.codex')))
    parser.add_argument('--state', type=Path)
    parser.add_argument('--demo', action='store_true', help='Label synthetic fixture data clearly')
    args = parser.parse_args()
    server = CalendarServer(('127.0.0.1', args.port), Handler)
    server.home = args.home.expanduser().resolve()
    server.demo = args.demo
    server.token = secrets.token_urlsafe(32)
    server.instance = secrets.token_hex(16)
    info = {'url': f'http://127.0.0.1:{server.server_port}', 'pid': os.getpid(),
            'root': str(ROOT), 'home': str(server.home), 'instance': server.instance,
            'startedAt': datetime.now(timezone.utc).isoformat()}
    if args.state:
        temporary = args.state.with_suffix('.tmp')
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as handle:
            json.dump(info, handle)
        temporary.replace(args.state)
    print(json.dumps(info), flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
