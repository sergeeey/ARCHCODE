"""ADR (Architectural Decision Record) generation."""

from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .validator import ValidationResult


def generate_adr(result: "ValidationResult") -> str:
    """
    Generate ADR markdown from ValidationResult.

    Args:
        result: ValidationResult object

    Returns:
        Markdown-formatted ADR content
    """
    timestamp = datetime.fromisoformat(result.timestamp).strftime("%Y-%m-%d")

    # Status mapping
    status_map = {"PASS": "✅ ACCEPTED", "WEAK": "⚠️ PARTIAL", "FAIL": "❌ REJECTED"}
    status = status_map.get(result.verdict, "UNKNOWN")

    # Build ADR
    adr = f"""# ADR: AlphaGenome {result.modality} Validation Result

**Date:** {timestamp}
**Status:** {status}
**Test Validity:** {result.test_validity}
**p-value:** {result.p_value:.2e}

---

## Context

AlphaGenome {result.modality} predictions were tested on {result.n_pearls} structural fragility candidates (pearls) vs {result.n_controls} benign controls.

**Validation approach:** Category-matched permutation test (falsification-first)

---

## Decision

**Verdict:** {result.verdict}

**Interpretation:** {result.interpretation}

"""

    # Add warning if present
    if result.warning:
        adr += f"""**Warning:** {result.warning}

"""

    # Add detailed results
    adr += """---

## Results

"""

    if result.test_validity == "PARTIAL" and result.insufficient_categories:
        adr += "### Category-Matched Control Availability\n\n"
        adr += "| Category | Pearl Count | Controls Available | Action |\n"
        adr += "|----------|-------------|-------------------|--------|\n"

        for category, info in result.insufficient_categories.items():
            adr += (
                f"| {category} | {info['pearl_count']} | "
                f"{info['available_controls']} | {info['action']} |\n"
            )
        adr += "\n"

    # Negative controls
    if result.negative_controls:
        adr += "### Negative Controls\n\n"
        for control_name, control_result in result.negative_controls.items():
            p = control_result.get("p_value", "N/A")
            interp = control_result.get("interpretation", "N/A")
            adr += f"- **{control_name}:** p={p}, {interp}\n"
        adr += "\n"

    # Seed sensitivity
    if result.seed_sensitivity:
        adr += "### Seed Sensitivity\n\n"
        p_range = result.seed_sensitivity.get("p_value_range", [0, 0])
        interp = result.seed_sensitivity.get("interpretation", "N/A")
        adr += f"- p-value range: {p_range[0]:.4f} to {p_range[1]:.4f}\n"
        adr += f"- {interp}\n\n"

    # Consequences
    adr += """---

## Consequences

"""

    if result.verdict == "PASS":
        adr += f"""✅ **AlphaGenome {result.modality} validated** on this dataset.

- Significant enrichment detected (p={result.p_value:.2e})
- All statistical controls passed
- Safe to use for hypothesis generation

**Next steps:**
- Expand to additional loci
- Wet-lab validation (MPRA, CAGE-seq, Hi-C)
- Cross-modality concordance check
"""

    elif result.verdict == "WEAK":
        adr += f"""⚠️ **Partial validation** (limitations apply).

- {result.interpretation}
- Use with caution, acknowledge limitations
- Additional evidence needed

**Next steps:**
- Expand control set (address insufficient categories)
- Independent validation on different dataset
- Consider orthogonal methods
"""

    else:  # FAIL
        adr += f"""❌ **Validation failed** (hypothesis not supported).

- {result.interpretation}
- Do NOT use for claims without additional evidence
- Honest null result documented

**Next steps:**
- Pivot to alternative hypothesis
- Check for orthogonal mechanisms
- Re-evaluate biological assumptions
"""

    # Metadata
    adr += f"""
---

## Metadata

- **Test:** Category-matched permutation
- **Modality:** {result.modality}
- **Pearls:** {result.n_pearls}
- **Controls:** {result.n_controls}
- **Timestamp:** {result.timestamp}
- **Tool:** ag-falsifier v0.1.0-alpha

---

_"Null results are results. Validation theater is not validation."_
"""

    return adr
