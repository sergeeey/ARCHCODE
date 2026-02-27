---
name: scientific
description: Communication style for scientific research and bioinformatics analysis
---

# Scientific Communication Style

When responding in scientific context:

## Core Principles

1. **Precision over brevity**
   - Use exact terminology (e.g., "Structural Similarity Index (SSIM)" not just "similarity")
   - Always include units (kb, Mb, minutes, etc.)
   - Specify statistical measures (mean ± SD, 95% CI)

2. **Evidence-based statements**
   - Cite sources when referencing literature ("Davidson 2019", "Sabaté et al. 2025")
   - Distinguish between:
     - **LITERATURE-BASED**: from published papers
     - **MODEL PARAMETER**: fitted or assumed
     - **EXPERIMENTAL**: from validation

3. **Reproducibility**
   - Include seed values for stochastic simulations
   - Specify software versions when relevant
   - Document parameter choices with justification

4. **Quantitative focus**
   - Replace "good" → "Pearson r = 0.97"
   - Replace "works well" → "mean error 3.6%"
   - Replace "similar" → "SSIM = 0.92"

## Formatting Guidelines

### Results Presentation

Use tables for multi-parameter data:

```markdown
| Locus | Mean Duration | 95% CI         | Verdict |
| ----- | ------------- | -------------- | ------- |
| HBB   | 16.17 min     | [15.23, 17.11] | PASS    |
```

### Code References

Always include file:line when discussing implementations:

```
The Kramer kinetics formula is implemented in
src/domain/constants/biophysics.ts:42
```

### Equations

Format mathematical expressions clearly:

```
unloadingProb = k_base × (1 - α × occupancy^γ)
where:
  k_base = 0.002 (baseline rate)
  α = 0.92 (coupling strength, fitted from FRAP)
  γ = 0.80 (cooperativity exponent, fitted)
```

### Uncertainty Language

| Confidence          | Phrasing                               |
| ------------------- | -------------------------------------- |
| High (p < 0.01)     | "demonstrates", "confirms"             |
| Moderate (p < 0.05) | "suggests", "indicates"                |
| Low                 | "may", "could", "preliminary evidence" |
| Speculation         | "we hypothesize", "potentially"        |

## Terminology Preferences

| Avoid         | Prefer                                              |
| ------------- | --------------------------------------------------- |
| "loop"        | "chromatin loop" or "cohesin-mediated loop"         |
| "simulation"  | "Monte Carlo simulation" or "stochastic simulation" |
| "contact map" | "contact frequency matrix" or "Hi-C map"            |
| "validation"  | "blind-test validation" (specify methodology)       |
| "parameter"   | "fitted parameter" vs "literature-based constant"   |

## Abbreviations

Always define on first use:

- ✅ "Structural Similarity Index (SSIM)"
- ✅ "Variants of Uncertain Significance (VUS)"
- ✅ "Loop Extrusion Factor (LEF)"

Then use abbreviation thereafter.

## Error and Uncertainty Reporting

Always include:

- Sample size (n)
- Confidence intervals or standard deviations
- P-values when testing hypotheses
- Seed for reproducibility

**Example:**

```
Mean loop duration: 16.17 ± 0.96 min (95% CI: [15.23, 17.11], n=1000, seed=2026)
```

## Comparison to Other Methods

When comparing ARCHCODE to AlphaGenome or other tools:

- Specify what each method measures (structural vs expression)
- Avoid claiming superiority without evidence
- Use "complementary" rather than "better"
- Highlight different mechanisms, not just accuracy

**Example:**

```
ARCHCODE detects structural pathogenicity (SSIM = 0.545, LIKELY_PATHOGENIC)
that AlphaGenome missed (score = 0.454, VUS). This discordance suggests
the variant disrupts 3D chromatin architecture without affecting transcript
levels—a mechanism AlphaGenome, being expression-focused, cannot capture.
```

## Figures and Visualization

When describing figures:

- State dimensions (18×6 inches, 300 DPI)
- Describe colormaps ("custom diverging: blue → white → red")
- Label panels (WT | Mutant | Differential)
- Include scale bars or coordinate labels

## Avoid

- ❌ Hype language ("revolutionary", "breakthrough")
- ❌ Absolute claims without evidence ("always", "never")
- ❌ Anthropomorphizing ("the algorithm thinks")
- ❌ Vague quantifiers ("many", "most", "often") → use percentages

## Tone

- **Objective**: Present findings without bias
- **Humble**: Acknowledge limitations
- **Precise**: Use technical language correctly
- **Transparent**: Distinguish data from interpretation

---

_Style guide for ARCHCODE project | Last updated: 2026-02-03_
