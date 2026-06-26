# ARCHCODE Master Plan — Falsification-First Reboot (2026-06-05)

**Author of plan:** user (Sergey) · **Executed/refined by:** Claude (Opus 4.8)
**Prime goal:** turn ARCHCODE from "VUS tool with a loud pathogenicity claim" into a
**falsification-first platform for tissue-specific 3D chromatin structural fragility**.

> Allowed thesis: *"ARCHCODE detects tissue-specific 3D chromatin structural fragility
> and uses falsification gates to prioritize regulatory-variant hypotheses."*
> Forbidden thesis: *"ARCHCODE predicts pathogenicity."* (falsified — see below)

---

## 0. What changed after grounding the plan against the real repo

The plan was correct in direction and **the evidence is even stronger than it assumed**.
Verified this session (read-only):

| Plan assumption | Verified status | Evidence |
|---|---|---|
| Engine works (engineering) | ✅ true | audit §2.1; runtime verified |
| Paper 2 almost ready (9/10) | ⚠️ **partially** — the submission package on disk is the *old loud paper*, not a narrow Paper 2 | `results/p1_paper2/PAPER2_READINESS_AUDIT.md` |
| BCL11A failed as 2nd locus | ✅ true | `3/3` + `6/6` not_observed_graphql |
| Cohen d=2.13 must be downgraded | ✅ **and then some** — it's a category artifact | `results/p2_hbb_truth/` |
| LSSIM may add residual signal | ❌ **falsified on HBB** — adds nothing over category; is a CTCF-distance proxy | `results/p3_confound/` |
| Falsification gate is the real strength | ✅ true | this whole exercise |

**Net:** the strongest honest result is a *negative* one, cleanly demonstrated. That is
publishable as a methods/cautionary + framework paper, and it protects the author from
a far worse outcome (post-publication retraction of an overclaim).

---

## DONE this session (executable, non-destructive)

| Etap | Deliverable | Verdict |
|---|---|---|
| 0 | `results/p0_governance/RULES.md` — frozen rails | ✅ |
| 1 | `results/p1_paper2/PAPER2_READINESS_AUDIT.md` — metadata audit + scope decision | ✅ (1 user decision pending) |
| 2 | `results/p2_hbb_truth/` — HBB truth audit (d −2.67 → −0.34 stratified; within-cat AUC 0.52) | ✅ |
| 3 | `results/p3_confound/` — K1 & K2 both fire; LSSIM ≈ f(category + CTCF-dist) | ✅ |

## Honest claim ledger (use these, retire the rest)

- ✅ **GO** — "LSSIM encodes a consequence-severity ordering by construction."
- ✅ **GO** — "Matched-category controls show LSSIM does not discriminate pathogenic
  vs benign (AUC 0.52–0.57); the headline AUC 0.977 is a category-distribution effect."
- ✅ **GO** — "LSSIM ≈ f(consequence category + distance-to-CTCF); no independent 3D
  signal on analytical HBB maps."
- ✅ **GO** — engine engineering validation (0.77 ms, stable loops, TAD boundaries).
- ❌ **NO-GO** — "ARCHCODE predicts pathogenicity."
- ❌ **NO-GO** — BCL11A as positive locus; 641 VUS "reclassified"; AlphaGenome-synthetic.

---

## Remaining phases — HONEST gates (NOT executable autonomously without external data)

These require data acquisition / decisions I cannot fabricate. Each is specified so it
can be run when its input exists. Marking them done now would be validation theater.

### Etap 1 (finish) — Paper 2 submit-ready
- **Blocker:** scope decision A/B/C (see readiness audit). **User decision required.**
- Then: canonicalize author name, fill ORCID, set article type/venue, verify supplement
  paths, add AI-use disclosure, skeptic-pass the abstract.

### Etap 4 — cherry-pick mechanistic-taxonomy experiments (P0/P1)
- EXP-003 tissue-mismatch controls, EXP-004 threshold/parameter sensitivity (P0);
  EXP-001/002 ablation + leave-one-out, EXP-008 CRISPRi benchmark (P1).
- **Gate:** cherry-pick only; NO full merge; exclude AlphaGenome-synthetic, BCL11A,
  three-layer-canon-if-conflicting, stress-biology branch.
- **Runnable now?** Partly — EXP-004 threshold sensitivity can reuse existing atlas;
  EXP-003 needs tissue-specific feature sets. Defer EXP-008 (needs CRISPRi data).

### Etap 5 — find a second CLEAN regulatory locus (replace BCL11A)
- Candidates: GATA1, HBA1/HBA2, other erythroid regulatory locus, Pcdh, Sox2.
  (Repo already has `data/clinvar_gata1_variants.csv`, `data/hba1_variants.csv`.)
- **Frozen gate (mandatory before any run):** source audit → build/coordinate sanity →
  category baseline → position-matched controls → gnomAD interpretation audit.
- **Kill criterion K3:** a locus failing the gate is NOT promoted (BCL11A precedent).
- **Critical lesson from Etap 2/3:** the locus must have a **non-degenerate
  category×label matrix** (both classes present within categories), or it will hit the
  same "matched test impossible" wall as HBB. Screen candidates on this FIRST.
- **PRE-GATE DONE (2026-06-05):** GATA1 and HBA1 both passed the degeneracy screen.
- **GATA1 FULL GATE RUN (2026-06-05): `FAIL_PROXY_ONLY`** — K3 fires.
  `results/p1_gata1_matched/GATA1_DECISION.md`. Two independent failure reasons:
  (1) **Tissue mismatch** — atlas built on K562 CTCF/H3K27ac; GATA1 is erythroid, K562 is wrong tissue.
  (2) **No regulatory spread** — all 183 variants in a 3,117 bp coding window; structural context is identical.
  (3) **Wrong-direction within missense** (n=34 path / 25 benign): AUC **0.464**, Cliff δ=+0.072 (pathogenic LSSIM HIGHER than benign). Synonymous AUC **0.314** (below chance).
  (4) K2 fires: category alone AUC 0.8584 > category+LSSIM 0.8572 (LSSIM degrades model).
- **HBA1 quick-screen (2026-06-05): same flags** — K562 tissue source, LSSIM delta=0.0023 (even smaller), 0 pearls.
  Full gate not needed; expect identical failure mode.
- **GATA1 = NOT promoted to positive locus (K3 fires).** HBA1 = same verdict expected.

### Etap 6 — real validation layer (computational prototype → research-grade)
- Real Hi-C import (.cool/.mcool), HiCRep / GenomeDISCO, P(s), insulation score,
  CRISPR perturbation validation.
- **This is where the residual-signal hypothesis gets its only fair re-test** (analytical
  maps falsified it; measured maps might differ). `[NEEDS-REAL-DATA]`.
- ~Annual roadmap item.

---

## Success levels (from the plan, with current status)

- **Level 1 (near):** Paper 2 submit-ready · Paper 3 honest feasibility · HBB
  category-severity report ✅ · Cohen d removed from central claim ✅.
  → **2 of 4 done; Paper 2 blocked on scope decision; Paper 3 framing ready.**
- **Level 2 (strong computational paper):** residual signal over category/position →
  **currently falsified on HBB**; needs Etap 5 (clean locus) + Etap 6 (real Hi-C).
- **Level 3 (high-impact):** wet-lab / CRISPR + real Hi-C + multi-locus → long-horizon.
- **Realistic venues w/o wet-lab:** Genome Biology / PLoS Genetics / PLoS Comp Biol /
  Bioinformatics (as a methods + falsification-framework paper). With wet-lab: Nat Genet territory.

## One-line summary

> Close Paper 2 as an honest, narrow proof-of-concept (no pathogenicity claim); rebuild
> Paper 3 as a falsification-first framework whose centerpiece is *how a loud HBB claim
> is correctly killed by matched controls* — then earn any positive claim only by
> passing a clean second locus (Etap 5) and real Hi-C/CRISPR (Etap 6).
