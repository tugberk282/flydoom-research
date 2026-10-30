import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "manuscript-figures-v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_figure_manifest_and_source_hashes():
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "complete"
    assert len(manifest["generated_files"]) == 15
    for relative, expected in manifest["source_hashes"].items():
        assert digest(ROOT / relative) == expected


def test_all_formats_exist_and_are_nonempty():
    for index in range(1, 6):
        matches = list(OUT.glob(f"figure-{index}-*"))
        assert {path.suffix for path in matches} == {".png", ".svg", ".pdf"}
        assert all(path.stat().st_size > 1_000 for path in matches)


def test_pngs_are_publication_resolution():
    for path in OUT.glob("*.png"):
        with Image.open(path) as image:
            width, height = image.size
        assert width >= 1800
        assert height >= 750
