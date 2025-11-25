import argparse


def cmd_sim(args):
    print("ARCHCODE simulation skeleton.")
    print("Core loop-extrusion engine is private.")


def cmd_rs(args):
    print("ARCHCODE RS-suite skeleton (RS-09/10/11).")
    print("Metric definitions are kept private.")


def cmd_hic(args):
    print("ARCHCODE Hi-C validation skeleton.")
    print("Full workflow will appear in future versions.")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="archcode",
        description="ARCHCODE тАУ 3D genome architecture modeling (public skeleton).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("sim")
    sp.set_defaults(func=cmd_sim)

    rp = sub.add_parser("rs")
    rp.set_defaults(func=cmd_rs)

    hp = sub.add_parser("hic")
    hp.set_defaults(func=cmd_hic)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
