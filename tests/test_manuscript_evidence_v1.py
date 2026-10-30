import json
from pathlib import Path


ROOT = Path("outputs/manuscript-evidence-v1")


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_evidence_manifest_is_complete_and_verified():
    manifest = load("manifest.json")
    assert manifest["status"] == "complete_frozen_manuscript_evidence"
    assert len(manifest["records"]) == 10
    assert manifest["all_expected_decisions_match"] is True
    assert load("verification.json")["status"] == "verified"


def test_negative_and_mixed_results_are_preserved():
    counts = load("manifest.json")["claim_class_counts"]
    assert counts["negative"] >= 4
    assert counts["mixed_finding"] == 1
    assert counts["development_finding"] == 2


def test_manuscript_build_does_not_train_or_fit():
    assert load("manifest.json")["training_or_fitting"] == 0
