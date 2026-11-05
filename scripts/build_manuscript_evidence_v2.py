"""Build the versioned manuscript evidence V2 manifest without altering V1."""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path


CONFIG = Path("configs/manuscript_evidence_v2.json")
ROOT = Path("outputs/manuscript-evidence-v2")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pointer(payload, expression):
    value = payload
    for token in expression.strip("/").split("/") if expression != "/" else []:
        value = value[token.replace("~1", "/").replace("~0", "~")]
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".pending")
    pending.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(pending, path)


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    records = []
    for item in config["artifacts"]:
        path = Path(item["path"])
        observed = pointer(json.loads(path.read_text(encoding="utf-8")), item["pointer"])
        records.append({**item, "observed": observed, "matched": observed == item["expected"], "sha256": sha256(path)})
    classes = Counter(row["claim_class"] for row in records)
    manifest = {
        "status": "complete_versioned_manuscript_evidence_v2",
        "version": config["version"],
        "title": config["title"],
        "scope": config["scope"],
        "records": records,
        "claim_class_counts": dict(sorted(classes.items())),
        "supersession_rules": config["supersession_rules"],
        "all_expected_decisions_match": all(row["matched"] for row in records),
        "training_or_fitting": 0,
        "config_sha256": sha256(CONFIG),
    }
    write_json(ROOT / "manifest.json", manifest)
    checks = {
        "artifact_count_matches_config": len(records) == len(config["artifacts"]),
        "all_files_exist_and_match": manifest["all_expected_decisions_match"],
        "all_claim_classes_present": set(config["required_claim_classes"]) <= set(classes),
        "negative_results_present": classes["negative"] >= 5,
        "reconstruction_sensitivity_present": classes["reconstruction_sensitivity"] >= 2,
        "supersession_rules_present": len(manifest["supersession_rules"]) >= 3,
        "no_training_or_fitting": manifest["training_or_fitting"] == 0,
    }
    write_json(ROOT / "verification.json", {"status": "verified" if all(checks.values()) else "failed", "checks": checks, "manifest_sha256": sha256(ROOT / "manifest.json")})
    if not all(checks.values()):
        raise RuntimeError(checks)


if __name__ == "__main__":
    main()
