# Manuscript figure plan V1

This plan freezes the first publication-quality figure package without changing the underlying analyses.

1. **Cross-dataset structure:** descriptive density and reciprocity at harmonized thresholds.
2. **Side/count sensitivity:** 1,000 correlated FAFB subsets with the MaleCNS reference and subset q99.
3. **Within-dataset enrichment:** BM midrank percentiles among sensory families in MaleCNS and FlyWire.
4. **Shared-family residual:** robust z scores after paired sensory-family scaling.
5. **Evidence map:** a visual separation of supported findings, mechanistic model, external tests and unresolved claims.

Every data figure is generated directly from frozen JSON/CSV outputs listed in `configs/manuscript_figures_v1.json`. PNG is for preview, SVG for editing, and PDF for manuscript assembly. Cross-dataset panels must never be described as isolating a biological sex effect. Matched subsets and shared families must not be presented as independent biological replicates.

## V2 reconstruction-sensitivity extension — 5 November 2026

V1 remains frozen. V2 adds two panels generated directly from the versioned sensitivity outputs:

6. **Reconstruction-sensitive residual:** Buhmann and Princeton robust-z trajectories under the same 52-family normalization.
7. **Reconstruction-matched temporal null:** Real retention, primary within-type-block null medians and the frozen 0.05 effect floor for each reconstruction product.

These panels treat neither product as ground truth and do not treat the two products as biological replicates. Diagnostic global rewiring is excluded from the primary contrast.
