import json
from pathlib import Path


ROOT = Path("outputs/manuscript-evidence-v2")


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_v2_manifest_is_complete_and_verified():
    manifest = load("manifest.json")
    assert manifest["status"] == "complete_versioned_manuscript_evidence_v2"
    assert len(manifest["records"]) == 14
    assert manifest["all_expected_decisions_match"] is True
    assert load("verification.json")["status"] == "verified"


def test_v2_preserves_source_conditional_and_negative_claims():
    counts = load("manifest.json")["claim_class_counts"]
    assert counts["historical_source_conditional"] == 1
    assert counts["reconstruction_sensitivity"] == 2
    assert counts["negative"] >= 5


def test_v2_has_explicit_supersession_and_no_fit():
    manifest = load("manifest.json")
    assert len(manifest["supersession_rules"]) >= 3
    assert manifest["training_or_fitting"] == 0
