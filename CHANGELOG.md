# Changelog

## [1.0.0-alpha] - 2025-11-23

### Added
- Initial ARCHCODE project structure
- Boundary Stability Predictor module (RS-06)
  - StabilityCalculator - Main interface
  - FactorAggregator - Factor aggregation
  - StabilityModel - Multiplicative model
  - Full integration with all ARCHCODE modules
- ARCHCODE Core Pipeline
  - Integrated analysis pipeline
  - Boundary stability integration
  - Batch processing support
- Boundary Stability Visualization
  - Stability profile plots
  - Category distribution charts
- RS-07: Boundary Collapse Simulation specification
- MCP Genomic Data Server
  - 9 genomic data access tools
  - Integration with ARCHCODE modules
  - Setup script for Cursor configuration
  - Full documentation

### MCP Genomic Data Server Tools
- `fetch_genomic_sequence` - UCSC/Ensembl sequence access
- `fetch_ctcf_chipseq` - ENCODE CTCF ChIP-seq data
- `fetch_hic_data` - Hi-C contact matrices
- `fetch_methylation_data` - CpG methylation profiles
- `search_gene` - Gene search and coordinates
- `fetch_te_annotations` - Transposon element annotations
- `classify_te_family` - TE family classification
- `calculate_insulation_score` - Hi-C insulation scores
- `detect_tads_from_hic` - TAD boundary detection

### Documentation
- MCP Servers Analysis
- MCP Integration Proposal
- MCP Genomic Data Integration Guide
- MCP Usage Guide
