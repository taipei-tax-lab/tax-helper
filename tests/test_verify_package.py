"""Release gates must reject valid-looking stale, extra and credential payloads."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import package_web
import verify_package


class PackageVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'hosting.zip'
        self.build(self.archive)
        with zipfile.ZipFile(self.archive) as z:
            self.contents = {name: z.read(name) for name in z.namelist()}

    def build(self, output):
        with contextlib.redirect_stdout(io.StringIO()):
            package_web.build(output, None)

    def replace(self, contents):
        with zipfile.ZipFile(self.archive, 'w') as z:
            for name, data in contents.items():
                z.writestr(name, data)

    def test_deterministic_package_and_fresh_extraction_only_fifteen_files(self):
        second = self.root / 'independent-path/hosting.zip'
        self.build(second)
        self.assertEqual(self.archive.read_bytes(), second.read_bytes())
        destination = self.root / 'pages'
        result = verify_package.verify(self.archive, destination)
        self.assertEqual(result['files'], 15)
        self.assertEqual(result['js_syntax_checks'], 10)
        actual = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
        self.assertEqual(actual, set(package_web.FILES) | {'MANIFEST.json'})
        for name in package_web.FILES:
            self.assertEqual((destination / name).read_bytes(), (package_web.ROOT / name).read_bytes())
        with self.assertRaisesRegex(ValueError, 'must be fresh'):
            verify_package.verify(self.archive, destination)

    def test_extra_traversal_and_duplicate_entries_cannot_be_published(self):
        for name in ['docs/PRIVATE.md', '../app.js', 'generated/faq.csv']:
            with self.subTest(entry=name):
                self.replace({**self.contents, name: b'excluded fixture'})
                with self.assertRaisesRegex(ValueError, 'entry set'):
                    verify_package.verify(self.archive, self.root / 'pages')
                self.assertFalse((self.root / 'pages').exists())
        self.replace(self.contents)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.archive, 'a') as z:
                z.writestr('app.js', self.contents['app.js'])
        with self.assertRaisesRegex(ValueError, 'entry set'):
            verify_package.verify(self.archive)

    def test_self_consistent_stale_release_still_fails_source_parity(self):
        changed = {**self.contents, 'app.js': self.contents['app.js'] + b'\n// stale release fixture'}
        manifest = json.loads(changed['MANIFEST.json'])
        manifest['files']['app.js'] = {'bytes': len(changed['app.js']),
                                     'sha256': hashlib.sha256(changed['app.js']).hexdigest()}
        changed['MANIFEST.json'] = json.dumps(manifest).encode()
        self.replace(changed)
        with self.assertRaisesRegex(ValueError, 'Stale source payload: app.js'):
            verify_package.verify(self.archive, self.root / 'pages')
        self.assertFalse((self.root / 'pages').exists())

    def test_incomplete_manifest_fails_before_extraction(self):
        changed = dict(self.contents)
        manifest = json.loads(changed['MANIFEST.json'])
        del manifest['files']['app.js']
        changed['MANIFEST.json'] = json.dumps(manifest).encode()
        self.replace(changed)
        with self.assertRaisesRegex(ValueError, 'Incomplete manifest'):
            verify_package.verify(self.archive, self.root / 'pages')
        self.assertFalse((self.root / 'pages').exists())

    def test_bad_crc_fails_before_extraction(self):
        with zipfile.ZipFile(self.archive) as z:
            entry = z.getinfo('app.js')
            offset = entry.header_offset + 30 + len(entry.filename.encode()) + len(entry.extra)
        corrupted = bytearray(self.archive.read_bytes())
        corrupted[offset] ^= 1
        self.archive.write_bytes(corrupted)
        with self.assertRaisesRegex((ValueError, zipfile.BadZipFile), 'CRC'):
            verify_package.verify(self.archive, self.root / 'pages')
        self.assertFalse((self.root / 'pages').exists())

    def test_credential_scan_covers_source_matching_mjs_without_printing_secret(self):
        fake_source = self.root / 'source'
        for name in package_web.FILES:
            target = fake_source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.contents[name])
        config = fake_source / 'assets/tax-ai/config.mjs'
        config.write_bytes(config.read_bytes() + b'\nconst client_secret = "test-secret-placeholder-only";\n')
        with patch.object(package_web, 'ROOT', fake_source), patch.object(verify_package, 'ROOT', fake_source):
            self.build(self.archive)
            with self.assertRaisesRegex(ValueError, '^Credential pattern: assets/tax-ai/config.mjs$'):
                verify_package.verify(self.archive, self.root / 'pages')
        self.assertFalse((self.root / 'pages').exists())


if __name__ == '__main__':
    unittest.main()
