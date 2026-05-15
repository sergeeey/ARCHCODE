-- ARCHCODE Annotation Database Schema
-- Pattern inspired by genechat-mcp patch.db
-- Purpose: Annotate once, query fast (no repeated API calls)

-- Version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES
    (1, 'Initial schema: loci, variants, predictions, validations');

-- Genomic loci (HBB, MLH1, TERT, BRCA1, TP53, GJB2, etc.)
CREATE TABLE IF NOT EXISTS loci (
    locus_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_symbol TEXT NOT NULL UNIQUE,
    locus_type TEXT NOT NULL CHECK(locus_type IN ('regulatory', 'coding')),
    chromosome TEXT NOT NULL,
    start_pos INTEGER NOT NULL,
    end_pos INTEGER NOT NULL,
    genome_build TEXT NOT NULL DEFAULT 'hg38',
    tissue_context TEXT, -- e.g., 'erythroid', 'liver', 'brain'
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_loci_gene ON loci(gene_symbol);
CREATE INDEX idx_loci_type ON loci(locus_type);

-- ClinVar variants
CREATE TABLE IF NOT EXISTS clinvar_variants (
    variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    locus_id INTEGER NOT NULL,
    vcv_id TEXT NOT NULL UNIQUE, -- ClinVar VCV accession
    rs_id TEXT, -- dbSNP rsID (if available)
    chromosome TEXT NOT NULL,
    position INTEGER NOT NULL, -- hg38 coordinate
    ref_allele TEXT NOT NULL,
    alt_allele TEXT NOT NULL,
    variant_type TEXT, -- e.g., 'SNV', 'deletion', 'insertion'
    clinical_significance TEXT NOT NULL, -- 'Pathogenic', 'Benign', etc.
    classification TEXT NOT NULL CHECK(classification IN ('P/LP', 'B/LB', 'VUS', 'other')),
    functional_consequence TEXT, -- e.g., 'promoter_variant', 'missense', 'frameshift'
    review_status TEXT, -- ClinVar review stars
    last_evaluated TEXT, -- ClinVar last evaluation date
    condition TEXT, -- Associated disease/phenotype
    source TEXT NOT NULL DEFAULT 'ClinVar', -- Data source
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (locus_id) REFERENCES loci(locus_id)
);

CREATE INDEX idx_clinvar_vcv ON clinvar_variants(vcv_id);
CREATE INDEX idx_clinvar_locus ON clinvar_variants(locus_id);
CREATE INDEX idx_clinvar_class ON clinvar_variants(classification);
CREATE INDEX idx_clinvar_pos ON clinvar_variants(chromosome, position);

-- AlphaGenome CAGE predictions
CREATE TABLE IF NOT EXISTS alphagenome_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL,
    cage_reference REAL NOT NULL, -- Reference allele CAGE signal
    cage_mutant REAL NOT NULL, -- Mutant allele CAGE signal
    cage_delta REAL NOT NULL, -- Mutant - Reference (can be positive = gain-of-function)
    cage_delta_pct REAL NOT NULL, -- (Mutant - Ref) / Ref * 100
    tissue_source TEXT DEFAULT 'FANTOM5', -- CAGE data source
    prediction_confidence REAL, -- If AlphaGenome provides confidence score
    api_version TEXT, -- AlphaGenome API version
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (variant_id) REFERENCES clinvar_variants(variant_id)
);

CREATE INDEX idx_alphag_variant ON alphagenome_predictions(variant_id);
CREATE INDEX idx_alphag_delta ON alphagenome_predictions(cage_delta);

-- ARCHCODE SSIM scores (3D chromatin disruption)
CREATE TABLE IF NOT EXISTS archcode_ssim (
    ssim_id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL,
    ssim_reference REAL NOT NULL CHECK(ssim_reference >= 0 AND ssim_reference <= 1),
    ssim_mutant REAL NOT NULL CHECK(ssim_mutant >= 0 AND ssim_mutant <= 1),
    ssim_delta REAL NOT NULL, -- Reference - Mutant (positive = disruption)
    disruption_category TEXT CHECK(disruption_category IN ('pearl', 'grey', 'coal', 'uncategorized')),
    hic_dataset TEXT, -- e.g., 'K562', 'GM12878', 'liver_tissue'
    resolution_kb INTEGER, -- Hi-C resolution (e.g., 5, 10, 25 kb)
    loop_context TEXT, -- Enhancer-promoter, CTCF-CTCF, etc.
    computed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (variant_id) REFERENCES clinvar_variants(variant_id)
);

CREATE INDEX idx_ssim_variant ON archcode_ssim(variant_id);
CREATE INDEX idx_ssim_category ON archcode_ssim(disruption_category);

-- Validation results (mechanism specificity analysis)
CREATE TABLE IF NOT EXISTS validation_results (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    locus_id INTEGER NOT NULL,
    analysis_type TEXT NOT NULL, -- 'mechanism_specificity', 'cross_locus', 'forensic_audit'
    alphag_mann_whitney_p REAL, -- AlphaGenome P/LP vs B/LB separation
    archcode_mann_whitney_p REAL, -- ARCHCODE P/LP vs B/LB separation
    spearman_rho REAL, -- Correlation between AlphaGenome and ARCHCODE
    spearman_p REAL,
    classification TEXT CHECK(classification IN ('CONCORDANT', 'WEAK-ORTHOGONAL', 'ORTHOGONAL')),
    n_variants INTEGER NOT NULL, -- Sample size
    n_plp INTEGER, -- Number of P/LP variants
    n_blb INTEGER, -- Number of B/LB variants
    notes TEXT, -- Caveats, limitations, sampling bias
    adr_reference TEXT, -- Link to ADR (e.g., 'ADR-027')
    computed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (locus_id) REFERENCES loci(locus_id)
);

CREATE INDEX idx_validation_locus ON validation_results(locus_id);
CREATE INDEX idx_validation_type ON validation_results(analysis_type);

-- Forensic audit trail (data integrity checks)
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_type TEXT NOT NULL, -- 'clinvar_source', 'coordinates', 'api_response', 'statistics'
    entity_type TEXT NOT NULL, -- 'variant', 'locus', 'validation'
    entity_id INTEGER NOT NULL, -- Foreign key to relevant table
    check_name TEXT NOT NULL, -- e.g., 'vcv_id_resolves', 'hg38_coordinates_valid'
    status TEXT NOT NULL CHECK(status IN ('PASS', 'FAIL', 'WARNING')),
    details TEXT, -- Error message or validation details
    audited_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_status ON audit_log(status);

-- Metadata: data sources and versions
CREATE TABLE IF NOT EXISTS data_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL, -- 'ClinVar', 'AlphaGenome', 'ARCHCODE', 'K562_HiC'
    version TEXT, -- Version or date (e.g., '2026-05-14', 'v1.2.3')
    url TEXT, -- Download/API URL
    file_path TEXT, -- Local file path if applicable
    description TEXT,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Example initial data sources
INSERT INTO data_sources (source_name, version, url, description) VALUES
    ('ClinVar', '2026-05-14', 'https://ftp.ncbi.nlm.nih.gov/pub/clinvar/', 'NCBI ClinVar variant database'),
    ('AlphaGenome', 'API_v1', 'https://alphagenome.ai', 'AlphaGenome CAGE prediction API'),
    ('K562_HiC', 'ENCODE_2023', 'https://www.encodeproject.org/', 'K562 Hi-C data for ARCHCODE SSIM');

-- Views for common queries

-- View: Variants with full annotations
CREATE VIEW IF NOT EXISTS variants_full AS
SELECT
    cv.variant_id,
    l.gene_symbol,
    l.locus_type,
    cv.vcv_id,
    cv.rs_id,
    cv.chromosome || ':' || cv.position AS genomic_position,
    cv.ref_allele,
    cv.alt_allele,
    cv.variant_type,
    cv.clinical_significance,
    cv.classification,
    cv.functional_consequence,
    ag.cage_reference,
    ag.cage_mutant,
    ag.cage_delta,
    ag.cage_delta_pct,
    arc.ssim_reference,
    arc.ssim_mutant,
    arc.ssim_delta,
    arc.disruption_category
FROM clinvar_variants cv
JOIN loci l ON cv.locus_id = l.locus_id
LEFT JOIN alphagenome_predictions ag ON cv.variant_id = ag.variant_id
LEFT JOIN archcode_ssim arc ON cv.variant_id = arc.variant_id;

-- View: Locus summary statistics
CREATE VIEW IF NOT EXISTS locus_summary AS
SELECT
    l.gene_symbol,
    l.locus_type,
    COUNT(DISTINCT cv.variant_id) AS n_variants,
    SUM(CASE WHEN cv.classification = 'P/LP' THEN 1 ELSE 0 END) AS n_plp,
    SUM(CASE WHEN cv.classification = 'B/LB' THEN 1 ELSE 0 END) AS n_blb,
    AVG(ag.cage_delta) AS avg_cage_delta,
    AVG(arc.ssim_delta) AS avg_ssim_delta,
    vr.classification AS mechanism_specificity
FROM loci l
LEFT JOIN clinvar_variants cv ON l.locus_id = cv.locus_id
LEFT JOIN alphagenome_predictions ag ON cv.variant_id = ag.variant_id
LEFT JOIN archcode_ssim arc ON cv.variant_id = arc.variant_id
LEFT JOIN validation_results vr ON l.locus_id = vr.locus_id AND vr.analysis_type = 'mechanism_specificity'
GROUP BY l.locus_id, l.gene_symbol, l.locus_type;

-- View: Audit status summary
CREATE VIEW IF NOT EXISTS audit_summary AS
SELECT
    entity_type,
    check_name,
    status,
    COUNT(*) AS count,
    MAX(audited_at) AS last_audit
FROM audit_log
GROUP BY entity_type, check_name, status
ORDER BY entity_type, check_name;
