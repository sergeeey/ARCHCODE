---
allowed-tools: Bash(npm:*), Bash(tsx:*), Read, Write
argument-hint: [locus-name]
description: Compare ARCHCODE vs AlphaGenome predictions for a specific genomic locus
---

# Compare ARCHCODE vs AlphaGenome

Perform a comprehensive comparison between ARCHCODE (structural) and AlphaGenome (expression) predictions for the specified locus.

## Task

Analyze **$ARGUMENTS** locus using both methods and generate a discordance report.

## Steps

1. **Run ARCHCODE validation**

   ```bash
   npm run validate:$ARGUMENTS
   ```

   Or if custom locus:

   ```bash
   npx tsx scripts/run-fountain-$ARGUMENTS.ts
   ```

2. **Read AlphaGenome predictions**
   Check parser integration data:

   ```bash
   cat results/alphagenome_predictions_$ARGUMENTS.json
   ```

   Or query parser directory:

   ```
   D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs/$ARGUMENTS/
   ```

3. **Calculate discordance**
   - ARCHCODE SSIM threshold: < 0.7 = pathogenic
   - AlphaGenome score threshold: > 0.7 = pathogenic
   - Discordant if verdicts differ

4. **Generate report**
   Create `results/discordance_$ARGUMENTS.md` with:

   ```markdown
   # ARCHCODE vs AlphaGenome Comparison: $ARGUMENTS

   ## ARCHCODE (Structural)

   - SSIM: X.XXX
   - Verdict: [PATHOGENIC | VUS | BENIGN]
   - Mechanism: [description]

   ## AlphaGenome (Expression)

   - Score: X.XXX
   - Verdict: [Pathogenic | VUS | Benign]
   - Prediction: [description]

   ## Discordance Analysis

   - Status: [CONCORDANT | DISCORDANT]
   - Type: [The Loop That Stayed | Post-transcriptional | Agreement]
   - Interpretation: [detailed explanation]
   ```

## Output

Print summary to console and save detailed report to file.

**Example output:**

```
✓ ARCHCODE: SSIM=0.545 → LIKELY_PATHOGENIC (structural disruption)
✓ AlphaGenome: Score=0.454 → VUS (no expression impact)
⚠ DISCORDANT: "The Loop That Stayed" — structural-only pathogenicity
📄 Report saved: results/discordance_hbb.md
```

## Available Loci

- `hbb` — Beta-globin (chr11:5,225,464-5,227,079)
- `igh` — Immunoglobulin Heavy Chain (chr14)
- `tcra` — T-Cell Receptor Alpha (chr14)
- `sox2` — SOX2 (chr3)
- `myc` — MYC oncogene (chr8)

If locus not recognized, treat as custom and guide user to provide coordinates.
