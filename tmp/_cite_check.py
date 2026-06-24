import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
texfiles = [
    "docs/Thesis/thesis_draft_uottawa.tex",
    "docs/Thesis/sec34_body_from_ledgers.tex",
    "docs/Thesis/_intro_body.tex",
    "docs/Thesis/_conclusion_body.tex",
    "docs/Thesis/_abstract_body.tex",
    "docs/Thesis/_dwz_replication.tex",
    "docs/Thesis/appendix_I_cash_scrutiny.tex",
    "docs/Thesis/_tables_from_bible.tex",
]
cite_re = re.compile(r"\\cite[tp]?(?:\[[^\]]*\])?\{([^}]*)\}")
citeauthor_re = re.compile(r"\\citeauthor\{([^}]*)\}")
bibitem_re = re.compile(r"\\bibitem\[[^\]]*\]\{([^}]*)\}")
used = {}
for f in texfiles:
    t = open(f, encoding="utf-8").read()
    for m in list(cite_re.finditer(t)) + list(citeauthor_re.finditer(t)):
        for key in m.group(1).split(","):
            key = key.strip()
            if key:
                used.setdefault(key, set()).add(f.split("/")[-1])
master = open("docs/Thesis/thesis_draft_uottawa.tex", encoding="utf-8").read()
defined = set(bibitem_re.findall(master))
print("DEFINED bibitems (", len(defined), "):", sorted(defined))
print("\nUSED keys -> files:")
for k in sorted(used):
    print("  %s: %s" % (k, sorted(used[k])))
print("\nUSED but NOT defined:", sorted(set(used) - defined))
print("DEFINED but NOT used:", sorted(defined - set(used)))
