"""Use only a temporary fixture home; never reads real Codex task data."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from launch import ROOT, verified_server


class LauncherTests(unittest.TestCase):
    def test_rejects_nonlocal_state_without_network(self):
        home=Path('/example')
        for url in ('https://example.com', 'http://127.0.0.1:1234@evil.test', 'http://localhost:1234', 'http://127.0.0.1:1234?query=yes'):
            info=dict(root=str(ROOT),home=str(home),url=url,pid=99999,instance='test')
            with patch('urllib.request.build_opener') as opener:
                self.assertFalse(verified_server(info,home));opener.assert_not_called()

    def test_rejects_another_plugin_root(self):
        self.assertFalse(verified_server({'root':'/another/plugin'},Path('/example')))

    def test_stale_stop_does_not_send_signal(self):
        with tempfile.TemporaryDirectory(prefix='calendar stop ') as folder:
            command=[sys.executable,str(ROOT/'scripts/launch.py'),'--home',folder]
            result=subprocess.run(command+['--stop'],capture_output=True,text=True,check=True)
            self.assertFalse(json.loads(result.stdout)['stopped'])

    def test_start_reuse_status_and_stop_in_fixture_home(self):
        with tempfile.TemporaryDirectory(prefix='calendar fixture ') as folder:
            command=[sys.executable,str(ROOT/'scripts/launch.py'),'--home',folder]
            def call(*args):
                result=subprocess.run(command+list(args),capture_output=True,text=True,timeout=15,check=True)
                return json.loads(result.stdout)
            try:
                first=call();self.assertEqual(first['home'],str(Path(folder).resolve()))
                second=call();self.assertEqual(first['instance'],second['instance'])
                self.assertTrue(call('--status')['running'])
                self.assertTrue(call('--stop')['stopped'])
                self.assertFalse(call('--status')['running'])
            finally:
                call('--stop')


if __name__=='__main__':unittest.main()
