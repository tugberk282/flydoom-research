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


def verify_evidence() -> tuple[list[str], int]:
    manifest = json.loads((ROOT / "outputs/manuscript-evidence-v2/manifest.json").read_text(encoding="utf-8"))
    errors = []
    for record in manifest["records"]:
        path = ROOT / record["path"]
        if not path.is_file():
            errors.append(f"missing evidence: {record['path']}")
        elif sha256(path) != record["sha256"]:
            errors.append(f"evidence hash mismatch: {record['path']}")
        if not record["matched"]:
            errors.append(f"frozen decision mismatch: {record['id']}")
    if not manifest["all_expected_decisions_match"]:
        errors.append("V2 expected-decision verification failed")
    return errors, len(manifest["records"])


def verify_figure_manifest(relative: str) -> tuple[list[str], int]:
    manifest = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    errors = verify_hash_map(manifest["source_hashes"])
    errors.extend(verify_hash_map(manifest["generated_hashes"]))
    return errors, len(manifest["generated_files"]) // 3


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify or rebuild the versioned manuscript V2 package.")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    if args.rebuild:
        run([sys.executable, "scripts/build_manuscript_evidence_v2.py"])
        run([sys.executable, "scripts/build_manuscript_figures_v1.py"])
        run([sys.executable, "scripts/build_manuscript_figures_v2.py"])
    errors, evidence_count = verify_evidence()
    v1_errors, v1_figures = verify_figure_manifest("outputs/manuscript-figures-v1/manifest.json")
    v2_errors, v2_figures = verify_figure_manifest("outputs/manuscript-figures-v2/manifest.json")
    errors.extend(v1_errors + v2_errors)
    if not args.skip_tests:
        run([sys.executable, "-m", "pytest", "tests/test_manuscript_evidence_v2.py", "tests/test_manuscript_figures_v1.py", "tests/test_manuscript_figures_v2.py", "-q"])
    result = {
        "status": "passed" if not errors else "failed",
        "evidence_records": evidence_count,
        "historical_v1_figures": v1_figures,
        "v2_extension_figures": v2_figures,
        "errors": errors,
        "scope": "Frozen artifact verification; raw third-party connectome reconstruction is not bundled.",
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
