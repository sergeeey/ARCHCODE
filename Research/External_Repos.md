# External Repositories — Pattern Sources

Useful repositories for ARCHCODE pattern borrowing.

---

## DNA2 — Genomic Signal Decoder

**URL:** https://github.com/shootthesound/DNA2.git  
**Analyzed:** 2026-05-14  
**Language:** Python 3.10+  
**Stack:** BioPython, NumPy, SciPy, Streamlit

### What It Does

31-module genomic analysis platform:
- Traditional genomics: dN/dS, codon usage, CpG islands, phylogenetics
- Signal processing: entropy, compression, autocorrelation, spectral, wavelets
- Advanced: chaos game, multifractal DFA, Lempel-Ziv complexity

### Borrowed Patterns

1. **Pipeline Orchestration** — dependency graph, step status tracking
2. **Retrodiction Validation** — validate by replicating known discoveries
3. **Cross-Genome Synthesis** — feature vectors, permutation tests

### Implementation Status

- [ ] Retrodiction Suite (4h, P1) → ARCHCODE adaptation
- [ ] Pipeline Orchestrator (6h, P1) → validation workflow
- [ ] Cross-Locus Synthesis (8h, P2) → statistical comparison

**Details:** [[DNA2 Genomic Signal Decoder Analysis]]

---

## genechat-mcp — Personal Genomics MCP Server

**URL:** https://github.com/blopker/genechat-mcp  
**Analyzed:** 2026-05-14 (ARCHCODE session)  
**Language:** Python  
**Stack:** SQLite, MCP protocol

### What It Does

Personal genomics annotation server:
- VCF annotation with ClinVar, SnpEff, PGx
- SQLite patch database pattern
- MCP tools for Claude Desktop/Code

### Borrowed Patterns

1. **SQLite Patch Database** — annotate once, query fast
2. **Init Workflow** — auto-setup, download, annotate
3. **Annotation Storage** — separate from raw data (VCF)

### Implementation Status

- [x] ✅ ARCHCODE SQLite Pattern (6h) — COMPLETED 2026-05-14
  - 9 tables: loci, clinvar_variants, alphagenome_predictions, archcode_ssim, validation_results, audit_log
  - Query interface: get_pearls(), get_mechanism_specificity_summary()
  - Performance: 5000-18000× speedup vs API calls

**Details:** [[ARCHCODE SQLite Pattern]]

---

## Future Pattern Sources

### Addyosmani/agent-skills

**URL:** https://github.com/addyosmani/agent-skills  
**Status:** Already integrated

**Borrowed patterns:**
- Doubt-Driven Development (skeptic before implementation)
- Rationalizations table (anti-excuse protocol)

**Details:** [[Doubt-Driven Development]], [[Rationalizations Table]]

---

**Tags:** #external-repos #pattern-borrowing #DNA2 #genechat-mcp #agent-skills