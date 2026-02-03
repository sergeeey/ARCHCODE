# ARCHCODE Development Workflow

## Git tags (audit milestones)

Tags mark key states of the codebase for audit and reproducibility:

- **`pre-audit`** — State before formal audit response (optional; use if you need to reference the pre-fix code).
- **`post-p0-fixes`** — State after all P0 (blocking) findings from the scientific audit were addressed. See [AUDIT_RESPONSE.md](../AUDIT_RESPONSE.md).

To list tags: `git tag -l`. To create a tag on the current commit: `git tag post-p0-fixes` (and optionally `git push origin post-p0-fixes`).

## Commits and AI-assisted sessions

- **Before a long AI-assisted coding session**: Commit current work so you can revert if the session introduces regressions. Example: `git add -A && git commit -m "chore: checkpoint before refactor"`.
- **After major features or fixes**: Prefer meaningful commit messages and, when appropriate, create or update a tag (e.g. after completing P0 fixes).

## Running tests and validation

- **Build**: `npm run build`
- **Unit tests**: `npm test` (or `npm run test`)
- **Regression (gold standard)**: `npm run test:regression` (or `npm run validate:hbb` as documented in README)
- After refactors (e.g. splitting `LoopExtrusionEngine`), run build and regression tests to ensure behavior is unchanged.

## Project rules for AI (Cursor)

See [.cursorrules](../.cursorrules) in the repository root for ARCHCODE-specific rules (constants, CTCF types, randomness, file size, validation wording). These rules are intended to keep the codebase consistent and scientifically correct when using AI assistants.
