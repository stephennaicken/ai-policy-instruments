"""Discriminant validity check for the v2 vocabulary against the UK corpus.

The v2 vocabulary was partly derived from the HEC Mauritius document. Scoring
that document with it would be circular. This script instead applies it to the
96 UK policies it was NOT built on, and asks: do the new dimensions fire, do
they vary between policies, and do they measure something the UK binary missed?
"""
import csv, sys, os, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from framing_v2 import load_vocab, score, DIMENSIONS

csv.field_size_limit(sys.maxsize)
V = load_vocab(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "vocab", "keyword-vocabularies-v2.csv"))
REPO = "uk-university-ai-policies"

rows = []
for r in csv.DictReader(open(f"{REPO}/data/corpus.csv")):
    s = score(r["text"], V)
    rows.append((r["institution"], s))

print(f"v2 vocabulary applied to {len(rows)} UK policies\n")
print(f"{'dimension':14s} {'per-1k mean':>11} {'median':>8} {'min':>6} {'max':>7} {'zero-hit policies':>18}")
for d in DIMENSIONS:
    vals = [s["per1k"][d] for _, s in rows]
    zero = sum(1 for v in vals if v == 0)
    print(f"{d:14s} {st.mean(vals):11.2f} {st.median(vals):8.2f} "
          f"{min(vals):6.2f} {max(vals):7.2f} {zero:14d}/{len(vals)}")

print("\nDerived indices across the UK corpus:")
for k in ("agency_share", "agency_share_strict", "detection_ratio", "enforcement_ratio", "ethics_share"):
    vals = [s["indices"][k] for _, s in rows]
    print(f"  {k:18s} mean {st.mean(vals):.3f}   median {st.median(vals):.3f}   "
          f"range {min(vals):.3f}–{max(vals):.3f}")

print("\nWhat the UK binary missed — policies classed Education-dominant by the")
print("original instrument, ranked by v2 enforcement_ratio (obligation vs development):")
pub = {r["institution"]: r for r in csv.DictReader(open(f"{REPO}/analysis/framing_analysis.csv"))}
edu_dom = [(s["indices"]["enforcement_ratio"], n, s) for n, s in rows
           if pub[n]["frame_category"] == "Education-dominant"]
edu_dom.sort(reverse=True)
print(f"  {'institution':44s} {'old ratio':>9} {'enforce':>8} {'agency share':>13}")
for er, n, s in edu_dom[:8]:
    print(f"  {n[:43]:44s} {float(pub[n]['framing_ratio']):9.2f} {er:8.2f} "
          f"{s['indices']['agency_share']:13.2f}")
