import sys


def main(argv=None):
    print("ARCHCODE pipeline skeleton.")
    print("Planned interface:")
    print("  python tools/run_pipeline.py run-pipeline --mode fast")
    print("  python tools/run_pipeline.py run-pipeline --mode full")
    print()
    print("Full implementation is private.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
