#!/usr/bin/env python3
"""MEMGRAPH DAY 1 SETUP TEST - Minimal version"""

import sys


def test_imports():
    """Test core dependencies."""
    print("=" * 60)
    print("MEMGRAPH DAY 1 SETUP TEST")
    print("=" * 60)
    print()

    required = {
        "anthropic": "Claude API",
        "networkx": "Graph fallback",
        "yaml": "Config parsing",
    }

    missing = []
    for pkg, desc in required.items():
        try:
            if pkg == "yaml":
                __import__("yaml")
            else:
                __import__(pkg)
            print(f"✓ {pkg:20s} {desc}")
        except ImportError:
            print(f"✗ {pkg:20s} {desc} - NOT FOUND")
            missing.append(pkg)

    print()

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("  pip install anthropic networkx pyyaml")
        return False
    else:
        print("✅ Core dependencies installed")
        print()
        print("Next steps:")
        print("  1. cd memgraph-research")
        print("  2. pip install -r requirements.txt")
        print("  3. Test graph manager and embeddings")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
