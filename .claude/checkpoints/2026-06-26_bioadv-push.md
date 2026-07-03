# Checkpoint: bioadv-submission push fix

**Date:** 2026-06-26
**Branch before:** experiment/spectral-collapse-pilot (c852232)
**Branch now:** manuscript/bioadv-submission (from origin/main)
**Stash:** WIP on experiment/spectral-collapse-pilot saved

## Task
Push only manuscript files (7 text files, ~50KB) to avoid pushing 1.5GB data files.

## Rollback
```
git checkout experiment/spectral-collapse-pilot
git stash pop
git branch -D manuscript/bioadv-submission
```

## Key commits to include
- 703e398: fix(manuscript): abstract/body mismatch + headline stats
- c852232: docs(manuscript): cover letter + references + competitor table

## Files to add (text only, no PDFs)
- manuscript/main.typ
- manuscript/abstract_content.typ
- manuscript/body_content.typ
- manuscript/taxonomy_paper/body_content.typ
- manuscript/taxonomy_paper/main.typ
- manuscript/taxonomy_paper/template.typ
- manuscript/references.typ
- manuscript/cover_letter_bioinformatics_advances.md
