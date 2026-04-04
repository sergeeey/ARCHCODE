from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_MARKERS = {
    Path("README.md"): "<!-- CANON_TIER: PUBLIC_CANONICAL -->",
    Path("docs/ENDORSEMENT_PACKET.md"): "**Canon Tier:** Public Canonical",
    Path("docs/READINESS.md"): "**Canon Tier:** Public Canonical",
    Path("docs/STATUS_DASHBOARD.md"): "**Canon Tier:** Public Canonical",
    Path("manuscript/taxonomy_paper/abstract_content.typ"): "// CANON_TIER: PUBLIC_CANONICAL",
}

TECHNICAL_MARKERS = {
    Path("docs/DISCOVERY_ENGINE_POSITIONING.md"): "**Canon Tier:** Technical Full-Scope",
    Path("docs/VALIDATION.md"): "**Canon Tier:** Technical Full-Scope",
    Path("docs/VALIDATION_PROTOCOL.md"): "**Canon Tier:** Technical Full-Scope",
    Path("docs/FAILURE_MODES.md"): "**Canon Tier:** Technical Full-Scope",
    Path("docs/PR_GATE.md"): "**Canon Tier:** Technical Full-Scope",
    Path("manuscript/taxonomy_paper/body_content.typ"): "// CANON_TIER: TECHNICAL_FULL_SCOPE",
}

TECHNICAL_JSON_FILES = [
    Path("results/competitor_comparison.json"),
    Path("results/statistical_strengthening.json"),
    Path("results/cross_locus_pearl_scan.json"),
    Path("results/alphagenome_batch_cage_9loci.json"),
]

REQUIRED_LEGACY_PATHS = [
    Path("archive/legacy/README.md"),
    Path("archive/legacy/ARCHCODE_Preprint.html"),
    Path("archive/legacy/ARCHCODE_Preprint_RU.html"),
    Path("archive/legacy/manuscript/biorxiv_version"),
    Path("archive/legacy/manuscript/biorxiv_version/README.md"),
    Path("archive/legacy/docs/COMPARISON_PDF_VS_REPO.md"),
    Path("archive/legacy/docs/COLD_EYE_AUDIT_REPORT.md"),
    Path("archive/legacy/docs/COLD_EYE_AUDIT_TZ.md"),
]

PUBLIC_BANNED_PATTERNS = [
    r"variant pathogenicity prediction",
    r"\b63,153\b",
    r"\b32,201\b",
    r"\b30,952\b",
    r"641 pearl-like",
    r'20 "Pearl"',
    r"Five tools independently fail",
]


def read_text(rel_path: Path) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def fail(msg: str, issues: list[str]) -> None:
    issues.append(msg)


def check_file_markers(issues: list[str]) -> None:
    for rel_path, marker in PUBLIC_MARKERS.items():
        abs_path = ROOT / rel_path
        if not abs_path.exists():
            fail(f"Missing public canonical file: {rel_path}", issues)
            continue
        text = abs_path.read_text(encoding="utf-8")
        if marker not in text:
            fail(f"Missing public canonical marker in {rel_path}", issues)

    for rel_path, marker in TECHNICAL_MARKERS.items():
        abs_path = ROOT / rel_path
        if not abs_path.exists():
            fail(f"Missing technical full-scope file: {rel_path}", issues)
            continue
        text = abs_path.read_text(encoding="utf-8")
        if marker not in text:
            fail(f"Missing technical full-scope marker in {rel_path}", issues)


def check_submission_metadata(issues: list[str]) -> None:
    rel_path = Path("submission_metadata.json")
    abs_path = ROOT / rel_path
    if not abs_path.exists():
        fail("Missing submission_metadata.json", issues)
        return
    data = json.loads(abs_path.read_text(encoding="utf-8"))
    if data.get("canon_tier") != "public_canonical":
        fail("submission_metadata.json canon_tier must be public_canonical", issues)
    if data.get("version") != "v2.17":
        fail("submission_metadata.json version must be v2.17", issues)
    if data.get("internal_package_version") != "2.0.0":
        fail("submission_metadata.json internal_package_version must be 2.0.0", issues)

    if data.get("class_b_variants") == 54:
        breakdown = str(data.get("class_b_breakdown", ""))
        if "25" not in breakdown or "29" not in breakdown:
            fail("submission_metadata.json must decompose 54 Class B into 25 + 29", issues)


def check_public_surface_text(issues: list[str]) -> None:
    for rel_path in PUBLIC_MARKERS:
        text = read_text(rel_path)
        for pattern in PUBLIC_BANNED_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"Public surface {rel_path} contains banned pattern: {pattern}", issues)

    readme = read_text(Path("README.md"))
    if "structural mechanism discovery" not in readme:
        fail("README.md must contain structural mechanism discovery positioning", issues)
    if "Discovery Engine, not a Prediction Tool" not in readme:
        fail("README.md must state discovery engine positioning", issues)
    if "25 high-confidence Class B variants at HBB" not in readme:
        fail("README.md must contain the 25-variant HBB public core", issues)
    if "29 additional Class B candidates" not in readme:
        fail("README.md must retain exploratory non-HBB candidates with context", issues)
    if "broader technical HBB definition includes 27 pearls" not in readme:
        fail("README.md must contextualize any 27-pearl technical definition", issues)
    if "ARCHCODE v2.17" not in readme:
        fail("README.md must show public research release v2.17", issues)

    for rel_path in [
        Path("docs/ENDORSEMENT_PACKET.md"),
        Path("docs/READINESS.md"),
        Path("docs/STATUS_DASHBOARD.md"),
    ]:
        text = read_text(rel_path)
        if "v2.17" not in text:
            fail(f"{rel_path} must reference v2.17", issues)


def check_technical_json_metadata(issues: list[str]) -> None:
    for rel_path in TECHNICAL_JSON_FILES:
        abs_path = ROOT / rel_path
        if not abs_path.exists():
            fail(f"Missing technical JSON surface: {rel_path}", issues)
            continue
        data = json.loads(abs_path.read_text(encoding="utf-8"))
        if data.get("canon_tier") != "technical_full_scope":
            fail(f"{rel_path} canon_tier must be technical_full_scope", issues)
        if data.get("release_facing") is not False:
            fail(f"{rel_path} release_facing must be false", issues)
        scope_note = str(data.get("scope_note", ""))
        if not scope_note:
            fail(f"{rel_path} must include a scope_note", issues)


def check_validation_contract_links(issues: list[str]) -> None:
    validation = ROOT / "docs/VALIDATION.md"
    compatibility = ROOT / "docs/VALIDATION_PROTOCOL.md"
    if not validation.exists():
        fail("docs/VALIDATION.md is missing", issues)
    if not compatibility.exists():
        fail("docs/VALIDATION_PROTOCOL.md compatibility stub is missing", issues)

    public_text = read_text(Path("docs/STATUS_DASHBOARD.md")) + "\n" + read_text(Path("docs/READINESS.md"))
    if "VALIDATION_PROTOCOL.md updated" in public_text:
        fail("Public canonical surfaces must not present VALIDATION_PROTOCOL.md as the active contract", issues)


def check_legacy_routes(issues: list[str]) -> None:
    for rel_path in REQUIRED_LEGACY_PATHS:
        if not (ROOT / rel_path).exists():
            fail(f"Missing required legacy path: {rel_path}", issues)

    legacy_marker_checks = {
        Path("archive/legacy/README.md"): "historical",
        Path("archive/legacy/ARCHCODE_Preprint.html"): "LEGACY / HISTORICAL / NOT CURRENT CANONICAL SURFACE",
        Path("archive/legacy/ARCHCODE_Preprint_RU.html"): "LEGACY / HISTORICAL / NOT CURRENT CANONICAL SURFACE",
        Path("archive/legacy/manuscript/biorxiv_version/README.md"): "LEGACY / HISTORICAL / NOT CURRENT CANONICAL SURFACE",
        Path("archive/legacy/docs/COMPARISON_PDF_VS_REPO.md"): "LEGACY / HISTORICAL / NOT CURRENT CANONICAL SURFACE",
        Path("archive/legacy/docs/COLD_EYE_AUDIT_REPORT.md"): "LEGACY / HISTORICAL / NOT CURRENT CANONICAL SURFACE",
        Path("archive/legacy/docs/COLD_EYE_AUDIT_TZ.md"): "LEGACY / HISTORICAL / NOT CURRENT CANONICAL SURFACE",
    }
    for rel_path, marker in legacy_marker_checks.items():
        text = read_text(rel_path)
        if marker not in text:
            fail(f"Legacy surface missing historical marker: {rel_path}", issues)

    for stale_path in [
        Path("ARCHCODE_Preprint.html"),
        Path("ARCHCODE_Preprint_RU.html"),
        Path("manuscript/biorxiv_version"),
        Path("docs/COMPARISON_PDF_VS_REPO.md"),
        Path("docs/COLD_EYE_AUDIT_REPORT.md"),
        Path("docs/COLD_EYE_AUDIT_TZ.md"),
    ]:
        if (ROOT / stale_path).exists():
            fail(f"Historical surface still present outside archive/legacy: {stale_path}", issues)


def main() -> int:
    issues: list[str] = []

    if not (ROOT / "PROJECT_CANON.md").exists():
        fail("Missing PROJECT_CANON.md", issues)

    check_file_markers(issues)
    check_submission_metadata(issues)
    check_public_surface_text(issues)
    check_technical_json_metadata(issues)
    check_validation_contract_links(issues)
    check_legacy_routes(issues)

    if issues:
        print("PROJECT CANON FAILED.")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("PROJECT CANON PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
