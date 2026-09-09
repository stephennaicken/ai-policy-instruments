"""Discriminant check for the regulation 5 screening instrument.

The 96 UK policies were written without reference to these regulations, so they
serve as a negative control. If the instrument is calibrated, they should show
wide variation and characteristic gaps rather than uniform pass or uniform fail.
"""
import csv, os, sys, statistics as st
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from conformance import load_spec, assess

csv.field_size_limit(sys.maxsize)
obs, els = load_spec()
rows = []
for r in csv.DictReader(open(os.path.join(HERE, "..", "uk-university-ai-policies",
                                          "data", "corpus.csv"))):
    rows.append((r["institution"], assess(r["text"], obs, els)))

cov = [x["coverage"] for _, x in rows]
print(f"{len(rows)} UK policies screened against regulation 5\n")
print(f"element coverage: mean {st.mean(cov)*100:.0f}%  median {st.median(cov)*100:.0f}%  "
      f"range {min(cov)*100:.0f}%–{max(cov)*100:.0f}%")

print("\nCoverage by obligation across the UK corpus "
      "(share of policies showing relevant language for every element):")
full = Counter(); absent = Counter(); titles = {}
for _, x in rows:
    for s in x["summary"]:
        titles[s["obligation"]] = s["title"]
        if s["band"] == "Full": full[s["obligation"]] += 1
        if s["band"] == "Absent": absent[s["obligation"]] += 1
print(f"{'reg':6s} {'obligation':38s} {'fully covered':>14} {'wholly absent':>14}")
for o in sorted(titles):
    print(f"{o:6s} {titles[o][:37]:38s} {full[o]:9d}/{len(rows):<4d} {absent[o]:9d}/{len(rows):<4d}")

print("\nElements least often addressed in UK policies:")
miss = Counter()
for _, x in rows:
    for e in x["elements"]:
        if not e["hits"]: miss[(e["obligation"], e["element"])] += 1
for (o, e), n in miss.most_common(12):
    print(f"  {n:3d}/{len(rows)}  {o}  {e}")
