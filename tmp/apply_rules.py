#!/usr/bin/env python3
"""Deterministic proposition identification — PROPOSITION_RULES.md as executable code.

Reads thesis_propositions.json (249 seeds), applies the 13 surface-marker triggers
+ special-block rules, emits filled proposition rows into thesis_propositions_A.json.
NEVER hallucinates — every trigger is substring/regex match against closed lists.

Run:  python tmp/apply_rules.py [--block "front-matter"]
"""
import json
import re
import sys
from pathlib import Path
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "Thesis" / "audit"
SEED_FILE = AUDIT / "thesis_propositions.json"
OUT_FILE = AUDIT / "thesis_propositions_A.json"

# ═══════════════════════════════════════════════════════════
# §1A. CITED-AUTHOR → bibkey
# ═══════════════════════════════════════════════════════════
SURNAME_MAP = OrderedDict([
    ("Dzielinski|Wagner|Zeckhauser", "dwz"),
    ("Loughran|McDonald", "lm2011"),
    ("Baker|Bloom", "baker2016"),           # Baker-Bloom-Davis → baker2016
    ("Davis", "davis2016"),                  # standalone → davis2016; ambiguity: global check
    ("Hassan", "hassan2020"),
    ("Hoberg|Phillips|TNIC", "hoberg2010"), # placeholder; co-cited with hoberg2016
    ("Bushee|Gow|Taylor", "bushee2018"),
    ("Everhart|Kravet|McVay|Warren", "everhart2025"),
    ("Gokkaya|Liu|Stulz", "gokkaya2025"),
    ("Lerman|Steffen|Zhang", "lerman2026"),
    ("Ragozzino|Reuer", "ragozzino2024"),
    ("Thewissen|Arslan-Ayaydin", "thewissen2024"),
])

# §1B. DATA VENDORS
VENDORS = ["Capital IQ", "SDC", "Compustat", "CRSP", "IBES"]

# §1C. LIT-PHRASES → (route, bibkeys)
LIT_PHRASES = [
    ("growing literature", "nlm",
     ["thewissen2024", "ragozzino2024", "everhart2025", "gokkaya2025"]),
    ("nearest work", "nlm", ["thewissen2024", "ragozzino2024"]),
    ("nearest to", "nlm", ["thewissen2024", "ragozzino2024"]),
    ("the nearest", "nlm", ["thewissen2024", "ragozzino2024"]),
    ("two papers closest to ours", "bib", None),
    ("what this work has not measured", "nlm",
     ["thewissen2024", "ragozzino2024", "everhart2025", "gokkaya2025"]),
    ("uncertainty dimension is still missing", "nlm",
     ["thewissen2024", "ragozzino2024", "everhart2025", "gokkaya2025"]),
    ("left empty", "nlm",
     ["thewissen2024", "ragozzino2024", "everhart2025", "gokkaya2025"]),
    ("standard cash regression", "missing-cite", None),
    ("determinants of cash", "missing-cite", None),
    ("established precedent", "nlm-or-missing", None),
    ("established uncertainty measures", "nlm-or-missing", None),
]

# §1D. METHOD MARKERS
METHOD_MARKERS = [
    "we estimate", "we regress", "regress", "fixed effect", "fixed-effect",
    "two-way", "2wfe", "clustered", "cluster", "ols", "one-tailed",
    "two-tailed", "wald", "interact", "pooled", "matched universe",
    "matched", "event study", "event-time", "difference-in-differences",
    "placebo", "baseline", "exclud", "drop", "cap" , "winsor",
    "lag", "partial-adjustment", "tokeniz", "parsed", "link table",
    "match", "require at least", "qualif", "sample", "tercile", "median",
    "decomposition", "residual"
]

# §1E. HYPOTHESIS MARKERS
HYPOTHESIS_MARKERS = [
    "\\textbf{h", "h1", "h1a", "h1b", " should ", "predicts",
    "prediction", "should be elevated", "should follow",
    "should resolve", "should persist",
]

# §1F. INFERENCE CONNECTIVES
INFERENCE_CONNECTIVES = [
    "so ", "therefore", "thus", " hence ", "because",
    "licenses the reading", "implies", "is the trace predicted",
    "is the differential-timing prediction", "we read it as",
    "we read this as", "so that", "which is what makes",
]

# §1G. CAVEAT MARKERS — each is a regex requiring word boundaries
CAVEAT_MARKERS = [
    r"\bnot a\b", r"\bnot yet\b", r"\bclaim no\b", r"\bno identification\b",
    r"\bcorrelational\b", r"\bfailure to find\b", r"\bfragile\b",
    r"\bsupported but\b", r"\blimit(?:ation|s)?\b", r"\bdoes not exclude\b",
    r"\bnot proof of absence\b", r"\bnot a powered\b",
    r"\bnot itself a test\b", r"\bdeliberately hedged\b", r"\bat one remove\b",
    r"\bcannot\b", r"\bleaves\b", r"\bnot a headline\b", r"\bnot pillars\b",
]
CAVEAT_RE = re.compile("|".join(CAVEAT_MARKERS), re.IGNORECASE)

# §1H. NUMBER PATTERNS
NUMBER_PAT = re.compile(
    r"-?\d*\.\d+|\bSE\s|\bR\^?2\b|\bn\.s\.\b|"
    r"\d{2,3},\d{3}|significant at|\d+\\?%\s*level|p<[\d.]"
)

# §1I. FORMULA PATTERNS
MATH_PAT = re.compile(r"\$[^$]+\$")
EQ_PAT = re.compile(r"equation\s*[14]|equation-[14]")

# §1J. CONSISTENCY / CROSS-REF EQUIVALENCE MARKERS
EQUIVALENCE_MARKERS = [
    "same table", "same event", "as in main analysis",
    "otherwise that of", "the same as", "identical",
    "nearly identical", "economically the same", "same forces",
    "same way", "reproduces the run-up", "against 0.0461 there",
]

# ═══════════════════════════════════════════════════════════
# BLOCK PREFIX MAP (§5A)
# ═══════════════════════════════════════════════════════════
PREFIX = {
    "front-matter": "FM",
    "Introduction": "INT",
    "Conceptual Framework": "CF",
    "Hypothesis Development": "HYP",
    "Estimation of the Main Variable": "EMV",
    "Methodology and Empirical Design": "MED",
    "Specification and Measurement of Key Constructs": "KC",
    "Data, Sample, and Variable Construction": "DS",
    "Main Analysis 1: The Pre-Announcement Run-Up": "MA1",
    "Main Analysis 2: Differential Timing Around the Announcement": "MA2",
    "Main Analysis 3: Cash-Specificity": "MA3",
    "Ruling Out Analyst Scrutiny": "RAS",
    "The Presentation-Side Contrast": "PSC",
    "Summary of Findings": "SUM",
    "Contributions": "CON",
    "Limitations": "LIM",
    "Directions for Future Research": "FUT",
    "bibliography": "BIB",
    "appendix-prose": "APX",
    "appendix-vartable": "VAR",
    "tables": "TAB",
}

# P2_REF for E rows in these blocks
P2_NUMERIC_BLOCKS = {"MA1", "MA2", "MA3", "RAS", "PSC"}

# ═══════════════════════════════════════════════════════════
# TRIGGER HELPERS
# ═══════════════════════════════════════════════════════════

def ic(s):
    """Case-insensitive regex escape."""
    return re.compile(re.escape(s), re.IGNORECASE)


def any_match(s, markers):
    """Case-insensitive substring match."""
    lo = s.lower()
    return any(m.lower() in lo for m in markers)


def extract_cite_keys(span):
    """Extract comma-separated bibkeys from \\citep{...} or \\citet{...}."""
    keys = []
    for m in re.finditer(r"\\(?:citep|citet)\{([^}]+)\}", span):
        for k in m.group(1).split(","):
            keys.append(k.strip())
    return keys


def surname_match(span):
    """Return list of bibkeys whose surname tokens appear in span (T2)."""
    lo = span.lower()
    matches = set()
    for pattern, key in SURNAME_MAP.items():
        if any(re.search(r"\b" + t.lower() + r"\b", lo) for t in pattern.split("|")):
            matches.add(key)
    # Davis ambiguity: if "global" present → davis2016; if Baker/Bloom → via baker2016 entry
    # already handled by checking both patterns
    return list(matches)


def lit_phrase_match(span):
    """Return list of (route, bibkeys) for lit-phrases found in span (T4)."""
    lo = span.lower()
    hits = []
    for phrase, route, keys in LIT_PHRASES:
        if phrase.lower() in lo:
            hits.append((route, keys, phrase))
    return hits


def find_numbers(span):
    """Find all number tokens in span (T5)."""
    nums = []
    for m in re.finditer(r"-?\d*\.\d+", span):
        nums.append(m.group())
    if re.search(r"\bn\.s\.\b", span):
        nums.append("n.s.")
    if re.search(r"\bR\^?2\b", span):
        nums.append("R2")
    if re.search(r"\bSE\b", span):
        nums.append("SE")
    # percentages
    for m in re.finditer(r"(\d+)\\?%\s*level", span):
        nums.append(m.group())
    for m in re.finditer(r"p<[\d.]+", span):
        nums.append(m.group())
    for m in re.finditer(r"\d{2,3},\d{3}", span):
        nums.append(m.group())
    if re.search(r"significant at", span):
        nums.append("significant at")
    return nums


# patterns that indicate a genuine formula (not stat notation like $p<.01$)
FORMULA_BODY = re.compile(r"[=+*/]|\\[a-zA-Z]+")


def find_formulas(span):
    """Return list of distinct formula/equation items in span (T6).
    Excludes single-stat inline notation like $p<.01$, $e=-1$, $t-2$."""
    items = []
    for m in MATH_PAT.finditer(span):
        body = m.group()
        # skip if it's just stat notation without formula content:
        # $p<.01$, $e=-1$, $t-2$, $N$, $n.s.$, $\%$, etc.
        inner = body[1:-1]  # strip $$
        if not FORMULA_BODY.search(inner):
            continue
        items.append(body)
    for m in EQ_PAT.finditer(span):
        items.append(m.group())
    return items


# ═══════════════════════════════════════════════════════════
# TRIGGER FUNCTIONS (return list of emitted row dicts or [])
# ═══════════════════════════════════════════════════════════

def clamp_verbatim(span, clause):
    """Extract the PROPOSITION VERBATIM CLAUSE from a span around a marker."""
    lo = span.lower()
    clause_lo = clause.lower()
    idx = lo.find(clause_lo)
    if idx >= 0:
        return span[idx:idx + len(clause)].strip()
    return clause.strip()


def emit_A(bibkey, clause, span, note=""):
    return {
        "proposition": 'Attributed to %s: "%s"' % (bibkey, clause),
        "category": "A", "role": "premise", "check_route": "nlm",
        "mapped_bibkey": bibkey, "note": note,
    }


def emit_B(clause, note="", bibkeys=None):
    return {
        "proposition": 'Uncited external reference: "%s"' % clause,
        "category": "B", "role": "premise", "check_route": "missing-cite",
        "mapped_bibkey": bibkeys[0] if bibkeys and len(bibkeys) == 1 else (bibkeys if bibkeys else None),
        "note": note,
    }


def emit_C(clause, note=""):
    return {
        "proposition": 'Design/method choice: "%s"' % clause,
        "category": "C", "role": "design", "check_route": "method-review",
        "mapped_bibkey": None, "note": note,
    }


def emit_D(clause, bibkey=None, note=""):
    return {
        "proposition": 'Definition/formula: "%s"' % clause,
        "category": "D", "role": "definition", "check_route": "formula-check",
        "mapped_bibkey": bibkey, "note": note,
    }


def emit_E(numbers, clause, note=""):
    nums = ", ".join(numbers) if numbers else clause[:80]
    return {
        "proposition": 'Own result: %s — "%s"' % (nums, clause),
        "category": "E", "role": "result", "check_route": "internal-verify",
        "mapped_bibkey": None, "note": note,
    }


def emit_F(clause, note=""):
    return {
        "proposition": 'Inference: "%s"' % clause,
        "category": "F", "role": "inference", "check_route": "logic-check",
        "mapped_bibkey": None, "note": note,
    }


def emit_G(h_label, clause, note=""):
    return {
        "proposition": 'Prediction %s: "%s"' % (h_label, clause),
        "category": "G", "role": "hypothesis", "check_route": "logic-check",
        "mapped_bibkey": None, "note": note,
    }


def emit_H(clause, note=""):
    return {
        "proposition": 'Self-limitation: "%s"' % clause,
        "category": "H", "role": "caveat", "check_route": "logic-check",
        "mapped_bibkey": None, "note": note,
    }


def emit_I(description):
    return {
        "proposition": description,
        "category": "I", "role": "metadata", "check_route": "bib",
        "mapped_bibkey": None,
    }


def emit_J(clause, note=""):
    return {
        "proposition": 'Cross-reference equivalence: "%s"' % clause,
        "category": "J", "role": "consistency", "check_route": "consistency",
        "mapped_bibkey": None, "note": note,
    }


def emit_K(note=""):
    return {
        "proposition": "",
        "category": "K", "role": "rhetoric", "check_route": "none",
        "mapped_bibkey": None, "note": note,
    }


# ═══════════════════════════════════════════════════════════
# PER-SEED RULE APPLICATION
# ═══════════════════════════════════════════════════════════

def apply_rules(seed):
    """Apply T1-T13 to a seed and return list of rows."""
    span = seed["verbatim_span"]
    block = seed["block"]
    note = seed.get("note") or ""

    # Special block routing (§4)
    if note and note.startswith("title-block:"):
        kind = note.split(":")[1]
        if kind == "title":
            return [emit_I("Metadata: thesis title — '" + span.split("{", 1)[1].rstrip("}") + "'")]
        elif kind == "author":
            return [emit_I("Metadata: thesis author — Sina Soleimanipour (Telfer School of Management, University of Ottawa)")]
        else:
            return [emit_I("Metadata: thesis date — June 2026")]

    if block == "bibliography":
        key = (note or "").replace("bibitem:", "")
        return [emit_I("Bib metadata: %s" % span)]

    if block == "tables":
        return [emit_J("Pointer: tables live in _tables_from_bible -> thesis_tables.tex (P2-verified)", note="POINTER")]

    if block == "appendix-vartable" and note == "table-row":
        if re.match(r"\\multicolumn\{2\}\{l\}\{.*\}", span):
            return [emit_K("vartable group header")]
        if not re.search(r"&", span):
            return [emit_K("vartable header row")]
        # D row for the definition
        rows = [emit_D(span)]
        # Inner T2/T4 on the definition text
        rhs = span.split("&", 1)[1] if "&" in span else span
        for sk in surname_match(rhs):
            rows.append(emit_A(sk, rhs.strip(), rhs.strip(),
                               "vartable surname ref: %s -> %s" % (sk, rhs[:40])))
        for (route, keys, phrase) in lit_phrase_match(rhs):
            if route == "nlm" and keys:
                for k in keys:
                    rows.append(emit_A(k, rhs.strip(), rhs.strip(),
                                       "vartable lit-phrase '%s'" % phrase))
        return rows

    if block == "appendix-prose":
        span = re.sub(r"^\\noindent\s*", "", span)

    # ── Run all 13 triggers ──
    emitted = []
    triggers_fired = set()

    # T1: \citep/\citet keys
    cite_keys = extract_cite_keys(span)
    if cite_keys:
        triggers_fired.add("T1")
        for ck in cite_keys:
            clause = span  # capture the full surrounding sentence
            emitted.append(emit_A(ck, clause, span, "T1 cite-key: %s" % ck))

    # T2: named author, no cite covering it
    covered = set(cite_keys)
    for sk in surname_match(span):
        if sk not in covered:
            triggers_fired.add("T2")
            emitted.append(emit_A(sk, span, span, "T2 named-no-cite: %s" % sk))

    # T3: vendor
    for v in VENDORS:
        if v in span:
            triggers_fired.add("T3")
            emitted.append(emit_B(span, "T3 uncited vendor: %s" % v))
            break  # one B row per seed for all vendors

    # T4: lit-phrase
    for (route, keys, phrase) in lit_phrase_match(span):
        triggers_fired.add("T4")
        if route == "nlm" and keys:
            for k in keys:
                emitted.append(emit_A(k, span, span, "T4 lit-phrase '%s'" % phrase))
        elif route == "missing-cite":
            emitted.append(emit_B(span, "T4 uncited lit-phrase '%s' — NEEDS-CITATION" % phrase))
        elif route == "nlm-or-missing":
            if cite_keys or surname_match(span):
                pass  # handled by T1/T2
            else:
                emitted.append(emit_B(span, "T4 uncited lit-phrase '%s' — NEEDS-CITATION" % phrase))

    # T5: numbers
    nums = find_numbers(span)
    if nums:
        triggers_fired.add("T5")
        emitted.append(emit_E(nums, span, "T5 numbers: %s" % ", ".join(nums)))

    # T6: formulas
    formulas = find_formulas(span)
    if formulas:
        triggers_fired.add("T6")
        for f in formulas:
            bib = "dwz" if "equation" in f.lower() else None
            nnote = "T6 formula" + (" (dwz)" if bib else "")
            emitted.append(emit_D(f, bibkey=bib, note=nnote))

    # T7: method markers
    if any_match(span, METHOD_MARKERS):
        triggers_fired.add("T7")
        emitted.append(emit_C(span, "T7 method markers"))

    # T8: hypothesis markers
    if any_match(span, HYPOTHESIS_MARKERS):
        triggers_fired.add("T8")
        h_label = ""
        lo = span.lower()
        for lbl in ["h1b", "h1a", "h1"]:
            if lbl in lo:
                h_label = lbl.upper()
                break
        emitted.append(emit_G(h_label or "H", span, "T8 hypothesis"))

    # T9: inference connectives
    if any_match(span, INFERENCE_CONNECTIVES):
        triggers_fired.add("T9")
        emitted.append(emit_F(span, "T9 inference"))

    # T10: caveat markers (word-boundary regex)
    if CAVEAT_RE.search(span):
        triggers_fired.add("T10")
        emitted.append(emit_H(span, "T10 caveat"))

    # T11: bibliography — handled via special block above

    # T12: equivalence markers
    if any_match(span, EQUIVALENCE_MARKERS):
        triggers_fired.add("T12")
        emitted.append(emit_J(span, "T12 cross-ref equivalence"))

    # T13 (Rule Z): zero triggers → K
    if not triggers_fired:
        emitted.append(emit_K("Rule Z: no trigger fired"))

    # ── Roadmap exception ──
    if re.search(r"\\ref\{|proceeds as follows|rest of the paper", span):
        # force K for pure roadmap sentences; drop any non-K rows
        return [emit_K("roadmap sentence")]
    if any_match(span, ["section~\\ref", "section~\\ref{sec:"]):
        # if that was the ONLY trigger, force K
        if triggers_fired == {"T12"}:
            return [emit_K("roadmap sentence (cross-ref only)")]

    return emitted


# ═══════════════════════════════════════════════════════════
# BOOKKEEPING: assign IDs, roles, p2_refs
# ═══════════════════════════════════════════════════════════
def fill_bookkeeping(rows):
    """Fill id, role, p2_ref, depends_on on emitted rows."""
    # Group by seq
    seq_groups = OrderedDict()
    for r in rows:
        seq_groups.setdefault(r["seq"], []).append(r)

    result = []
    for seq, group in seq_groups.items():
        block = group[0]["block"]
        pref = PREFIX.get(block, "XX")
        seq3 = "%03d" % seq

        for ri, row in enumerate(group):
            # ID
            n = len(group)
            if n == 1:
                row["id"] = "%s-%s" % (pref, seq3)
            else:
                row["id"] = "%s-%s%s" % (pref, seq3, chr(ord('a') + ri))

            # role (already set by emit_*, but reinforce)
            if not row.get("role"):
                cat_role = {"A": "premise", "B": "premise", "C": "design",
                           "D": "definition", "E": "result", "F": "inference",
                           "G": "hypothesis", "H": "caveat", "I": "metadata",
                           "J": "consistency", "K": "rhetoric"}
                row["role"] = cat_role.get(row["category"], "premise")

            # p2_ref
            pref2 = PREFIX.get(block, "")
            if row["category"] == "E" and pref2 in P2_NUMERIC_BLOCKS:
                row["p2_ref"] = "findings.json (P2 numeric audit); verify_draft_numbers.py"
            elif row["category"] == "C" and "winsor" in (row.get("note") or "").lower():
                row["p2_ref"] = "methodology_audit.json#M2-03"
            elif row["category"] == "C" and any(w in (row.get("note") or "").lower()
                    for w in ["post-withdrawal", "truncat", "window cap", "drop"]):
                row["p2_ref"] = "methodology_audit.json#M2-04"
            elif row["category"] == "C" and any(w in (row.get("proposition") or "").lower()
                    for w in ["one-tailed", "two-tailed", "tail"]):
                row["p2_ref"] = "methodology_audit.json#M2-02"

            # depends_on (sparse)
            span = row.get("verbatim_span", "").lower()
            if "equation 4" in span or "equation-4" in span:
                row["depends_on"] = ["DS-080"]  # canonical DWZ eq-4 row
            if "equation 1" in span:
                row["depends_on"] = ["DS-082"]  # canonical UncPre eq-1 row

            # DEDUP tag for NLM stage
            lo = span
            if "equation 4" in lo or "equation-4" in lo:
                if row["category"] in ("A", "C"):
                    row["note"] = (row.get("note") or "") + " dwz-eq4-instance"
            if "equation 1" in lo:
                if row["category"] in ("A", "C"):
                    row["note"] = (row.get("note") or "") + " dwz-eq1-instance"

            result.append(row)

    return result


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    seeds = data["claims"]
    target_block = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--block" else None

    # Restore seeds from pristine file (undo any partial fills)
    all_rows = []
    for seed in seeds:
        block = seed["block"]
        if target_block and block != target_block:
            all_rows.append(seed)  # keep as-is (seed or previously filled)
            continue
        # Apply rules
        base = {
            "seq": seed["seq"], "block": seed["block"],
            "file_line": seed["file_line"], "verbatim_span": seed["verbatim_span"],
            "proposition": None, "category": None, "role": None,
            "check_route": None, "mapped_bibkey": None, "p2_ref": None,
            "depends_on": [], "verdict": None, "evidence": None,
            "note": seed.get("note"),
        }
        emitted = apply_rules(seed)
        if not emitted:
            emitted = [emit_K("FALLBACK: no emission")]
        for e in emitted:
            r = dict(base)
            r.update(e)
            r["p2_ref"] = r.get("p2_ref")  # preserve None
            all_rows.append(r)

    all_rows = fill_bookkeeping(all_rows)

    # Global dedup: identical category + verbatim clause → keep one
    deduped = []
    seen = set()
    for r in all_rows:
        key = (r["seq"], r["category"], r.get("proposition"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    data["claims"] = deduped
    OUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8")
    ct = {}
    for r in deduped:
        ct[r["category"]] = ct.get(r["category"], 0) + 1
    desc = "BLOCK '%s'" % target_block if target_block else "ALL BLOCKS"
    print("apply_rules: %s -> %d rows (%d seeds, +%d expansions)" %
          (desc, len(deduped), len(seeds), max(0, len(deduped) - len(seeds))))
    for cat in "ABCDEFGHIJK":
        if cat in ct:
            print("  %s: %d" % (cat, ct[cat]))

    # warn about unprocessed seeds
    unproc = sum(1 for r in deduped if r.get("proposition") is None)
    if unproc:
        print("WARNING: %d seeds still proposition=null" % unproc)


if __name__ == "__main__":
    main()
