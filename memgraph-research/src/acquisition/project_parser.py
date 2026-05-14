"""
Project Parser - Extract metadata from project files.

Supports:
- project.yaml (if exists)
- Auto-detection from git repo
- Fallback to directory scan
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class ProjectParser:
    """Parse project metadata from various sources."""

    def __init__(self, project_path: Path):
        self.path = Path(project_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")

    def parse(self) -> Dict[str, Any]:
        """
        Extract project metadata.

        Priority:
        1. project.yaml (if exists)
        2. Git repo detection
        3. Directory scan fallback
        """
        # Try project.yaml
        yaml_path = self.path / "project.yaml"
        if yaml_path.exists():
            return self._parse_yaml(yaml_path)

        # Try git detection
        git_path = self.path / ".git"
        if git_path.exists():
            return self._parse_git()

        # Fallback: directory scan
        return self._parse_directory()

    def _parse_yaml(self, yaml_path: Path) -> Dict[str, Any]:
        """Parse explicit project.yaml."""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        logger.info(f"✓ Parsed project.yaml: {data.get('name')}")
        return data

    def _parse_git(self) -> Dict[str, Any]:
        """Extract metadata from git repo."""
        # Get repo name from directory
        name = self.path.name

        # Detect domain from README or primary language
        domain = self._detect_domain()

        # Count files
        file_count = sum(1 for _ in self.path.rglob("*") if _.is_file())

        metadata = {
            "name": name,
            "domain": domain,
            "path": str(self.path),
            "type": "git_repo",
            "file_count": file_count,
        }

        logger.info(f"✓ Detected git repo: {name} (domain: {domain})")
        return metadata

    def _parse_directory(self) -> Dict[str, Any]:
        """Fallback: basic directory scan."""
        name = self.path.name
        domain = self._detect_domain()
        file_count = sum(1 for _ in self.path.rglob("*") if _.is_file())

        metadata = {
            "name": name,
            "domain": domain,
            "path": str(self.path),
            "type": "directory",
            "file_count": file_count,
        }

        logger.info(f"✓ Parsed directory: {name}")
        return metadata

    def _detect_domain(self) -> str:
        """
        Heuristic domain detection from file extensions.

        Returns: genomics, nlp, computer_vision, finance, general
        """
        # Check for genomic file extensions
        genomic_exts = {".vcf", ".fasta", ".fastq", ".bam", ".sam", ".bed"}
        nlp_exts = {".txt", ".md", ".pdf"}
        cv_exts = {".jpg", ".png", ".tiff", ".npy"}
        code_exts = {".py", ".ts", ".js", ".rs"}

        exts = set()
        for file_path in self.path.rglob("*"):
            if file_path.is_file():
                exts.add(file_path.suffix.lower())

        # Priority: genomics > NLP > CV > code
        if exts & genomic_exts:
            return "genomics"
        elif exts & nlp_exts and not (exts & code_exts):  # Avoid README.md = NLP
            return "nlp"
        elif exts & cv_exts:
            return "computer_vision"
        elif ".py" in exts or ".ts" in exts:
            return "general_software"
        else:
            return "unknown"

    def get_key_files(self) -> Dict[str, Optional[Path]]:
        """
        Find important project files.

        Returns dict with: readme, decisions, active_context, code_files
        """
        files = {}

        # README
        for name in ["README.md", "README.txt", "README"]:
            readme = self.path / name
            if readme.exists():
                files["readme"] = readme
                break
        else:
            files["readme"] = None

        # Decisions (ARCHCODE pattern)
        decisions = self.path / ".claude" / "memory" / "decisions.md"
        files["decisions"] = decisions if decisions.exists() else None

        # Active context
        active_ctx = self.path / ".claude" / "memory" / "activeContext.md"
        files["active_context"] = active_ctx if active_ctx.exists() else None

        # Code files (top 10 by size)
        code_files = []
        for ext in [".py", ".ts", ".js", ".rs", ".go"]:
            code_files.extend(self.path.rglob(f"*{ext}"))

        # Sort by size, take top 10
        code_files = sorted(code_files, key=lambda p: p.stat().st_size, reverse=True)[:10]
        files["code_files"] = code_files

        return files
