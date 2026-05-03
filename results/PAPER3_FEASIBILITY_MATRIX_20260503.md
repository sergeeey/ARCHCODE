# Paper 3 Feasibility Matrix

Generated from local atlas files only. This is a feasibility artifact, not a results claim.

|locus|role|total_rows|snv_rows|regulatory_category_rows|pearl_true_rows|lssim_min|lssim_q05|candidate_primary_bottom5_regulatory_snv_rows|candidate_boundary_lt099_regulatory_snv_rows|vep_present_rows|cadd_present_rows|status|warnings|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|HBB|positive_proof_of_concept|1103|912|728|20|0.8659|0.8870|0|44|1103|908|READY_FOR_DRY_RUN|none|
|HBA1|candidate_positive_regulatory|111|0|26|0|0.9857|0.9943|0|0|0|0|NEEDS_SUBSET_AUDIT|no non-synthetic regulatory SNVs in bottom 5% LSSIM; VEP unavailable; CADD unavailable|
|BCL11A_erythroid|candidate_positive_regulatory|182|182|182|0|0.9782|0.9791|11|17|0|0|READY_FOR_DRY_RUN|VEP unavailable; CADD unavailable; category field is broad 'other'|
|GATA1|candidate_positive_regulatory|183|0|29|0|0.9701|0.9892|0|0|0|0|NEEDS_SUBSET_AUDIT|no non-synthetic regulatory SNVs in bottom 5% LSSIM; VEP unavailable; CADD unavailable|
|CFTR|mechanism_boundary|3349|2592|1007|0|0.8329|0.9814|27|28|2594|0|READY_FOR_DRY_RUN|CADD unavailable|
|BRCA1|negative_coding_control|10682|7218|2262|0|0.8767|0.9829|96|97|0|0|READY_FOR_DRY_RUN|VEP unavailable; CADD unavailable|
|TP53|negative_coding_control|2794|1977|750|0|0.9443|0.9674|4|7|0|0|READY_FOR_DRY_RUN|VEP unavailable; CADD unavailable|

## Interpretation Guardrails

- `candidate_primary_bottom5_regulatory_snv_rows` is a dry-run cohort size for planning.
- It must not be reported as validation evidence until gnomAD queries are run and audited.
- Broad `other` categories require source review before being treated as enhancer/regulatory.
- Synthetic/mock/demo rows are excluded from primary Paper 3 evidence.
- Absence from gnomAD is a triage signal, not proof of universal constraint.
