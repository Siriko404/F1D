#!/usr/bin/env python3
"""REP-3 scoring: stratified P/R for v1 vs v2 using my blind labels.
Labels assigned by reading TEXT ONLY (construct: attention to cash level OR
its retain/return/deploy disposition), independent of which bucket fired.
Stratified estimator over v2 strata (weights = population stratum sizes).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "tmp" / "_cash_lex_gold_meta.json").read_text())

# my blind labels (1 = attention to cash holdings/disposition)
LAB = {
 1:0,2:1,3:1,4:0,5:1,6:1,7:1,8:0,9:1,10:1,11:1,12:1,13:0,14:0,15:1,16:1,17:1,18:1,19:1,20:0,
 21:0,22:1,23:1,24:1,25:0,26:1,27:1,28:1,29:1,30:0,
 31:0,32:0,33:0,34:0,35:0,36:0,37:0,38:0,39:0,40:0,41:0,42:0,43:1,44:0,45:0,46:0,47:0,48:0,49:0,50:1,
 51:0,52:0,53:0,54:0,55:0,56:0,57:0,58:0,59:0,60:0,61:0,62:0,63:0,64:0,65:0,66:0,67:1,68:0,69:0,70:0,
 71:0,72:0,73:0,74:0,75:0,
 76:0,77:0,78:1,79:0,80:0,81:0,82:0,83:0,84:0,85:0,86:0,87:0,88:0,89:0,90:0,
}
W = META["weights"]          # population sizes per v2 stratum
rows = META["rows"]

strata = {}
for gid, info in rows.items():
    s = info["stratum"]
    strata.setdefault(s, []).append((int(LAB[int(gid)]), info["v1"], info["v2"]))

def stratified(metric_pred):
    """Return (precision, recall, predpos, truepos, pos) population estimates."""
    Pp = TP = P = 0.0
    for s, items in strata.items():
        w = W[s]; n = len(items)
        mean_pred = sum(metric_pred(v1, v2) for (_, v1, v2) in items) / n
        mean_tp   = sum((metric_pred(v1, v2) and lab) for (lab, v1, v2) in items) / n
        mean_pos  = sum(lab for (lab, v1, v2) in items) / n
        Pp += w * mean_pred; TP += w * mean_tp; P += w * mean_pos
    prec = TP / Pp if Pp else float("nan")
    rec = TP / P if P else float("nan")
    return prec, rec, Pp, TP, P

# per-stratum positive rate (for transparency)
print("per-stratum: n, pos_rate, weight")
for s, items in strata.items():
    n = len(items); pr = sum(l for l, _, _ in items) / n
    print(f"  {s:5} n={n:2d} pos={pr:.3f} w={W[s]:,}")

pv1 = stratified(lambda v1, v2: v1)
pv2 = stratified(lambda v1, v2: v2)
print(f"\nv1: precision={pv1[0]:.3f}  recall={pv1[1]:.3f}  (predpos~{pv1[2]:,.0f}, TP~{pv1[3]:,.0f}, pos~{pv1[4]:,.0f})")
print(f"v2: precision={pv2[0]:.3f}  recall={pv2[1]:.3f}  (predpos~{pv2[2]:,.0f}, TP~{pv2[3]:,.0f}, pos~{pv2[4]:,.0f})")

# recall WITHIN cash-family universe (exclude the noisy no-cashfam stratum)
def recall_cashfam(metric_pred):
    TP = P = 0.0
    for s in ("flag", "ufcf"):
        items = strata[s]; w = W[s]; n = len(items)
        TP += w * sum((metric_pred(v1, v2) and lab) for (lab, v1, v2) in items) / n
        P  += w * sum(lab for (lab, v1, v2) in items) / n
    return TP / P if P else float("nan")
print(f"\nrecall within cash-family universe:  v1={recall_cashfam(lambda a,b:a):.3f}  v2={recall_cashfam(lambda a,b:b):.3f}")
print(f"labeled positives total: {sum(LAB.values())}/90")
