import re, os
texfiles=["docs/Thesis/thesis_draft_uottawa.tex","docs/Thesis/sec34_body_from_ledgers.tex","docs/Thesis/_tables_from_bible.tex","docs/Thesis/_intro_body.tex","docs/Thesis/_conclusion_body.tex","docs/Thesis/_abstract_body.tex","docs/Thesis/_dwz_replication.tex","docs/Thesis/appendix_I_cash_scrutiny.tex"]
used=set()
cite_re=re.compile(r"\cite[a-z]*\{([^}]*)\}")
bib_re=re.compile(r"\bibitem\[[^\]]*\]\{([^}]+)\}")
for tf in texfiles:
    if not os.path.exists(tf):
        print("MISSING",tf); continue
    t=open(tf,encoding="utf-8").read()
    for m in cite_re.finditer(t):
        for k in m.group(1).split(","):
            used.add(k.strip())
master=open("docs/Thesis/thesis_draft_uottawa.tex",encoding="utf-8").read()
defined=set(bib_re.findall(master))
print("USED keys ("+str(len(used))+"):", sorted(used))
print("DEFINED bibitems ("+str(len(defined))+"):", sorted(defined))
print("USED-UNDEFINED:", sorted(used-defined))
print("DEFINED-UNUSED:", sorted(defined-used))
