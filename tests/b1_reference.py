"""Keep B1 bytes pinned in Git while testing the explicitly authorized B2 integration."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
B1_COMMIT = "e01ef42e7e0caa05c96083c5709b0554127d8e5f"
AUTHORIZED_CHANGES = {"index.html", "app.js"}


def read_b1(name):
    return subprocess.check_output(["git", "show", f"{B1_COMMIT}:{name}"], cwd=ROOT)


def source_files(version="integration"):
    manifest_bytes = (ROOT / "tests" / "source_baseline.json").read_bytes()
    assert manifest_bytes == read_b1("tests/source_baseline.json"), "Immutable B1 manifest changed"
    manifest = json.loads(manifest_bytes)
    baseline = {name: read_b1(name) for name in manifest["file_sha256"]}
    for name, content in baseline.items():
        assert hashlib.sha256(content).hexdigest() == manifest["file_sha256"][name], name
    if version == "b1":
        return baseline
    assert version == "integration"
    current = {name: (ROOT / name).read_bytes() for name in baseline}
    changed = {name for name in baseline if current[name] != baseline[name]}
    assert changed == AUTHORIZED_CHANGES, f"Unexpected original source changes: {changed}"
    for path in (ROOT / "assets" / "tax-ai").iterdir():
        if path.suffix in {".mjs", ".css"}:
            current[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    return current
