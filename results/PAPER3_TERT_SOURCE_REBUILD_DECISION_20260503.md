# Paper 3 TERT Source-Rebuild Gate

Date: 2026-05-03

This gate finalizes the current TERT source-semantics pass. It does not query gnomAD.

## Executive Verdict

- Decision: **REBUILD_OR_SWITCH**
- Can TERT serve as the second regulatory-positive locus now? **NO / NOT YET**
- Rebuilt candidates: `0`
- Rebuilt controls: `0`
- Main blocker: all candidate-like promoter rows remain mixed germline/somatic/cancer-context rows or lack clean positive-candidate semantics.
- Next required action: either perform a deeper TERT source-resolution import, or switch to a cleaner regulatory locus such as GATA1 if local source rows support it.

## Rebuild Result

| Group | n | live_gate_include | interpretation |
| --- | --- | --- | --- |
| strict rebuilt TERT candidates | 0 | 0 | empty; live gate blocked |
| strict rebuilt TERT controls | 0 | 0 | empty because candidates are empty |
| potential promoter/5_prime_UTR benign controls | 3 | 0 | useful only if a clean candidate set is rebuilt |

## External Source-Resolution Notes

The current candidate-like TERT promoter rows are not discarded as biology; they are excluded from this live gate because source semantics are mixed enough to confound population interpretation.

| ClinVar_ID | HGVS_c | ClinVar_Significance | kircher_value | external_source_semantics | external_source_url |
| --- | --- | --- | --- | --- | --- |
| VCV000242210 | NM_198253.3(TERT):c.-57A>C | Conflicting classifications of pathogenicity | 0.65 | mixed_germline_and_somatic | https://www.ncbi.nlm.nih.gov/clinvar/variation/242210/ |
| VCV001299388 | NM_198253.3(TERT):c.-124C>T | Conflicting classifications of pathogenicity | 2.0 | mixed_germline_and_strong_somatic | https://www.ncbi.nlm.nih.gov/clinvar/variation/1299388/ |
| VCV002443072 | NM_198253.3(TERT):c.-146C>T | Pathogenic | 1.42 | somatic_dominated_or_mixed | https://www.ncbi.nlm.nih.gov/clinvar/variation/2443072/ |

## Potential Controls Preserved For Future Design

| ClinVar_ID | HGVS_c | ClinVar_Significance | kircher_value | mechanism_match_quality |
| --- | --- | --- | --- | --- |
| VCV003354133 | NM_198253.3(TERT):c.-6C>A | Likely benign | 0.06 | good_for_rebuilt_promoter_5utr_benign_control |
| VCV003036157 | NM_198253.3(TERT):c.-5C>A | Likely benign | -0.01 | good_for_rebuilt_promoter_5utr_benign_control |
| VCV003029714 | NM_198253.3(TERT):c.-3G>A | Likely benign | -0.03 | good_for_rebuilt_promoter_5utr_benign_control |

## Live Query Gate

- Live gnomAD: **NOT RUN**.
- Strict dry-run: **SKIPPED** because rebuilt candidates and rebuilt controls are empty.
- Treat-not-found-as-absent mode: **NOT RUN**.

## Allowed Claim

TERT remains biologically plausible and source-rich, but the current source-rebuild gate does not produce a clean non-empty regulatory-positive candidate/control cohort.

## Not Allowed

- "TERT validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"

## Decision

**REBUILD_OR_SWITCH**

Do not run live gnomAD on the current TERT set. The next efficient move is a bounded source-resolution import; if that still leaves candidates empty, switch locus.

## Reproducibility

```powershell
python scripts\paper3_tert_source_rebuild_gate.py
```
