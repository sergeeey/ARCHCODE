#!/usr/bin/env python
"""
Stage 1: Enformer mirror test on HBB variants.
Paper 3 — addresses reviewer W5: apply mirror diagnostic to an external model.

Enformer (Avsec 2021, Nature Methods) predicts 5313 genomic tracks from sequence.
We use CTCF/ATAC/DNase tracks as structural proxy: delta = max|pred_mut - pred_wt|.

Infrastructure: PyTorch + transformers (pip install transformers torch)
Sequence:       NCBI E-utilities (no local FASTA needed)
Weights:        auto-download from HuggingFace on first run (~2 GB)
Runtime:        ~90 min CPU for 1103 HBB variants (5 sec/variant)
"""

import csv
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

ROOT  = Path(__file__).resolve().parents[4]
ATLAS = ROOT / "results/HBB_Unified_Atlas_95kb.csv"
OUT   = Path(__file__).parent / "results_enformer_mirror.json"

ENFORMER_INPUT_LEN = 393_216
TARGET_LEN         = 896
CTCF_TRACKS        = list(range(447, 456))
ATAC_TRACKS        = list(range(684, 689))
DNASE_TRACKS       = list(range(694, 699))

# UCSC Genome Browser API (0-based half-open coords; no auth needed)
UCSC_BASE   = "https://api.genome.ucsc.edu/getData/sequence"
UCSC_GENOME = "hg38"
UCSC_CHROM  = "chr11"


def fetch_sequence(acc, start, end):
    params = {"db":"nucleotide","id":acc,"seq_start":start,"seq_end":end,
               "rettype":"fasta","retmode":"text"}
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    url = NCBI_BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                fasta = r.read().decode()
            return "".join(fasta.split("\n")[1:]).upper().replace(" ","")
        except:
            if attempt == 2: raise
            time.sleep(2**attempt)


def make_mutant(seq, center, win_start, ref, alt):
    offset = center - win_start
    if seq[offset:offset+len(ref)] != ref:
        return None
    return seq[:offset] + alt + seq[offset+len(ref):]


def pad_or_crop(seq, n):
    if len(seq) < n:
        pad = (n-len(seq))//2
        return "N"*pad + seq + "N"*(n-len(seq)-pad)
    s = (len(seq)-n)//2
    return seq[s:s+n]


_BASE = {"A":0,"C":1,"G":2,"T":3}

def one_hot(seq):
    arr = np.zeros((len(seq),4), dtype=np.float32)
    for i,b in enumerate(seq):
        if b in _BASE:
            arr[i,_BASE[b]] = 1.0
    return arr


_model = None

def get_enformer():
    global _model
    if _model is None:
        import torch
        from transformers import AutoModel
        print("Loading Enformer from HuggingFace (~2 GB first run)...")
        _model = AutoModel.from_pretrained(
            "EleutherAI/enformer-official-rough", trust_remote_code=True).eval()
        if torch.cuda.is_available():
            _model = _model.cuda()
        print("Enformer loaded.")
    return _model


def predict(seq):
    import torch
    model = get_enformer()
    x = torch.from_numpy(one_hot(pad_or_crop(seq, ENFORMER_INPUT_LEN))).unsqueeze(0)
    if next(model.parameters()).is_cuda:
        x = x.cuda()
    with torch.no_grad():
        out = model(x)
    return out["human"].squeeze(0).cpu().numpy()


def delta_score(wt, mut, tracks):
    bins = slice(TARGET_LEN//2-5, TARGET_LEN//2+6)
    return float(np.max(np.abs(mut[bins][:,tracks] - wt[bins][:,tracks])))


def auc_mw(p, b):
    if not p or not b: return float("nan")
    u,_ = mannwhitneyu(-np.array(p,float), -np.array(b,float), alternative="two-sided")
    return float(u/(len(p)*len(b)))


def main():
    rows = list(csv.DictReader(open(ATLAS)))
    print(f"Atlas: {len(rows)} variants")
    results = {"locus":"HBB","model":"Enformer","variants":[]}
    by_label = {"Pathogenic":[], "Benign":[]}
    by_cat   = {}

    for i, row in enumerate(rows):
        pos = int(row["Position_GRCh38"])
        ref = row["Ref"].upper()
        alt = row["Alt"].upper()
        label = row["Label"]
        cat = row["Category"]

        if max(len(ref),len(alt)) > 20:
            results["variants"].append({"pos":pos,"label":label,"cat":cat,"status":"skipped_complex"})
            continue

        half = ENFORMER_INPUT_LEN // 2
        start0 = max(0, pos - 1 - half)  # 1-based pos -> 0-based
        end0   = pos - 1 + half + len(ref)

        try:
            seq = fetch_sequence(UCSC_CHROM, start0, end0)
            time.sleep(0.12)
        except Exception as e:
            results["variants"].append({"pos":pos,"label":label,"cat":cat,"status":f"fetch_error:{e}"})
            continue

        mut = make_mutant(seq, pos-1, start0, ref, alt)  # both 0-based
        if mut is None:
            results["variants"].append({"pos":pos,"label":label,"cat":cat,"status":"ref_mismatch"})
            continue

        try:
            t0 = time.time()
            wt_p  = predict(seq)
            mut_p = predict(mut)
            dt = time.time() - t0
        except Exception as e:
            results["variants"].append({"pos":pos,"label":label,"cat":cat,"status":f"model_error:{e}"})
            continue

        d_ctcf  = delta_score(wt_p, mut_p, CTCF_TRACKS)
        d_atac  = delta_score(wt_p, mut_p, ATAC_TRACKS)
        d_all   = max(d_ctcf, d_atac, delta_score(wt_p, mut_p, DNASE_TRACKS))

        entry = {"pos":pos,"ref":ref,"alt":alt,"label":label,"cat":cat,
                  "delta_ctcf":round(d_ctcf,6),"delta_atac":round(d_atac,6),
                  "delta_max":round(d_all,6),
                  "archcode_lssim":float(row.get("ARCHCODE_LSSIM",0)),
                  "runtime_sec":round(dt,2),"status":"ok"}
        results["variants"].append(entry)
        by_label[label].append(d_all)
        by_cat.setdefault(cat,{"Pathogenic":[],"Benign":[]})
        by_cat[cat][label].append(d_all)

        if (i+1)%50==0:
            n_ok = sum(1 for v in results["variants"] if v.get("status")=="ok")
            print(f"  [{i+1}/{len(rows)}] ok={n_ok}")
            OUT.write_text(json.dumps(results, indent=2))

    auc_std = auc_mw(by_label["Pathogenic"], by_label["Benign"])
    auc_inv = auc_mw([-s for s in by_label["Pathogenic"]], [-s for s in by_label["Benign"]])
    mirror_gap = round(abs(auc_std-(1-auc_inv)), 4)

    within_cat = {}
    for cat, d in by_cat.items():
        if d["Pathogenic"] and d["Benign"]:
            within_cat[cat] = {"n_path":len(d["Pathogenic"]),"n_benign":len(d["Benign"]),
                                 "auc":round(auc_mw(d["Pathogenic"],d["Benign"]),4)}

    results["diagnostics"] = {
        "global_auc":round(auc_std,4), "inverted_auc":round(auc_inv,4),
        "mirror_gap":mirror_gap,
        "mirror_verdict":"LOOKUP-LIKE (gap<0.10)" if mirror_gap<0.10 else "GENUINE SIGNAL (gap≥0.10)",
        "within_category":within_cat,
        "n_path":len(by_label["Pathogenic"]), "n_benign":len(by_label["Benign"])
    }
    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nDone -> {OUT}")
    print(json.dumps(results["diagnostics"], indent=2))


if __name__ == "__main__":
    main()
