# ARCHCODE Claude Code Configuration

This directory contains Claude Code configuration for the ARCHCODE project.

## Structure

```
.claude/
├── settings.json          # Permissions, hooks, project settings
├── agents/                # Custom subagents for specialized tasks
│   └── vus-analyzer.md    # VUS pathogenicity analysis agent
├── commands/              # Custom slash commands
│   ├── compare-alphagenome.md  # Compare ARCHCODE vs AlphaGenome
│   ├── render-figure.md        # Generate publication figures
│   └── validate-blind.md       # Run blind-test validations
├── output-styles/         # Communication styles
│   └── scientific.md      # Scientific/academic style
├── skills/                # Contextual skills (planner/implementer/reviewer/security-check)
└── hooks/                 # Shell scripts for hooks (future)
```

## Quick Start

### Using Subagents

**VUS Analyzer** — Analyze variant pathogenicity:

```
> Use vus-analyzer to analyze VCV000000302
```

The agent will:

1. Extract variant info from HBB_Clinical_Atlas.csv
2. Run ARCHCODE simulation (or use cached)
3. Calculate SSIM
4. Compare with AlphaGenome if available
5. Return structured JSON with interpretation

### Using Slash Commands

**Compare predictions:**

```
/compare-alphagenome hbb
```

**Generate figure:**

```
/render-figure VCV000000302
```

**Run validation:**

```
/validate-blind igh
```

### Using Output Styles

```
/output-style scientific
```

Then all responses will follow scientific communication guidelines (precise terminology, citations, quantitative focus).

## Settings

### Permissions (settings.json)

**Allowed:**

- File operations (Edit, Write, Read)
- Search (Glob, Grep)
- Git operations
- npm/npx/tsx/node commands
- Python scripts

**Denied:**

- Destructive commands (rm -rf, sudo)
- Dangerous chmod operations

### Hooks (settings.json)

**PostToolUse hooks:**

- After **Edit**: Auto-run `npm run typecheck`
- After **Write/Edit**: Auto-format with Prettier

**Stop hooks:**

- Remind to update CLAUDE.md if significant changes

## Adding New Components

### New Subagent

Create `.claude/agents/my-agent.md`:

```markdown
---
name: my-agent
description: What this agent does and when to use it
tools: Read, Write, Bash(npm:*)
model: sonnet
---

# Agent Instructions

Your detailed prompt here...
```

### New Slash Command

Create `.claude/commands/my-command.md`:

```markdown
---
allowed-tools: Bash, Read, Write
argument-hint: [what-to-pass]
description: What this command does
---

# Command Description

Steps:

1. Do this
2. Do that
3. Return result
```

### New Output Style

Create `.claude/output-styles/my-style.md`:

```markdown
---
name: my-style
description: When to use this style
---

# Style Guidelines

- Rule 1
- Rule 2
```

## Integration with ARCHCODE Workflow

### Codex process files

- Root `AGENTS.md` defines plan-first + approval gate + implemented/verified reporting.
- Root `CLAUDE.md` defines scientific integrity (NO phantom refs, NO invisible synthetic, NO "fitted" without code).
- `docs/CODEX_ZERO_HALLUCINATION_GATES.md` defines evidence and security completion gates.
- `docs/templates/IMPLEMENTED_VERIFIED_TEMPLATE.md` is the required completion report format.

### Claim governance (publication-facing)

- **Canonical sources of truth:** `results/validation_canonical_index_2026-03-06.json`, `results/publication_claim_matrix_2026-03-06.json`. Все формулировки для manuscript/препринта сверять с матрицей (ALLOWED / BLOCKED / ALLOWED_WITH_CAVEAT).
- **Legacy narratives:** `docs/internal/LEGACY_CLAIM_HYGIENE_2026-03-06.md` — список файлов, помеченных non-canonical; не использовать для клинических/каузальных claims.

### Typical Session

1. **Start with scientific style:**

   ```
   /output-style scientific
   ```

2. **Analyze variants:**

   ```
   > Use vus-analyzer for batch analysis of variants in results/mysterious_vus.csv
   ```

3. **Compare methods:**

   ```
   /compare-alphagenome hbb
   ```

4. **Generate figures:**

   ```
   /render-figure VCV000000302
   ```

5. **Update documentation** (automatic via Stop hook)

### Batch Processing

For analyzing multiple variants, the VUS analyzer agent will automatically use efficient batch processing (quick-atlas.ts approach) instead of full simulation for each variant.

## Best Practices

1. **Let subagents handle isolation:** Don't manually run simulations for VUS analysis—delegate to vus-analyzer
2. **Use slash commands for repetitive tasks:** Standardized workflows via commands
3. **Scientific style for writeups:** Switch to scientific style when writing methods/results
4. **Check hooks output:** Typecheck errors appear after edits—fix before continuing

## Troubleshooting

**Hooks failing:**

- Check that npm/prettier are in PATH
- Verify timeout is sufficient (15s for typecheck)

**Subagent not auto-invoked:**

- Use explicit invocation: `Use vus-analyzer agent to...`
- Check that description keywords match your prompt

**Slash command not found:**

- Run `/help` to list available commands
- Check file exists in `.claude/commands/`

## Future Enhancements

- [ ] `code-reviewer` agent for security/quality checks
- [ ] `/batch-clinvar` command for analyzing all ClinVar updates
- [ ] `paper-writer` skill for auto-loading when editing .md files
- [ ] Pre-commit hook for running tests before git operations

---

_Created: 2026-02-03 | ARCHCODE v1.1.0_
