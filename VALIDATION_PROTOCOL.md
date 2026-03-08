# VALIDATION_PROTOCOL

Date: 2026-03-06
Project: ARCHCODE
Mode: Zero-Hallucination Validation

## 0) Strategic Positioning (CRITICAL)

### ARCHCODE is a Discovery Engine, NOT a Prediction Tool

This distinction governs all validation claims below:

| Aspect | Prediction Tool (❌ WRONG) | Discovery Engine (✅ CORRECT) |
|--------|---------------------------|-------------------------------|
| **Primary claim** | "AUC = 0.977, better than VEP" | "Discovered 27 pearl variants invisible to VEP" |
| **Validation** | Hold-out test set accuracy | Orthogonal evidence (9 methods) |
| **Limitation** | "Needs more training data" | "Requires experimental validation" |
| **Success metric** | Accuracy, F1, precision/recall | Novel findings, testable hypotheses |

**Implication for this protocol:**
- AUC/accuracy metrics are **secondary** (characterization, not primary claim)
- **Primary claims** must be discovery-focused (pearl variants, structural blind spot, mechanistic insight)
- Validation requires **orthogonal evidence**, not just hold-out test sets

See: `docs/DISCOVERY_ENGINE_POSITIONING.md` for full strategic rationale.

## 1) Purpose

This protocol defines how ARCHCODE claims are validated without overclaiming.
No scientific or product claim is accepted without reproducible evidence.

## 2) Claim Levels

- `EXPLORATORY`: pattern observed, not tested against strict acceptance criteria.
- `SUPPORTED`: statistically supported on defined data, but external replication pending.
- `VALIDATED`: passes pre-declared criteria, reproducible, with independent or orthogonal confirmation.

Claims must explicitly state level.

## 3) Provenance Classes

- `EXPERIMENTAL`: measured external biological data (Hi-C, RNA-seq, etc.).
- `REAL_API`: real model/service output (for example AlphaGenome with real key).
- `MOCK_SYNTHETIC`: mock or synthetic outputs for development only.

Publication-grade conclusions require `EXPERIMENTAL` and/or `REAL_API` evidence.
`MOCK_SYNTHETIC` can support engineering checks only.

## 4) Mandatory Evidence Contract

Every claim must map to all items below:

1. Exact command(s) used.
2. Output artifact path(s).
3. Commit hash used for run.
4. Data provenance tag (`EXPERIMENTAL`, `REAL_API`, `MOCK_SYNTHETIC`).
5. Acceptance criteria and observed result.

If any item is missing, claim status is `UNVERIFIED`.

## 5) Statistical Minimum

- Report effect size and confidence interval when possible.
- Report sample size `n`.
- For multiple comparisons: apply FDR correction (or explicitly justify why not needed).
- For ranking/classification: report at least one discrimination metric (`AUC`, `precision/recall`, or equivalent).
- Report negative results and failed checks.

## 6) Anti-Hallucination Gates

Before marking a task complete:

1. `Implemented` lists only changed files and behavior.
2. `Verified` lists only executed commands and observed outputs.
3. `UNVERIFIED` lists gaps explicitly.
4. No causal language from correlational evidence.
5. No claim of superiority without direct baseline comparison.

## 7) Go/No-Go Criteria by Task

## Task 1: AI Blind Spot (ARCHCODE vs DL baselines)

Go when all are true:
- Same loci compared across methods.
- Metrics reported for ARCHCODE vs AlphaGenome and/or Akita.
- At least one orthogonal reference metric reported (for example Hi-C correlation where available).

No-Go:
- Mixed loci windows/resolutions without normalization.
- Missing provenance for AlphaGenome outputs.

## Task 2: Loop That Stayed

Go when all are true:
- Structural signature is reproducible.
- Splicing/functional proxy is reported separately.
- Conclusion remains mechanistic hypothesis unless functional evidence exists.

No-Go:
- Causal disease claims from structure-only evidence.

## Task 3: Weak CTCF Paradox

Go when all are true:
- Ablation design defined (weak-site perturbation vs control).
- Effect on loop/TAD metrics quantified.
- Stability checked across seeds or repeated runs.

No-Go:
- Single-run conclusion.

## Task 4: Tissue-Specific 3D Pathogenicity

Go when all are true:
- Same variant classes tested across tissue-relevant contexts.
- Positive and negative tissue controls included.
- Limitations on tissue mismatch stated.

No-Go:
- Generalization claims from one tissue only.

## Task 5: VUS Stratification

Go when all are true:
- Stratification rules are explicit and reproducible.
- Output includes per-variant rationale and provenance tags.
- Structural vs post-transcriptional interpretation is separated as hypothesis-level unless externally validated.

No-Go:
- Reclassification claims without functional validation disclaimer.
- For strict HBB VUS ranking gate: if `within-category LSSIM AUC < 0.55` or `enrichment p-value > 0.01`, set claim level to `EXPLORATORY` and block clinical utility escalation.
- Reference artifact (2026-03-06): `results/hbb_vus_validation_report_2026-03-06.json` (`go_no_go=NO_GO`).

## 8) Required Report Format (per task)

- `Task`
- `Implemented`
- `Verified`
- `UNVERIFIED`
- `Risks`
- `Verdict` (`READY` / `NEEDS_FIXES` / `BLOCKED`)

## 9) Merge Rules

No merge for validation updates unless:
- Evidence contract is complete.
- Security/secret checks pass for touched scope.
- Contradictions with existing audit/falsification docs are resolved or explicitly documented.
