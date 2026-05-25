# ARCHCODE Number Provenance

**Single source of truth for all numerical claims in the project.**

**Last verified:** 2026-05-25 (commit `a3bbef2` — P0 audit)
**Script:** `scripts/count_unique_variants.py`
**Output:** `results/dataset_count_verification.txt`

---

## 🎯 Default Public Identity (use these everywhere)

| Quantity | Value | Source | When to use |
|----------|-------|--------|-------------|
| **Core variants** | **26,225** | 9 loci, deduplicated | README, manuscript, abstract, figures, all public materials |
| **Core loci** | **9** | HBB, TP53, BRCA1, MLH1, TERT, GJB2, CFTR, GATA1, PTEN | Public materials |
| **HBB pilot** | **15 path + 15 ben** | AlphaGenome batch | Power analysis, pilot reporting |
| **HBB pearls** | **25** (canonical), **27** (broader technical) | Q2b set | Use 25 in public; clarify "27 in broader technical definition" |

---

## 🟡 Technical Full-Scope (use only in technical/legacy contexts)

These numbers exist in archived documents and `.claude/agents/vus-analyzer.md`. **Do NOT use in public materials** without explicit context label.

| Quantity | Value | Definition | Why excluded from public |
|----------|-------|------------|--------------------------|
| Legacy 9-loci raw count | 30,318 | Pre-deduplication ClinVar fetch | Replaced by 26,225 after dedup verification |
| 13 loci expansion | 32,201 | 9 core + 4 expansion (GATA1, PTEN, etc.) | Expansion loci have sparse data; not all tested |
| VUS subset | 30,952 | Variants of Uncertain Significance only | Subset, not total |
| Full technical scope | 63,153 | 32,201 + 30,952 (with overlap accounting) | Composite of legacy expansion + VUS |
| Pearl-like candidates | 641 | Broader pattern-match before quality filter | Pre-curation count |

**Policy (from `PROJECT_CANON.md:108`):**
> "32,201, 30,952, 63,153, and 641 pearl-like are not part of the default public identity. They belong in technical full-scope or legacy material only."

---

## 📍 Reconciliation: 30,318 → 26,225

| Step | Count | Action |
|------|-------|--------|
| Raw ClinVar fetch (9 loci, March 2026) | 30,318 | Initial download from ClinVar API |
| Deduplication (P0 audit, May 2026) | 26,225 | Removed duplicates: same variant from multiple submitters, multi-ClinVar IDs |
| Verified count (commit `a3bbef2`) | **26,225** | Used in manuscript v2.18 + all current claims |

**Difference:** 4,093 duplicates removed (13.5% of raw fetch).
**Reproduction:** `python scripts/count_unique_variants.py`

---

## 📍 Reconciliation: 25 vs 27 HBB pearls

| Definition | Count | Used in |
|------------|-------|---------|
| **Canonical (Q2b)** | **25** | Public papers, abstract, conclusions |
| Broader technical (Q2b extended) | 27 | Technical appendix, supplementary, code comments |

**Difference:** 2 variants with borderline LSSIM scores (just above/below the strict threshold).
**Recommended public language:** "25 high-confidence pearls (27 in broader technical definition)"

---

## 🚨 Hard Rules

1. **Public materials (README, manuscript, abstract, figures, Zenodo metadata, BibTeX):**
   - MUST use 26,225 for variant count
   - MUST use 25 for pearls (with optional "27 in broader technical definition" clarification)

2. **Technical/legacy materials:**
   - MAY use 30,318 with footnote "raw count, pre-deduplication"
   - MAY use 32,201 / 63,153 / 30,952 / 641 with explicit "technical full-scope" label

3. **Citations of Research Square v1 (rs-9090074):**
   - Preprint v1 was submitted with 30,318 number (historic record)
   - v2 (manuscript_v2_full.md) uses 26,225 (verified after P0 audit)
   - When citing v1, footnote "preprint v2 reports verified count of 26,225 after deduplication"

4. **New documents:**
   - Default to 26,225 unless writing about pre-audit history
   - Cite this file: `docs/NUMBER_PROVENANCE.md`

---

## 🔍 Verification Commands

```bash
# Verify core variant count (should print 26,225)
cd D:/ДНК
python scripts/count_unique_variants.py | grep "CORE TOTAL"

# Verify invariant tests pass (13 tests, ~0.1s)
python -m pytest tests/test_alphagenome_invariants.py -v

# Verify HBB pilot statistics (p=4×10⁻⁶, ratio=5.4)
python -c "
import json
with open('results/alphagenome_batch_cage_9loci.json') as f:
    d = json.load(f)
hbb = d['results']['HBB_reference']
print(f'HBB: p={hbb[\"p\"]:.2e}, ratio={hbb[\"ratio\"]:.2f}')
"
```

Expected outputs:
- `CORE TOTAL 26,225 variants`
- `13 passed in 0.XXs`
- `HBB: p=4.00e-06, ratio=5.40`

---

## 📚 Cross-References

- **Policy:** `PROJECT_CANON.md:108`
- **Verification script:** `scripts/count_unique_variants.py`
- **P0 audit:** `docs/CODE_AUDIT_HARDENING_2026-05-25.md` (Layer 7 Provenance)
- **Manuscript (uses 26,225):** `manuscript/manuscript_v2_full.md:20`, `manuscript/abstract_content.typ:3`
- **Power analysis:** `docs/MLH1_POWER_ANALYSIS_2026-05-25.md`
- **Reframe context:** `docs/ADR-036_manuscript_reframe_HBB_pilot.md`
