# AlphaGenome Research Repository Analysis

**Date**: 2026-02-03
**Repository**: [https://github.com/google-deepmind/alphagenome_research](https://github.com/google-deepmind/alphagenome_research)
**Purpose**: Integration context for ARCHCODE validation

---

## 1. Model Architecture
AlphaGenome follows a hierarchical transformer-based structure:
- **Input**: DNA Sequence (1M bp context window).
- **Encoder**: Convolutional layers for local pattern recognition (motifs).
- **Transformer Tower**: 9 layers for long-range interactions (crucial for 3D loops).
- **Decoder**: Multimodal heads for epigenetic tracks and contact maps.

## 2. Contact Map Scoring (Orca Method)
The model evaluates variants using the **Structural Impact Score** (Zhou et al., 2022):
- Calculation: `abs_diff = jnp.abs(alt - ref).mean(axis=0)`
- This metric represents the average absolute log fold change between Wild-Type and Variant contact maps.

## 3. Validation Metrics
The research codebase confirms that ARCHCODE's validation strategy is aligned with industry standards:
- **Pearson R**: Primary linear correlation metric.
- **MSE/MAE**: Error quantification.
- **SSIM**: Structural similarity (recommended for future integration).

## 4. Hardware Requirements
- **Inference**: High-end GPUs (NVIDIA H100) are required for local execution.
- **TPU**: Optimized for Google's TPU v3/v4 infrastructure.

## 5. Strategic Recommendations for ARCHCODE
- **Maintain Mock Mode**: Since H100 infrastructure is not locally available, the robust Mock mode is essential for CI/CD and front-end development.
- **Triangulation**: Use the published Nature 2026 data as a "Static Gold Standard" to bypass API limitations for high-impact figures.
- **Python Wrapper**: Future versions should consider a JAX-based wrapper to call the model weights directly from Kaggle/HuggingFace if local GPU resources permit.
