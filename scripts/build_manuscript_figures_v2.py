from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1793836800")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = [1, 3, 5]
METRICS = [("density_log2_ratio", "Density"), ("reciprocity_log2_ratio", "Reciprocity")]
COLORS = {"Buhmann": "#D55E00", "Princeton": "#0072B2"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "legend.fontsize": 8, "axes.spines.top": False,
        "axes.spines.right": False, "grid.color": "#D9D9D9", "grid.linewidth": 0.6,
        "svg.fonttype": "none", "svg.hashsalt": "flydoom-manuscript-figures-v2", "pdf.fonttype": 42,
    })


def panel_label(ax, label: str) -> None:
    ax.text(-0.14, 1.08, label, transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")


def save(fig, stem: Path, formats: list[str], dpi: int) -> list[str]:
    outputs = []
    for fmt in formats:
        path = stem.with_suffix(f".{fmt}")
        metadata = {"Creator": "FlyDoom manuscript figures V2"}
        if fmt == "svg":
            metadata["Date"] = None
        kwargs = {"bbox_inches": "tight", "facecolor": "white", "metadata": metadata}
        if fmt == "png":
            kwargs["dpi"] = dpi
        fig.savefig(path, **kwargs)
        outputs.append(path.relative_to(ROOT).as_posix())
    plt.close(fig)
    return outputs


def figure6(buhmann: dict, princeton: dict, out: Path, formats: list[str], dpi: int) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25), sharey=True)
    new_summaries = princeton["shared_sensory_residual"]["summaries"]
    for ax, (metric, title) in zip(axes, METRICS):
        old = [buhmann["summaries"][str(t)][metric]["robust_z"] for t in THRESHOLDS]
        new = [new_summaries[str(t)][metric]["robust_z"] for t in THRESHOLDS]
        ax.axhspan(-2, 2, color="#EEEEEE", zorder=0)
        ax.axhline(0, color="#777777", linewidth=0.8)
        ax.axhline(3, color="#A52A2A", linestyle="--", linewidth=1, label="Frozen strong criterion")
        ax.plot(THRESHOLDS, old, marker="o", linewidth=2, color=COLORS["Buhmann"], label="Buhmann")
        ax.plot(THRESHOLDS, new, marker="s", linewidth=2, color=COLORS["Princeton"], label="Princeton")
        ax.set_xticks(THRESHOLDS)
        ax.set_xlabel("Minimum synapse threshold")
        ax.set_title(title)
        ax.grid(axis="y")
    axes[0].set_ylabel("Robust z vs 52 shared sensory families")
    axes[0].set_ylim(-2.05, 3.25)
    axes[1].legend(frameon=False, loc="lower right")
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    fig.suptitle("The threshold-5 BM residual is reconstruction-product sensitive", y=1.03, fontweight="bold")
    fig.subplots_adjust(bottom=0.24, top=0.82, wspace=0.20)
    fig.text(0.5, 0.03, "Threshold-5 reciprocity changes from z=2.82 to z=-0.08; Princeton is a sensitivity product, not ground truth.", ha="center", fontsize=8, color="#555555")
    return save(fig, out / "figure-6-reconstruction-sensitive-residual", formats, dpi)


def old_real_and_primary(old: dict) -> tuple[float, float]:
    female = old["systems"]["female"]
    real = next(row["relative_retention"] for row in female["real_metrics"] if row["delay"] == 8)
    summary = female["families"]["within_type_block_directed_degree_rewire"]
    median = summary["median_delay8_retention"]
    return float(real), float(median)


def figure7(real_sensitivity: dict, new_null: dict, old_null: dict, out: Path, formats: list[str], dpi: int) -> list[str]:
    old_real, old_median = old_real_and_primary(old_null)
    new_real = float(new_null["princeton_real_delay8_retention"])
    new_median = float(new_null["family_summaries"]["within_type_block_directed_degree_rewire"]["median_delay8_retention"])
    princeton_metrics = real_sensitivity["conditions"]["princeton_no_threshold"]["real_metrics"]
    frozen_new_real = next(row["relative_retention"] for row in princeton_metrics if row["delay"] == 8)
    assert np.isclose(new_real, frozen_new_real)
    labels = ["Buhmann", "Princeton"]
    real = [old_real, new_real]
    null = [old_median, new_median]
    effects = np.asarray(real) - np.asarray(null)
    x = np.arange(2)
    width = 0.34
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25))
    axes[0].bar(x - width / 2, real, width, label="Real", color="#009E73")
    axes[0].bar(x + width / 2, null, width, label="Primary null median", color="#999999")
    axes[0].set_xticks(x, labels)
    axes[0].set_ylabel("Delay-8 relative retention")
    axes[0].set_ylim(0, 0.62)
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y")
    axes[1].bar(x, effects, width=0.56, color=[COLORS[label] for label in labels])
    axes[1].axhline(0.05, color="#A52A2A", linestyle="--", linewidth=1.4, label="Frozen effect floor")
    axes[1].set_xticks(x, labels)
    axes[1].set_ylabel("Real - primary-null median")
    axes[1].set_ylim(0, 0.058)
    axes[1].legend(frameon=False)
    axes[1].grid(axis="y")
    for index, value in enumerate(effects):
        axes[1].text(index, value + 0.002, f"{value:.3f}", ha="center", fontsize=8)
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    fig.suptitle("Higher absolute retention does not establish Real-wiring superiority", y=1.03, fontweight="bold")
    fig.subplots_adjust(bottom=0.24, top=0.82, wspace=0.30)
    fig.text(0.5, 0.03, "Both reconstruction-matched contrasts remain below the prospectively frozen 0.05 floor.", ha="center", fontsize=8, color="#555555")
    return save(fig, out / "figure-7-reconstruction-matched-temporal-null", formats, dpi)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/manuscript_figures_v2.json")
    args = parser.parse_args()
    config_path = ROOT / args.config
    config = load_json(config_path)
    sources = {name: ROOT / relative for name, relative in config["sources"].items()}
    out = ROOT / config["output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    style()
    generated = []
    generated += figure6(load_json(sources["buhmann_residual"]), load_json(sources["princeton_claim_impact"]), out, config["formats"], config["dpi"])
    generated += figure7(load_json(sources["princeton_temporal"]), load_json(sources["princeton_matched_null"]), load_json(sources["buhmann_matched_null"]), out, config["formats"], config["dpi"])
    manifest = {
        "status": "complete", "version": config["version"], "config": config_path.relative_to(ROOT).as_posix(),
        "config_sha256": sha256(config_path),
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in sources.values()},
        "generated_files": generated,
        "generated_hashes": {relative: sha256(ROOT / relative) for relative in generated},
        "guardrails": config["interpretation_guardrails"],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "figures": 2, "files": len(generated)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
