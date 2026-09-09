"""Check the reimplemented scorer against the published framing_analysis.csv."""
import csv, sys, ast
sys.path.insert(0, "assessment")
from framing import load_vocab, score

csv.field_size_limit(sys.maxsize)
REPO = "uk-university-ai-policies"
det, edu = load_vocab(f"{REPO}/data/keyword-vocabularies.csv")
corpus = {r["institution"]: r for r in csv.DictReader(open(f"{REPO}/data/corpus.csv"))}
pub = list(csv.DictReader(open(f"{REPO}/analysis/framing_analysis.csv")))

fields = ["word_count", "detection_raw", "education_raw", "detection_per_1k",
          "education_per_1k", "framing_ratio", "frame_category"]
mismatch = {f: 0 for f in fields}
examples = {f: [] for f in fields}
n = 0
for p in pub:
    row = corpus.get(p["institution"])
    if not row:
        print("MISSING from corpus:", p["institution"]); continue
    n += 1
    got = score(row["text"], det, edu)
    for f in fields:
        a, b = got[f], p[f]
        if f in ("word_count", "detection_raw", "education_raw"):
            ok = a == int(b)
        elif f == "frame_category":
            ok = a == b
        else:
            ok = abs(a - float(b)) < 1e-6
        if not ok:
            mismatch[f] += 1
            if len(examples[f]) < 3:
                examples[f].append((p["institution"], a, b))

print(f"compared {n} policies")
for f in fields:
    status = "OK" if mismatch[f] == 0 else f"{mismatch[f]} mismatches"
    print(f"  {f:20s} {status}")
    for ex in examples[f]:
        print(f"      {ex[0][:40]:42s} got={ex[1]!r:>12} published={ex[2]!r}")
