# -*- coding: utf-8 -*-
"""Rigorous §4.5 claim verification. Ground truth = rob_4tables.tex cells (parsed,
not hand-typed) + the two result JSONs. Checks each claimed number appears in the
right prop with the right stars; runs internal-arithmetic + honesty scans."""
import json, re
from pathlib import Path
ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing")
TEX = (ROOT/"F1D/outputs/econometric/firstdeal_robustness/2026-06-23_162451/rob_4tables.tex").read_text(encoding="utf-8")
P45 = json.load(open(ROOT/"F1D-phase3/docs/Thesis/rewrite/_final/section4.5_paragraph_ledger.json", encoding="utf-8"))
J = json.load(open(ROOT/"F1D-phase3/tmp/logit_fullcontrols_results.json", encoding="utf-8"))
F = json.load(open(ROOT/"F1D-phase3/tmp/fe_results.json", encoding="utf-8"))
props = {pr["prop_id"]: pr for pa in P45["paragraphs"] for pr in pa["proposition_chain"]}

def ptext(pid):
    p = props[pid]; return p["statement"] + " " + " ".join(p.get("numbers", []))

def cellval(cell):
    cell = cell.strip()
    if cell in ("---", ""): return (None, "")
    st = ""
    m = re.search(r'\$\^\{(\*+)\}\$', cell)
    if m: st = m.group(1)
    v = re.search(r'-?\d+\.\d+', cell)
    return (v.group(0) if v else None, st)

# split into table blocks
lines = TEX.splitlines()
def block(tag_start, tag_end=None):
    s = next(i for i,l in enumerate(lines) if tag_start in l)
    e = next((i for i,l in enumerate(lines) if tag_end and tag_end in l), len(lines))
    return lines[s:e]
B = {
 "5.2": block("Table 5.2", "Table 5.3"),
 "5.3": block("Table 5.3", "Table 5.4"),
 "5.4": block("Table 5.4", "Table 5.5"),
 "5.5": block("Table 5.5"),
}
def row(tbl, label):
    blk = B[tbl]
    for i, ln in enumerate(blk):
        s = ln.strip()
        if s.startswith(label+" &") or s.startswith(label+"&"):
            cells = [c.replace(r"\\","").strip() for c in s.split("&")[1:]]
            return [cellval(c) for c in cells]
    return None

def serow(tbl, label):
    """the SE line is the line immediately after the coef row; cells like '(0.0140)'."""
    blk = B[tbl]
    for i, ln in enumerate(blk):
        s = ln.strip()
        if s.startswith(label+" &") or s.startswith(label+"&"):
            se = blk[i+1].strip()
            cells = [c.replace(r"\\","").strip() for c in se.split("&")[1:]]
            out = []
            for c in cells:
                m = re.search(r'\((\d+\.\d+)\)', c)
                out.append(m.group(1) if m else None)
            return out
    return None

flags=[]
def chk(desc, ok, got=""):
    print(f"  [{'OK ' if ok else 'FLAG'}] {desc}" + (f"   {got}" if not ok else ""))
    if not ok: flags.append(desc)
def star_lbl(s): return s if s else "n.s."

def in_prop(pid, val, stars):
    t = ptext(pid)
    if val is None: return False, "no value parsed"
    if val not in t: return False, f"{val} ABSENT from prop"
    if stars:
        ok = (val+stars in t) and (val+stars+"*" not in t)
        return ok, f"want {val}{stars}"
    else:
        bad = re.search(re.escape(val)+r'\*', t)
        return (bad is None), f"want {val} as n.s. (no star)"

print("="*64)
print("A. TABLE PROPS  (ground truth parsed from rob_4tables.tex)")
print("="*64)

# --- T5.2 PreAnnounceQtr: 16 cols; all-cash-CshR=8, all-cash-UncR=9, all-stock-UncR=13
r = row("5.2","PreAnnounceQtr")
chk("T5.2 PreAnnounceQtr -> 16 cells", r is not None and len(r)==16, f"got {len(r) if r else None}")
cells = {"all-cash-CshR": r[8], "all-cash-UncR": r[9], "all-stock-UncR": r[13]}
print(f"   parsed all-deals: cash-CshR={r[8]} cash-UncR={r[9]} stock-UncR={r[13]}  (first-deal cash-UncR={r[1]} <- must NOT appear)")
for lbl,(v,s) in cells.items():
    ok,msg = in_prop("4.5-PARA1-a", v, s); chk(f"PARA1-a {lbl} = {v}{star_lbl(s)}", ok, msg)
chk("PARA1-a does NOT cite first-deal cash-UncR 0.0461 as all-deals", "0.0461" not in ptext("4.5-PARA1-a"))

# --- T5.3 matched: all-UncRes = col idx2
for label in ["PRE1","Drop: PRE1 $-$ GAP","Drop: PRE1 $-$ POST"]:
    v,s = row("5.3",label)[2]
    ok,msg = in_prop("4.5-PARA2-a", v, s); chk(f"PARA2-a T5.3 {label} all-UncRes = {v}{star_lbl(s)}", ok, msg)

# --- T5.4 by-payment: all-cash=idx2, all-stock=idx3
for label,idx,who in [("PRE1",2,"cash"),("PRE1",3,"stock"),
                      ("Drop: PRE1 $-$ POST",2,"cash"),("Drop: PRE1 $-$ GAP",3,"stock")]:
    v,s = row("5.4",label)[idx]
    ok,msg = in_prop("4.5-PARA2-b", v, s); chk(f"PARA2-b T5.4 {label} {who} = {v}{star_lbl(s)}", ok, msg)

# --- T5.5 Wald: all-UncRes Wald=idx3, cause CashR(m)=idx4, thesis Wald=idx0; cash/stock arms idx3
cash = row("5.5","Pre-announce qtr, Cash")[3]
stock = row("5.5","Pre-announce qtr, Stock")[3]
waldrow = row("5.5","Cash $-$ Stock (Wald)")
wald, cause, fd = waldrow[3], waldrow[4], waldrow[0]
print(f"   T5.5 all-deals: cash={cash} stock={stock} Wald={wald} cause-CashR(m)={cause} | first-deal-Wald={fd}")
for lbl,(v,s) in [("cash arm",cash),("stock arm",stock),("Wald",wald),("cause CashR(m)",cause),("first-deal Wald (inline)",fd)]:
    ok,msg = in_prop("4.5-PARA3-a", v, s); chk(f"PARA3-a T5.5 {lbl} = {v}{star_lbl(s)}", ok, msg)
ca,so,wa = float(cash[0]), float(stock[0]), float(wald[0])
chk(f"PARA3-a internal arithmetic: cash({ca}) - stock({so}) = Wald({wa})", abs((ca-so)-wa) < 0.0002, f"got {ca-so:.4f}")

print("="*64)
print("A2. STANDARD ERRORS  (parsed from .tex SE rows, must appear in prop)")
print("="*64)
def se_check(pid, tbl, label, idx, who):
    se = serow(tbl, label)[idx]
    ok = se is not None and se in ptext(pid)
    chk(f"{pid} {tbl} {label} {who} SE {se}", ok, f"SE {se} absent")
se_check("4.5-PARA1-a","5.2","PreAnnounceQtr",9,"cash-UncR")
se_check("4.5-PARA1-a","5.2","PreAnnounceQtr",8,"cash-CshR")
se_check("4.5-PARA1-a","5.2","PreAnnounceQtr",13,"stock-UncR")
se_check("4.5-PARA2-a","5.3","PRE1",2,"all-UncRes")
se_check("4.5-PARA2-a","5.3","Drop: PRE1 $-$ GAP",2,"all-UncRes")
se_check("4.5-PARA2-a","5.3","Drop: PRE1 $-$ POST",2,"all-UncRes")
se_check("4.5-PARA2-b","5.4","PRE1",2,"cash")
se_check("4.5-PARA2-b","5.4","PRE1",3,"stock")
se_check("4.5-PARA2-b","5.4","Drop: PRE1 $-$ POST",2,"cash")
se_check("4.5-PARA2-b","5.4","Drop: PRE1 $-$ GAP",3,"stock")
se_check("4.5-PARA3-a","5.5","Pre-announce qtr, Cash",3,"cash arm")
se_check("4.5-PARA3-a","5.5","Pre-announce qtr, Stock",3,"stock arm")
se_check("4.5-PARA3-a","5.5","Cash $-$ Stock (Wald)",3,"Wald")
se_check("4.5-PARA3-a","5.5","Cash $-$ Stock (Wald)",4,"cause")

print("="*64)
print("B. LOGIT / FE PROPS  (ground truth from result JSONs)")
print("="*64)
def r4(x): return f"{x:.4f}"
A,FA = J["TEST_A"], F["TEST_A"]
for lbl,val,star in [("LPM",r4(A["lpm"]["key"]["beta"]),"***"),("logit",r4(A["logit"]["key"]["beta"]),"***"),("FE-LPM",r4(FA["key"]["beta"]),"***")]:
    ok,msg = in_prop("4.5-PARA1-b", val, star); chk(f"PARA1-b {lbl} = {val}{star}", ok, msg)
chk(f"PARA1-b LPM p2={A['lpm']['key']['p2']:.4f} < .01 -> *** valid", A['lpm']['key']['p2']<.01)
chk(f"PARA1-b FE  p2={FA['key']['p2']:.4f} < .01 -> *** valid", FA['key']['p2']<.01)
chk("PARA1-b N 40,004 present", "40,004" in ptext("4.5-PARA1-b"))
chk("PARA1-b FE N 39,557 present", "39,557" in ptext("4.5-PARA1-b"))
B_,FB = J["TEST_B"], F["TEST_B"]
for lbl,val,star in [("LPM",r4(B_["lpm"]["key"]["beta"]),"**"),("logit",r4(B_["logit"]["key"]["beta"]),"**"),("FE-LPM",r4(FB["key"]["beta"]),"")]:
    ok,msg = in_prop("4.5-PARA3-b", val, star); chk(f"PARA3-b {lbl} = {val}{star_lbl(star)}", ok, msg)
chk(f"PARA3-b LPM p2={B_['lpm']['key']['p2']:.4f} < .05 -> ** valid", B_['lpm']['key']['p2']<.05)
chk(f"PARA3-b FE  p2={FB['key']['p2']:.4f} > .10 -> n.s. valid", FB['key']['p2']>.10)
chk("PARA3-b base rate 88.9% present", "88.9" in ptext("4.5-PARA3-b"))
chk(f"PARA3-b cash982+stock123==1105 & ==base {B_['cash_base_rate']:.4f}", 982+123==1105 and abs(982/1105-B_['cash_base_rate'])<0.001)

print("="*64)
print("C. DESCRIPTIVE SAMPLE STATS  (now confirmed vs json: event_rate / n_cash / n_stock)")
print("="*64)
chk(f"PARA1-b deal-rate 2.84% == TEST_A.event_rate {A['event_rate']:.5f}",
    "2.84%" in ptext("4.5-PARA1-b") and abs(A['event_rate']-0.0284)<0.0005,
    f"event_rate={A['event_rate']:.5f}, n_events={A['n_events']}")
chk(f"PARA3-b cash 982 == TEST_B.n_cash {B_['n_cash']}", "982" in ptext("4.5-PARA3-b") and B_['n_cash']==982)
chk(f"PARA3-b stock 123 == TEST_B.n_stock {B_['n_stock']}", "123" in ptext("4.5-PARA3-b") and B_['n_stock']==123)

print("="*64)
print("D. HONESTY / REGISTER")
print("="*64)
FORBID=["suppress","dampen","strict specificity"]
for pid,p in props.items():
    t=(p["statement"]+" "+p.get("reason","")).lower()
    for w in FORBID: chk(f"{pid}: no '{w}'", w not in t)
chk("PARA3-a locks: mechanism-open + concentration-not-strict-specificity",
    {"mechanism-open","concentration-not-strict-specificity"}.issubset(set(props["4.5-PARA3-a"]["register_locks"])))
chk("PARA1-b is correlational-only (no within-firm overclaim on pooled logit)",
    props["4.5-PARA1-b"]["register_locks"]==["correlational"])

print("="*64)
if flags:
    print(f"RESULT: {len(flags)} FLAG(S)")
    for f in flags: print("   -", f)
else:
    print("RESULT: ALL CLAIMS VERIFIED vs PRIMARY SOURCE. 0 flags.")
