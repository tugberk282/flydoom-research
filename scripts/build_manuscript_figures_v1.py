from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1793318400")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
COLORS = {"MaleCNS": "#0072B2", "FAFB": "#D55E00", "BANC": "#7B61A8"}
METRICS = {
    "nonself_directed_density": "Non-self directed density",
    "nonself_reciprocal_directed_fraction": "Reciprocal directed fraction",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "grid.color": "#D9D9D9",
            "grid.linewidth": 0.6,
            "svg.fonttype": "none",
            "svg.hashsalt": "flydoom-manuscript-figures-v1",
            "pdf.fonttype": 42,
        }
    )


def panel_label(ax, label: str) -> None:
    ax.text(-0.14, 1.08, label, transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")


def save_figure(fig, stem: Path, formats: list[str], dpi: int) -> list[str]:
    outputs = []
    for fmt in formats:
        path = stem.with_suffix(f".{fmt}")
        metadata = {"Creator": "FlyDoom manuscript figures V1"}
        if fmt == "svg":
            metadata["Date"] = None
        kwargs = {"bbox_inches": "tight", "facecolor": "white", "metadata": metadata}
        if fmt == "png":
            kwargs["dpi"] = dpi
        fig.savefig(path, **kwargs)
        outputs.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    plt.close(fig)
    return outputs


def figure1(data: dict, out: Path, formats: list[str], dpi: int) -> list[str]:
    df = pd.DataFrame(data["records"])
    df["system"] = df["system"].replace({"BANC_v888_paper_v2": "BANC"})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for ax, metric in zip(axes, METRICS):
        for system in ["MaleCNS", "FAFB", "BANC"]:
            group = df[df.system == system].sort_values("threshold")
            ax.plot(group.threshold, group[metric], marker="o", linewidth=2, color=COLORS[system], label=system)
        ax.set_xticks([1, 3, 5])
        ax.set_xlabel("Minimum synapse threshold")
        ax.set_ylabel(METRICS[metric])
        ax.grid(axis="y")
    axes[0].set_yscale("log")
    axes[0].legend(frameon=False)
    axes[1].set_ylim(-0.03, 0.83)
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    fig.suptitle("Descriptive BM structural comparison across datasets", y=1.03, fontweight="bold")
    fig.subplots_adjust(bottom=0.22, top=0.84, wspace=0.32)
    fig.text(0.5, 0.035, "Dataset effects are not interpretable as biological sex effects.", ha="center", fontsize=8, color="#555555")
    return save_figure(fig, out / "figure-1-cross-dataset-structure", formats, dpi)


def figure2(draws: pd.DataFrame, analysis: dict, out: Path, formats: list[str], dpi: int) -> list[str]:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2))
    thresholds = [3, 5]
    metrics = list(METRICS)
    for row, threshold in enumerate(thresholds):
        subset = draws[draws.threshold == threshold]
        for col, metric in enumerate(metrics):
            ax = axes[row, col]
            values = subset[metric].to_numpy()
            male = analysis["male_metrics"][str(threshold)][metric]
            ax.hist(values, bins=25, color="#B8B8B8", edgecolor="white", linewidth=0.4)
            ax.axvline(male, color=COLORS["MaleCNS"], linewidth=2.2, label="MaleCNS BM")
            ax.axvline(np.quantile(values, 0.99), color="#444444", linestyle="--", linewidth=1.2, label="Subset q99")
            ax.set_xlabel(METRICS[metric])
            ax.set_ylabel("Subset count")
            ax.set_title(f"Threshold ≥ {threshold}")
            ax.grid(axis="y")
            if row == 0 and col == 0:
                ax.legend(frameon=False)
            panel_label(ax, chr(ord("A") + row * 2 + col))
    fig.suptitle("MaleCNS BM excess persists in 1,000 side/count-matched FAFB subsets", y=1.01, fontweight="bold")
    fig.text(0.5, -0.01, "Sensitivity draws are correlated subsets, not independent biological replicates.", ha="center", fontsize=8, color="#555555")
    fig.tight_layout()
    return save_figure(fig, out / "figure-2-side-count-matched-sensitivity", formats, dpi)


def figure3(data: dict, out: Path, formats: list[str], dpi: int) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
    markers = {"nonself_directed_density": "o", "nonself_reciprocal_directed_fraction": "s"}
    for ax, system in zip(axes, ["MaleCNS", "FlyWire"]):
        for metric, label in METRICS.items():
            ys = [data["summaries"][system][str(t)][metric]["bm_percentile_midrank"] for t in [1, 3, 5]]
            ax.plot([1, 3, 5], ys, marker=markers[metric], linewidth=1.8, markersize=6, label=label)
        ax.axhline(0.95, color="#555555", linestyle="--", linewidth=1, label="Exploratory 0.95 guide")
        ax.set_title(f"{system}: BM vs sensory families")
        ax.set_xlabel("Minimum synapse threshold")
        ax.set_xticks([1, 3, 5])
        ax.set_ylim(0.30, 1.02)
        ax.grid(axis="y")
    axes[0].set_ylabel("BM midrank percentile")
    axes[0].legend(frameon=False, loc="lower right")
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    fig.suptitle("Within-dataset sensory-family enrichment is mixed", y=1.03, fontweight="bold")
    fig.subplots_adjust(bottom=0.23, top=0.82, wspace=0.20)
    fig.text(0.5, 0.035, "MaleCNS threshold-5 reciprocity is high; the overall pattern does not isolate a BM-specific effect.", ha="center", fontsize=8, color="#555555")
    return save_figure(fig, out / "figure-3-within-dataset-enrichment", formats, dpi)


def figure4(data: dict, out: Path, formats: list[str], dpi: int) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
    for ax, metric in zip(axes, ["density_log2_ratio", "reciprocity_log2_ratio"]):
        zs = [data["summaries"][str(t)][metric]["robust_z"] for t in [1, 3, 5]]
        ax.axhspan(-2, 2, color="#ECECEC", zorder=0)
        ax.axhline(0, color="#777777", linewidth=0.8)
        ax.axhline(3, color="#B22222", linestyle="--", linewidth=1, label="Frozen criterion: z ≥ 3")
        ax.plot([1, 3, 5], zs, color="#333333", marker="o", linewidth=1.8)
        if metric == "reciprocity_log2_ratio":
            ax.scatter([5], [zs[-1]], s=75, facecolor="#E69F00", edgecolor="black", zorder=3, label="Candidate residual")
        ax.set_xticks([1, 3, 5])
        ax.set_xlabel("Minimum synapse threshold")
        ax.set_title("Density" if metric.startswith("density") else "Reciprocity")
        ax.grid(axis="y")
    axes[0].set_ylabel("Robust z vs 52 shared sensory families")
    axes[1].legend(frameon=False, loc="lower right")
    axes[0].set_ylim(-1.1, 3.25)
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    fig.suptitle("Shared-family scaling explains most BM contrast", y=1.03, fontweight="bold")
    fig.subplots_adjust(bottom=0.23, top=0.82, wspace=0.20)
    fig.text(0.5, 0.035, "Threshold-5 reciprocity (z = 2.82) is a candidate below the frozen z ≥ 3 criterion.", ha="center", fontsize=8, color="#555555")
    return save_figure(fig, out / "figure-4-shared-family-residual", formats, dpi)


def figure5(out: Path, formats: list[str], dpi: int) -> list[str]:
    fig, ax = plt.subplots(figsize=(7.2, 4.1))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    boxes = [
        (0.2, 4.8, 2.8, 1.3, "Development finding", "MaleCNS BM has dense, reciprocal\npartner topology", "#DCEEF8"),
        (3.6, 4.8, 2.8, 1.3, "Mechanistic model", "Partner topology → class allocation\n→ dominant sensory-axis gain", "#EEE5F6"),
        (7.0, 4.8, 2.8, 1.3, "External tests", "FAFB controls + BANC local\nmechanism audit", "#FCE8D5"),
        (1.4, 1.4, 3.0, 1.4, "Supported", "Structural excess survives\nside/count matching", "#E2F0E7"),
        (5.6, 1.4, 3.0, 1.4, "Not established", "BM specificity and local mechanism\ndo not replicate decisively", "#F4DFDF"),
    ]
    for x, y, w, h, title, body, color in boxes:
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=color, edgecolor="#333333", linewidth=1)
        ax.add_patch(patch)
        ax.text(x + 0.18, y + h - 0.30, title, fontweight="bold", va="top", fontsize=9)
        ax.text(x + 0.18, y + h - 0.67, body, va="top", fontsize=7.7, linespacing=1.3)
    arrows = [((8.4, 4.8), (7.2, 2.8)), ((1.6, 4.8), (2.9, 2.8))]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, linewidth=1.2, color="#444444"))
    ax.text(5, 6.65, "Evidence map: from development result to bounded conclusion", ha="center", fontweight="bold", fontsize=11)
    ax.text(5, 0.45, "Current conclusion: a reproducible structural contrast and a constrained mechanistic hypothesis—not a confirmed sex-specific discovery.", ha="center", fontsize=8.5)
    return save_figure(fig, out / "figure-5-evidence-map", formats, dpi)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/manuscript_figures_v1.json")
    args = parser.parse_args()
    config_path = ROOT / args.config
    config = load_json(config_path)
    out = ROOT / config["output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    style()
    sources = {name: ROOT / rel for name, rel in config["sources"].items()}
    generated = []
    generated += figure1(load_json(sources["cross_dataset"]), out, config["formats"], config["dpi"])
    generated += figure2(pd.read_csv(sources["matched_draws"]), load_json(sources["matched_analysis"]), out, config["formats"], config["dpi"])
    generated += figure3(load_json(sources["within_dataset"]), out, config["formats"], config["dpi"])
    generated += figure4(load_json(sources["scale_residual"]), out, config["formats"], config["dpi"])
    generated += figure5(out, config["formats"], config["dpi"])
    manifest = {
        "status": "complete",
        "version": config["version"],
        "config": str(config_path.relative_to(ROOT)).replace("\\", "/"),
        "config_sha256": sha256(config_path),
        "source_hashes": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in sources.values()},
        "generated_files": generated,
        "generated_hashes": {rel: sha256(ROOT / rel) for rel in generated},
        "guardrails": config["interpretation_guardrails"],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "figures": len(config["figures"]), "files": len(generated)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
