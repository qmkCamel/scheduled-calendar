"""Check the distinct portal package contract and reviewer fixture safety."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_submission import build, ROOT
from reviewer_fixture import create


class SubmissionTests(unittest.TestCase):
    def test_reproducible_root_bundle_and_runtime(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            first = build(Path(temp) / 'one')
            second = build(Path(temp) / 'two')
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as z:
                self.assertIsNone(z.testzip())
                names = set(z.namelist())
                self.assertIn('skills/scheduled-calendar/SKILL.md', names)
                self.assertNotIn('.agents/plugins/marketplace.json', names)
                self.assertNotIn('assets/calendar-demo.png', names)
                manifest = json.loads(z.read('.codex-plugin/plugin.json'))
                self.assertNotIn('screenshots', manifest['interface'])
                for field in ('logo', 'composerIcon'):
                    self.assertIn(manifest['interface'][field][2:], names)
                for prefix in ('scripts/', 'web/', 'skills/'):
                    for name in names:
                        if name.startswith(prefix):
                            self.assertEqual(z.read(name), (ROOT / name).read_bytes())
                self.assertIn('TERMS.md', names)
                self.assertIn('SUPPORT.md', names)

    def test_unsafe_runtime_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'plugin'
            (root / '.codex-plugin').mkdir(parents=True)
            (root / '.codex-plugin/plugin.json').write_bytes((ROOT / '.codex-plugin/plugin.json').read_bytes())
            (root / 'scripts').mkdir()
            (root / 'scripts/server.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Runtime data'):
                build(Path(temp) / 'out', root)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'plugin'
            (root / '.codex-plugin').mkdir(parents=True)
            (root / '.codex-plugin/plugin.json').write_bytes((ROOT / '.codex-plugin/plugin.json').read_bytes())
            (root / 'scripts').symlink_to(ROOT / 'scripts', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                build(Path(temp) / 'out', root)

    def test_fixture_never_overwrites_existing_data(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            home = Path(temp) / 'reviewer'
            create(home)
            tasks = list(home.glob('automations/*/automation.toml'))
            self.assertEqual(len(tasks), 9)
            before = {p: p.read_bytes() for p in tasks}
            with self.assertRaisesRegex(ValueError, 'new or empty'):
                create(home)
            self.assertEqual(before, {p: p.read_bytes() for p in tasks})
            self.assertIn('REVIEWER_INJECTION_EXECUTED', (home / 'automations/demo-1/automation.toml').read_text())


if __name__ == '__main__':
    unittest.main()
