# Frozen external-validation protocol

This protocol becomes active only when a genuinely independent adult CNS specimen with a sufficiently comparable reconstruction pipeline becomes available.

## Eligibility gates

1. New biological specimen, not a new snapshot of an existing segmentation.
2. Adult CNS or brain coverage containing the BM sensory family.
3. Exact BM-family membership with body/root IDs.
4. Side coverage at least95%.
5. Explicit proofreading/reconstruction status and source version.
6. Edge counts sufficient to compute non-self thresholds3 and5.
7. Source and preprocessing hashes locked before primary metrics are viewed.

Failure of any gate yields `external_replication_ineligible`; no replacement endpoint is selected.

## Primary endpoint

Threshold5 non-self reciprocal-directed fraction for BM, normalized against exact shared sensory families using the frozen Jeffreys-smoothed log2-ratio and median/1.4826-MAD residual procedure.

Primary support requires:

- Positive residual robust z greater than3;
- Midrank percentile at least.95;
- Direction consistent with the frozen Male candidate;
- No integrity or metadata gate failure.

## Required controls

- Threshold3 BM density and reciprocity paired-scale residuals;
- Threshold5 density residual;
- Common autapse policy or explicit non-self exclusion;
- Node-count and side summary;
- Shared-family count at least30;
- Version/snapshot analysis proving biological independence.

## Outcomes

- `external_candidate_supported`: all primary requirements pass.
- `external_candidate_not_supported`: eligible specimen,primary gate fails.
- `external_replication_ineligible`: metadata,coverage or independence gate fails.

No secondary endpoint rescues a failed primary result. Mechanism-chain replication would require a separate prospective partner-topology/class-allocation contract after structural eligibility; it is not automatically inferred from reciprocity support.

