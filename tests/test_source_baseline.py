import hashlib
import json
from pathlib import Path
import unittest
from b1_reference import read_b1, source_files

ROOT = Path(__file__).resolve().parents[1]


class SourceBaselineTests(unittest.TestCase):
    def test_eight_original_files_match_approved_zip_bytes(self):
        self.assertEqual((ROOT / "tests" / "source_baseline.json").read_bytes(), read_b1("tests/source_baseline.json"))
        manifest = json.loads((ROOT / "tests" / "source_baseline.json").read_text())
        self.assertEqual(len(manifest["file_sha256"]), 8)
        for name, expected in manifest["file_sha256"].items():
            with self.subTest(file=name):
                source = read_b1(name)
                self.assertEqual(len(source), manifest["file_bytes"][name])
                self.assertEqual(hashlib.sha256(source).hexdigest(), expected)

    def test_integration_preserves_six_files_and_changes_only_authorized_originals(self):
        self.assertIn("assets/tax-ai/controller.mjs", source_files("integration"))


if __name__ == "__main__":
    unittest.main()
