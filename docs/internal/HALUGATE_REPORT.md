# HaluGate Verification Report: METHODS.md

**Auditor**: Claude Code (HaluGate Pipeline)
**Date**: 2026-02-02
**Document**: `METHODS.md` (ARCHCODE v1.0)
**Method**: Cross-reference with primary literature sources

---

## Executive Summary

| Category                      | Count |
| ----------------------------- | ----- |
| ENTAILMENT (verified)         | 7     |
| NEUTRAL (needs disclaimer)    | 5     |
| CONTRADICTION (factual error) | 2     |

**Overall Status**: ⚠️ REQUIRES CORRECTIONS before publication

---

## 1. ENTAILMENT (Verified Claims)

### 1.1 Convergent CTCF Rule

**Claim (METHODS.md §1.2)**:

> "Loops form predominantly between CTCF sites in convergent orientation (R...F)"

**Literature**:

- [Rao et al. 2014](https://pubmed.ncbi.nlm.nih.gov/25497547/): ">90% of looped pairs contain convergent CTCF sites"
- [Sanborn et al. 2015](https://www.pnas.org/doi/10.1073/pnas.1518552112): "loops only form between convergent CTCF motifs"

**Verdict**: ✅ **ENTAILMENT** — Correct, well-supported

---

### 1.2 P(s) Power-Law Exponent

**Claim (METHODS.md §3.2)**:

> "Target: α ≈ -1.0 (consistent with Hi-C literature for interphase chromatin)"

**Literature**:

- [Lieberman-Aiden et al. 2009](https://www.science.org/doi/10.1126/science.1181369): α ≈ -1.08 (fractal globule model)

**Verdict**: ✅ **ENTAILMENT** — Correct within measurement uncertainty

---

### 1.3 Cohesin Residence Time (~20 min)

**Claim (METHODS.md §1.1)**:

> "Mean residence time: ~1200 steps (approximately 20 min if 1 step = 1s)"

**Literature**:

- [Gerlich et al. 2006](https://pubmed.ncbi.nlm.nih.gov/16890534/): "residence time of about 20 minutes" in G1
- Multiple FRAP studies: 20-25 min range confirmed

**Verdict**: ✅ **ENTAILMENT** — Correct (with step-time caveat, see §2.1)

---

### 1.4 Bidirectional Extrusion

**Claim (METHODS.md §1.1)**:

> "Symmetric bidirectional extrusion: L-1========R+1"

**Literature**:

- [Davidson et al. 2019](https://www.science.org/doi/10.1126/science.aaz4475): "cohesin dimer extrudes DNA loops bidirectionally"
- [Ganji et al. 2018](https://www.science.org/doi/10.1126/science.aar7831): Note — condensin is ASYMMETRIC, but cohesin is bidirectional

**Verdict**: ✅ **ENTAILMENT** — Correct for cohesin

---

### 1.5 ATP-Dependent Motor

**Claim (METHODS.md implicit)**:

> Cohesin is a molecular motor

**Literature**:

- [Davidson et al. 2019](https://www.science.org/doi/10.1126/science.aaz4475): "cohesin-NIPBL as an ATP-driven molecular machine capable of loop extrusion"

**Verdict**: ✅ **ENTAILMENT** — Correct

---

### 1.6 CTCF at Loop Anchors

**Claim (METHODS.md §4.1)**:

> Validate against "Known CTCF-mediated loops"

**Literature**:

- [Rao et al. 2014](https://pubmed.ncbi.nlm.nih.gov/25497547/): "CTCF and cohesin subunits were found to occupy 86% of contact peak loci"

**Verdict**: ✅ **ENTAILMENT** — Correct

---

### 1.7 Sanborn et al. Simulation Correlation

**Claim (README.md, referenced in METHODS)**:

> "Pearson's r ≥ 0.7" as target

**Literature**:

- [Sanborn et al. 2015](https://www.pnas.org/doi/10.1073/pnas.1518552112): "Pearson's r = 0.964" on chr4 region with their model

**Verdict**: ✅ **ENTAILMENT** — Target is reasonable (though Sanborn achieved higher)

---

## 2. NEUTRAL (Needs Disclaimer)

### 2.1 Step-to-Time Mapping

**Claim (METHODS.md §1.1)**:

> "1 step = 1 second (tunable parameter)"

**Issue**:
This is a MODEL ASSUMPTION, not a measured value. The mapping is arbitrary and affects all time-dependent claims.

**Recommendation**:
Add explicit disclaimer:

```markdown
**Note**: Step-to-time mapping (default 1 step = 1s) is a model parameter,
not a physical constant. Biological interpretation of time-dependent
quantities requires calibration against experimental kinetics.
```

**Verdict**: ⚠️ **NEUTRAL** — Add disclaimer

---

### 2.2 CTCF Blocking Efficiency (85%/15%)

**Claim (METHODS.md §1.2)**:

> "Convergent (R...F): 85% blocking efficiency (ensemble average, Rao et al. 2014)"
> "Non-convergent: 15% leaky blocking (estimated from de Wit et al. 2015)"

**Issue**:

- Rao et al. 2014 reports **loop frequency statistics**, not blocking efficiency
- ">90% convergent" describes observed loops, not the probability of blocking per encounter
- The 85%/15% values are **model parameters fit to reproduce Hi-C data**, not direct measurements

**Literature**:

- [Rao et al. 2014](https://pubmed.ncbi.nlm.nih.gov/25497547/): Reports loop statistics, NOT efficiency
- No single-molecule study directly measures "blocking efficiency"

**Recommendation**:

```markdown
**Blocking efficiency** (model parameters fit to ensemble data):

- **Convergent (R...F)**: 85% blocking efficiency
  (MODEL PARAMETER calibrated to reproduce Rao et al. 2014 loop frequencies)
- **Non-convergent**: 15% leaky blocking
  (MODEL PARAMETER; no direct measurement available)

**Note**: These are population-averaged parameters, not single-molecule efficiencies.
```

**Verdict**: ⚠️ **NEUTRAL** — Misleading citation; add MODEL PARAMETER label

---

### 2.3 Unloading Probability (0.0005/step)

**Claim (METHODS.md §1.1)**:

> "Cohesin unloads stochastically with probability 0.000833/step"

**Issue**:
This value is **derived** from residence time assumption:

```
P_unload = 1 / mean_residence_steps = 1 / 1200 ≈ 0.000833
```

This is a MODEL CALCULATION, not a measured rate constant. The unloading kinetics are regulated by WAPL and PDS5, which are not modeled.

**Recommendation**:
Add: "Calculated from target residence time; assumes simple exponential kinetics without WAPL/PDS5 regulation."

**Verdict**: ⚠️ **NEUTRAL** — Add derivation note

---

### 2.4 Bookmarking Efficiency (50%)

**Claim (AUDIT_RESPONSE.md)**:

> "bookmarking efficiency (50%)"

**Issue**:
No citation provided. This appears to be an assumed default.

**Verdict**: ⚠️ **NEUTRAL** — Requires HIGH UNCERTAINTY label

---

### 2.5 Boundary Exclusion Zone (10%)

**Claim (LoopExtrusionEngine.ts, noted in AUDIT)**:

> Respawn excludes 10% of genome at each end

**Issue**:
No biological justification provided. This is a numerical convenience.

**Verdict**: ⚠️ **NEUTRAL** — Document assumption

---

## 3. CONTRADICTION (Factual Errors)

### 3.1 ❌ Velocity Attribution Error

**Claim (METHODS.md §1.1)**:

> "Velocity: 500-2000 bp/step (default: 1000 bp/step = ~1 kb/s biological)"

**Claim (AUDIT_RESPONSE.md)**:

> "EXTRUSION_SPEED_BP_PER_S | Literature-based | Ganji et al. (2018)"

**Literature**:

- [Ganji et al. 2018](https://www.science.org/doi/10.1126/science.aar7831): Studies **CONDENSIN**, not cohesin!
  - Condensin: up to 1500 bp/s
- [Davidson et al. 2019](https://www.science.org/doi/10.1126/science.aaz4475): Studies **COHESIN**
  - Cohesin: **0.5 kb/s average** (500 bp/s), up to 2.1 kb/s maximum

**Problem**:
ARCHCODE models **cohesin** loop extrusion, but cites **condensin** velocity from Ganji 2018. These are different SMC complexes with different speeds:

- **Condensin**: faster, mitotic, asymmetric extrusion
- **Cohesin**: slower, interphase, bidirectional extrusion

**Correction Required**:

```markdown
| Parameter | Value            | Source                                 |
| --------- | ---------------- | -------------------------------------- |
| Velocity  | 500-2000 bp/step | Davidson et al. (2019) for cohesin     |
| Default   | 500 bp/step      | Mean rate from single-molecule studies |
| Maximum   | 2100 bp/step     | Upper bound from Davidson et al.       |
```

**Verdict**: ❌ **CONTRADICTION** — Wrong citation, wrong organism's protein

---

### 3.2 ❌ Processivity Overestimate

**Claim (METHODS.md §1.1, biophysics.ts)**:

> "Processivity: 600 kb"

**Claim (README.md)**:

> "processivity": 600 // kb

**Literature**:

- [Davidson et al. 2019](https://www.science.org/doi/10.1126/science.aaz4475): "average size of extruded loops was **33 kb**"
- [Stigler et al. 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5346154/): "within an hour, cohesin could translocate 7 kb" on nucleosomal DNA
- Computational estimates: "cohesin needs to translocate up to 500 kb to form a chromosomal domain"

**Problem**:
600 kb processivity is **~18× higher** than the measured 33 kb average loop size. While large domains "hundreds of kilobases" exist, this is achieved through:

1. Multiple cohesin molecules
2. Loading near boundary elements
3. Ensemble averaging

Single-molecule processivity is much lower.

**Correction Options**:

1. Lower default to 50-100 kb with disclaimer
2. Or explicitly state: "MODEL PARAMETER chosen to achieve domain-scale loops; single-molecule processivity is ~30-50 kb"

**Verdict**: ❌ **CONTRADICTION** — Order of magnitude discrepancy with single-molecule data

---

## 4. Summary Table

| Claim                   | Section        | Verdict          | Action                   |
| ----------------------- | -------------- | ---------------- | ------------------------ |
| Convergent CTCF rule    | §1.2           | ✅ ENTAILMENT    | None                     |
| P(s) ~ s^-1             | §3.2           | ✅ ENTAILMENT    | None                     |
| Residence ~20 min       | §1.1           | ✅ ENTAILMENT    | None                     |
| Bidirectional extrusion | §1.1           | ✅ ENTAILMENT    | None                     |
| ATP-dependent motor     | implicit       | ✅ ENTAILMENT    | None                     |
| CTCF at anchors (86%)   | §4.1           | ✅ ENTAILMENT    | None                     |
| Pearson r ≥ 0.7 target  | §4.3           | ✅ ENTAILMENT    | None                     |
| Step = 1 second         | §1.1           | ⚠️ NEUTRAL       | Add disclaimer           |
| 85%/15% efficiency      | §1.2           | ⚠️ NEUTRAL       | Label as MODEL PARAMETER |
| Unloading probability   | §1.1           | ⚠️ NEUTRAL       | Add derivation           |
| Bookmarking 50%         | AUDIT_RESPONSE | ⚠️ NEUTRAL       | HIGH UNCERTAINTY         |
| 10% boundary exclusion  | Engine         | ⚠️ NEUTRAL       | Document                 |
| **Velocity from Ganji** | §1.1           | ❌ CONTRADICTION | Fix citation → Davidson  |
| **Processivity 600 kb** | §1.1           | ❌ CONTRADICTION | Lower or add disclaimer  |

---

## 5. Recommended Fixes

### 5.1 Critical (Before Publication)

1. **Fix velocity citation**:

   ```diff
   - | EXTRUSION_SPEED_BP_PER_S | Literature-based | Ganji et al. (2018) |
   + | EXTRUSION_SPEED_BP_PER_S | Literature-based | Davidson et al. (2019) |
   ```

2. **Fix processivity or add disclaimer**:

   ```diff
   - | Processivity | 600 kb | - |
   + | Processivity | 600 kb | MODEL PARAMETER (single-molecule: ~33 kb avg) |
   ```

3. **Add parameter classification section to METHODS.md**:

   ```markdown
   ## Parameter Sources

   | Parameter       | Type       | Literature Value   | Model Value  | Justification                      |
   | --------------- | ---------- | ------------------ | ------------ | ---------------------------------- |
   | Velocity        | LITERATURE | 500 bp/s mean      | 1000 bp/step | Upper range for faster dynamics    |
   | Processivity    | MODEL      | ~33 kb             | 600 kb       | Scaled for domain-level simulation |
   | CTCF efficiency | MODEL      | N/A (not measured) | 85%/15%      | Fit to Rao 2014 loop frequencies   |
   | Residence time  | LITERATURE | 20-25 min          | 1200 steps   | Gerlich 2006                       |
   ```

### 5.2 Recommended (Scientific Clarity)

4. Add explicit **Assumptions and Limitations** section to METHODS.md
5. Distinguish LITERATURE-BASED vs MODEL PARAMETER in all constants
6. Add uncertainty ranges where available

---

## 6. Sources Consulted

1. [Ganji et al. 2018 - Science](https://www.science.org/doi/10.1126/science.aar7831) - Condensin single-molecule
2. [Davidson et al. 2019 - Science](https://www.science.org/doi/10.1126/science.aaz4475) - Cohesin single-molecule
3. [Rao et al. 2014 - Cell](https://pubmed.ncbi.nlm.nih.gov/25497547/) - Hi-C loop analysis
4. [Sanborn et al. 2015 - PNAS](https://www.pnas.org/doi/10.1073/pnas.1518552112) - Extrusion model
5. [Gerlich et al. 2006 - Curr Biol](https://pubmed.ncbi.nlm.nih.gov/16890534/) - Cohesin FRAP
6. [Lieberman-Aiden et al. 2009 - Science](https://www.science.org/doi/10.1126/science.1181369) - Hi-C P(s) curve
7. [Fudenberg et al. 2016 - Cell Reports](https://pmc.ncbi.nlm.nih.gov/articles/PMC5346154/) - Loop extrusion review

---

**Report generated by Claude Code HaluGate Pipeline**
**Severity**: 2 CONTRADICTIONS require immediate attention before publication
