# Connectome-derived finite-horizon sensory gain is dataset-specific after cross-connectome structural normalization

## Status

Internal manuscript V1, 30 October 2026. This draft reports completed analyses only. Figure production, full statistical methods formatting and journal-specific references remain separate later stages.

## Abstract

Large connectomes make it possible to use biological wiring as the recurrent substrate of computational models, but a structure–function association observed in one reconstructed animal may reflect specimen-specific wiring, annotation granularity or reconstruction pipeline rather than a general biological mechanism. We studied a finite-horizon sensory-retention phenotype in neuron-level adult *Drosophila* connectomes. In a MaleCNS development graph, matched-null and intervention analyses localized the effect to a body-mechanosensory (BM) recurrent block and supported a frozen mechanistic chain: partner topology, reciprocal-versus-unidirectional weight allocation, and gain along a dominant sensory axis. Class-allocation perturbations reproduced 84–98% of the full weight-shuffle effect across three operator metrics. However, the original common two-system development gate failed, fresh-cue generalization did not establish a common biological advantage, and an independent BANC BM-family assay did not reproduce the Male mechanism.

We therefore audited cross-dataset confounds before making a biological claim. Male BM density and reciprocity remained elevated after common synapse thresholds, autapse exclusion, exact side recovery and 1,000 side-and-count-matched FlyWire subsets. Nevertheless, within-dataset sensory-family normalization did not meet the preregistered BM-specific enrichment criterion. Across 52 exact shared sensory families, the Male-to-FlyWire BM density and reciprocity ratios at the three-synapse threshold lay at the centre of the control distribution (robust z = −0.034 and −0.048). At the five-synapse threshold, BM reciprocity was the largest observed residual (percentile 1.0) but did not cross the frozen robust-z criterion (z = 2.816; required >3). We conclude that the MaleCNS mechanism is a dataset-specific, pipeline-confounded development finding, with strong-edge BM reciprocity retained as a prespecified external-replication candidate. No public same-pipeline independent adult CNS specimen was available for confirmation.

## Introduction

Connectome-constrained models promise a direct bridge between anatomical wiring and computation. Their central inferential problem is that a connectome is usually reconstructed from one animal. Graph structure therefore varies jointly with biological specimen, sex, age, imaging, synapse prediction, proofreading, annotation and filtering. A successful model based on one graph does not by itself show that the biological topology caused the behaviour or that the result generalizes across animals.

The present project began with maze-navigation models but found that raw-camera navigation success was not sufficiently diagnostic of connectome contribution. The work therefore pivoted to controlled temporal cue assays and then to neuron-level graphs, matched structural nulls and fitting-free finite-horizon transfer operators. The main development signal appeared in the MaleCNS BM sensory block. Rather than optimizing the same endpoint until it succeeded, we froze the mechanism, preserved failed gates and attempted external validation using FlyWire and BANC resources.

The study asks three nested questions:

1. Can the MaleCNS finite-horizon signal be localized to a reproducible structural mechanism?
2. Does the mechanism transfer to an independent connectome specimen?
3. If raw cross-dataset structure differs, is the difference BM-specific or a general source-pipeline scale shift?

## Results

### 1. The original two-system matched-null gate failed

The neuron-level interface passed the small identifiability preflight, but the matched-null development criterion required a minimum effect in both biological systems. The Male Real-minus-null median was +0.12912 and rank 1/17, whereas the female value was +0.00349 and rank 8/17. The frozen decision was `development_gate_failed_stop_without_confirmation`; the planned 200-null confirmation and learned temporal assay were not opened.

This negative result is foundational: all later Male analyses are mechanism-development analyses, not confirmation of a common biological effect.

### 2. Male development analyses localized a frozen BM mechanism

Finite-horizon linear cue transfer exactly reproduced the nonlinear retention ordering across the development systems. Time-resolved block cuts localized most of the Male excess to recurrent `BM→BM` wiring rather than to a single descending outlet. Full sensory-space analysis showed that the BM intervention was strongly low-dimensional, although low dimensionality was also present in null systems.

Reciprocity-preserving nulls retained most of the Male Real-minus-null gain, showing that reciprocal-pair quantity and node reciprocal degree were insufficient explanations. Fixed-support source-local weight shuffles showed a mixed contribution from topology and weight-target alignment. A paired topology-by-weight factorial demonstrated that weight effects were strong on Real support and approximately absent on rewired support.

Finally, class-allocation perturbations preserved support, source weight pools, out-strength and within-class target rank while exchanging weight budget between reciprocal and unidirectional edge classes. They reproduced 84.0% of the normalized-trace full-shuffle effect, 98.3% of the Frobenius effect and 97.9% of the maximum-eigenvalue effect. The frozen development chain was therefore:

`BM partner topology → reciprocal/unidirectional class allocation → dominant sensory-axis gain`.

### 3. Prospective generalization and external replication did not confirm the chain

Thirty-two fresh cue directions did not pass the frozen generalization criteria. The BM block effect was positive for 22/32 cues with median excess loss +0.02271, below the required 24/32 and +0.05 gates. The top-five reciprocal-pair intervention was positive for 19/32 with median +0.00668, below 24/32 and +0.02.

For BANC, an outcome-blind evidence hierarchy resolved 427/437 frozen types. `LoVP108` lacked a validated homolog: the official NBLAST audit yielded no validated or rank-one match. Exact 437-type confirmation was therefore not opened.

A separately versioned exploratory BM-family assay used 63 resolved BANC BM nodes, 269 directed pairs and 300 nulls. Source-local weight placement was highly influential, but the Male partner-topology and class-allocation signature did not replicate. The frozen decision was `local_signature_not_replicated`.

### 4. Male BM structural excess survived simple harmonization

At common thresholds of at least three synapses, non-self directed density was 0.08483 in MaleCNS, 0.02022 in FlyWire and 0.00256 in BANC. Reciprocal-directed fractions were 0.68844, 0.30534 and 0.20000. At at least five synapses, densities were 0.05051, 0.00309 and 0.00051, and reciprocal fractions were 0.76793, 0 and 0.

BANC contained many autapses under its source policy, whereas the MaleCNS and FlyWire induced BM graphs contained none. Primary comparisons therefore excluded autapses. The Male structural excess remained, showing that a common threshold and autapse policy alone did not explain it.

### 5. Side and node count did not explain the excess

Official annotations recovered exact IDs and side for all 69 MaleCNS and 81 FlyWire BM-family nodes. MaleCNS contained 39 left and 30 right BM nodes; FlyWire contained 39 left and 42 right. Annotation resolution was not identical: MaleCNS used a coarse `BM` label, whereas FlyWire divided the family into six subtypes.

We generated 1,000 unique FlyWire subsets containing all 39 left and 30 sampled right nodes. At the three-synapse threshold, the 99th percentile subset density was 0.02408 and reciprocity was 0.34783, both below Male values 0.08483 and 0.68844. At five synapses, the 99th percentile density was 0.00384 and reciprocity was zero, compared with Male values 0.05051 and 0.76793. No subset reached the Male value. These correlated subsets are sensitivity draws, not independent biological replicates or inferential p-values.

### 6. BM was not uniquely enriched within the Male sensory graph

BM was compared with similarly sized non-BM sensory families within each graph. The prespecified primary score averaged density and reciprocity percentiles at thresholds three and five. Scores were 0.898 for MaleCNS and 0.737 for FlyWire. Because the frozen Male criterion was at least 0.95, the decision was `global_scale_or_inconclusive`.

Male BM reciprocity at the five-synapse threshold was top-ranked among 26 controls, but BM density was exceeded by several other Male sensory families. The BM-only enrichment claim was therefore not supported.

### 7. Shared-family normalization attributed most of the difference to dataset scale

Fifty-two non-BM sensory families with exact shared labels and at least 20 nodes in each graph formed a paired source-scale reference. At the three-synapse threshold, the BM Male-to-FlyWire density log2 ratio was 2.065 versus a control median 2.121 (robust z = −0.034; percentile 0.509). The reciprocity log2 ratio was 1.165 versus 1.221 (z = −0.048; percentile 0.509). Thus, the large raw BM difference at this threshold was typical of the broader MaleCNS-to-FlyWire sensory-family shift.

At five synapses, the BM density residual remained modest (z = 0.434; percentile 0.717). Reciprocity was the largest residual among the 52 controls (z = 2.816; percentile 1.0) but remained below the frozen z > 3 threshold. Zero of four primary cells met the combined strong-residual rule, yielding `mixed_residual`.

### 8. Public data do not permit same-pipeline specimen confirmation

MaleCNS v1.0, FlyWire v783 and BANC v888 are separate single-specimen resources. BANC connectivity versions represent alternative snapshots of the same specimen, not biological replication. MANC lacks the brain and MAOL covers only the right optic lobe. We found no public second adult CNS specimen reconstructed with the same pipeline that could confirm the BM residual.

## Discussion

The main positive development result is mechanistically specific: in one MaleCNS graph, BM partner placement and reciprocal-versus-unidirectional weight allocation govern gain along a dominant sensory axis. Multiple controlled nulls rule out several simpler explanations within that graph.

The main external result is cautionary. The exact mechanism did not replicate in BANC, and most of the raw Male-to-FlyWire structural difference tracked a broad source-scale shift shared across sensory families. The strongest remaining candidate—five-synapse BM reciprocity—was the largest shared-family residual but missed its frozen criterion. It should be treated as a hypothesis for a new specimen, not as a rescued positive finding.

This work illustrates a general methodological point: raw cross-connectome density or reciprocity differences should not be interpreted biologically before common thresholds, autapse policy, node composition and dataset-wide family scaling are audited. Version changes of one reconstruction must not be counted as independent specimens.

## Limitations

- MaleCNS, FlyWire and BANC are single specimens generated by different reconstruction and annotation pipelines.
- Sex, specimen, age, genotype, image acquisition, synapse prediction and proofreading are not independently varied.
- The Male mechanism was localized after a development outcome and is not confirmatory.
- Type granularity differs: MaleCNS coarse `BM` versus six FlyWire BM-family subtypes.
- Null draws and sensory families are not independent biological animals.
- Synapse count is a structural proxy, not a direct physiological conductance measurement.
- The study does not establish biological memory, behavioural superiority or population-level sexual dimorphism.

## Methods summary

Neuron-level induced graphs retained 306 sensory, 125 internal and 6 descending frozen types from official MaleCNS and FlyWire edge sources. Structural nulls preserved progressively stronger invariants, including type-block directed degrees, reciprocal degrees, fixed support, source weight pools and class-specific allocation constraints. Finite-horizon effects were evaluated with frozen transfer operators and intervention-derived gain metrics.

Cross-dataset audits used exact resolved BM membership, non-self directed density, reciprocal-directed fraction and common synapse-count thresholds. Side/count sensitivity used 1,000 deterministic 69-node FlyWire subsets. Within-dataset enrichment used non-BM sensory families within 0.5–2.0 times the BM node count. Shared-family scaling used 52 exact common sensory labels, Jeffreys-smoothed Male/FlyWire log2 ratios and median/1.4826-MAD robust residuals. All decision rules were committed before their corresponding outcome metrics were opened.

## Data and code availability

The evidence manifest is `outputs/manuscript-evidence-v1/manifest.json`. It records source paths, decision pointers and SHA-256 hashes for ten authoritative result artifacts. Large third-party connectome files are not redistributed. Their official source locations and local hashes are documented in the individual manifests and findings reports.

## Current conclusion

The supported classification is:

> A dataset-specific, pipeline-confounded MaleCNS development mechanism with a prespecified external-replication candidate in strong-edge BM reciprocity.

The project is `data_waiting_external_replication`; additional training on the existing specimens cannot resolve the biological question.

