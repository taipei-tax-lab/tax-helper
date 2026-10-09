"""Fail closed on extra/stale files, credentials or invalid JS before Pages upload."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

from package_web import FILES, ROOT

# Reused from the accepted 1999 verify_hosting.py; includes TAX AI .mjs payloads.
PATTERNS = [
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    r'"type"\s*:\s*"service_account"', r'"private_key"\s*:',
    r'AIza[0-9A-Za-z_-]{30,}', r'(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}',
    r'ya29\.[A-Za-z0-9_-]{15,}',
    r'(?:access_token|refresh_token|client_secret|api_key)\s*[:=]\s*[\x22\x27][^\x22\x27]{8,}',
    r'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}',
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(archive, destination=None):
    expected = set(FILES) | {'MANIFEST.json'}
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        require(len(names) == len(expected) and set(names) == expected, 'Unexpected ZIP entry set')
        require(z.testzip() is None, 'ZIP CRC failure')
        require(all((x.external_attr >> 16) & 0o170000 in (0, 0o100000) for x in z.infolist()),
                'ZIP entries must be regular files')
        manifest = json.loads(z.read('MANIFEST.json'))
        require(manifest.get('schema') == 1 and set(manifest['files']) == set(FILES), 'Incomplete manifest')
        for name, item in manifest['files'].items():
            data = z.read(name)
            require(len(data) == item['bytes'], f'Byte count mismatch: {name}')
            require(hashlib.sha256(data).hexdigest() == item['sha256'], f'Hash mismatch: {name}')
            require(data == (ROOT / name).read_bytes(), f'Stale source payload: {name}')
        for name in names:
            if Path(name).suffix in {'.html', '.js', '.mjs', '.css', '.json'}:
                require(not any(re.search(pattern, z.read(name).decode('utf-8')) for pattern in PATTERNS),
                        f'Credential pattern: {name}')
        scripts = [name for name in FILES if Path(name).suffix in {'.js', '.mjs'}]
        for name in scripts:
            subprocess.run(['node', '--check', str(ROOT / name)], check=True, capture_output=True)
        if destination is not None:
            require(not destination.exists() and not destination.is_symlink(), 'Extraction destination must be fresh')
            z.extractall(destination)
            actual = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
            require(actual == expected, 'Extracted file set mismatch')
            require(all((destination / name).read_bytes() == z.read(name) for name in names), 'Extraction byte mismatch')
    return {'status': 'PASS', 'runtime_files': len(FILES), 'files': len(expected),
            'js_syntax_checks': len(scripts), 'credential_scan': 'PASS',
            'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--extract', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, args.extract)))
