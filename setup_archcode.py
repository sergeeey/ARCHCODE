#!/usr/bin/env python3
"""
ARCHCODE Auto-Setup Script

Устанавливает все зависимости и проверяет работоспособность проекта.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run command and return success status."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False


def main() -> None:
    """Main setup function."""
    print("=" * 60)
    print("🚀 ARCHCODE v1.0-alpha - Auto Setup")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Install base requirements
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing ARCHCODE dependencies",
    ):
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Install dev requirements
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"],
        "Installing development dependencies",
    ):
        print("⚠️  Warning: Some dev dependencies failed to install")

    # Verify imports
    print("\n" + "=" * 60)
    print("🔍 Verifying critical imports")
    print("=" * 60)

    critical_imports = [
        "numpy",
        "scipy",
        "numba",
        "pandas",
        "yaml",
        "torch",
        "matplotlib",
        "biopython",
        "cooler",
        "pydantic",
    ]

    failed_imports = []
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n⚠️  Warning: Failed to import: {', '.join(failed_imports)}")
        print("   Some features may not work correctly")
    else:
        print("\n✅ All critical imports successful!")

    # Run basic tests
    print("\n" + "=" * 60)
    print("🧪 Running basic tests")
    print("=" * 60)

    if Path("tests").exists():
        run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            "Running pytest",
        )

    print("\n" + "=" * 60)
    print("✅ ARCHCODE setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review config/ files")
    print("  2. Check risk_matrix/ for engineering unknowns")
    print("  3. Start with research_specs/RS-01.md")
    print("\nHappy coding! 🧬")


if __name__ == "__main__":
    main()










