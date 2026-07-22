"""The deterministic gate every speaker-note draft has to pass.

Written before a single note exists. That ordering is the point: thresholds
chosen after drafting get tuned until the drafts pass, which is the author
grading himself with extra steps. These were fixed in EXECUTION_ALLOCATION.md
before any script was written and this file only implements them.

What it checks is everything about the notes that is computable: length against
the measured budget, sentence complexity, unglossed jargon, forbidden dashes,
and the specific spoken phrasings that the claim ledger and the examiner sweep
recorded as overstatements.

What it cannot check is whether a sentence is true, whether it lands, or whether
it belongs on its slide. Those go to an independent audit. A green gate means
the draft is worth auditing, never that it is correct.

Usage:
    python gate.py NOTES.md [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# From SPEAKER_NOTES_BUDGET.md. Measured, not chosen.
BUDGET = {1: 65, 2: 150, 3: 150, 4: 150, 5: 120, 6: 185, 7: 185,
          8: 265, 9: 265, 10: 215, 11: 140, 12: 120, 13: 100}
TOTAL_CEILING = 2110
TOTAL_FLOOR = 1930
# Per slide the stopwatch precision is worth about ten percent either way.
SLIDE_TOLERANCE = 0.10

MEAN_SENTENCE_WORDS_MAX = 18.0
LONG_SENTENCE_WORDS = 25
LONG_SENTENCE_SHARE_MAX = 0.10
HARD_SENTENCE_WORDS = 30

# Every term whose first spoken use must carry its own explanation, with the
# slide U02 assigned it to. A defense that refuses to say "coefficient" is not a
# defense, so nothing here is banned. The rule is only that the first time it is
# said aloud, the same sentence explains it.
GLOSS_TERMS = [
    "material information", "disclosure state", "estimand", "descriptive result",
    "within-firm comparison", "fixed effects", "clustered standard errors",
    "identification", "event study", "counterfactual", "residual",
    "residualization", "coefficient", "standard error", "confidence interval",
    "attenuation", "parallel trends", "nondifferential", "Wald test",
    "Tobin's Q", "firm-quarter", "two-tailed", "cash ratio",
]

# A gloss is present when the sentence explains itself. Detected by an
# apposition marker or a parenthetical. This is a heuristic and will pass a
# sentence that contains the marker without really explaining anything, so it
# catches the cold unglossed use rather than proving quality.
GLOSS_MARKERS = re.compile(
    r"(,\s*(that is|which is|meaning|so\b|in other words)|\(|:\s|\bis\s+(the|how|what|whether|one)\b)",
    re.I,
)

# Spoken forms the claim ledger and the examiner sweep recorded as exceeding
# what the thesis supports. Each carries the reason so a future reader does not
# delete it as fussiness.
FORBIDDEN = [
    (r"no pre-?trend", "PRE2 is an absence of detected elevation, not proof no pre-trend exists"),
    (r"indistinguishable from baseline", "slide 9: a nonsignificant GAP is a decline result, not an equivalence result"),
    (r"\bequivalent to baseline\b|\bsignal is gone\b|\bfully resolved\b", "same equivalence overclaim as above"),
    (r"significantly elevated (gap|after|through)", "persistence rests on the ABSENCE of a PRE1 to GAP decline, not an elevated level"),
    (r"thesis reports a (95|ninety[- ]five)[^.]*interval", "the intervals are derived from estimate and SE; the deck says so on screen"),
    (r"isolates? (the )?(true|actual|deal-related|what the CEO)", "slide 7: residualization leaves an unexplained residual used as a proxy"),
    (r"clean counterfactual", "slide 3: cash is the relatively cleaner setting, not a clean counterfactual"),
    (r"\binstruments?\b", "slide 12: invites an IV question the design has no exclusion restriction for"),
    (r"(therefore |so )?(it is |this is )?conservative\b", "onset is unobserved, so the direction of the bias cannot be signed"),
    (r"\blower bound\b", "same unsigned-bias problem as calling it conservative"),
    (r"\bproves?\b|\bproof\b", "the thesis is descriptive; nothing here proves anything"),
    (r"\bcaus(es|ed|al effect)\b", "descriptive contrast, not a causal effect"),
    (r"only adds noise|just adds noise", "the unsigned-bias error, already caught twice in this project"),
    (r"no prior work (occupies|has|examines)", "slide 5 says to our knowledge; the qualifier may not be dropped"),
    (r"exact (point|moment) (when|at which)", "the unit is a quarterly call; the design does not timestamp a state change"),
    (r"cash-only|strictly cash-specific", "the thesis says concentrated in cash, not cash-only"),
]

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.,%-]*", text)


def parse(path: Path) -> dict[int, str]:
    """Read a notes file into {slide number: spoken text}.

    Lines starting with '>' are stage directions, not speech, and are excluded
    from every word count. A pause cue must not cost words.
    """
    raw = path.read_text(encoding="utf-8")
    parts = re.split(r"^##\s*Slide\s+(\d+)\s*$", raw, flags=re.M)
    notes: dict[int, str] = {}
    for i in range(1, len(parts), 2):
        body = "\n".join(
            line for line in parts[i + 1].splitlines() if not line.strip().startswith(">")
        )
        notes[int(parts[i])] = body.strip()
    return notes


def check(path: Path) -> dict:
    notes = parse(path)
    failures: list[str] = []
    warnings: list[str] = []
    per_slide = {}

    missing = [n for n in BUDGET if n not in notes]
    if missing:
        failures.append(f"no note for slide(s) {missing}")

    total = 0
    for n in sorted(notes):
        text = notes[n]
        wc = len(words(text))
        total += wc
        budget = BUDGET.get(n)
        sentences = [s for s in SENTENCE_SPLIT.split(text) if words(s)]
        lengths = [len(words(s)) for s in sentences]
        mean = sum(lengths) / len(lengths) if lengths else 0.0
        long_share = (sum(1 for x in lengths if x > LONG_SENTENCE_WORDS) / len(lengths)) if lengths else 0.0
        hard = [s for s, x in zip(sentences, lengths) if x > HARD_SENTENCE_WORDS]

        per_slide[n] = {"words": wc, "budget": budget, "sentences": len(sentences),
                        "mean_sentence": round(mean, 1),
                        "long_share": round(long_share, 3),
                        "over_hard_limit": len(hard)}

        if budget:
            lo, hi = budget * (1 - SLIDE_TOLERANCE), budget * (1 + SLIDE_TOLERANCE)
            if not lo <= wc <= hi:
                failures.append(f"slide {n}: {wc} words, budget {budget} (allowed {lo:.0f} to {hi:.0f})")
        if mean > MEAN_SENTENCE_WORDS_MAX:
            failures.append(f"slide {n}: mean sentence {mean:.1f} words, ceiling {MEAN_SENTENCE_WORDS_MAX}")
        if long_share > LONG_SENTENCE_SHARE_MAX:
            failures.append(f"slide {n}: {long_share:.0%} of sentences over {LONG_SENTENCE_WORDS} words, ceiling {LONG_SENTENCE_SHARE_MAX:.0%}")
        for s in hard:
            failures.append(f"slide {n}: sentence over {HARD_SENTENCE_WORDS} words: {s[:70]}...")

    if total > TOTAL_CEILING:
        failures.append(f"total {total} words exceeds the ceiling {TOTAL_CEILING}")
    if total < TOTAL_FLOOR:
        warnings.append(f"total {total} words is below {TOTAL_FLOOR}, the talk may run short")

    joined = "\n".join(notes[n] for n in sorted(notes))

    for ch, name in (("—", "em dash"), ("–", "en dash")):
        if ch in joined:
            failures.append(f"{name} present; forbidden in anything spoken or shown")

    for pattern, why in FORBIDDEN:
        for m in re.finditer(pattern, joined, re.I):
            failures.append(f"forbidden phrasing '{m.group(0)}': {why}")

    # First spoken use of each term must explain itself.
    for term in GLOSS_TERMS:
        hit = re.search(r"\b" + re.escape(term) + r"\b", joined, re.I)
        if not hit:
            continue
        start = joined.rfind(".", 0, hit.start()) + 1
        end = joined.find(".", hit.end())
        sentence = joined[start: end if end != -1 else len(joined)]
        if not GLOSS_MARKERS.search(sentence):
            failures.append(f"'{term}' is used before it is explained: {sentence.strip()[:80]}...")

    return {"file": str(path), "total_words": total, "ceiling": TOTAL_CEILING,
            "per_slide": per_slide, "failures": failures, "warnings": warnings,
            "passed": not failures}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("notes")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = check(Path(args.notes))
    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if report["passed"] else 1
    print(f"{report['total_words']} words against a ceiling of {report['ceiling']}\n")
    for n, d in sorted(report["per_slide"].items()):
        print(f"  slide {n:>2}: {d['words']:>4}w / {d['budget']:<4} "
              f"mean sentence {d['mean_sentence']:>4}  long {d['long_share']:.0%}")
    for w in report["warnings"]:
        print(f"\nWARNING  {w}")
    if report["failures"]:
        print(f"\nFAILED, {len(report['failures'])} problems\n")
        for f in report["failures"]:
            print(f"  - {f}")
        return 1
    print("\nPASSED every deterministic check.")
    print("This says the draft is worth auditing. It does not say it is correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
