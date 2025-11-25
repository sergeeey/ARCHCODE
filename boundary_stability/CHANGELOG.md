# Changelog

## [1.0.0-alpha] - 2024-01-XX

### Added
- Initial Boundary Stability Predictor module
- StabilityCalculator - Main interface
- FactorAggregator - Factor aggregation from ARCHCODE modules
- StabilityModel - Multiplicative stability model
- Configuration file (boundary_stability.yaml)
- Unit tests

### Model
- Multiplicative formula: `Stability = S_ctcf × (1 + E_barrier) × E_epi × (1 + M_te) × T_time`
- Thresholds: stable (≥0.7), variable (≤0.4), intermediate (0.4-0.7)
- Integration with all ARCHCODE modules

### Engineering Unknowns
- Exact threshold calibration (0.7, 0.4)
- Factor weight optimization
- Temporal factor calculation method










