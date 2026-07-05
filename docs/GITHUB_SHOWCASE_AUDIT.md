# GitHub Showcase Audit — sergeeey/ARCHCODE

**Date:** 2026-07-05
**Auditor:** github-showcase-architect skill, read-only pass (no repo writes performed)

## 1. Executive Verdict

Current: **5.5/10** → Target: **8/10**. Top 3 blockers:

1. **Branch drift, not just doc drift.** The GitHub-visible `main` branch and the local working
   branch (`experiment/spectral-collapse-pilot`) have **materially different READMEs** — different
   variant counts (63,153/13 loci on `main` vs 26,225/9 loci locally), different subtitle framing,
   and `main` has no mention of the new category-confound preprint (rs-10254695) at all, because
   that work was never merged to `main`. A visitor landing on the repo today sees an older,
   partially-superseded story.
2. **Repo topics are empty** (`"topics": []`). Zero discoverability tags. This is the literal thing
   you asked to fix — quick win.
3. **Repo description is stale.** Says arXiv "pending (B9P837)" — per project memory, that
   endorsement was refused in May. No mention of rs-10254695 either.

## 2. Current Score / Target Score

| Dimension | Current | Target | Why |
|---|---|---|---|
| First impression | 6/10 | 8/10 | Hero section is strong on the local README; `main` shows an older, more overclaiming variant |
| Truthfulness | 7/10 | 9/10 | Both README versions actually DO disclose the falsification caveat — good — but `main`'s subtitle ("...for variant pathogenicity prediction") contradicts its own body text ("Discovery Engine, not a Prediction Tool") |
| Reproducibility | 6/10 | 8/10 | Scripts/data referenced in local README's newest work (`analysis/fig_category_confound.py` etc.) live only on `backup/snapshot-20260706`, not `main` — a reader following `main`'s README cannot find them |
| Engineering hygiene | 7/10 | 8/10 | 3 CI workflows exist and run; no `CITATION.cff` (gap for a research repo with 2 preprints + pending arXiv) |
| Visual clarity | 6/10 | 7/10 | Badges present, one figure embedded; no social preview image |
| Documentation structure | 6/10 | 8/10 | Good section anchors, but "which branch has what" is undocumented anywhere |
| Public-safety readiness | 8/10 | 8/10 | Already public, MIT-licensed, no obvious secrets in tracked files (not exhaustively re-scanned this pass) |
| Portfolio value | 6/10 | 8/10 | Falsification-first framing is a genuine differentiator — most repos hide this, ARCHCODE's honesty is the actual selling point |
| Reviewer confidence | 6/10 | 8/10 | A rigorous reader who diffs `main` vs the paper repo's actual scripts will notice the gap immediately |

## 3. Best Positioning Sentence

> "This repository is a **falsification-first 3D-chromatin variant scoring toolkit** that helps
> **computational biologists and reviewers** achieve **an honest read on whether structural
> simulation adds signal beyond variant category** by **running open validation and category-matched
> control tests that a reader can reproduce**, while explicitly avoiding **any claim that the current
> model predicts pathogenicity beyond category composition**."

This is the real differentiator: most repos market capability; this one is notable for
systematically disproving its own headline claim in public. That is rarer and more trust-building
than another "state-of-the-art predictor" repo.

## 4. Audience-Specific First Impression

Primary audience: **research collaborator / reviewer** (someone deciding whether to cite, extend,
or collaborate on this work).

- **30 sec:** repo description + topics + README hero should immediately say: (a) what this is
  (3D-chromatin variant scoring framework), (b) that it has TWO honest published outputs — a
  taxonomy paper (rs-9090074) and a category-confound negative-result paper (rs-10254695) — and
  (c) that it does NOT claim to be a working pathogenicity predictor.
- **3 min trust:** the falsification caveat, visible on both READMEs, is the trust anchor — keep it
  prominent, don't bury it.
- **10 min run:** currently broken for the newest analysis — the category-confound scripts and data
  live on `backup/snapshot-20260706`, not `main`. A 10-minute-run reader following `main`'s README
  will not find `analysis/fig_category_confound.py`.

## 5. Recommended Repo Description (GitHub "About" field)

Replace current:
> "Physics-based 3D chromatin loop extrusion framework for regulatory variant interpretation.
> Research Square rs-9090074 | arXiv q-bio.GN pending (B9P837) | Zenodo v2.17"

With:
> "Falsification-first 3D-chromatin variant scoring framework — honestly tested against category
> confounding across 9 disease loci. Research Square rs-9090074 (taxonomy) + rs-10254695
> (category-confound negative result) | Zenodo v2.17"

Rationale: drops the stale "arXiv pending" claim (per memory, that endorsement was refused),
adds the new preprint, and leads with the honesty framing rather than a capability claim.

## 6. Recommended Topics (GitHub repo topics = the "hashtags" asked for)

```
bioinformatics
computational-biology
genomics
chromatin
variant-interpretation
clinvar
3d-genome
loop-extrusion
falsifiability
reproducible-research
python
typescript
```

12 topics (GitHub max is 20). Chosen for: field discoverability (bioinformatics, genomics,
computational-biology), specific technique (chromatin, 3d-genome, loop-extrusion), what it's
tested against (clinvar, variant-interpretation), and what makes it distinctive
(falsifiability, reproducible-research) — plus the two languages actually in the stack.

## 7. README Sync Plan (the real fix, bigger than topics)

Three options, ranked by effort:

**A — Minimal (5 min):** Add one line near the top of `main`'s README pointing to the new preprint
and to the branch with the newest reproducible code:
> "Latest analysis (category-confound negative result, rs-10254695): see
> [`backup/snapshot-20260706`](https://github.com/sergeeey/ARCHCODE/tree/backup/snapshot-20260706)."

**B — Proper (30-60 min):** Merge the honest, updated local README (currently only on
`experiment/spectral-collapse-pilot`, not pushed due to the large-file history problem) onto `main`,
either by pushing just the README file to `main` directly, or by finally running `git filter-repo`
to clean the working branch's history and merge properly. Also add the rs-10254695 section.

**C — Full (2+ hours):** Run `git filter-repo` to strip the >100MB files from
`experiment/spectral-collapse-pilot`'s history (already identified culprits: `AlphaMissense_hg38.tsv.gz`
637MB, DepMap CRISPR/expression files), merge cleanly into `main`, retire the orphan
`backup/snapshot-*` branches once their content is folded in properly.

**Recommendation: do A now (quick, safe, no history rewrite), park B/C** — the user is stepping back
from ARCHCODE after this session; a full history rewrite is not worth doing today.

## 8. Engineering Hygiene Findings

| Check | Status |
|---|---|
| CI exists | ✅ 3 workflows: `publication-integrity.yml`, `secrets-history-scan.yml`, `security-gates.yml` |
| LICENSE | ✅ MIT, file present |
| CITATION.cff | ❌ Missing — gap for a repo backing 2 preprints |
| Git tags | ✅ 5 tags (v0.1-skeleton → v4.0-submission-ready) — none post-date the new paper |
| .gitignore | ✅ 147 lines, includes the large-data patterns added 2026-07 |
| README length | 417 lines (local) — reasonable, not bloated |

## 9. Public-Safety Findings

Already public. No new sensitive-file exposure identified in this pass (not re-run from scratch —
prior sessions already did a secrets/large-file cleanup this week). No action needed here.

## 10. Overclaim Gate

| Claim | Marker | Note |
|---|---|---|
| `main` subtitle: "...for variant pathogenicity prediction" | `[UNSUPPORTED]` — contradicted by same doc's own caveat and later "Discovery Engine, not a Prediction Tool" line | Rewrite subtitle to match the honest framing already used lower in the same file |
| Local README subtitle: "falsification-first validation suite for honest evaluation" | `[VERIFIED-REAL]` | Keep — matches actual repo content and both preprints |
| "27 pearls" / "641 VUS" (main) | `[VERIFIED-REAL]`, but now **incomplete** — doesn't reflect that the pearl/Class-B claim was further falsified 2026-07-04 | Needs a short update note, not a rewrite |

## 11. 30-Minute Fixes (do these now)

1. Update repo description (Section 5 text) — via GitHub web UI "About" gear icon, or `gh repo edit`
   once `gh auth` is fixed (currently returns `401 Bad credentials` in this environment).
2. Add the 12 topics (Section 6) — same UI, "About" → topics field.
3. Add Option A's one-line pointer to `main`'s README, linking to `backup/snapshot-20260706`.
4. Fix `main`'s contradictory subtitle (Section 10).

## 12. Before-Next-Public-Update Checklist

- [ ] Repo description updated
- [ ] Topics added
- [ ] `main` README references the new preprint + branch with runnable code
- [ ] Subtitle contradiction fixed
- [ ] (Optional, not urgent) CITATION.cff added
- [ ] (Optional, not urgent) full branch consolidation via git filter-repo
