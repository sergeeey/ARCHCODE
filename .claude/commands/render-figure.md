---
allowed-tools: Bash(python:*), Read, Glob
argument-hint: [variant-id]
description: Generate high-resolution publication figure for a variant using render_matrix.py
---

# Render Publication Figure

Generate a 3-panel publication-quality figure (WT | Mutant | Differential) for the specified variant.

## Input

**$ARGUMENTS** — ClinVar ID (e.g., `VCV000000302`) or genomic position (e.g., `5225620`)

## Steps

1. **Extract variant information**
   ```bash
   grep "$ARGUMENTS" results/HBB_Clinical_Atlas.csv
   ```
   Or from KEY_FINDINGS.json:
   ```bash
   cat results/KEY_FINDINGS.json | jq '.loopThatStayed[] | select(.clinvar_id == "$ARGUMENTS")'
   ```

2. **Check if render_matrix.py needs updates**
   ```python
   # scripts/render_matrix.py
   VARIANT_VCV302 = {
       'clinvar_id': '$ARGUMENTS',
       'position': XXXX,  # Update this
       'category': 'splice_region',  # Update this
       'archcode_ssim': X.XXX,  # Update this
       'alphagenome_score': X.XXX  # Update this
   }
   ```

3. **Run visualization**
   ```bash
   python scripts/render_matrix.py
   ```

4. **Verify output**
   Check: `results/figures/FIG_1_DISCORDANCE_$ARGUMENTS.png`
   - Resolution: 300 DPI
   - Size: 18x6 inches
   - Format: PNG

5. **Display result**
   Show the generated figure to user using Read tool

## Styling

The figure uses ARCHCODE brand colors:
- Dark background: `#0F172A`
- Orange accent: `#FF6B35`
- Text color: `#E2E8F0`

## Output Format

```
=======================================================
ARCHCODE Matrix Visualization: 'The Loop That Stayed'
=======================================================
Variant: VCV000000302 @ chr11:5,225,620
Category: splice_region
Kramer kinetics: α=0.92, γ=0.80, k_base=0.002

Simulating WT (healthy) matrix...
Simulating Mutant (VCV302) matrix...

Statistics:
  WT mean (upper tri): 0.XXXX
  Mutant mean (upper tri): 0.XXXX
  Max |differential|: 0.XXXX

Rendering figure...

✓ Figure saved: results/figures/FIG_1_DISCORDANCE_VCV302.png
  Resolution: 300 DPI
  Size: 18x6 inches
```

## Troubleshooting

- **Import errors**: Check matplotlib, numpy installed
- **BigWig errors**: Skip epigenetic tracks (use mock data)
- **Memory issues**: Reduce N_BINS or RESOLUTION

## Use Cases

- bioRxiv figure generation
- Supplementary materials
- Conference presentations
- "The Loop That Stayed" showcase
