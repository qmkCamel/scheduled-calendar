"""Build a portable local-marketplace ZIP using an explicit public-file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIRS = {'.codex-plugin', 'skills', 'scripts', 'web', 'vendor', 'assets', 'tests', 'distribution'}
PUBLIC_FILES = {'README.md', 'LICENSE', 'PRIVACY.md', 'THIRD_PARTY_NOTICES.md', 'CHANGELOG.md', 'VERIFICATION.md'}


def public_files(root):
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f'Release cannot include symlinks: {relative}')
        if not path.is_file() or '__pycache__' in relative.parts or path.suffix == '.pyc':
            continue
        if len(relative.parts) == 1:
            if relative.name not in PUBLIC_FILES:
                continue
        elif relative.parts[0] not in PUBLIC_DIRS:
            continue
        if path.suffix in {'.db', '.sqlite', '.log'} or path.name in {'auth.json', 'server.json', '.DS_Store'}:
            raise ValueError(f'Runtime data is not permitted: {relative}')
        yield path, relative.as_posix()


def build(output):
    version = json.loads((ROOT/'.codex-plugin/plugin.json').read_text())['version']
    output.mkdir(parents=True, exist_ok=True)
    prefix = f'scheduled-calendar-{version}'
    archive = output/f'{prefix}.zip'
    entries = [(f'{prefix}/plugins/scheduled-calendar/{rel}', p.read_bytes()) for p, rel in public_files(ROOT)]
    entries += [(f'{prefix}/.agents/plugins/marketplace.json', (ROOT/'distribution/marketplace.json').read_bytes()),
                (f'{prefix}/LICENSE', (ROOT/'LICENSE').read_bytes()),
                (f'{prefix}/README.md', b'# Scheduled Calendar\n\nRead plugins/scheduled-calendar/README.md before installing.\n\nFrom this directory:\n\n```sh\ncodex plugin marketplace add .\ncodex plugin add scheduled-calendar@scheduled-calendar-community\n```\n\nmacOS + Python 3.11+. Experimental, local-only, read-only calendar.\n')]
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026,9,8,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = output/'SHA256SUMS'
    checksum.write_text(f'{digest}  {archive.name}\n')
    print(json.dumps({'archive': str(archive.resolve()), 'sha256': digest, 'files': len(entries)}))
    return archive


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    build(parser.parse_args().output)
