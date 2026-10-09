#!/usr/bin/env python3
"""Deterministic runtime ZIP; Actions uploads only its verified fresh extraction."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted([
    'index.html', 'app.js', 'style.css', 'questionBank.js', 'learningBank.js',
    'search.js', 'searchDictionary.js', 'logo.png.gif',
    *('assets/tax-ai/' + name for name in [
        'config.mjs', 'controller.mjs', 'messenger-transport.mjs',
        'mock-messenger.mjs', 'result-model.mjs', 'style.css']),
])


def build(output, manifest_path):
    contents = {name: (ROOT / name).read_bytes() for name in FILES}
    manifest = {
        'schema': 1, 'purpose': 'TAX AI B3 runtime byte parity; not the Pages Actions artifact',
        'files': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                  for name, data in contents.items()},
    }
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted({**contents, 'MANIFEST.json': encoded}.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 9, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(FILES) | {'MANIFEST.json'}
        assert archive.read('MANIFEST.json') == encoded
        assert all(archive.read(name) == data for name, data in contents.items())
    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(encoded)
    print(json.dumps({'files': len(FILES), 'bytes': output.stat().st_size,
                      'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='ZIP outside Git; never commit it')
    parser.add_argument('--manifest', type=Path, help='Optional durable runtime manifest')
    args = parser.parse_args()
    build(args.output, args.manifest)
