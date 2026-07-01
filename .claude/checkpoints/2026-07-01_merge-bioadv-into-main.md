# Checkpoint — merge honest manuscript branch into main

**Date:** 2026-07-01
**Trigger:** git merge into main-tracking branch (checkpoint-guard flagged as risky)

## State before this operation

- Main repo (`C:/Users/sboi/ARCHCODE_review`): on branch `feat/archcode-sv-v1`, uncommitted work
  (ARCHCODE-SV independent validation, H3 ablation, deep-research skill output). NOT touched by this operation.
- Remote `origin/main` HEAD: `799ae1f` (v2.16 bioRxiv manuscript, still shows unqualified AUC=0.977 in README)
- Remote `origin/manuscript/bioadv-submission` HEAD: `a58ffe8` (1 commit ahead of main — honest
  Bioinformatics Advances submission draft with Simpson's Paradox disclosure, within-category AUC=0.52
  disclosed as null result)

## Operation performed

1. Created isolated worktree: `C:/Users/sboi/ARCHCODE_honest_merge` on new local branch
   `integrity/merge-bioadv-readme`, tracking `origin/main`
2. Fast-forward merged `origin/manuscript/bioadv-submission` into this branch (`799ae1f` → `a58ffe8`)
3. Next: will update `README.md` to reflect honest findings (not part of the bioadv branch),
   fix stale `submission_metadata.json` (hardcoded path, old bioRxiv-rejected note)

## Rollback

- Worktree is disposable: `git worktree remove C:/Users/sboi/ARCHCODE_honest_merge --force`
- Local branch `integrity/merge-bioadv-readme` can be deleted: `git branch -D integrity/merge-bioadv-readme`
- **Nothing has been pushed to origin.** `origin/main` is untouched until an explicit `git push` is
  run and confirmed by the user.
- Main working repo (`feat/archcode-sv-v1`, uncommitted SV work) is entirely unaffected — separate worktree.

## Completed (2026-07-01)

1. ✅ README.md updated with honest AUC=0.977 caveat (within-category AUC=0.52, position-only control=0.551)
2. ✅ submission_metadata.json fixed (removed hardcoded `C:/Users/serge/Desktop/...` paths, flagged version staleness, documented unconfirmed Bioinformatics Advances draft status)
3. ✅ `results/p2_hbb_truth/HBB_TRUTH_AUDIT.md` brought into main (previously stranded on feat/archcode-sv-v1)
4. ✅ User confirmed push — pushed `integrity/merge-bioadv-readme` → `origin/main` as fast-forward (799ae1f/a58ffe8 → 1b14805)
5. ✅ Verified via `git fetch origin main`: origin/main HEAD = 1b14805
6. ✅ Worktree removed (`C:/Users/sboi/ARCHCODE_honest_merge`)

## Rollback (if needed later)

`git push origin 799ae1f:main --force` would revert origin/main to the pre-merge state
(NOT recommended without explicit user request — this would re-hide the disclosed finding).
