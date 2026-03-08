# VALIDATION_EXECUTION_2026-03-06_TASK1_1MB

## Task

Validate the 1Mb-scale benchmark hypothesis using real ground truth and reproducible artifacts.

Top-level canonical index (primary governance source):
- `results/validation_canonical_index_2026-03-06.json`

## Implemented

- Installed missing extraction dependency in project venv:
  - `cooler==0.10.4`
- Added 1Mb BRCA1 locus config:
  - `config/locus/brca1mb_1mb.json`
  - window: `chr17:42600000-43600000`, `1000 bins x 1000bp`
- Added alias mapping for the new locus:
  - `scripts/lib/locus_config.py`
  - `scripts/tda_proof_of_concept.py`
- Extracted real 1Mb Hi-C matrix from local 4DN mcool:
  - input: `data/reference/4DNFI18UHVRO.mcool`
  - output matrix: `data/reference/BRCA1MB_K562_HiC_1000bp.npy` (1000x1000)
  - output metadata: `data/reference/BRCA1MB_K562_HiC_1000bp_meta.json`
- Ran 1Mb benchmarks:
  - `scripts/benchmark_alphagenome.py --locus brca1mb_1mb ...`
  - `scripts/benchmark_akita.py --locus brca1mb_1mb ...`

## Verified

- Artifacts created:
  - `results/task1_alphagenome_benchmark_brca1mb_1mb_2026-03-06.json`
  - `results/task1_akita_benchmark_brca1mb_1mb_2026-03-06.json`

- 1Mb correlation vs Hi-C (Pearson r):
  - ARCHCODE vs Hi-C: `-0.0100`
  - AlphaGenome vs Hi-C: `0.0593`
  - Akita vs Hi-C: `0.0090`

- 1Mb local SSIM vs Hi-C:
  - ARCHCODE vs Hi-C: `0.7340`
  - AlphaGenome vs Hi-C: `0.0591`
  - Akita vs Hi-C: `0.0273`

- 95kb reference (existing artifacts):
  - ARCHCODE vs Hi-C Pearson: `0.0724`
  - AlphaGenome vs Hi-C Pearson: `0.0510`
  - Akita vs Hi-C Pearson: `-0.0499`

## UNVERIFIED

- The claim "on 1Mb AlphaGenome Pearson rises to >0.5" is not supported by this run.
- Cross-cell comparability remains a limitation:
  - prediction track: `GM12878` (AlphaGenome/Akita)
  - ground truth: `K562` (local mcool extraction)

## Verdict

- Hypothesis `1Mb => Pearson > 0.5` for this setup: `REJECTED`.
- Current evidence supports keeping the benchmark claim at `EXPLORATORY` until cell-matched and protocol-matched ground truth is used.
