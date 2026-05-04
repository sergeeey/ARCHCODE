# Paper 3 LDLR Control Rebuild Decision

Date: 2026-05-03

Bounded local control rebuild only. No gnomAD query was run.

## Executive Verdict

- Decision: **STOP_LDLR_AS_CLEAN_POSITIVE_GATE**
- Can LDLR serve as the second clean regulatory-positive locus now? **NO / NOT YET**
- Accepted strict controls: `0`
- Frozen strict controls written: `0`
- Main blocker: no benign queryable row satisfies same promoter/upstream window, promoter/5_prime_UTR mechanism, exact Kircher overlap, and non-bottom LSSIM simultaneously.
- Next required action: stop LDLR as the current clean positive gate and move to HBG1 atlas/config import or another complete regulatory source import.

## Pre-Specified Control Rule

- Same configured LDLR promoter/upstream H3K27ac window from `config/locus/ldlr_300kb.json`.
- Queryable SNV.
- Benign or Likely benign local source semantics.
- Outside LDLR queryable bottom 5% by `ARCHCODE_LSSIM`.
- Primary control additionally requires promoter/5_prime_UTR mechanism and exact Kircher overlap.

## Control Rebuild Counts

| Metric | Value |
| --- | --- |
| same-window total rows | 40 |
| same-window benign/queryable rows | 40 |
| strict accepted controls | 0 |
| same-mechanism but low-LSSIM controls | 3 |
| relaxed non-bottom different-mechanism rows | 18 |
| outside-window benign options | 937 |

## Same-Mechanism Low-LSSIM Rows

These rows look mechanism-matched, but fail as controls because they are also in the low-LSSIM tail.

| ClinVar_ID | Position_GRCh38 | Ref | Alt | HGVS_c | ARCHCODE_LSSIM | ldlr_bottom5 | kircher_value | control_rebuild_gate_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCV000250925 | 11089281 | G | T | NM_000527.5(LDLR):c.-268G>T | 0.9831 | True | 0.06 | REJECT_LOW_LSSIM_CONFOUNDED |
| VCV000918511 | 11089383 | A | G | NM_000527.4(LDLR):c.-166A>G | 0.9835 | True | 0.22 | REJECT_LOW_LSSIM_CONFOUNDED |
| VCV000430744 | 11089521 | G | C | NM_000527.5(LDLR):c.-28G>C | 0.9836 | True | -0.12 | REJECT_LOW_LSSIM_CONFOUNDED |

## Relaxed Non-Bottom Rows

These rows are same-window and non-bottom, but they are not promoter/5_prime_UTR exact-Kircher controls. They are not accepted for the clean gate.

| ClinVar_ID | Position_GRCh38 | Ref | Alt | HGVS_c | Category | mechanism_subclass | ARCHCODE_LSSIM | control_rebuild_gate_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCV001756614 | 11089554 | G | A | c.6G>A | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV001077440 | 11089557 | C | T | c.9C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV002812733 | 11089563 | C | G | c.15C>G | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV001776145 | 11089563 | C | T | c.15C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV000925039 | 11089575 | C | T | c.27C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV002911824 | 11089581 | C | G | c.33C>G | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV001135175 | 11089581 | C | T | c.33C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV000921122 | 11089593 | C | T | c.45C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV004757623 | 11089594 | C | T | c.46C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV003673747 | 11089596 | C | T | c.48C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV000250983 | 11089596 | C | A | c.48C>A | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV001097179 | 11089599 | C | T | c.51C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV000375773 | 11089601 | C | T | c.53C>T | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV000924946 | 11089602 | G | C | c.54G>C | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV000161272 | 11089606 | G | A | c.58G>A | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV001172187 | 11089608 | G | A | c.60G>A | synonymous | coding_synonymous | 0.999 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV002912195 | 11089611 | T | G | c.63T>G | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |
| VCV004756886 | 11089611 | T | C | c.63T>C | synonymous | coding_synonymous | 0.9991 | RELAXED_ONLY_DIFFERENT_MECHANISM |

## Dry-Run / Live Gate

- LDLR strict dry-run: **NOT RUN** because strict controls are empty.
- Live gnomAD: **NOT RUN**.

## Allowed Claim

LDLR remains source-rich and biologically relevant, but the strict control rebuild fails; it should not be used as the second clean regulatory-positive Paper 3 locus from current local artifacts.

## Not Allowed

- "LDLR validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"

## Decision

**STOP_LDLR_AS_CLEAN_POSITIVE_GATE**

Move to HBG1 atlas/config import or another complete regulatory source import before any further live population gate.

## Reproducibility

```powershell
python scripts\paper3_ldlr_control_rebuild.py
```
