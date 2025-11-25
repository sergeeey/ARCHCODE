#!/usr/bin/env python3
"""
Convenience script to run ARCHCODE pipeline.

This is a wrapper around archcode.cli that ensures proper path setup.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Now import and run CLI
from src.archcode.cli import main

if __name__ == "__main__":
    main()


