"""Start, reuse, inspect, or stop this plugin's loopback server. Python 3.11+."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request
from urllib.parse import urlsplit

if sys.version_info < (3, 11):
    raise SystemExit('Scheduled Calendar requires Python 3.11 or newer.')
if sys.platform == 'win32':
    raise SystemExit('This preview supports macOS. Windows is not yet supported.')

import fcntl

ROOT = Path(__file__).resolve().parents[1]


def verified_server(info, home):
    """Never follow a URL from a stale or edited state file outside loopback."""
    if not isinstance(info, dict) or info.get('root') != str(ROOT) or info.get('home') != str(home):
        return False
    try:
        url = urlsplit(info['url'])
        if url.scheme != 'http' or url.hostname != '127.0.0.1' or not url.port:
            return False
        if url.username or url.password or url.path or url.query or url.fragment:
            return False
        if not isinstance(info.get('pid'), int) or info['pid'] <= 1 or not info.get('instance'):
            return False
        # A loopback health probe must not use environment-configured HTTP proxies.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(info['url'] + '/health', timeout=2) as response:
            health = json.load(response)
        return health.get('service') == 'scheduled-calendar' and all(
            health.get(key) == info[key] for key in ('root', 'home', 'pid', 'instance')
        )
    except (OSError, ValueError, KeyError, TypeError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, help='Explicit Codex data directory (for fixture testing)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--stop', action='store_true', help='Stop only the verified plugin service')
    group.add_argument('--status', action='store_true', help='Report service status without starting it')
    args = parser.parse_args()
    home = (args.home or Path(os.environ.get('CODEX_HOME', Path.home()/'.codex'))).expanduser().resolve()
    runtime = home/'cache'/'scheduled-calendar'
    runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
    state = runtime/'server.json'
    with (runtime/'launch.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            info = json.loads(state.read_text())
        except (OSError, ValueError):
            info = {}
        alive = verified_server(info, home)
        if args.status:
            print(json.dumps({'running': alive, **(info if alive else {})}))
            return
        if args.stop:
            if not alive:
                print(json.dumps({'stopped': False, 'reason': 'No matching live service'}))
                return
            try:
                os.kill(info['pid'], signal.SIGTERM)
            except ProcessLookupError:
                pass
            state.unlink(missing_ok=True)
            print(json.dumps({'stopped': True}))
            return
        if alive:
            print(json.dumps(info))
            return
        state.unlink(missing_ok=True)
        with (runtime/'server.log').open('a') as log:
            process = subprocess.Popen(
                [sys.executable, str(ROOT/'scripts/server.py'), '--state', str(state), '--home', str(home)],
                stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True,
            )
        for _ in range(60):
            if process.poll() is not None:
                raise RuntimeError(f'日历启动失败，请查看 {runtime / "server.log"}')
            try:
                info = json.loads(state.read_text())
                if verified_server(info, home):
                    print(json.dumps(info))
                    return
            except (OSError, ValueError):
                pass
            time.sleep(.1)
        process.terminate()
        raise RuntimeError('日历服务启动超时')


if __name__ == '__main__':
    main()
