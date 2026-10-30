# FlyDoom research artifact V1

[![Verify frozen research artifact](https://github.com/tugberk282/flydoom-research/actions/workflows/artifact-verification.yml/badge.svg)](https://github.com/tugberk282/flydoom-research/actions/workflows/artifact-verification.yml)

FlyDoom is an independent computational research project examining how Drosophila connectome structure changes finite-horizon sensory transfer and controller behaviour. This public artifact contains the software framework, the frozen manuscript evidence package, and five publication figures.

## Current scientific conclusion

The project found a reproducible structural contrast in the MaleCNS BM subgraph and a development-set mechanism involving partner topology and reciprocal/unidirectional weight allocation. However, the local mechanism did not replicate decisively in BANC, and paired cross-dataset controls explain most of the contrast as dataset-scale variation. The remaining threshold-5 reciprocity residual is a candidate (`robust z = 2.82`) below the frozen `z >= 3` criterion.

This release does **not** establish a biological sex difference, population-level generalization, consciousness, a whole-brain simulation, or superior behaviour caused by the real connectome.

## Verify in one command

Python 3.12 is recommended. After installing the project dependencies:

```bash
python scripts/reproduce_publication_v1.py
```

To regenerate the evidence manifest and all PNG/SVG/PDF figures before verification:

```bash
python scripts/reproduce_publication_v1.py --rebuild
```

The command checks ten frozen evidence records, source and artifact hashes, five figures, and the focused test suite. It verifies the committed research artifact; it does not reconstruct third-party connectomes from raw data.

## Package map

- `docs/manuscript_v1/`: manuscript draft, claim/evidence matrix, chronology, external-validation protocol and figure legends.
- `outputs/manuscript-evidence-v1/`: frozen decision and hash manifest.
- `outputs/manuscript-figures-v1/`: five figures in PNG, SVG and PDF.
- `src/flydoom/`: reusable controller and data interfaces.
- `scripts/reproduce_publication_v1.py`: single-command verification entry point.
- `RELEASE_MANIFEST.json`: hashes for every file in this export.

## Data and provenance

Raw MaleCNS, FlyWire and BANC data are not redistributed. Their source licenses and citations remain authoritative. Small derived analysis tables and JSON summaries are included only where needed to audit the reported figures and frozen decisions. See `docs/manuscript_v1/REFERENCES.md` and `REFERENCES.bib`.

## License and citation

The project source code is released under the MIT License; see `LICENSE`. Third-party connectome datasets retain their own licenses and attribution requirements. Cite this software with `CITATION.cff` and cite each external dataset used by an analysis. The canonical repository is <https://github.com/tugberk282/flydoom-research>.

## Author

Tuğberk Öztürkcan — undergraduate student at Istanbul Beykent University and AI/software developer.
