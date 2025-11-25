"""
ARCHCODE command-line interface (skeleton).

This file intentionally contains no core simulation or RS-engine logic.
It only defines public entry points and help messages.
"""

import argparse


def cmd_sim(args: argparse.Namespace) -> None:
    print("ARCHCODE simulation skeleton.")
    print("Core loop-extrusion engine is not included in the public release.")


def cmd_rs(args: argparse.Namespace) -> None:
    print("ARCHCODE RS-suite skeleton (RS-09/10/11).")
    print("Metric definitions and formulas are kept private.")


def cmd_hic(args: argparse.Namespace) -> None:
    print("ARCHCODE Hi-C validation skeleton.")
    print("Full validation workflow will be available in future versions.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="archcode",
        description="ARCHCODE – framework for 3D genome architecture and loop extrusion modeling (public skeleton).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sim_p = subparsers.add_parser("sim", help="Run simulation (skeleton).")
    sim_p.set_defaults(func=cmd_sim)

    rs_p = subparsers.add_parser("rs", help="Evaluate RS-metrics (skeleton).")
    rs_p.set_defaults(func=cmd_rs)

    hic_p = subparsers.add_parser("hic", help="Validate against Hi-C (skeleton).")
    hic_p.set_defaults(func=cmd_hic)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
