# Etap 0 — Frozen Governance Rules (ARCHCODE Falsification-First Reboot)

**Date:** 2026-06-05
**Authority:** These rules govern all ARCHCODE work under the 2026-06-05 plan.
They sit ON TOP of the project `CLAUDE.md` (Scientific Integrity Protocol) and the
global falsification-ladder / integrity / skeptic rules. On conflict, the STRICTER
rule wins.

---

## A. Hard "do not touch" list (irreversibility guard)

1. **Do not overwrite canonical JSON / atlas files in place.** Canonical artifacts
   (`data/*canonical*`, `data/archcode_hbb_*`, `results/HBB_Unified_Atlas*.csv`,
   `results/*canonical_status*`) are READ-ONLY inputs. New computation writes to
   `results/p0_*`, `results/p1_*`, `results/p2_*`, `results/p3_*` only.
2. **Do not overwrite the HBB atlas.** Re-derivations go to a new dated filename.
3. **Do not modify the submitted/preprint manuscript** (`manuscript/`,
   `ARCHCODE_Preprint*.pdf`, Zenodo PDF) except via an explicit, separate **v3
   proposal** reviewed before any edit.
4. **Do not delete** `null_results/`, audit reports, or `FALSIFICATION_REPORT.md`.

## B. Hard "do not claim" list (overclaim guard)

5. **Do not claim "ARCHCODE predicts pathogenicity."** Falsified for HBB (see
   `results/p2_hbb_truth/HBB_TRUTH_AUDIT.md`): the AUC 0.977 / Cohen d effect is a
   category-distribution artifact (stratified d ≈ −0.34; within-category AUC ≈ 0.52).
6. **Do not use BCL11A as a second positive locus.** Failed: primary subset
   `3/3 not_observed_graphql`, controls `6/6 not_observed_graphql`.
7. **Do not present AlphaGenome synthetic/mock output as validation.** The repo
   contains three contradictory AlphaGenome states (excluded / confirms / REAL) —
   until resolved with a real API rerun, AlphaGenome = `[NEEDS-REAL-DATA]`.
8. **Do not inflate the 641 "pearl-like" VUS into "reclassified".** They are
   hypothesis-generating candidates, `NO_GO / UNVERIFIED`.
9. **Do not claim "pre-registered" / "blind"** for anything whose parameters and
   results were committed together (no timestamp proof exists).

## C. Positive framing (what we ARE allowed to claim)

10. Allowed headline: *"ARCHCODE detects tissue-specific 3D chromatin structural
    fragility and uses falsification gates to prioritize regulatory-variant
    hypotheses."* Engineering-validated engine + honest descriptive structural layer.
11. Allowed HBB claim: *"LSSIM encodes a consequence-severity ordering by
    construction; matched-category controls show no independent discrimination."*
    (HBB as the worked falsification example, not as proof.)

## D. Process rules

12. **Two tracks stay separate.** Paper 2 (narrow, defensible) must NOT depend on
    Paper 3 / BCL11A / AlphaGenome / wet-lab. No Paper 3 risk claims bleed into Paper 2.
13. **Every new result folder carries a `claim.md`-style header**: question type,
    falsifiable claim, check, caveat / "what this does NOT mean".
14. **Skeptic gate before any ≥90% / "all passed" / round-number claim.**
15. **Real vs synthetic split is mandatory.** Validation claims need `[VERIFIED-REAL]`
    with ≥3 cited real sources; synthetic = `[VERIFIED-SYNTHETIC]` (unit test only).
16. **No mass multi-locus run without a frozen gate** (source audit → build/coords
    sanity → category baseline → position-matched controls → gnomAD interpretation).

## E. Kill criteria (pre-registered for the open questions)

- **K1 (regulatory-distance triviality):** if LSSIM<0.95 coincides >85–90% with
  "near CTCF/enhancer", the structural claim is a regulatory-distance proxy → trivial.
- **K2 (no residual value):** if Model C (distances+category+LSSIM) ≈ Model B
  (distances+category), LSSIM adds nothing → drop the "residual 3D information" claim.
- **K3 (second locus):** a candidate locus that fails the frozen gate is NOT promoted
  to positive evidence (BCL11A precedent).

---

*This file is the contract. Violations are logged, not silently fixed.*
