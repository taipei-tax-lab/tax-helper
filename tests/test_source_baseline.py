import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SourceBaselineTests(unittest.TestCase):
    def test_eight_original_files_match_approved_zip_bytes(self):
        manifest = json.loads((ROOT / "tests" / "source_baseline.json").read_text())
        self.assertEqual(len(manifest["file_sha256"]), 8)
        for name, expected in manifest["file_sha256"].items():
            with self.subTest(file=name):
                source = (ROOT / name).read_bytes()
                self.assertEqual(len(source), manifest["file_bytes"][name])
                self.assertEqual(hashlib.sha256(source).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
