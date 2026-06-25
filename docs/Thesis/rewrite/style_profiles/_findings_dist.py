import json, glob, re, os, collections

base = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\style_profiles"
files = sorted(glob.glob(os.path.join(base, "*_profile.json")))

def sec_of(para_id):
    m = re.search(r'(abstract|\d+(?:\.\d+)?)', para_id or '')
    return m.group(1) if m else (para_id or '?')

def top_of(sub):
    if sub == 'abstract': return 'abstract'
    return sub.split('.')[0]

prof_counts = {}
sub_counts = collections.Counter()          # distinct findings touching each subsection
sub_by_prof = collections.defaultdict(collections.Counter)
total_findings = 0
multi = 0

for f in files:
    data = json.load(open(f, encoding='utf-8'))
    prof = data.get('type')
    findings = data.get('profile', [])
    prof_counts[prof] = len(findings)
    for fd in findings:
        total_findings += 1
        subs = set(sec_of(q.get('para_id','')) for q in fd.get('our_quotes', []))
        subs = {s for s in subs if s}
        if len(subs) > 1: multi += 1
        for s in subs:
            sub_counts[s] += 1
            sub_by_prof[s][prof] += 1

top_counts = collections.Counter()
for sub, c in sub_counts.items():
    top_counts[top_of(sub)] += c

def order_key(s):
    if s == 'abstract': return (-1,)
    parts = s.split('.')
    return tuple(int(p) for p in parts)

print("=== PER PROFILE (the 8 writing-type buckets the findings NATIVELY live in) ===")
for p in sorted(prof_counts, key=lambda x: -prof_counts[x]):
    print(f"  {p:<12} {prof_counts[p]:>3}")
print(f"  {'TOTAL':<12} {sum(prof_counts.values()):>3}   avg/profile = {sum(prof_counts.values())/len(prof_counts):.1f}")

print("\n=== PER SUBSECTION (by our_quotes para_id; a finding spanning N subs counts in each) ===")
for s in sorted(sub_counts, key=order_key):
    profs = ", ".join(f"{k}:{v}" for k,v in sub_by_prof[s].most_common())
    print(f"  {s:<10} {sub_counts[s]:>3}   [{profs}]")
print(f"  subsections present = {len(sub_counts)}   sum(with multi-count) = {sum(sub_counts.values())}")
print(f"  avg/subsection = {sum(sub_counts.values())/len(sub_counts):.1f}   min = {min(sub_counts.values())}   max = {max(sub_counts.values())}")
thin = [s for s,c in sub_counts.items() if c <= 5]
print(f"  THIN subsections (<=5 findings): {len(thin)} -> {sorted(thin, key=order_key)}")

print("\n=== PER TOP-LEVEL SECTION (abstract + 1..5) ===")
for s in sorted(top_counts, key=order_key):
    print(f"  {s:<10} {top_counts[s]:>3}")
print(f"  sections present = {len(top_counts)}   avg/section = {sum(top_counts.values())/len(top_counts):.1f}")

print(f"\n  (findings touching >1 subsection: {multi} of {total_findings})")
