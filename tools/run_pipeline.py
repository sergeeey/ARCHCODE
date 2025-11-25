"""
ARCHCODE reproducible science pipeline (skeleton).

This script documents the planned public interface for running
ARCHCODE pipelines. The full implementation is kept private.
"""

import sys


def main(argv=None) -> int:
    print("ARCHCODE pipeline skeleton.")
    print("Planned interface:")
    print("  python tools/run_pipeline.py run-pipeline --mode fast")
    print("  python tools/run_pipeline.py run-pipeline --mode full")
    print()
    print("The full reproducible pipeline will be released in future versions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
