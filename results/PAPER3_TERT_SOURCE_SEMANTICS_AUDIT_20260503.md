# Paper 3 TERT Source-Semantics Audit

Date: 2026-05-03

This is a local source-semantics audit before any live gnomAD query. No live population query was run.

## Executive Verdict

- Decision: **REBUILD**
- Can TERT be interpreted as a regulatory-positive candidate locus now? **NOT YET**
- Why: the local TERT cohort contains real promoter/5_prime_UTR rows with exact Kircher overlap, but the candidate-like pathogenic/conflicting promoter rows need germline-versus-somatic source resolution before live population interpretation.
- Main blocker: after pre-live exclusions, clean positive candidates are `0`; control-like promoter rows remain useful only after candidate rebuild.
- Next required action: rebuild a smaller TERT promoter/5_prime_UTR cohort from source rows whose germline/cancer/somatic semantics are explicitly auditable, or switch to another regulatory locus with cleaner noncoding source provenance.

## Audit Counts

| Group | n | promoter/5_prime_UTR | exact Kircher overlap | source-ambiguous candidate-like | benign/control-like | live_gate_include | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Candidates | 8 | 6 | 6 | 3 | 3 | 0 | current candidate set is not live-ready |
| Controls | 8 | 3 | 3 | 0 | 3 | 0 | 3 controls are useful for a rebuilt promoter/5_prime_UTR design, but not without candidates |

## Germline / Cancer Semantics

- Local rows do not encode a definitive germline-versus-somatic flag.
- Benign/Likely benign promoter/5_prime_UTR rows are treated as germline-compatible control-like source context, not positive candidate evidence.
- Pathogenic or conflicting TERT promoter/5_prime_UTR rows are treated as cancer/somatic/cancer-predisposition ambiguous until their original source semantics are checked.
- Splice-region or intronic rows are not accepted as primary promoter/5_prime_UTR regulatory-positive candidates in this gate.

### Locally Germline-Compatible Promoter/5_prime_UTR Rows

These rows are not definitive germline truth-set rows; they are benign/Likely benign promoter/5_prime_UTR rows with exact local Kircher overlap and are therefore control-like source context.

| group | ClinVar_ID | pos | allele | HGVS_c | ClinVar | Kircher value | pre-live action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate | VCV003765386 | 1295154 | G>C | NM_198253.3(TERT):c.-165C>G | Likely benign | -0.26 | exclude_from_positive_candidate_set_benign_control_like |
| candidate | VCV002575426 | 1295163 | C>G | NM_198253.3(TERT):c.-174G>C | Likely benign | -0.16 | exclude_from_positive_candidate_set_benign_control_like |
| candidate | VCV001212208 | 1295207 | G>C | NM_198253.2(TERT):c.-218C>G | Benign/Likely benign | -0.03 | exclude_from_positive_candidate_set_benign_control_like |
| control | VCV003354133 | 1294995 | G>T | NM_198253.3(TERT):c.-6C>A | Likely benign | 0.06 | hold_until_candidate_set_is_rebuilt |
| control | VCV003036157 | 1294994 | G>T | NM_198253.3(TERT):c.-5C>A | Likely benign | -0.01 | hold_until_candidate_set_is_rebuilt |
| control | VCV003029714 | 1294992 | C>T | NM_198253.3(TERT):c.-3G>A | Likely benign | -0.03 | hold_until_candidate_set_is_rebuilt |

### Cancer/Somatic/Cancer-Predisposition Ambiguous Rows

These are the candidate-like promoter/5_prime_UTR rows that must be excluded before live population screening unless the original source semantics are resolved.

| group | ClinVar_ID | pos | allele | HGVS_c | ClinVar | Kircher value | pre-live action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate | VCV000242210 | 1295046 | T>G | NM_198253.3(TERT):c.-57A>C | Conflicting classifications of pathogenicity | 0.65 | exclude_until_germline_vs_somatic_source_semantics_resolved |
| candidate | VCV001299388 | 1295113 | G>A | NM_198253.3(TERT):c.-124C>T | Conflicting classifications of pathogenicity | 2.0 | exclude_until_germline_vs_somatic_source_semantics_resolved |
| candidate | VCV002443072 | 1295135 | G>A | NM_198253.3(TERT):c.-146C>T | Pathogenic | 1.42 | exclude_until_germline_vs_somatic_source_semantics_resolved |

## Exact Kircher / Source Overlap

- Candidates with exact Kircher overlap: `6/8`.
- Controls with exact Kircher overlap: `3/8`.
- Candidate/control exact-overlap rows are not the same variants, but both groups draw from the same local Kircher source family for the promoter/5_prime_UTR subset.
- Source overlap is incomplete for splice/intronic rows, so those rows should not be mixed into a promoter/5_prime_UTR live gate.

## Controls Mechanism Matching

| Control subset | n | interpretation |
| --- | --- | --- |
| promoter/5_prime_UTR benign exact-Kircher controls | 3 | good mechanism match for a rebuilt promoter/5_prime_UTR candidate set |
| splice-region benign controls | 2 | partial match only if splice candidates are kept, which this audit excludes |
| pathogenic/intronic controls | 3 | poor controls for a promoter/5_prime_UTR regulatory cohort |

## Rows To Exclude Before Live Gate

### Candidates

| ClinVar_ID | pos | allele | category | ClinVar | Kircher exact | local source interpretation | audit flag | pre-live action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCV002932179 | 1294664 | C>G | splice_region | Likely benign | False | not_primary_promoter_5utr_regulatory | not_primary_regulatory_promoter_5utr | exclude_not_promoter_or_5_prime_UTR |
| VCV001570434 | 1294664 | C>T | splice_region | Likely benign | False | not_primary_promoter_5utr_regulatory | not_primary_regulatory_promoter_5utr | exclude_not_promoter_or_5_prime_UTR |
| VCV000242210 | 1295046 | T>G | 5_prime_UTR | Conflicting classifications of pathogenicity | True | promoter_5utr_candidate_like_but_cancer_somatic_ambiguous | source_semantics_ambiguous_possible_cancer_context | exclude_until_germline_vs_somatic_source_semantics_resolved |
| VCV001299388 | 1295113 | G>A | 5_prime_UTR | Conflicting classifications of pathogenicity | True | promoter_5utr_candidate_like_but_cancer_somatic_ambiguous | source_semantics_ambiguous_possible_cancer_context | exclude_until_germline_vs_somatic_source_semantics_resolved |
| VCV002443072 | 1295135 | G>A | 5_prime_UTR | Pathogenic | True | promoter_5utr_candidate_like_but_cancer_somatic_ambiguous | source_semantics_ambiguous_possible_cancer_context | exclude_until_germline_vs_somatic_source_semantics_resolved |
| VCV003765386 | 1295154 | G>C | 5_prime_UTR | Likely benign | True | promoter_5utr_benign_germline_compatible_control_like | benign_control_like_not_positive_candidate | exclude_from_positive_candidate_set_benign_control_like |
| VCV002575426 | 1295163 | C>G | 5_prime_UTR | Likely benign | True | promoter_5utr_benign_germline_compatible_control_like | benign_control_like_not_positive_candidate | exclude_from_positive_candidate_set_benign_control_like |
| VCV001212208 | 1295207 | G>C | 5_prime_UTR | Benign/Likely benign | True | promoter_5utr_benign_germline_compatible_control_like | benign_control_like_not_positive_candidate | exclude_from_positive_candidate_set_benign_control_like |

### Controls

| ClinVar_ID | pos | allele | category | ClinVar | Kircher exact | local source interpretation | audit flag | pre-live action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCV003967333 | 1282623 | C>T | splice_region | Likely benign | False | not_primary_promoter_5utr_regulatory | partial_for_excluded_splice_rows_only | exclude_if_primary_promoter_5utr_candidate_set_is_used |
| VCV002922492 | 1282623 | C>A | splice_region | Likely benign | False | not_primary_promoter_5utr_regulatory | partial_for_excluded_splice_rows_only | exclude_if_primary_promoter_5utr_candidate_set_is_used |
| VCV003354133 | 1294995 | G>T | 5_prime_UTR | Likely benign | True | promoter_5utr_benign_germline_compatible_control_like | good_for_rebuilt_promoter_5utr_benign_control | hold_until_candidate_set_is_rebuilt |
| VCV003036157 | 1294994 | G>T | 5_prime_UTR | Likely benign | True | promoter_5utr_benign_germline_compatible_control_like | good_for_rebuilt_promoter_5utr_benign_control | hold_until_candidate_set_is_rebuilt |
| VCV003029714 | 1294992 | C>T | 5_prime_UTR | Likely benign | True | promoter_5utr_benign_germline_compatible_control_like | good_for_rebuilt_promoter_5utr_benign_control | hold_until_candidate_set_is_rebuilt |
| VCV000012738 | 1294770 | C>T | intronic | Pathogenic/Likely pathogenic | False | intronic_or_splice_pathogenic_control_not_clean | poor_control_pathogenic_or_ambiguous | exclude_pathogenic_or_ambiguous_control_semantics |
| VCV001697481 | 1294769 | A>G | intronic | Likely pathogenic | False | intronic_or_splice_pathogenic_control_not_clean | poor_control_pathogenic_or_ambiguous | exclude_pathogenic_or_ambiguous_control_semantics |
| VCV003240577 | 1294769 | A>T | intronic | Likely pathogenic | False | intronic_or_splice_pathogenic_control_not_clean | poor_control_pathogenic_or_ambiguous | exclude_pathogenic_or_ambiguous_control_semantics |

## Allowed Claim

TERT remains a plausible source-rebuild target because local rows include promoter/5_prime_UTR exact Kircher overlap, but the current 8-row TERT candidate/control gate is not clean enough for live gnomAD interpretation.

## Not Allowed

- "TERT validates ARCHCODE"
- "multi-locus confirmed"
- "Paper 3 ready"
- "not found proves constraint"
- "ARCHCODE beats VEP/CADD"

## Decision

**REBUILD**

Do not run live gnomAD for the current TERT 8-candidate / 8-control set. Rebuild or externally audit source semantics first.

## Reproducibility

```powershell
python scripts\paper3_tert_source_semantics_audit.py
```
