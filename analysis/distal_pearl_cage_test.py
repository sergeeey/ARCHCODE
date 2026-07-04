#!/usr/bin/env python3
"""Distal pearl CAGE rescue-or-kill test (2026-07-04). Real ClinVar SNVs only."""

import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("D:/ДНК")
sys.path.insert(0, str(ROOT / "scripts"))
from alphagenome_real_experiments import get_client, make_interval, make_variant

ATLAS = ROOT / "results" / "HBB_Clinical_Atlas_REAL.csv"
OUT = ROOT / "results" / "distal_pearl_cage_test.json"


def clean_snv(ref, alt):
    return (
        isinstance(ref, str)
        and isinstance(alt, str)
        and len(ref) == 1
        and len(alt) == 1
        and ref in "ACGT"
        and alt in "ACGT"
    )


def cage_pct(client, interval, pos, ref, alt):
    from alphagenome.models.dna_output import OutputType

    var = make_variant("chr11", pos, ref, alt)
    out = client.predict_variant(
        interval, var, requested_outputs=[OutputType.CAGE], ontology_terms=["EFO:0002784"]
    )
    if out.reference.cage is None or out.alternate.cage is None:
        return None
    ref_c = np.array(out.reference.cage.values)
    alt_c = np.array(out.alternate.cage.values)
    if ref_c.size == 0 or alt_c.size == 0:
        return None
    return float((np.mean(alt_c) - np.mean(ref_c)) / (np.mean(ref_c) + 1e-10) * 100)


def main():
    a = pd.read_csv(ATLAS)
    z = a[(a["Position_GRCh38"] >= 5226500) & (a["Position_GRCh38"] <= 5227050)].copy()
    z["clean"] = [clean_snv(r, al) for r, al in zip(z["Ref"], z["Alt"])]
    z = z[z["clean"]]
    pearls = z[z["Pearl"] == True]
    ctrls = (
        z[(z["Pearl"] == False) & (z["Category"] == "missense")]
        .drop_duplicates(subset=["Position_GRCh38"])
        .head(10)
    )
    print(f"Clean-SNV distal pearls: {len(pearls)} | matched missense controls: {len(ctrls)}")

    client = get_client()
    interval = make_interval("chr11", 5200000, 5240000)

    def run(rows, label):
        res = []
        for _, r in rows.iterrows():
            pos, ref, alt = int(r["Position_GRCh38"]), str(r["Ref"]), str(r["Alt"])
            try:
                pct = cage_pct(client, interval, pos, ref, alt)
                print(f"  [{label}] {pos} {ref}>{alt} [{r['Category']}] CAGE {pct:+.2f}%")
                res.append(
                    {
                        "pos": pos,
                        "ref": ref,
                        "alt": alt,
                        "cat": r["Category"],
                        "cage_pct": pct,
                        "is_pearl": bool(r["Pearl"]),
                    }
                )
            except Exception as e:
                print(f"  [{label}] {pos} {ref}>{alt} ERROR: {e}")
            time.sleep(0.4)
        return res

    print("\n=== PEARLS ===")
    pr = run(pearls, "pearl")
    print("\n=== CONTROLS ===")
    cr = run(ctrls, "ctrl")

    pv = [x["cage_pct"] for x in pr if x["cage_pct"] is not None]
    cv = [x["cage_pct"] for x in cr if x["cage_pct"] is not None]
    summary = {
        "pearl_n": len(pv),
        "ctrl_n": len(cv),
        "pearl_cage_pct": pv,
        "ctrl_cage_pct": cv,
        "pearl_mean": float(np.mean(pv)) if pv else None,
        "ctrl_mean": float(np.mean(cv)) if cv else None,
    }
    if len(pv) >= 1 and len(cv) >= 2:
        from scipy.stats import mannwhitneyu

        try:
            u, p = mannwhitneyu(pv, cv, alternative="less")
            summary["mannwhitney_p_pearl_more_disrupted"] = float(p)
        except Exception as e:
            summary["mannwhitney_error"] = str(e)

    out = {
        "experiment": "distal pearl CAGE rescue-or-kill",
        "date": "2026-07-04",
        "assay": "AlphaGenome predict_variant CAGE K562, real ClinVar SNVs",
        "pearls": pr,
        "controls": cr,
        "summary": summary,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {OUT}")
    print("SUMMARY:", json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
