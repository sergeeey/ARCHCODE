# VALIDATION_EXECUTION_2026-03-05

## Scope

Execution of `VALIDATION_PROTOCOL.md` and sequential start of 5 strategic tasks:

1. AI blind spot benchmark
2. Loop That Stayed
3. Weak CTCF / CTCF-KD
4. Tissue-specific context validation
5. VUS stratification

Update (2026-03-06 canonicalization):
- Historical Task 3 status in this file is superseded for claim-level decisions by:
  - `results/task3_canonical_status_2026-03-06.json`

---

## Implemented

- Added protocol:
  - `VALIDATION_PROTOCOL.md`

- Fixed compatibility regression discovered during Task 2 run:
  - `src/services/AlphaGenomeNodeService.ts`
  - Change: restored re-export `AlphaGenomeService` from node adapter module.
  - Impact: scripts importing `AlphaGenomeService` from `AlphaGenomeNodeService` work again.

- Created task artifacts:
  - `results/task1_ai_blindspot_summary_2026-03-05.json`
  - `results/task1_ai_blindspot_fresh_2026-03-05.json`
  - `results/task1_alphagenome_benchmark_95kb_2026-03-05.json`
  - `results/task1_akita_benchmark_95kb_2026-03-05.json`
  - `results/task2_loop_that_stayed_status_2026-03-05.json`
  - `results/task3_ctcf_summary_2026-03-05.json`
  - `results/task3_weak_ctcf_isolated_2026-03-05.json`
  - `results/task4_epigenome_crossval_2026-03-05.json`
  - `results/task5_vus_stratification_summary_2026-03-05.json`

---

## Verified

### Baseline integrity after edits

- `npx tsx scripts/validate-mysterious-vus.ts`
  - Result: `PASS`
  - Evidence:
    - `results/vus_validation_report.json`
    - `results/alphagenome_forum_post.md`

- `npm run validate:ctcf-kd`
  - Result: `PASS`
  - Key output:
    - Mean loop duration: `16.89 min`
    - 95% CI: `[13.42, 20.35]`
  - Evidence:
    - `results/blind_test_validation_2025.md`

- `npx tsx scripts/test_weak_ctcf.ts --runs=200 --steps=36000`
  - Result: `PASS` (script execution)
  - Key output:
    - Weak readthrough delta vs baseline: `0.00 pp`
    - Verdict: `INCONCLUSIVE_NO_WEAK_EVENTS`
  - Evidence:
    - `results/task3_weak_ctcf_isolated_2026-03-05.json`

- `python scripts/epigenome_crossval_alphagenome.py --loci 95kb cftr tp53 brca1 mlh1 ldlr --output results/task4_epigenome_crossval_2026-03-05.json`
  - Result: `PASS` (6/6 loci successful)
  - Aggregate:
    - CTCF mean recall: `1.0`
    - H3K27ac mean recall: `0.8535`
  - Evidence:
    - `results/task4_epigenome_crossval_2026-03-05.json`

- `python scripts/within_category_analysis.py`
  - Result: `PASS`
  - Evidence:
    - `results/within_category_analysis.json`

- `.venv\\Scripts\\python.exe scripts/benchmark_alphagenome.py --locus 95kb --cell-line GM12878 --output results/task1_alphagenome_benchmark_95kb_2026-03-05.json`
  - Result: `PASS`
  - Evidence:
    - `results/task1_alphagenome_benchmark_95kb_2026-03-05.json`
  - Added metrics:
    - `local_metrics.*.local_ssim_mean` (window=50, n=25 windows)

- `.venv\\Scripts\\python.exe scripts/benchmark_akita.py --locus 95kb --cell-type GM12878 --output results/task1_akita_benchmark_95kb_2026-03-05.json`
  - Result: `PASS`
  - Evidence:
    - `results/task1_akita_benchmark_95kb_2026-03-05.json`
  - Added metrics:
    - `local_metrics.*.local_ssim_mean` (window=50, n=25 windows)

### Task-specific summaries generated

- Task 1:
  - `results/task1_ai_blindspot_summary_2026-03-05.json`
  - Built from available benchmark artifacts in `results/alphagenome_benchmark_*.json` and `results/akita_benchmark_*.json`.
  - Fresh rerun summary:
    - `results/task1_ai_blindspot_fresh_2026-03-05.json`
  - 95kb interpretation policy:
    - Pearson/Spearman kept as secondary
    - Local SSIM (`window=50`) added as primary micro-window metric

- Task 2:
  - `results/task2_loop_that_stayed_status_2026-03-05.json`
  - `results/task2_reconciliation_2026-03-05.json`
  - Detects contradiction between legacy and fresh artifacts and records reconciliation policy.

- Task 3:
  - `results/task3_ctcf_summary_2026-03-05.json`
  - `results/task3_weak_ctcf_isolated_2026-03-05.json`
  - Combines ablation + CTCF-KD kinetics evidence + isolated weak-site perturbation run.

- Task 5:
  - `results/task5_vus_stratification_summary_2026-03-05.json`
  - Combines candidate stratification and within-category discrimination context.
  - Anti-overclaim policy embedded: clinical reclassification remains `UNVERIFIED`.

---

## UNVERIFIED

- Weak CTCF paradox as strict claim:
  - Direct weak-site-only perturbation with explicit `<0.85` site mutation is executed, but strict interpretation is inconclusive in this slice due to `weakEncounter=0`.
  - Current status: `PARTIAL_SUPPORT` (CTCF-KD kinetics validated; weak-site strict claim not resolved for this locus geometry).

- Task 4/5 causal and clinical claims:
  - Task 4 overlap metrics validate input-feature consistency, not causal biology.
  - Task 5 stratification metrics are hypothesis-generating; clinical reclassification remains unverified without orthogonal validation.

---

## Key Findings (current run only)

- Task 2 (fresh pipeline):
  - Top-5 VUS batch produced `BENIGN` structural verdicts with mechanistic interpretation toward post-transcriptional effects.
  - This conflicts with older high-claim Loop That Stayed artifact; contradiction is explicitly recorded and reconciled in `results/task2_reconciliation_2026-03-05.json`.

- Task 1 (95kb metric hardening):
  - LSSIM was added to both AlphaGenome and Akita benchmarks.
  - For 95kb, Pearson remains low and is treated as secondary; LSSIM is now recorded as the primary local structural metric.

- Task 4:
  - Strong CTCF positional recall against ENCODE-aligned config features across 6 loci.
  - H3K27ac agreement is locus-dependent and lower precision/F1 than CTCF.
  - Interpretation limited to input-feature alignment (`SUPPORTED`), not causal/clinical inference (`UNVERIFIED`).

- Task 3:
  - Isolated weak-CTCF experiment executed (`task3_weak_ctcf_isolated_2026-03-05.json`).
  - For current HBB setup, strict weak-site readthrough claim is inconclusive because weak-barrier encounters were not observed.

- Task 5:
  - Global separation may exist in some loci, but within-category separation is often modest.
  - Supports conservative interpretation: stratification is hypothesis-generating unless functionally validated.
  - Candidate counts are not equivalent to clinical reclassification.

---

## Risk Notes

- Several legacy artifacts and narratives are inconsistent; mixed-generation reports must not be merged into publication claims without reconciliation.
- Script ecosystem contains optional heavy dependencies not pinned as mandatory runtime requirements; reproducibility is environment-sensitive.
- Mock/synthetic pathways still exist and require explicit provenance in every output used for claims.

---

## Verdict

- `READY` for protocol adoption and continued staged validation.
- `NEEDS_FIXES` before publication-grade claims for:
  - strict weak-CTCF isolated experiment,
  - reconciliation of contradictory Loop That Stayed narratives.



