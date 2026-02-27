---
allowed-tools: Bash(npm:*), Bash(npx:*), Read, Grep
argument-hint: [locus]
description: Run blind-test validation for a genomic locus
---

# Blind-Test Validation

Run comprehensive blind-test validation for a genomic locus to verify ARCHCODE's predictive accuracy.

## Input

**$ARGUMENTS** — Locus identifier (e.g., `hbb`, `igh`, `tcra`, `sox2`, `myc`)

## Validation Protocol

### Step 1: Check if validation script exists

```bash
ls scripts/run-fountain-$ARGUMENTS.ts
```

If not exists, check standard validation:

```bash
npm run validate:$ARGUMENTS
```

### Step 2: Run ensemble simulation

```bash
# Standard validation (1000 runs)
npm run validate:$ARGUMENTS

# Or custom ensemble
npx tsx scripts/run-fountain-$ARGUMENTS.ts
```

### Step 3: Analyze results

Check output for:

- **Mean loop duration** (should be ~16-17 min for most loci)
- **95% Confidence Interval** (narrow CI = consistent)
- **Contact probability** (compare to Hi-C data if available)
- **Power-law exponent** (should be ~-1.0)

### Step 4: Compare to literature

Known benchmarks:

- **HBB**: 16.17 min [15.23, 17.11] (Sabaté et al. 2024 (bioRxiv))
- **IGH**: 16.18 min [15.28, 17.08] (blind, PASS)
- **TCRα**: Similar range expected
- **SOX2**: Similar range expected

### Step 5: Generate report

Create `results/validation_$ARGUMENTS.md`:

```markdown
# Blind-Test Validation: $ARGUMENTS

## Parameters

- Seed: 2026 (reproducibility)
- Runs: 1000
- Kramer kinetics: α=0.92, γ=0.80, k_base=0.002

## Results

| Metric        | Value          | Target           | Status          |
| ------------- | -------------- | ---------------- | --------------- |
| Mean Duration | XX.XX min      | 16-17 min        | ✓ PASS / ✗ FAIL |
| 95% CI        | [XX.XX, XX.XX] | Narrow (<2 min)  | ✓ PASS / ✗ FAIL |
| Contact Prob  | X.XX%          | Literature value | ✓ PASS / ✗ FAIL |

## Interpretation

[Analysis of whether results match expected biophysics]

## Verdict

**PASS** / **FAIL** — [reasoning]
```

## Success Criteria

| Criterion           | Threshold    |
| ------------------- | ------------ |
| Mean duration       | 14-18 min    |
| CI width            | < 2 min      |
| Pearson r (vs Hi-C) | > 0.95       |
| Power-law α         | -0.9 to -1.1 |

## Troubleshooting

**Mean duration too high (>20 min):**

- Check processivity parameter
- Verify CTCF barrier strengths
- Review unloading rate (k_base)

**Mean duration too low (<12 min):**

- Increase residence time
- Reduce unloading rate
- Check if FountainLoader is active

**High variance (CI > 3 min):**

- Increase number of runs (>1000)
- Check for stochastic blocking issues
- Verify SeededRandom usage

## Available Loci

✅ **Validated:**

- `hbb` — HBB (beta-globin)
- `igh` — Immunoglobulin Heavy Chain
- `tcra` — T-Cell Receptor Alpha
- `sox2` — SOX2 transcription factor

⏳ **Pending:**

- `myc` — MYC oncogene
- `hoxd` — HOXD cluster
- `tp53` — TP53 tumor suppressor

## Output Example

```
=================================================
Blind-Test Validation: IGH
=================================================
Seed: 2026 | Runs: 1000 | Kramer: α=0.92, γ=0.80

Results:
  Mean Duration: 16.18 min
  95% CI: [15.28, 17.08]
  Contact Prob: 3.26%

Comparison to HBB (calibration):
  ΔDuration: +0.01 min (negligible)
  ΔSSIM: 0.97 (highly similar)

✓ VERDICT: PASS

Report saved: results/validation_igh.md
```
