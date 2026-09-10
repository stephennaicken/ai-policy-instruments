"""Score a policy on six dimensions and place it against the 96 UK policies.

Usage: python3 assessment/score_v2.py <policy.txt> [--name NAME]
"""
import argparse, csv, re, sys, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from framing_v2 import load_vocab, score, DIMENSIONS, AMBIGUOUS_AGENCY
from textnorm import normalise

csv.field_size_limit(sys.maxsize)
REPO = os.path.join(HERE, "..", "uk-university-ai-policies")
V = load_vocab(os.path.join(HERE, "vocab", "keyword-vocabularies-v2.csv"))


def uk_reference():
    out = {d: [] for d in DIMENSIONS}
    idx = {}
    for r in csv.DictReader(open(os.path.join(REPO, "data", "corpus.csv"))):
        s = score(r["text"], V)
        for d in DIMENSIONS:
            out[d].append(s["per1k"][d])
        for k, v in s["indices"].items():
            idx.setdefault(k, []).append(v)
    return out, idx


def pct(v, dist):
    return sum(1 for x in dist if x < v) / len(dist) * 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--name", default=None)
    a = ap.parse_args()
    text = normalise(open(a.path, encoding="utf-8", errors="replace").read())
    s = score(text, V)
    name = a.name or os.path.basename(a.path)
    ref, refidx = uk_reference()

    print(f"\n{name}   ({s['word_count']:,} words)")
    print("=" * (len(name) + 20))
    print(f"{'dimension':14s} {'raw':>5} {'per 1k':>8} {'UK median':>10} {'UK pctile':>10}")
    for d in DIMENSIONS:
        print(f"{d:14s} {s['raw'][d]:5d} {s['per1k'][d]:8.2f} "
              f"{st.median(ref[d]):10.2f} {pct(s['per1k'][d], ref[d]):9.0f}th")
    print(f"\n{'index':20s} {'value':>7} {'UK median':>10} {'UK pctile':>10}")
    for k, v in s["indices"].items():
        print(f"{k:20s} {v:7.3f} {st.median(refidx[k]):10.3f} {pct(v, refidx[k]):9.0f}th")

    if any(s["negated"].values()):
        print("\nhits inside rejection clauses (reported, not removed; the *_adj indices set them aside):")
        print("   ", ", ".join(f"{d} {n}" for d, n in s["negated"].items() if n))
        for d, term, pos in s["negated_hits"][:6]:
            print(f"    [{d[:4]}] ...{re.sub(r'\s+', ' ', text[max(0, pos - 60):pos + 45])}...")
    print("\nagency terms present (* role-ambiguous, excluded from agency_share_strict):")
    fired = {t: n for t, n in s["hits"]["agency"].items() if n}
    print("   ", ", ".join(f"{t}{'*' if t in AMBIGUOUS_AGENCY else ''} ({n})"
                           for t, n in sorted(fired.items(), key=lambda x: -x[1])) or "(none)")
    print("datafication terms present:")
    fired = {t: n for t, n in s["hits"]["datafication"].items() if n}
    print("   ", ", ".join(f"{t} ({n})" for t, n in sorted(fired.items(), key=lambda x: -x[1])) or "(none)")


if __name__ == "__main__":
    main()
