# Paper 3 HBA1 MANGO Queryable Atlas

This file is derived from local HBA1 atlas rows that overlap HUDEP2 H3K27ac MANGO interaction anchors.

- Input atlas: `results\HBA1_Unified_Atlas_300kb.csv`
- MANGO overlap: `results\PAPER3_HBA1_MANGO_VARIANT_OVERLAP_20260503.csv`
- Rows with MANGO evidence: `67`
- Queryable SNVs recovered: `66`
- Recovery source: UCSC hg38 sequence API + local `HGVS_c` substitution

Rows with `allele_recovery_status=RECOVERED_UCSC_HGVS_MATCH` passed a reference-base sanity check.
