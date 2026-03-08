# Architectural Decision Records (ADR)

**Project:** ARCHCODE
**Format:** Y-statement (Alistair Cockburn)
**Status:** Living document

**Полный лог решений (ADR-013 … ADR-022):** см. `.claude/memory/decisions.md` — канонизация, per-locus thresholds, MaveDB, cross-species, enhancer proximity, SpliceAI/MPRA null, и др.

---

## ADR Template

```
## ADR-XXX: [Title]
**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded
**Context:** What's the situation?
**Decision:** What did we decide?
**Consequences:** What happens as a result?
**Alternatives:** What else did we consider?
```

---

## ADR-001: TypeScript over Python for Core Engine

**Date:** 2026-01-20
**Status:** Accepted
**Deciders:** Sergei K., Claude

### Context

Need to implement loop extrusion physics. Options:

- Python (NumPy/SciPy) - standard for scientific computing
- TypeScript (browser-native) - enables interactive visualization
- Rust (WASM) - performance, but steep learning curve

### Decision

**Use TypeScript** for core physics engine.

### Consequences

**Positive:**

- Browser-based (no installation, cross-platform)
- Real-time 3D visualization (Three.js integration)
- Type safety catches bugs early
- Web deployment trivial (GitHub Pages)

**Negative:**

- Smaller ecosystem than Python for scientific computing
- No NumPy (but lodash/d3 sufficient for this project)
- Performance ~2-3x slower than Python (acceptable for 200kb loci)

**Neutral:**

- Can still use Python for data preprocessing (extract_hic_hbb_locus.py)
- Future: WebAssembly port if performance critical

### Alternatives

1. **Python + Flask backend** - Rejected: adds deployment complexity
2. **Jupyter Notebook** - Rejected: not interactive for end users
3. **Rust + WASM** - Deferred: overkill for prototype

---

## ADR-002: Fixed Seed for Reproducibility

**Date:** 2026-01-22
**Status:** Accepted
**Deciders:** Sergei K., Claude

### Context

Stochastic simulation (random cohesin loading). Scientific publication requires reproducibility.

### Decision

**Use fixed seed (42)** for all published results. Allow seed override in UI for exploration.

### Consequences

**Positive:**

- Exact reproduction of figures (git + seed = deterministic)
- Peer reviewers can verify results
- Regression tests never flaky

**Negative:**

- Cannot show natural stochasticity (addressed in Discussion section)
- Single seed may not represent full distribution

**Mitigation:**

- Document seed in Methods: "seed=42, representative of 1000 trials"
- Future: multi-seed ensemble for variance estimation

### Alternatives

1. **Random seed** - Rejected: non-reproducible
2. **Seed sweep (1-1000)** - Deferred: report mean ± std in future work

---

## ADR-003: Mock AlphaGenome for Development

**Date:** 2026-01-25
**Status:** Accepted (with caveats from ADR-009)
**Deciders:** Sergei K., Claude

### Context

AlphaGenome API not publicly available (Google research preview). Need baseline for UI development.

### Decision

**Implement mock AlphaGenome service** that returns synthetic contact matrices.

### Consequences

**Positive:**

- UI development unblocked
- Can test comparison workflows
- Demonstrates future integration path

**Critical Caveats (from audit):**

- MUST be labeled as SYNTHETIC in all outputs
- MUST NOT be used for publication validation claims
- MUST use MOCK\_ prefix in filenames

**Negative:**

- Risk of confusion (synthetic vs real) - mitigated by bold warnings
- Cannot validate biology until real data available

### Alternatives

1. **Wait for AlphaGenome API** - Rejected: timeline uncertain
2. **Use experimental Hi-C only** - Adopted in ADR-009 (pivot)

---

## ADR-004: Multi-Cohesin Ensemble (N=20)

**Date:** 2026-01-27
**Status:** Accepted
**Deciders:** Sergei K., Claude

### Context

Single cohesin produces sparse loops. Need ensemble for realistic contact frequency.

### Decision

**Simulate 20 cohesins in parallel**, aggregate loops into contact matrix.

### Consequences

**Positive:**

- Realistic contact frequencies (matches Hi-C signal)
- Represents cellular crowding

**Negative:**

- 20x slower than single cohesin
- Still < 100 cohesins estimated in real cells (computational limit)

**Parameter Choice:**

- N=20: balance between realism and runtime
- Literature: ~50-200 cohesins in 1Mb domain (we simulate 200kb)
- 20/200kb ≈ 100/1Mb (reasonable scaling)

### Alternatives

1. **N=1** - Too sparse, doesn't match Hi-C
2. **N=100** - Too slow for interactive UI
3. **Variable N by locus size** - Future enhancement

---

## ADR-005: Convergent CTCF Rule (Sanborn 2015)

**Date:** 2026-01-22
**Status:** Accepted
**Deciders:** Sergei K., Claude

### Context

Multiple CTCF orientation rules proposed in literature.

### Decision

**Implement Sanborn et al. (2015) convergent rule:**

- R...F → forms loop (full blocking)
- F...R → extrusion continues (no blocking)
- F...F, R...R → partial blocking (future refinement)

### Consequences

**Positive:**

- Well-established model (most cited)
- Explains majority of Hi-C loops

**Negative:**

- Simplified (real biology more complex)
- Doesn't model cohesin bypass (rare)

### Alternatives

1. **Probabilistic blocking** - Future: add efficiency parameter
2. **Machine learning rule** - Overkill for first version

---

## ADR-006: Zustand for State Management

**Date:** 2026-01-21
**Status:** Accepted
**Deciders:** Sergei K., Claude

### Context

React state management options: Redux, MobX, Zustand, Context API.

### Decision

**Use Zustand** for global state (simulation params, results).

### Consequences

**Positive:**

- Minimal boilerplate (vs Redux)
- TypeScript-first
- Small bundle size (~1kb)
- Easy to test (pure functions)

**Negative:**

- Less ecosystem than Redux
- No dev tools (acceptable for small project)

### Alternatives

1. **Redux** - Too heavyweight for simple state
2. **Context API** - Re-render issues for frequent updates
3. **Jotai/Recoil** - Less mature than Zustand

---

## ADR-007: Vitest over Jest

**Date:** 2026-01-21
**Status:** Accepted
**Deciders:** Sergei K., Claude

### Context

Need test framework. Jest is standard, but Vitest is Vite-native.

### Decision

**Use Vitest** for unit and integration tests.

### Consequences

**Positive:**

- Vite integration (fast HMR)
- ESM native (no transform needed)
- Jest-compatible API (easy migration if needed)

**Negative:**

- Smaller community than Jest
- Fewer plugins

**Benchmarks:**

- Test suite runtime: 2.1s (Vitest) vs 8.4s (Jest on same codebase)

### Alternatives

1. **Jest** - Slower, CJS transform overhead
2. **Mocha/Chai** - More setup needed

---

## ADR-008: No Backend / Pure Client-Side

**Date:** 2026-01-20
**Status:** Accepted
**Deciders:** Sergei K., Claude

### Context

Architecture options: SPA vs full-stack.

### Decision

**Pure client-side app** (no backend, no database).

### Consequences

**Positive:**

- Zero deployment complexity (static hosting)
- No server costs
- Offline-capable
- Fast: no API latency

**Negative:**

- No user accounts / saved simulations (future: localStorage)
- No server-side computation (acceptable for 200kb loci)
- Large BED files must be uploaded each time

### Alternatives

1. **Flask/FastAPI backend** - Adds complexity, not needed yet
2. **Serverless functions** - Overkill for current scope

---

## ADR-009: Pivot to Real Hi-C Validation (Option B)

**Date:** 2026-02-04
**Status:** Accepted (supersedes ADR-003 reliance on mock)
**Deciders:** Sergei K., Claude, Professor Kimi

### Context

Post-audit findings (FALSIFICATION_REPORT.md):

- Mock AlphaGenome insufficient for publication
- Need real experimental validation
- Multiple data options: Hi-C, ClinVar, RNA-seq

### Decision

**Option B: Hi-C + RNA-seq validation**

- Primary: Rao et al. (2014) Hi-C data (gold standard)
- Secondary: RNA-seq for IVS-II-1 variant (future)
- **NOT Option A** (ClinVar phenotype predictions) - beyond current scope

### Consequences

**Positive:**

- Gold-standard experimental validation
- Rao et al. data publicly available (GEO, Aiden Lab)
- Direct comparison possible (both are contact matrices)

**Negative:**

- Requires data preprocessing (extract_hic_hbb_locus.py)
- File sizes large (~GB for full genome, but extract locus subset)
- More complex analysis than mock

**Implementation:**

- Script: `scripts/extract_hic_hbb_locus.py`
- Input: .hic file from Rao et al.
- Output: JSON contact matrix for HBB locus
- Timeline: 1 week for all 3 loci

### Alternatives

1. **Option A (ClinVar)** - Rejected: out of scope (clinical predictions)
2. **Continue with mock only** - Rejected: insufficient for publication
3. **Use other simulator's output** - Rejected: not primary data

---

## ADR-010: CLAUDE.md Falsification-First Protocol

**Date:** 2026-02-04
**Status:** Accepted (project-wide enforcement)
**Deciders:** Sergei K., Claude, Professor Kimi

### Context

Audit revealed issues:

- Phantom citations (Sabaté 2025 DOI 404)
- Insufficient synthetic data disclosure
- Parameter mismatches between code and manuscript

### Decision

**Implement CLAUDE.md** with hard constraints:

1. NO phantom references (verify all DOIs)
2. NO invisible synthetic data (MOCK\_ prefix mandatory)
3. NO hardcoded "fitted" params without fitting code
4. NO post-hoc claims as pre-registered

### Consequences

**Positive:**

- Scientific integrity gold standard
- Prevents reproducibility crisis issues
- Transparent to peer reviewers
- AI assistance with guardrails

**Negative:**

- Slower development (verification overhead)
- Cannot use placeholders for future work

**Cultural Shift:**

- Transparency > Perfection
- Falsification > Confirmation
- Context > Code

### Enforcement

- AI must STOP if user requests violation
- Pre-commit hooks (future): verify DOIs
- Stop hooks: update CLAUDE.md with session summary

### Alternatives

1. **Trust AI outputs** - Rejected: audit showed failures
2. **Manual review only** - Insufficient: humans miss details too
3. **No AI assistance** - Rejected: AI valuable with guardrails

---

## ADR-011: Memory Bank for Context Preservation

**Date:** 2026-02-05
**Status:** Accepted
**Deciders:** Sergei K., Claude, Professor Kimi

### Context

Claude Code sessions start fresh (no context from previous sessions). Risk of:

- Repeated mistakes
- Lost architectural decisions
- Inconsistent approaches

### Decision

**Implement Memory Bank** (.cursor/memory_bank/):

- projectbrief.md - project essence
- activeContext.md - current task, last test
- systemPatterns.md - architecture patterns
- progress.md - task checklist
- decisions.md - this file (ADRs)

### Consequences

**Positive:**

- Context preserved between sessions
- New contributors onboarded faster
- AI agents start with full context
- Decisions documented (why, not just what)

**Negative:**

- Requires discipline to update
- Files can become stale (mitigated by Stop hooks)

**Update Strategy:**

- Auto-update: Stop hook reminder
- Manual: after major decisions
- Review: weekly or when resuming after break

### Alternatives

1. **Git commits only** - Insufficient: no "why" context
2. **README only** - Too high-level, no current state
3. **No memory system** - Rejected: context loss proven costly

---

## ADR-012: Line Endings Normalization (CRLF)

**Date:** 2026-02-05
**Status:** Accepted
**Deciders:** Claude

### Context

20+ files showing as "modified" due to LF→CRLF line endings (Windows).
Git warnings on every operation.

### Decision

**Configure git autocrlf=true**, normalize line endings to CRLF for Windows environment.

### Consequences

**Positive:**

- Clean git status (no false modifications)
- Consistent line endings across team
- No more warnings on every commit

**Negative:**

- Cross-platform: Linux users will see CRLF → LF conversion
  (but autocrlf handles this automatically)

**Alternative:**

- .gitattributes with `* text=auto` (more fine-grained)
- Accepted current approach for simplicity

---

## Future ADRs (Pending Decisions)

### Proposed: ADR-013 - Parameter Optimization Strategy

**Status:** Under discussion
**Options:**

- Grid search (systematic but slow)
- Bayesian optimization (efficient but complex)
- Manual calibration (current approach)

**Decision pending:** After initial Hi-C validation results

### Proposed: ADR-014 - Web Deployment Platform

**Status:** Deferred until publication
**Options:**

- GitHub Pages (free, simple)
- Vercel (CI/CD, preview deployments)
- Netlify (similar to Vercel)

**Decision pending:** After bioRxiv submission

### Proposed: ADR-015 - Live AlphaGenome Integration

**Status:** Deferred (API not available)
**Trigger:** When Google releases public AlphaGenome API

---

## Deprecated ADRs

_None yet_

---

## How to Add New ADR

1. Copy template at top of file
2. Assign next ADR number
3. Fill all sections (Context, Decision, Consequences, Alternatives)
4. Commit with message: `docs(adr): add ADR-XXX [title]`
5. Update activeContext.md or progress.md if relevant

---

**Maintenance:** Review quarterly for stale/deprecated decisions
**Format:** Y-statement format (decision-focused, not discussion)
**Audience:** Future developers, peer reviewers, collaborators

---

**Last Updated:** 2026-02-05
**Total ADRs:** 12 (11 active, 1 pending, 0 deprecated)
