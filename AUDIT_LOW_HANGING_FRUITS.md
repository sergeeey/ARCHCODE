# AUDIT LOW HANGING FRUITS

Date: 2026-05-05

## Selection Criteria

Low-hanging fruits are changes that reduce scientific-integrity risk without changing raw data, scientific results, or production code semantics. This file is a plan only; no fixes are applied here.

## Top 10

| Rank | Item | Impact | Effort | Verification |
|---:|---|---|---|---|
| 1 | Create a tracked `CURRENT_TRUTH.md` or update `PROJECT_CANON.md` with current claim boundaries | Prevents public/technical drift | Low | `npm run validate:project-canon` |
| 2 | Run and record full release gate: `verify_manuscript`, `check_redflags`, `secret_scan`, `results-contracts`, `npm test` | Converts partial audit to release-grade gate | Low/Medium | Command outputs |
| 3 | Make a `CLAIM_DRIFT_TODO.md` listing exact files/phrases to downgrade | Stops silent overclaim leakage | Low | Manual diff + redflag scan |
| 4 | Add a lineage manifest for modified `generate-unified-atlas.ts` -> `HBB_Unified_Atlas.csv` -> summary JSON | Reduces data/result ambiguity | Medium | Rerun command + artifact hashes |
| 5 | Split dirty tree into safe categories before any commit | Avoids `git add .` disaster | Low | `git status --short`, explicit file list |
| 6 | Re-run `python -m validation_suite run --all` and compare against stored `master_results.json` | Detects stale falsification artifacts | Medium | New master results artifact |
| 7 | Add a "not_found is not constraint" boilerplate to all population-screen templates | Blocks universal-constraint overclaim | Low | `rg "not_found|not_observed|absent"` |
| 8 | Add `SYNTHETIC_`/provenance checks for new generated synthetic scans | Prevents synthetic/real mixing | Low/Medium | `check_redflags.py` extension |
| 9 | Reconcile version labels (`v2.17`, `v2.18`, `v5.0`) | Prevents public confusion | Low | `rg "v2\\.17|v2\\.18|v5\\.0"` |
| 10 | Create a Paper3 promotion checklist requiring frozen cohort, controls, command, artifact, and caveat | Keeps exploratory results out of public canon | Low | New checklist + canon gate |

## Fast Documentation Fixes

| Fix | Why |
|---|---|
| Add `Canon Tier` header to every new Paper3 doc | Makes public vs technical status explicit |
| Add `Not clinical evidence` sentence to candidate lists | Prevents reclassification drift |
| Add `generated_by`, `input_files`, and `command` blocks to new result markdown | Improves lineage |
| Add `NEEDS_VERIFICATION` marker to claims lacking command output | Prevents false certainty |
| Add `effective_n` caveat to promoter-cluster AlphaGenome claims | Prevents pseudoreplication overclaim |

## Fast Engineering Fixes

| Fix | Why |
|---|---|
| Quiet or gate verbose engine logs in tests | Makes CI output easier to audit |
| Add a script that summarizes dirty tree by category | Prevents accidental broad commits |
| Add validation-suite command to package scripts | Makes falsification gate easier to run |
| Add checksums command compatible with Windows | Current `sha256sum` guidance may not work natively |
| Add result schema validation for `Unified_Atlas` CSVs | Catches silent column drift |

## Fast Scientific Fixes

| Fix | Why |
|---|---|
| Reframe TP53 as "signal requiring matched baseline replication" | RF baseline currently beats SSIM in inspected artifact |
| Explicitly downgrade MPRA to null everywhere | Promoted artifact supports null, not positive validation |
| Require AlphaGenome claims to say auxiliary/model-based | Blocks "independent confirmation" overclaim |
| Require BCL11A docs to say "bridge, not second canonical locus" | Matches existing canon |
| Require all gnomAD absence claims to say "descriptive, not universal constraint" | Matches `CLAUDE.md` |

## Do First

1. Run missing gates.
2. Freeze dirty tree categories.
3. Create claim-drift TODO with exact file/line references.
4. Rerun or explicitly defer validation suite.
5. Only then consider any manuscript/README claim edits.

