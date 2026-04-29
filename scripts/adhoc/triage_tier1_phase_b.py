"""Triage Tier 1 (86 events) into CLASSIFY / MAYBE / DUPLICATE / EXCLUDE.

Based on Q1_detail / Q2A_detail / Q3_detail / Q4_detail role text per row.
Writes EXCLUDE + DUPLICATE rows directly to sudden_classified_tier4_tier3.csv
with is_sudden=BLANK + confidence=H + reason notes. Leaves CLASSIFY rows
for downstream web-search classification.

Triage logic:
- DUPLICATE: same gvkey + same date as a previously classified event → EXCLUDE
- NOT_CEO_NAME: exec_name_canonical is junk (looks like company name or generic
  string like "AUDIT COMMITTEE", "GEAR PUMP DIVISION", "FOUNDING LESTER", or
  "HUMAN RESOURCE WILHELMENIA") → EXCLUDE
- NOT_CEO_ROLE: only role mentions explicitly indicate non-CEO position
  (Director, Board Member, EVP, CFO, COO, Senior VP, Audit Committee,
  General Manager, Division CEO, Regional CEO, Co-Founder, Founder/Founding,
  Emeritus, Chairman Emeritus, Lead Director, Former Chairman, "Chairman of
  the Board" alone without CEO mention) → EXCLUDE
- CEO_DEATH: Q2A action=Deceased + role=CEO; or Q3 with Chairman/CEO,
  President/CEO, CEO; or Q1 headline mentioning "CEO died" → CLASSIFY
- AMBIGUOUS Q4-only: Q4 reason=DECEASED with no other source corroboration
  → MAYBE (one quick check before classify)
"""

from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "data" / "raw" / "ceo_death_events" / "sudden_classification_template.csv"
OUT = ROOT / "data" / "raw" / "ceo_death_events" / "sudden_classified_tier4_tier3.csv"


# Already-classified events (gvkey, date) → exclude duplicates from Tier 1
ALREADY_CLASSIFIED = set()
with OUT.open("r", encoding="utf-8") as f:
    rows = csv.DictReader(f)
    for r in rows:
        ALREADY_CLASSIFIED.add((r["gvkey"], r["death_date_canonical"]))


JUNK_NAME_PATTERNS = [
    r"^HANOVER COMPRESSOR$",
    r"^FOUNDING ",
    r"^GEAR PUMP",
    r"^HUMAN RESOURCE",
    r"^MASTERCARD WORLDWIDE$",
    r"^CITIZENS COMMUNICATIONS$",
    r"^AUDIT COMMITTEE$",
]


def is_junk_name(name: str) -> bool:
    return any(re.search(p, name) for p in JUNK_NAME_PATTERNS)


# Role classification — extract role from any non-empty *_detail
def parse_role(q1: str, q2a: str, q3: str, q4: str) -> str:
    """Return one of: CEO, NOT_CEO, AMBIGUOUS_Q4_ONLY."""

    # Q3 priority — has clean rolename
    if q3:
        # Match clean CEO at corporate level
        if re.search(r"\b(?:President\/CEO|Chairman\/CEO|Chairman\/President\/CEO|"
                     r"Chairman\/President\/Co-CEO|Chairman\/Co-CEO)\b", q3):
            return "CEO"
        # Plain CEO without prefix (Q3 outside corporate role)
        if re.search(r"^CEO\b|\| CEO ", q3) and not re.search(
            r"Division|Regional|Interim|Co-CEO\s*\|", q3
        ):
            return "CEO"
        # Co-CEO at corporate (rare but valid)
        if "Co-CEO" in q3 and not re.search(r"Division|Regional", q3):
            return "CEO"
        # Anything Division/Regional/Interim → not the CEO event we care about
        if re.search(r"Division|Regional", q3):
            return "NOT_CEO"

    # Q2A: action=Deceased + role
    if q2a:
        # Pattern: "Director; Chairman; CEO | action=Deceased" or "President; CEO | action=Deceased"
        # Need CEO in role list
        role_part = q2a.split("|")[0]
        if re.search(r"\bCEO\b", role_part):
            return "CEO"

    # Q1: headline parsing
    if q1:
        # Strong NEGATIVE indicators (non-CEO roles)
        non_ceo_role_patterns = [
            r"\bDirector\b(?!.*\bCEO\b)",  # Director without CEO mention
            r"\bBoard Member\b",
            r"\bExecutive Vice President\b",
            r"\bSenior Vice President\b",
            r"\bvice president\b",
            r"\bChief Financial Officer\b",
            r"\bCFO\b",
            r"\bChief Marketing Officer\b",
            r"\bChief Operating Officer\b",
            r"\bAudit Committee\b",
            r"\bChairman Emeritus\b",
            r"\bGeneral Manager\b",
            r"\bCo-Founder\b",
            r"\bFounder\b(?!.*\bCEO\b)",
            r"\bFounding\b",
            r"\bLead Director\b",
            r"\bFormer Chairman\b",
            r"\bNon-Executive Chairman\b",
            r"\bBoard Chair\b",
            r"\bDivision\b",
            r"\bHead of Operations\b",
            r"\bRegional\b",
            r"\bMember of the\b",
            r"\bMember of its Board",
        ]
        for p in non_ceo_role_patterns:
            if re.search(p, q1, re.IGNORECASE):
                return "NOT_CEO"

        # POSITIVE indicators (CEO at death)
        if re.search(r"\bCEO\b|Chief Executive Officer", q1, re.IGNORECASE):
            # If headline mentions CEO + death, classify
            if re.search(r"\bdied|death|passed away", q1, re.IGNORECASE):
                return "CEO"

        # If headline only says "Death of <name>" with no role → NOT_CEO (vague)
        if re.search(r"^[A-Za-z][\w\s\-,'\.]+ Announces? (the )?Death of [A-Z]", q1):
            # Vague headline like "Foo Announces Death of John Smith" with no role
            # → most likely director/board, classify as NOT_CEO
            return "NOT_CEO"

    # Q4 only: reason=DECEASED + ceoann=CEO
    if q4 and not (q1 or q2a or q3):
        if "reason=DECEASED" in q4 and "ceoann=CEO" in q4:
            return "AMBIGUOUS_Q4_ONLY"

    # Default
    return "NOT_CEO"


def main():
    template_rows = []
    with TEMPLATE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            template_rows.append(r)

    tier1 = [r for r in template_rows if r["tier"] == "1"]
    print(f"Tier 1 rows: {len(tier1)}")

    classify = []
    maybe = []
    duplicate = []
    exclude_non_ceo = []
    exclude_junk_name = []

    for r in tier1:
        key = (r["gvkey"], r["death_date_canonical"])
        if key in ALREADY_CLASSIFIED:
            duplicate.append(r)
            continue
        # Check junk name first
        if is_junk_name(r["exec_name_canonical"]):
            exclude_junk_name.append(r)
            continue
        role = parse_role(
            r.get("Q1_detail", ""),
            r.get("Q2A_detail", ""),
            r.get("Q3_detail", ""),
            r.get("Q4_detail", ""),
        )
        if role == "CEO":
            classify.append(r)
        elif role == "AMBIGUOUS_Q4_ONLY":
            maybe.append(r)
        else:
            exclude_non_ceo.append(r)

    print(f"\n=== TRIAGE RESULTS ===")
    print(f"CLASSIFY (web search needed): {len(classify)}")
    for r in classify:
        sources = r["sources_matched"]
        detail = r.get("Q3_detail") or r.get("Q2A_detail") or r.get("Q1_detail")
        print(f"  - {r['gvkey']} {r['exec_name_canonical']:30s} {r['death_date_canonical']} [{sources}] {detail[:80]}")

    print(f"\nMAYBE (Q4-only): {len(maybe)}")
    for r in maybe:
        print(f"  - {r['gvkey']} {r['exec_name_canonical']:30s} {r['death_date_canonical']}")

    print(f"\nDUPLICATE (already classified): {len(duplicate)}")
    for r in duplicate:
        print(f"  - {r['gvkey']} {r['exec_name_canonical']:30s} {r['death_date_canonical']}")

    print(f"\nEXCLUDE non-CEO role: {len(exclude_non_ceo)}")
    print(f"EXCLUDE junk name: {len(exclude_junk_name)}")

    # Write EXCLUDE + DUPLICATE rows to CSV
    with OUT.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for r in duplicate:
            writer.writerow([
                "1",
                r["sources_matched"],
                r["gvkey"],
                r["exec_name_canonical"],
                r["death_date_canonical"],
                "",  # is_sudden BLANK
                "",
                "",
                "",
                "H",
                f"DUPLICATE: same (gvkey, date) as already-classified higher-tier event",
            ])
        for r in exclude_junk_name:
            writer.writerow([
                "1",
                r["sources_matched"],
                r["gvkey"],
                r["exec_name_canonical"],
                r["death_date_canonical"],
                "",
                "",
                "",
                "",
                "H",
                f"DATA QUALITY: junk name parse '{r['exec_name_canonical']}' — A1 parser bug; not a real CEO event",
            ])
        for r in exclude_non_ceo:
            detail = (r.get("Q1_detail") or r.get("Q2A_detail") or r.get("Q3_detail") or r.get("Q4_detail") or "")
            writer.writerow([
                "1",
                r["sources_matched"],
                r["gvkey"],
                r["exec_name_canonical"],
                r["death_date_canonical"],
                "",
                "",
                "",
                "",
                "H",
                f"NOT CEO: role evidence '{detail[:100].replace(chr(34), chr(39))}' — director/board/EVP/CFO/division/emeritus pattern",
            ])

    print(f"\nWrote {len(duplicate)+len(exclude_junk_name)+len(exclude_non_ceo)} EXCLUDE/DUPLICATE rows to CSV.")
    print(f"Remaining work: {len(classify)} CEO events to web-search + {len(maybe)} MAYBE.")


if __name__ == "__main__":
    main()
