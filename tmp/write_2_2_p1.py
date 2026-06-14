# Write §2.2 P1 (funnel) into the locked thesis_draft.tex + apply the reframe's P7 softening.
# Byte-safe, fail-closed: (1) remove the stale TODO line; (2) cut P7 'and we do not try'; (3) insert 2.2 P1.
src = "docs/Thesis/thesis_draft.tex"
t = open(src, encoding="utf-8").read()  # text mode normalizes CRLF->LF on read

old_p7 = "Our design cannot distinguish them, and we do not try."
# the string appears twice pre-edit: in the TODO comment AND in P7 prose
assert t.count(old_p7) == 2, f"expected 2 occurrences (TODO + prose), got {t.count(old_p7)}"

# 1) remove the stale TODO line (whole line)
lines = t.split("\n")
todo_idx = [i for i, l in enumerate(lines) if l.startswith("% TODO(scrutiny-reframe")]
assert len(todo_idx) == 1, f"expected 1 TODO line, got {len(todo_idx)}"
del lines[todo_idx[0]]
t = "\n".join(lines)

# 2) now the prose occurrence is unique -> cut the overclaim
assert t.count(old_p7) == 1, f"after TODO removal expected 1, got {t.count(old_p7)}"
t = t.replace(old_p7, "Our design cannot distinguish them.")

# 3) insert 2.2 (heading + P1) immediately after P7's closing sentence
anchor = "It is in this deliberately bounded register that the empirical strategy of the following sections puts the pattern to the test."
assert t.count(anchor) == 1, "P7 closing-sentence anchor not unique"
p1_block = r"""\subsection{Hypothesis Development}

The preceding section isolates two dimensions of the pattern we expect: an \emph{anticipatory} dimension, in which CEO uncertainty language is elevated while an acquisition remains undisclosed and recedes once it is announced, and a \emph{cash-concentrated} dimension, in which that elevation is stronger for cash acquisitions than for stock. This section turns those dimensions into formal, falsifiable predictions about \emph{where} and \emph{when} the signal appears in a CEO's unscripted answers---not why it appears, a mechanism the framework leaves open. The object of each prediction is the call-varying residual of CEO uncertainty language in the Q\&A---the component that remains once a CEO's persistent speaking style is netted out, which the next section defines formally---and every prediction is read in descriptive, correlational terms. Timing is measured in event time: $e$ counts calendar quarters relative to a firm's first acquisition announcement, so that $e=-1$ denotes the call in the quarter immediately before it. The focal pre-announcement indicator is $\mathrm{PreAnnounceQtr} = \mathbf{1}[e=-1]$, defined for a firm's first acquisition financed at least half in cash. The three hypotheses that follow---H1, H1a, and H1b---are stated here as predictions and confronted with the data by the designs developed below."""
t = t.replace(anchor, anchor + "\n\n" + p1_block)

open(src, "w", encoding="utf-8", newline="\n").write(t)

# sanity report
print("done. checks:")
print("  TODO removed:", "% TODO(scrutiny-reframe" not in t)
print("  'and we do not try' gone:", "and we do not try" not in t)
print("  'cannot distinguish them.' present:", "Our design cannot distinguish them." in t)
print("  2.2 heading present:", "\\subsection{Hypothesis Development}" in t)
print("  P1 last sentence present:", "confronted with\nthe data".replace("\n"," ") in t.replace("\n"," "))
