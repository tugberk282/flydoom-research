import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "manuscript-figures-v2"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v2_figure_manifest_and_frozen_sources():
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "complete"
    assert manifest["version"] == "manuscript-figures-v2"
    assert len(manifest["generated_files"]) == 6
    for relative, expected in manifest["source_hashes"].items():
        assert digest(ROOT / relative) == expected


def test_v2_formats_and_resolution():
    for index in (6, 7):
        matches = list(OUT.glob(f"figure-{index}-*"))
        assert {path.suffix for path in matches} == {".png", ".svg", ".pdf"}
        assert all(path.stat().st_size > 1_000 for path in matches)
    for path in OUT.glob("*.png"):
        with Image.open(path) as image:
            assert image.width >= 1800
            assert image.height >= 750


def test_v2_guardrails_name_primary_null_and_ground_truth_limit():
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    joined = " ".join(manifest["guardrails"]).lower()
    assert "within-type-block" in joined
    assert "ground truth" in joined
    assert "0.05" in joined
