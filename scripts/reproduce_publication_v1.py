from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hash_map(mapping: dict[str, str]) -> list[str]:
    errors = []
    for relative, expected in mapping.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing: {relative}")
        elif sha256(path) != expected:
            errors.append(f"hash mismatch: {relative}")
    return errors


def verify_evidence() -> list[str]:
    manifest_path = ROOT / "outputs/manuscript-evidence-v1/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    for record in manifest["records"]:
        path = ROOT / record["path"]
        if not path.is_file():
            errors.append(f"missing evidence: {record['path']}")
        elif sha256(path) != record["sha256"]:
            errors.append(f"evidence hash mismatch: {record['path']}")
        if not record["matched"]:
            errors.append(f"frozen decision mismatch: {record['id']}")
    return errors


def verify_figures() -> list[str]:
    manifest = json.loads((ROOT / "outputs/manuscript-figures-v1/manifest.json").read_text(encoding="utf-8"))
    errors = verify_hash_map(manifest["source_hashes"])
    errors.extend(verify_hash_map(manifest["generated_hashes"]))
    return errors


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify or rebuild the frozen manuscript V1 package.")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild evidence and figures before verification.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip focused pytest checks.")
    args = parser.parse_args()
    if args.rebuild:
        run([sys.executable, "scripts/build_manuscript_evidence_v1.py"])
        run([sys.executable, "scripts/build_manuscript_figures_v1.py"])
    errors = verify_evidence() + verify_figures()
    if not args.skip_tests:
        run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_manuscript_evidence_v1.py",
                "tests/test_manuscript_figures_v1.py",
                "-q",
            ]
        )
    result = {
        "status": "passed" if not errors else "failed",
        "evidence_records": 10,
        "figures": 5,
        "errors": errors,
        "scope": "Artifact verification; raw third-party connectome reconstruction is not bundled.",
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
