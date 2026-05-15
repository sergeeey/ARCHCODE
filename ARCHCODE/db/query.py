"""
ARCHCODE Annotation Database - Query Helpers

Pattern inspired by genechat-mcp.
Purpose: Fast queries without repeated API calls.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Variant:
    """Variant with full annotations."""

    variant_id: int
    gene_symbol: str
    locus_type: str
    vcv_id: str
    rs_id: Optional[str]
    genomic_position: str
    ref_allele: str
    alt_allele: str
    variant_type: str
    clinical_significance: str
    classification: str
    functional_consequence: Optional[str]
    cage_reference: Optional[float]
    cage_mutant: Optional[float]
    cage_delta: Optional[float]
    cage_delta_pct: Optional[float]
    ssim_reference: Optional[float]
    ssim_mutant: Optional[float]
    ssim_delta: Optional[float]
    disruption_category: Optional[str]


@dataclass
class LocusSummary:
    """Locus summary statistics."""

    gene_symbol: str
    locus_type: str
    n_variants: int
    n_plp: int
    n_blb: int
    avg_cage_delta: Optional[float]
    avg_ssim_delta: Optional[float]
    mechanism_specificity: Optional[str]


@dataclass
class ValidationResult:
    """Mechanism specificity validation result."""

    validation_id: int
    locus_id: int
    gene_symbol: str
    analysis_type: str
    alphag_mann_whitney_p: Optional[float]
    archcode_mann_whitney_p: Optional[float]
    spearman_rho: Optional[float]
    spearman_p: Optional[float]
    classification: Optional[str]
    n_variants: int
    n_plp: Optional[int]
    n_blb: Optional[int]
    notes: Optional[str]
    adr_reference: Optional[str]
    computed_at: Optional[str]


class ARCHCODEDatabase:
    """Query interface for ARCHCODE annotation database."""

    def __init__(self, db_path: Path = Path(__file__).parent / "archcode_annotations.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    # ==================== Locus Queries ====================

    def get_locus(self, gene_symbol: str) -> Optional[Dict[str, Any]]:
        """Get locus metadata by gene symbol."""
        with self.conn:
            cursor = self.conn.execute("SELECT * FROM loci WHERE gene_symbol = ?", (gene_symbol,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_loci(self, locus_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all loci, optionally filtered by type."""
        query = "SELECT * FROM loci"
        params = []
        if locus_type:
            query += " WHERE locus_type = ?"
            params.append(locus_type)
        query += " ORDER BY gene_symbol"

        with self.conn:
            cursor = self.conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # ==================== Variant Queries ====================

    def get_variant(self, vcv_id: str) -> Optional[Variant]:
        """Get variant by ClinVar VCV ID with full annotations."""
        with self.conn:
            cursor = self.conn.execute("SELECT * FROM variants_full WHERE vcv_id = ?", (vcv_id,))
            row = cursor.fetchone()
            return Variant(**dict(row)) if row else None

    def get_variants_by_locus(
        self, gene_symbol: str, classification: Optional[str] = None
    ) -> List[Variant]:
        """Get all variants for a locus, optionally filtered by classification."""
        query = "SELECT * FROM variants_full WHERE gene_symbol = ?"
        params = [gene_symbol]

        if classification:
            query += " AND classification = ?"
            params.append(classification)

        query += " ORDER BY genomic_position"

        with self.conn:
            cursor = self.conn.execute(query, params)
            return [Variant(**dict(row)) for row in cursor.fetchall()]

    def get_variants_by_category(
        self, gene_symbol: str, functional_consequence: str
    ) -> List[Variant]:
        """Get variants filtered by functional consequence (e.g., 'promoter_variant')."""
        query = """
            SELECT * FROM variants_full
            WHERE gene_symbol = ? AND functional_consequence LIKE ?
            ORDER BY genomic_position
        """
        with self.conn:
            cursor = self.conn.execute(query, (gene_symbol, f"%{functional_consequence}%"))
            return [Variant(**dict(row)) for row in cursor.fetchall()]

    def get_pearls(self, gene_symbol: str) -> List[Variant]:
        """Get 'pearl' variants (high structural disruption) for a locus."""
        query = """
            SELECT * FROM variants_full
            WHERE gene_symbol = ? AND disruption_category = 'pearl'
            ORDER BY ssim_delta DESC
        """
        with self.conn:
            cursor = self.conn.execute(query, (gene_symbol,))
            return [Variant(**dict(row)) for row in cursor.fetchall()]

    # ==================== Validation Queries ====================

    def get_validation_results(
        self, gene_symbol: Optional[str] = None, analysis_type: str = "mechanism_specificity"
    ) -> List[ValidationResult]:
        """Get validation results, optionally filtered by locus."""
        query = """
            SELECT vr.*, l.gene_symbol
            FROM validation_results vr
            JOIN loci l ON vr.locus_id = l.locus_id
            WHERE vr.analysis_type = ?
        """
        params = [analysis_type]

        if gene_symbol:
            query += " AND l.gene_symbol = ?"
            params.append(gene_symbol)

        query += " ORDER BY vr.computed_at DESC"

        with self.conn:
            cursor = self.conn.execute(query, params)
            return [ValidationResult(**dict(row)) for row in cursor.fetchall()]

    def get_locus_summary(self, gene_symbol: Optional[str] = None) -> List[LocusSummary]:
        """Get summary statistics for loci."""
        query = "SELECT * FROM locus_summary"
        params = []

        if gene_symbol:
            query += " WHERE gene_symbol = ?"
            params.append(gene_symbol)

        query += " ORDER BY gene_symbol"

        with self.conn:
            cursor = self.conn.execute(query, params)
            return [LocusSummary(**dict(row)) for row in cursor.fetchall()]

    # ==================== Statistics Queries ====================

    def get_mechanism_specificity_summary(self) -> Dict[str, Any]:
        """Get mechanism specificity across all loci."""
        query = """
            SELECT
                locus_type,
                COUNT(*) AS n_loci,
                SUM(CASE WHEN classification = 'CONCORDANT' THEN 1 ELSE 0 END) AS n_concordant,
                SUM(CASE WHEN classification = 'WEAK-ORTHOGONAL' THEN 1 ELSE 0 END) AS n_weak_orthogonal,
                SUM(CASE WHEN classification = 'ORTHOGONAL' THEN 1 ELSE 0 END) AS n_orthogonal,
                AVG(spearman_rho) AS avg_rho,
                AVG(alphag_mann_whitney_p) AS avg_alphag_p,
                AVG(archcode_mann_whitney_p) AS avg_archcode_p
            FROM validation_results vr
            JOIN loci l ON vr.locus_id = l.locus_id
            WHERE vr.analysis_type = 'mechanism_specificity'
            GROUP BY locus_type
        """
        with self.conn:
            cursor = self.conn.execute(query)
            rows = cursor.fetchall()
            return {row["locus_type"]: dict(row) for row in rows}

    def get_cage_gain_of_function_variants(self, min_delta_pct: float = 20.0) -> List[Variant]:
        """Get variants with CAGE gain-of-function (positive delta ≥ threshold)."""
        query = """
            SELECT * FROM variants_full
            WHERE cage_delta_pct >= ?
            ORDER BY cage_delta_pct DESC
        """
        with self.conn:
            cursor = self.conn.execute(query, (min_delta_pct,))
            return [Variant(**dict(row)) for row in cursor.fetchall()]

    # ==================== Audit Queries ====================

    def get_audit_summary(self) -> List[Dict[str, Any]]:
        """Get audit status summary."""
        with self.conn:
            cursor = self.conn.execute(
                "SELECT * FROM audit_summary ORDER BY entity_type, check_name"
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_failed_audits(self) -> List[Dict[str, Any]]:
        """Get all failed audit checks."""
        query = """
            SELECT * FROM audit_log
            WHERE status = 'FAIL'
            ORDER BY audited_at DESC
        """
        with self.conn:
            cursor = self.conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    # ==================== Insert Operations ====================

    def insert_locus(
        self,
        gene_symbol: str,
        locus_type: str,
        chromosome: str,
        start_pos: int,
        end_pos: int,
        tissue_context: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> int:
        """Insert a new locus. Returns locus_id."""
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO loci (gene_symbol, locus_type, chromosome, start_pos, end_pos, tissue_context, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (gene_symbol, locus_type, chromosome, start_pos, end_pos, tissue_context, notes),
            )
            self.conn.commit()
            return cursor.lastrowid

    def insert_variant(
        self,
        locus_id: int,
        vcv_id: str,
        chromosome: str,
        position: int,
        ref_allele: str,
        alt_allele: str,
        clinical_significance: str,
        classification: str,
        **kwargs,
    ) -> int:
        """Insert a ClinVar variant. Returns variant_id."""
        fields = [
            "locus_id",
            "vcv_id",
            "chromosome",
            "position",
            "ref_allele",
            "alt_allele",
            "clinical_significance",
            "classification",
        ]
        values = [
            locus_id,
            vcv_id,
            chromosome,
            position,
            ref_allele,
            alt_allele,
            clinical_significance,
            classification,
        ]

        # Add optional fields
        for key, value in kwargs.items():
            if value is not None:
                fields.append(key)
                values.append(value)

        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO clinvar_variants ({', '.join(fields)}) VALUES ({placeholders})"

        with self.conn:
            cursor = self.conn.execute(query, values)
            self.conn.commit()
            return cursor.lastrowid

    def insert_alphagenome_prediction(
        self, variant_id: int, cage_reference: float, cage_mutant: float, **kwargs
    ) -> int:
        """Insert AlphaGenome CAGE prediction. Returns prediction_id."""
        cage_delta = cage_mutant - cage_reference
        cage_delta_pct = (cage_delta / cage_reference * 100) if cage_reference != 0 else 0

        fields = ["variant_id", "cage_reference", "cage_mutant", "cage_delta", "cage_delta_pct"]
        values = [variant_id, cage_reference, cage_mutant, cage_delta, cage_delta_pct]

        for key, value in kwargs.items():
            if value is not None:
                fields.append(key)
                values.append(value)

        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO alphagenome_predictions ({', '.join(fields)}) VALUES ({placeholders})"

        with self.conn:
            cursor = self.conn.execute(query, values)
            self.conn.commit()
            return cursor.lastrowid

    def insert_archcode_ssim(
        self, variant_id: int, ssim_reference: float, ssim_mutant: float, **kwargs
    ) -> int:
        """Insert ARCHCODE SSIM score. Returns ssim_id."""
        ssim_delta = ssim_reference - ssim_mutant  # Positive = disruption

        fields = ["variant_id", "ssim_reference", "ssim_mutant", "ssim_delta"]
        values = [variant_id, ssim_reference, ssim_mutant, ssim_delta]

        for key, value in kwargs.items():
            if value is not None:
                fields.append(key)
                values.append(value)

        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO archcode_ssim ({', '.join(fields)}) VALUES ({placeholders})"

        with self.conn:
            cursor = self.conn.execute(query, values)
            self.conn.commit()
            return cursor.lastrowid

    def insert_validation_result(
        self, locus_id: int, analysis_type: str, n_variants: int, **kwargs
    ) -> int:
        """Insert validation result. Returns validation_id."""
        fields = ["locus_id", "analysis_type", "n_variants"]
        values = [locus_id, analysis_type, n_variants]

        for key, value in kwargs.items():
            if value is not None:
                fields.append(key)
                values.append(value)

        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO validation_results ({', '.join(fields)}) VALUES ({placeholders})"

        with self.conn:
            cursor = self.conn.execute(query, values)
            self.conn.commit()
            return cursor.lastrowid

    def log_audit(
        self,
        audit_type: str,
        entity_type: str,
        entity_id: int,
        check_name: str,
        status: str,
        details: Optional[str] = None,
    ) -> int:
        """Log an audit check. Returns audit_id."""
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO audit_log (audit_type, entity_type, entity_id, check_name, status, details)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (audit_type, entity_type, entity_id, check_name, status, details),
            )
            self.conn.commit()
            return cursor.lastrowid


# ==================== Convenience Functions ====================


def init_database(db_path: Path, schema_path: Path) -> None:
    """Initialize database from schema.sql."""
    with sqlite3.connect(db_path) as conn:
        with open(schema_path) as f:
            conn.executescript(f.read())
    print(f"✅ Database initialized: {db_path}")


def print_locus_summary(db: ARCHCODEDatabase, gene_symbol: Optional[str] = None) -> None:
    """Pretty-print locus summary."""
    summaries = db.get_locus_summary(gene_symbol)

    print("\n📊 Locus Summary")
    print("=" * 80)
    for s in summaries:
        print(f"{s.gene_symbol} ({s.locus_type}):")
        print(f"  Variants: {s.n_variants} total ({s.n_plp} P/LP, {s.n_blb} B/LB)")
        if s.avg_cage_delta is not None:
            print(f"  CAGE Δ: {s.avg_cage_delta:.3f}")
        if s.avg_ssim_delta is not None:
            print(f"  SSIM Δ: {s.avg_ssim_delta:.4f}")
        if s.mechanism_specificity:
            print(f"  Mechanism: {s.mechanism_specificity}")
        print()


def print_validation_results(db: ARCHCODEDatabase) -> None:
    """Pretty-print validation results."""
    results = db.get_validation_results()

    print("\n🔬 Validation Results (Mechanism Specificity)")
    print("=" * 80)
    for r in results:
        print(f"{r.gene_symbol} (N={r.n_variants}):")
        if r.alphag_mann_whitney_p is not None:
            print(f"  AlphaGenome p={r.alphag_mann_whitney_p:.6f}")
        if r.archcode_mann_whitney_p is not None:
            print(f"  ARCHCODE p={r.archcode_mann_whitney_p:.6f}")
        if r.spearman_rho is not None:
            print(f"  Spearman ρ={r.spearman_rho:.3f}, p={r.spearman_p:.6f}")
        if r.classification:
            print(f"  Classification: {r.classification}")
        if r.adr_reference:
            print(f"  ADR: {r.adr_reference}")
        print()
