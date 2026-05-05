# Paper 3 HBG1 ARCHCODE Runner Gate

Date: 2026-05-03

Local source-to-ARCHCODE gate only. No live gnomAD query was run.

## Executive Verdict

- Decision: **STOP_NO_PRIMARY_ARCHCODE_CANDIDATES**
- Can HBG1 serve as the second regulatory-positive locus now? **NO**
- Main blocker: 0 MPRA effect rows fall inside the ARCHCODE bottom-5% source-runner tail; the bottom-5% row is not a candidate.
- Next required action: review source semantics and decide whether a source-effect MPRA cohort is acceptable before any strict live gate.

## Counts

| Metric | Value |
| --- | --- |
| source rows in runner | 16 |
| MPRA effect rows | 8 |
| MPRA near-zero controls | 8 |
| ARCHCODE bottom-5% threshold | 0.9875 |
| bottom-5% MPRA effect rows | 0 |
| bottom-5% near-zero control rows | 1 |
| primary LSSIM candidates | 0 |
| position/source controls | 7 |
| raw ARCHCODE atlas | results\HBG1_Unified_Atlas_hbg1.csv |
| raw ARCHCODE summary | results\UNIFIED_ATLAS_SUMMARY_hbg1.json |

## Candidate vs Controls

| Group | n | source semantics | ARCHCODE rule | live eligible |
|---|---:|---|---|---|
| Candidates | 0 | Kircher MPRA effect rows | bottom 5% inside 16-row HBG1 source runner | NO |
| Controls | 7 | Kircher MPRA near-zero rows | not bottom 5%, position/source matched | NO |

## Dry-Run Result

| Group | local dry-run status | reason |
|---|---|---|
| Candidates | BLOCKED_ZERO_ROWS | `0` candidate rows after ARCHCODE gate |
| Controls | PREVIEW-ONLY eligible | `7` control rows after ARCHCODE gate |

## Dry-Run Commands

Candidate dry-run:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_HBG1_ARCHCODE_CANDIDATES_20260503.csv --chrom 11 --cohort-column hbg1_archcode_candidate --cohort-op equals --cohort-value true --locus-name HBG1_archcode_candidates --out paper3_hbg1_archcode_candidates_dryrun_20260503 --rate-limit 3.0 --dry-run
```

Control dry-run:

```powershell
python scripts\population_filter.py --atlas results\PAPER3_HBG1_ARCHCODE_CONTROLS_20260503.csv --chrom 11 --cohort-column hbg1_archcode_control --cohort-op equals --cohort-value true --locus-name HBG1_archcode_controls --out paper3_hbg1_archcode_controls_dryrun_20260503 --rate-limit 3.0 --dry-run
```

## Allowed Claim

HBG1 now has a small local Kircher MPRA source-effect cohort with ARCHCODE LSSIM values and matched near-zero source controls, but it remains a source-semantics review target rather than a population-positive Paper 3 locus.

## Not Allowed

- "HBG1 validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"

## Reproducibility

```powershell
python scripts\paper3_hbg1_archcode_runner.py
```

The runner invokes:

```powershell
npx tsx scripts\generate-unified-atlas.ts --locus hbg1
```
