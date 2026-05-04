# Paper 3 LDLR / HBG1 Design Audit

Date: 2026-05-03

Local source-design audit only. No gnomAD query was run.

## Executive Verdict

- Decision: **LDLR_CONTROL_REBUILD_OR_HBG1_IMPORT**
- LDLR: **REBUILD_CONTROLS_BEFORE_DRY_RUN**
- HBG1: **IMPORT_ARCHCODE_ATLAS**
- Can either serve as the second regulatory-positive locus now? **NOT YET**
- Why: LDLR has cleaner germline disease/source semantics and many promoter/5_prime_UTR candidate-like rows, but strict same-mechanism non-bottom controls are too limited; HBG1 has useful MPRA-like source rows but no local ARCHCODE atlas/config gate.
- Next required action: rebuild LDLR controls before dry-run, or import HBG1 ARCHCODE atlas/config before any population gate.

## LDLR Source Counts

| Metric | Value |
| --- | --- |
| atlas rows | 3284 |
| queryable SNVs | 2344 |
| promoter/5_prime_UTR queryable rows | 16 |
| primary P/LP promoter exact-Kircher candidates | 8 |
| conflicting promoter exact-Kircher candidate-like rows | 4 |
| strict same-mechanism benign non-bottom controls | 0 |
| benign promoter exact-Kircher rows inside bottom5 | 3 |
| relaxed 3_prime_UTR benign options | 44 |
| relaxed coding synonymous benign options | 583 |
| frozen rebuild candidates | 8 |
| frozen rebuild controls | 0 |

## LDLR Candidate Semantics

LDLR promoter/5_prime_UTR P/LP rows are more interpretable than TERT promoter rows because the local disease context is familial hypercholesterolemia rather than mixed tumor/somatic interpretation. This is still not enough for a live or manuscript claim without mechanism-matched controls.

### Frozen Candidate Rows

| ClinVar_ID | Position_GRCh38 | Ref | Alt | HGVS_c | ClinVar_Significance | ARCHCODE_LSSIM | kircher_value | ldlr_rebuild_candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCV000375769 | 11089381 | A | G | NM_000527.4(LDLR):c.-168A>G | Likely pathogenic | 0.9831 | 0.54 | False |
| VCV000250945 | 11089397 | C | T | NM_000527.5(LDLR):c.-152C>T | Pathogenic/Likely pathogenic | 0.9831 | -1.33 | False |
| VCV001334394 | 11089541 | C | A | NM_000527.5(LDLR):c.-8C>A | Likely pathogenic | 0.9831 | -0.26 | False |
| VCV000375772 | 11089450 | A | G | NM_000527.4(LDLR):c.-99A>G | Likely pathogenic | 0.9832 | -0.5 | False |
| VCV000250956 | 11089414 | C | G | NM_000527.5(LDLR):c.-135C>G | Pathogenic/Likely pathogenic | 0.9836 | -2.7 | False |
| VCV003893685 | 11089514 | C | G | NM_000527.5(LDLR):c.-35C>G | Likely pathogenic | 0.9836 | 0.05 | False |
| VCV000440535 | 11089451 | C | T | NM_000527.4(LDLR):c.-98C>T | Pathogenic | 0.9837 | -0.46 | False |
| VCV000440533 | 11089398 | C | G | NM_000527.4(LDLR):c.-151C>G | Pathogenic | 0.9838 | -0.48 | False |

### Strict Same-Mechanism Controls

No rows.

### Control Option Classes

| option_class | n | gate_status | note |
| --- | --- | --- | --- |
| coding_synonymous_benign | 583 | RELAXED_ONLY_CODING_CONTROL | Queryable benign coding control; not a regulatory mechanism match. |
| other_benign | 347 | REJECT_UNMATCHED | Benign row without sufficient mechanism match. |
| noncoding_3utr_benign | 44 | RELAXED_ONLY_DIFFERENT_UTR_MECHANISM | Noncoding and benign, but 3_prime_UTR rather than promoter/5_prime_UTR. |
| same_mechanism_but_low_lssim | 3 | REJECT_AS_CONTROL_LOW_LSSIM_CONFOUNDED | Same promoter/5_prime_UTR mechanism, but also low-LSSIM; cannot test candidate-vs-position-control separation. |

## Old LDLR Artifacts Are Not Positive Evidence

- Old matched-control file exists: `True`.
- Old live audit exists: `True`.
- The old controls were not strict promoter/5_prime_UTR mechanism matches, and the prior live audit had query failures. Those artifacts remain design-level only.

## HBG1 Source-Only Audit

| Metric | Value |
| --- | --- |
| source_file | data\kircher_HBG1_GRCh38.tsv |
| source_exists | True |
| rows | 907 |
| queryable_snvs | 822 |
| positions | 274 |
| positive_effect_rows | 4 |
| negative_effect_rows | 94 |
| has_archcode_atlas | False |
| has_locus_config | False |
| decision | IMPORT_ARCHCODE_ATLAS |

## Dry-Run / Live Gate

- LDLR strict dry-run: **NOT RUN** because same-mechanism controls are not sufficient for the frozen gate.
- HBG1 strict dry-run: **NOT RUN** because no local ARCHCODE atlas/config gate exists.
- Live gnomAD: **NOT RUN**.

## Allowed Claim

LDLR is the current best local source-rich design candidate, but it needs a stricter control rebuild before any dry-run/live population screen. HBG1 is a plausible import target, not a current local cohort.

## Not Allowed

- "LDLR validates ARCHCODE"
- "HBG1 validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"

## Decision

**LDLR_CONTROL_REBUILD_OR_HBG1_IMPORT**

Do not run live gnomAD. The next narrow task is an LDLR control rebuild; if strict controls remain sparse, import HBG1 or another regulatory locus with a complete ARCHCODE atlas/config.

## Reproducibility

```powershell
python scripts\paper3_ldlr_hbg1_design_audit.py
```
