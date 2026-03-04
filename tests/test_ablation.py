"""
Regression tests for ARCHCODE ablation study results.

Verifies that ablation_effectstrength.json and conservation_pearl_analysis.json
contain expected values. These tests protect against accidental data corruption
during manuscript preparation or pipeline re-runs.

Run: python -m pytest tests/test_ablation.py -v
"""

import json
import os
import pytest

# ПОЧЕМУ: paths relative to repo root, not test file
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "results")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(filename: str) -> dict:
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_mode(data: dict, mode_name: str) -> dict:
    """Extract a mode dict from the ablation 'modes' array."""
    for m in data["modes"]:
        if m["mode"] == mode_name:
            return m
    raise KeyError(f"Mode '{mode_name}' not found in ablation data")


# ---------------------------------------------------------------------------
# Ablation study tests
# ---------------------------------------------------------------------------

class TestAblationStructure:
    """Verify ablation JSON structure and metadata."""

    @pytest.fixture(autouse=True)
    def load_data(self):
        self.data = load_json("ablation_effectstrength.json")

    def test_file_exists(self):
        path = os.path.join(RESULTS_DIR, "ablation_effectstrength.json")
        assert os.path.exists(path), "ablation_effectstrength.json not found"

    def test_has_required_keys(self):
        for key in ("experiment", "locus", "n_variants", "modes", "conclusions"):
            assert key in self.data, f"Missing key: {key}"

    def test_variant_count(self):
        assert self.data["n_variants"] == 1103, \
            f"Expected 1103 HBB variants, got {self.data['n_variants']}"

    def test_pathogenic_count(self):
        assert self.data["n_pathogenic"] == 353

    def test_benign_count(self):
        assert self.data["n_benign"] == 750

    def test_five_modes_present(self):
        mode_names = {m["mode"] for m in self.data["modes"]}
        expected = {"categorical", "position-only", "uniform-medium", "inverted", "random"}
        assert mode_names == expected, f"Missing modes: {expected - mode_names}"

    def test_each_mode_has_auc(self):
        for m in self.data["modes"]:
            assert "auc" in m, f"Mode '{m['mode']}' missing 'auc'"
            assert isinstance(m["auc"], (int, float)), f"AUC not numeric for {m['mode']}"


class TestAblationValues:
    """Verify ablation AUC values match manuscript claims."""

    @pytest.fixture(autouse=True)
    def load_data(self):
        self.data = load_json("ablation_effectstrength.json")

    def test_categorical_auc(self):
        """Categorical mode should have AUC ~0.975 (Table 5 in manuscript)."""
        cat = get_mode(self.data, "categorical")
        assert 0.96 <= cat["auc"] <= 0.99, \
            f"Categorical AUC {cat['auc']} outside expected range [0.96, 0.99]"

    def test_position_only_auc(self):
        """Position-only should be near chance (~0.55)."""
        pos = get_mode(self.data, "position-only")
        assert 0.45 <= pos["auc"] <= 0.65, \
            f"Position-only AUC {pos['auc']} not near chance"

    def test_uniform_medium_auc(self):
        """Uniform-medium should also be near chance."""
        uni = get_mode(self.data, "uniform-medium")
        assert 0.45 <= uni["auc"] <= 0.65, \
            f"Uniform-medium AUC {uni['auc']} not near chance"

    def test_inverted_auc(self):
        """Inverted should be ~1-categorical (mirror effect)."""
        inv = get_mode(self.data, "inverted")
        cat = get_mode(self.data, "categorical")
        # AUC(inverted) ≈ 1 - AUC(categorical)
        expected = 1.0 - cat["auc"]
        assert abs(inv["auc"] - expected) < 0.05, \
            f"Inverted AUC {inv['auc']} not mirror of categorical ({expected:.3f})"

    def test_random_auc(self):
        """Random should be near 0.5 (no signal)."""
        rand = get_mode(self.data, "random")
        assert 0.40 <= rand["auc"] <= 0.60, \
            f"Random AUC {rand['auc']} not near chance"

    def test_categorical_best(self):
        """Categorical must have highest AUC among all modes."""
        cat_auc = get_mode(self.data, "categorical")["auc"]
        for m in self.data["modes"]:
            if m["mode"] != "categorical":
                assert cat_auc > m["auc"], \
                    f"Categorical AUC ({cat_auc}) not > {m['mode']} ({m['auc']})"

    def test_inverted_worst(self):
        """Inverted must have lowest AUC (below chance)."""
        inv_auc = get_mode(self.data, "inverted")["auc"]
        for m in self.data["modes"]:
            if m["mode"] != "inverted":
                assert inv_auc < m["auc"], \
                    f"Inverted AUC ({inv_auc}) not < {m['mode']} ({m['auc']})"

    def test_delta_signs(self):
        """Categorical should have positive delta, inverted negative."""
        cat = get_mode(self.data, "categorical")
        inv = get_mode(self.data, "inverted")
        assert cat["delta"] > 0, "Categorical delta should be positive"
        assert inv["delta"] < 0, "Inverted delta should be negative"


# ---------------------------------------------------------------------------
# Conservation analysis tests
# ---------------------------------------------------------------------------

class TestConservationStructure:
    """Verify conservation JSON structure."""

    @pytest.fixture(autouse=True)
    def load_data(self):
        self.data = load_json("conservation_pearl_analysis.json")

    def test_file_exists(self):
        path = os.path.join(RESULTS_DIR, "conservation_pearl_analysis.json")
        assert os.path.exists(path)

    def test_has_pearl_positions(self):
        assert "pearl_positions" in self.data

    def test_has_background(self):
        assert "background" in self.data

    def test_has_fold_enrichment(self):
        assert "fold_enrichment" in self.data

    def test_has_gtex(self):
        assert "gtex_eqtl" in self.data


class TestConservationValues:
    """Verify conservation values match manuscript claims."""

    @pytest.fixture(autouse=True)
    def load_data(self):
        self.data = load_json("conservation_pearl_analysis.json")

    def test_pearl_count(self):
        """17 unique pearl positions (manuscript Section 3.3)."""
        assert self.data["pearl_positions"]["n_unique"] == 17

    def test_phylop_enrichment(self):
        """Pearl PhyloP should be >2x background (manuscript: 3.3x)."""
        pearl_mean = self.data["pearl_positions"]["phyloP_mean"]
        bg_mean = self.data["background"]["phyloP_mean"]
        fold = pearl_mean / bg_mean
        assert fold > 2.0, f"PhyloP fold enrichment {fold:.1f} < 2.0"

    def test_fold_enrichment_value(self):
        """Fold enrichment ~3.3 as reported."""
        fe = self.data["fold_enrichment"]
        assert 2.5 <= fe <= 4.5, f"Fold enrichment {fe:.1f} outside range [2.5, 4.5]"

    def test_phylop_mean_positive(self):
        """Pearl positions should have positive PhyloP (conserved)."""
        assert self.data["pearl_positions"]["phyloP_mean"] > 1.0

    def test_gerp_all_constrained(self):
        """All pearl positions in GERP constrained elements (score > 4)."""
        gerp_min = self.data["pearl_positions"]["gerp_range"][0]
        assert gerp_min > 4.0, f"GERP min {gerp_min} < 4 (not constrained)"

    def test_gtex_zero_eqtls(self):
        """Zero eQTLs for HBB in Whole Blood (extreme purifying selection)."""
        assert self.data["gtex_eqtl"]["n_eqtls"] == 0

    def test_conserved_fraction(self):
        """At least 40% of pearls should have PhyloP > 2."""
        pct = self.data["pearl_positions"]["pct_conserved_gt2"]
        assert pct >= 0.40, f"Only {pct:.0%} conserved (>2), expected ≥40%"


# ---------------------------------------------------------------------------
# Cross-file consistency
# ---------------------------------------------------------------------------

class TestCrossConsistency:
    """Verify consistency between ablation and atlas files."""

    def test_atlas_csv_exists(self):
        """Main HBB atlas CSV must exist."""
        path = os.path.join(RESULTS_DIR, "HBB_Unified_Atlas_95kb.csv")
        assert os.path.exists(path)

    def test_ablation_mode_csvs_exist(self):
        """All ablation mode CSVs must exist."""
        for suffix in ("POSITION_ONLY", "UNIFORM_MEDIUM", "INVERTED", "RANDOM"):
            path = os.path.join(RESULTS_DIR, f"HBB_Unified_Atlas_95kb_{suffix}.csv")
            assert os.path.exists(path), f"Missing ablation CSV: {suffix}"

    def test_atlas_row_count(self):
        """Atlas CSV row count should match ablation n_variants."""
        import csv
        ablation = load_json("ablation_effectstrength.json")
        csv_path = os.path.join(RESULTS_DIR, "HBB_Unified_Atlas_95kb.csv")
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            rows = sum(1 for _ in reader)
        assert rows == ablation["n_variants"], \
            f"CSV has {rows} rows, ablation says {ablation['n_variants']}"
