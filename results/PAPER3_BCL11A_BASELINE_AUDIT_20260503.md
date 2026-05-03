# Paper 3 BCL11A Baseline Audit

Generated from local atlas, source audit, and locus config only.

## Group Summary

| group | n | bottom5_overlap | lssim_median | lssim_min |
|---|---:|---:|---:|---:|
| all_atlas | 182 | 11 | 0.9953 | 0.9782 |
| near_feature_1kb | 17 | 11 | 0.9789 | 0.9782 |
| near_feature_5kb | 18 | 11 | 0.9790 | 0.9782 |
| splice_or_intronic | 15 | 3 | 0.9948 | 0.9785 |
| coding_missense_or_synonymous | 147 | 7 | 0.9953 | 0.9782 |
| primary_audited_ids | 3 | 3 | 0.9785 | 0.9785 |

## Category Counts

| category | count |
|---|---:|
| other | 182 |

## HGVS-Derived Subclass Counts

| subclass | count |
|---|---:|
| coding_missense_or_synonymous | 147 |
| coding_nonsense | 18 |
| splice_region_or_intronic | 15 |
| utr_or_transcript_flank | 2 |

## Interpretation

- Category-only baseline is currently uninformative because all BCL11A rows are `other`.
- Position-window baseline is necessary: all 11 bottom-5% rows are within 1 kb of a configured feature.
- The 3 primary audited rows are a small promoter-proximal splice/UTR-like pilot, not an enhancer-wide validation set.
