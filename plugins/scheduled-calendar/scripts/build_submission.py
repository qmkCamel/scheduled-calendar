"""Build a skills-only portal ZIP, not a local-marketplace installation ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from build_release import ROOT, public_files


def build(output, root=ROOT):
    manifest = json.loads((root / '.codex-plugin/plugin.json').read_text())
    if 'mcpServers' in manifest or 'apps' in manifest:
        raise ValueError('Skills-only submission cannot include MCP or app references')
    for name in ('.mcp.json', '.app.json'):
        if (root / name).exists():
            raise ValueError(f'Skills-only submission cannot include {name}')
    # Directory screenshots are not supported by the Skills-only upload route.
    manifest['interface'].pop('screenshots', None)
    entries = {}
    for path, relative in public_files(root):
        if relative.startswith('distribution/') or relative == 'assets/calendar-demo.png':
            continue
        entries[relative] = path.read_bytes()
    entries['.codex-plugin/plugin.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    if not any(p.startswith('skills/') and p.count('/') == 2 and p.endswith('/SKILL.md') for p in entries):
        raise ValueError('At least one skills/<name>/SKILL.md is required')
    for field in ('logo', 'composerIcon'):
        asset = manifest['interface'].get(field, '')
        if not asset.startswith('./') or '..' in Path(asset).parts or asset[2:] not in entries:
            raise ValueError(f'Missing or unsafe branding asset: {field}')
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"scheduled-calendar-{manifest['version']}-skills-only.zip"
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
    print(json.dumps({'archive': str(archive.resolve()), 'sha256': digest, 'files': len(entries)}))
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    build(parser.parse_args().output)
