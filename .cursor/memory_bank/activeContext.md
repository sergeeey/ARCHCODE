# Active Context
**Last Updated:** 2026-02-05 09:42 UTC+6
**Mode:** PLAN → ACT
**Branch:** main

---

## 🎯 Current Task

**Phase:** Hi-C Validation with Real Experimental Data

**Objective:**
Extract real Hi-C contact matrix for HBB locus from Rao et al. (2014) data and compare with ARCHCODE simulation output.

**Why Now:**
- Previous validation used mock AlphaGenome (synthetic baseline)
- Audit (FALSIFICATION_REPORT.md) identified need for real experimental validation
- Option B approved: Hi-C + RNA-seq validation (not ClinVar)

---

## 📋 Session Plan

### ✅ Completed (This Session)
1. Project audit (PROJECT_AUDIT_2026-02-05.md)
2. Git checkpoint commit (7e72d38)
3. Line endings normalization
4. Memory Bank creation
5. projectbrief.md populated

### 🔄 In Progress
**Step 1:** Extract Hi-C data
- Script: `scripts/extract_hic_hbb_locus.py`
- Input: Rao et al. (2014) .hic file
- Output: HBB locus contact matrix (JSON/CSV)
- Status: Script exists, ready to run

### ⏭️ Next Steps
1. Run `extract_hic_hbb_locus.py`
2. Validate output format
3. Load into ContactMatrixViewer.tsx
4. Calculate Pearson correlation (simulation vs real Hi-C)
5. Update manuscript with real validation results
6. Generate publication figures

---

## 🧪 Last Test Status

**Test:** Not run yet (starting fresh session)

**Expected:**
```bash
cd scripts
python extract_hic_hbb_locus.py
# Expected output: HBB_contact_matrix_real.json
```

**Success Criteria:**
- JSON file generated
- Matrix dimensions: ~40x40 (5kb bins, 200kb locus)
- No NaN values
- Pearson r with simulation: target ≥ 0.7

---

## 🚨 Critical Flags (From CLAUDE.md)

### Active Guardrails
1. ✅ NO phantom references (all DOIs verified)
2. ✅ NO invisible synthetic data (mock AlphaGenome clearly labeled)
3. ✅ NO post-hoc claims (git timestamps preserve chronology)
4. 🔄 Hi-C data = REAL experimental (Rao et al. 2014)

### Watch Out For
- Do NOT mix synthetic and real data in same figure
- Do NOT claim "fitted" parameters without fitting code
- Do NOT generate fake Hi-C data if extraction fails
- If extraction fails → document limitation, not workaround

---

## 🗂️ Recent Context (Last 5 Commits)

```
7e72d38 - chore: pre-hic-validation checkpoint (TODAY)
14a14fa - plan: CORRECTED Option B - Hi-C + RNA-seq
08ad309 - plan: Option B real ClinVar data pipeline
4347493 - protocol: add CLAUDE.md scientific integrity
d401974 - AUDIT: falsification-first QC completed
```

**Trend:** Post-audit correction phase → real data validation

---

## 📁 Working Files (Current Focus)

### Immediate Attention
- `scripts/extract_hic_hbb_locus.py` - Hi-C extraction
- `src/components/ui/ContactMatrixViewer.tsx` - Display real vs sim
- `manuscript/FULL_MANUSCRIPT.md` - Update with real results

### Reference (Read-Only)
- `CLAUDE.md` - Scientific integrity protocol
- `METHODS.md` - Algorithm details for publication
- `config/default.json` - Simulation parameters

### Generated (Do Not Commit)
- `data/samples/` - Experimental data
- `results/` - Validation outputs

---

## 🔄 Mode Transitions

**Current:** ACT mode (executing Hi-C extraction)

**Transitions:**
- PLAN → ACT: After this document created
- ACT → VERIFY: After extraction runs
- VERIFY → PLAN: If extraction fails (need new approach)
- VERIFY → ACT: If validation succeeds (next locus: Sox2)

---

## 🎓 Lessons Learned (Recent)

### From Audit (FALSIFICATION_REPORT.md)
1. **Sabaté 2025 phantom citation**
   - Lesson: Always verify DOI before using
   - Fix: Use Sabaté 2024 bioRxiv (real)

2. **AlphaGenome disclosure gap**
   - Lesson: Synthetic data needs bold warnings
   - Fix: MOCK_ prefix + watermarks

3. **Parameter mismatch (α, γ)**
   - Lesson: Code and manuscript must match exactly
   - Fix: Single source of truth (config/default.json)

### From MCP Configuration (Today)
1. Context7 is Must-Have #1 (up-to-date library docs)
2. Memory Bank prevents lost context between sessions
3. Git discipline = scientific lab notebook

---

## 🧠 Short-Term Memory (This Session Only)

**User Intent:**
- Work on ARCHCODE project (D:\ДНК)
- Hi-C validation is priority
- Follow Professor Kimi's recommendation (Variant C → A)

**Key Files Read:**
- CLAUDE.md (scientific protocol)
- README.md (project overview)
- package.json (dependencies)
- Git log (recent commits)

**Decisions Made:**
1. Git checkpoint before starting (DONE)
2. Memory Bank creation (IN PROGRESS)
3. Hi-C extraction next (PENDING)

---

## 🎯 Success Criteria for This Phase

**Minimum Viable:**
- [ ] Extract Hi-C data for HBB locus
- [ ] Calculate Pearson r with simulation
- [ ] Document result (even if r < 0.7)

**Target:**
- [ ] Pearson r ≥ 0.7 (validates model)
- [ ] Generate comparison figure
- [ ] Update manuscript Methods section

**Stretch:**
- [ ] Extract Sox2 and Pcdh loci too
- [ ] Parameter sweep to optimize r
- [ ] Statistical significance test (p-value)

---

## 🔧 Environment Status

**Tools Available:**
- Node.js v22.20.0
- Python 3.x (for extract_hic_hbb_locus.py)
- npm dependencies installed
- Git clean (no uncommitted changes)

**MCP Servers (Global):**
- ✅ Memory (basic-memory-server)
- ✅ Context7 (API key configured)
- ⚠️ GitHub (not authenticated yet)
- ✅ Filesystem

**Branch:**
- main (up to date with origin)
- Alternative: ARCHCODE-AlphaGenome (feature branch)

---

## 📝 Notes for Next Session

**If this session is interrupted:**
1. Read this file first (activeContext.md)
2. Check progress.md for task status
3. Review git log for recent commits
4. Continue from "Next Steps" section above

**Key Files to Update:**
- progress.md (when tasks complete)
- decisions.md (if approach changes)
- CLAUDE.md (if new integrity issues found)

---

**Last Action:** Memory Bank creation complete → Ready for Hi-C extraction

**Next Action:** Run `scripts/extract_hic_hbb_locus.py`
