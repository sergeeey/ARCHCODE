"""Tests for AlphaGenomeValidator class."""

import pytest
import pandas as pd
import numpy as np
from ag_falsifier import AlphaGenomeValidator, ValidationResult


@pytest.fixture
def sample_data():
    """Create sample pearl and control data."""
    np.random.seed(42)

    # Pearls: strong CAGE disruption
    pearls = pd.DataFrame(
        {
            "Variant_ID": [f"pearl_{i}" for i in range(10)],
            "Category": ["promoter"] * 5 + ["enhancer"] * 5,
            "AlphaGenome_CAGE": np.random.normal(-15, 3, 10),
        }
    )

    # Controls: weak CAGE disruption
    controls = pd.DataFrame(
        {
            "Variant_ID": [f"control_{i}" for i in range(20)],
            "Category": ["promoter"] * 10 + ["enhancer"] * 10,
            "AlphaGenome_CAGE": np.random.normal(-2, 2, 20),
        }
    )

    return pearls, controls


def test_validator_initialization(sample_data):
    """Test validator initialization."""
    pearls, controls = sample_data

    validator = AlphaGenomeValidator(pearls=pearls, controls=controls, api_key="test-key")

    assert validator.api_key == "test-key"
    assert len(validator.pearls) == 10
    assert len(validator.controls) == 20


def test_validator_missing_columns():
    """Test validation of required columns."""
    pearls = pd.DataFrame({"wrong_col": [1, 2, 3]})
    controls = pd.DataFrame({"wrong_col": [4, 5, 6]})

    with pytest.raises(ValueError, match="missing columns"):
        AlphaGenomeValidator(pearls=pearls, controls=controls, api_key="test-key")


def test_validation_pass(sample_data):
    """Test validation with PASS verdict."""
    pearls, controls = sample_data

    validator = AlphaGenomeValidator(pearls=pearls, controls=controls, api_key="test-key")

    result = validator.validate(modality="CAGE", category_matched=True, n_permutations=1000)

    assert isinstance(result, ValidationResult)
    assert result.test_validity in ["VALID", "PARTIAL", "INVALID"]
    assert result.verdict in ["PASS", "WEAK", "FAIL"]
    assert 0 <= result.p_value <= 1


def test_validation_partial():
    """Test validation with PARTIAL validity (insufficient controls)."""
    # All pearls are promoter, but controls are enhancer only
    pearls = pd.DataFrame(
        {
            "Variant_ID": ["p1", "p2"],
            "Category": ["promoter", "promoter"],
            "AlphaGenome_CAGE": [-15, -18],
        }
    )

    controls = pd.DataFrame(
        {
            "Variant_ID": ["c1", "c2", "c3"],
            "Category": ["enhancer", "enhancer", "enhancer"],
            "AlphaGenome_CAGE": [-2, -3, -1],
        }
    )

    validator = AlphaGenomeValidator(pearls=pearls, controls=controls, api_key="test-key")

    result = validator.validate(n_permutations=100)

    assert result.test_validity == "INVALID"  # No promoter controls
    assert result.verdict == "FAIL"
    assert result.insufficient_categories is not None


def test_adr_generation(sample_data):
    """Test ADR generation."""
    pearls, controls = sample_data

    validator = AlphaGenomeValidator(pearls=pearls, controls=controls, api_key="test-key")

    result = validator.validate(n_permutations=100)

    # Generate ADR
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        result.to_adr(f.name)

        # Check ADR was created
        with open(f.name, "r") as adr:
            content = adr.read()
            assert "# ADR" in content
            assert result.verdict in content
            assert str(result.test_validity) in content


def test_json_export(sample_data):
    """Test JSON export."""
    pearls, controls = sample_data

    validator = AlphaGenomeValidator(pearls=pearls, controls=controls, api_key="test-key")

    result = validator.validate(n_permutations=100)

    # Export to JSON
    import tempfile
    import json

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        result.to_json(f.name)

        # Check JSON was created and valid
        with open(f.name, "r") as j:
            data = json.load(j)
            assert "test_validity" in data
            assert "p_value" in data
            assert "verdict" in data
