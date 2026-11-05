# FlyDoom research artifact V2

[![Verify frozen research artifact](https://github.com/tugberk282/flydoom-research/actions/workflows/artifact-verification.yml/badge.svg)](https://github.com/tugberk282/flydoom-research/actions/workflows/artifact-verification.yml)

FlyDoom is an independent computational research project examining how Drosophila connectome structure changes finite-horizon sensory transfer and controller behaviour. This public artifact contains the software framework, a versioned frozen manuscript evidence package, five historical figures, and two reconstruction-sensitivity figures.

## Current scientific conclusion

The project found a descriptive MaleCNS BM structural contrast and a development-set mechanism involving partner topology and reciprocal/unidirectional weight allocation. However, the local mechanism did not replicate decisively in BANC. More importantly, the former threshold-5 reciprocity residual is reconstruction-product sensitive: it changes from `robust z = 2.82` with the historical Buhmann FlyWire product to `z = -0.08` with the Princeton product under the same frozen normalization.

Absolute female delay-8 retention also changes across products (`0.435` to `0.539`), but the reconstruction-matched Real-minus-primary-null contrasts remain below the prospectively frozen `0.05` effect floor (`0.0035` for Buhmann and `0.0298` for Princeton). The current evidence therefore does not support neuron-specific Real-wiring superiority in either product.

This release does **not** establish a biological sex difference, population-level generalization, consciousness, a whole-brain simulation, or superior behaviour caused by the real connectome.

## Release status

Version `v0.2.0` is the current public artifact. V1 remains preserved as the historical `v0.1.0` release. The V2 archive is deterministic; its SHA-256 is recorded in `RELEASE_MANIFEST.json`. Continuous integration reruns the versioned evidence and figure checks on Linux.

## Verify in one command

Python 3.12 is recommended. After installing the project dependencies:

```bash
python scripts/reproduce_publication_v2.py
```

To regenerate the evidence manifest and all PNG/SVG/PDF figures before verification:

```bash
python scripts/reproduce_publication_v2.py --rebuild
```

The command checks 14 frozen evidence records, source and artifact hashes, five historical V1 figures, two V2 reconstruction-sensitivity figures, and the focused test suite. It verifies the committed research artifact; it does not reconstruct third-party connectomes from raw data.

For a quick result review, start with `docs/manuscript_v1/ADDENDUM_2026-11-04.md`, then read `MANUSCRIPT_DRAFT.md`, `CLAIMS_AND_EVIDENCE.md`, and the figure legends. The addendum supersedes source-dependent V1 wording. For provenance auditing, start with `outputs/manuscript-evidence-v2/manifest.json`.

## Package map

- `docs/manuscript_v1/`: manuscript draft, claim/evidence matrix, chronology, external-validation protocol and figure legends.
- `outputs/manuscript-evidence-v2/`: authoritative versioned decision and hash manifest.
- `outputs/manuscript-figures-v1/`: five preserved historical figures in PNG, SVG and PDF.
- `outputs/manuscript-figures-v2/`: two reconstruction-sensitivity figures in PNG, SVG and PDF.
- `src/flydoom/`: reusable controller and data interfaces.
- `scripts/reproduce_publication_v2.py`: single-command verification entry point.
- `RELEASE_MANIFEST.json`: hashes for every file in this export.

## Data and provenance

Raw MaleCNS, FlyWire and BANC data are not redistributed. Their source licenses and citations remain authoritative. Small derived analysis tables and JSON summaries are included only where needed to audit the reported figures and frozen decisions. See `docs/manuscript_v1/REFERENCES.md` and `REFERENCES.bib`.

## License and citation

The project source code is released under the MIT License; see `LICENSE`. Third-party connectome datasets retain their own licenses and attribution requirements. Cite this software with `CITATION.cff` and cite each external dataset used by an analysis. The canonical repository is <https://github.com/tugberk282/flydoom-research>.

## Author

Tuğberk Öztürkcan — undergraduate student at Istanbul Beykent University and AI/software developer.
