"""Score one policy document against the Illingworth (2026) framing method
and place it in the UK distribution of 96 policies.

Usage:  python3 assessment/score_policy.py <policy.txt> [--name "My University"]
"""
import argparse, csv, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from framing import load_vocab, score

csv.field_size_limit(sys.maxsize)
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "uk-university-ai-policies")


def uk_ratios():
    path = os.path.join(REPO, "analysis", "framing_analysis.csv")
    return sorted(float(r["framing_ratio"]) for r in csv.DictReader(open(path)))


def percentile_of(ratio, dist):
    below = sum(1 for x in dist if x < ratio)
    return below / len(dist) * 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--name", default=None)
    ap.add_argument("--top", type=int, default=12,
                    help="how many hit keywords to list per frame")
    args = ap.parse_args()

    text = open(args.path, encoding="utf-8", errors="replace").read()
    det, edu = load_vocab(os.path.join(REPO, "data", "keyword-vocabularies.csv"))
    s = score(text, det, edu)
    name = args.name or os.path.basename(args.path)

    dist = uk_ratios()
    pct = percentile_of(s["framing_ratio"], dist)

    print(f"\n{name}")
    print("=" * len(name))
    print(f"  words                {s['word_count']:,}")
    print(f"  detection terms      {s['detection_raw']}  ({s['detection_per_1k']} per 1k words)")
    print(f"  education terms      {s['education_raw']}  ({s['education_per_1k']} per 1k words)")
    print(f"  framing ratio        {s['framing_ratio']:.3f}   (detection / [detection + education])")
    print(f"  category             {s['frame_category']}")
    print(f"  UK percentile        {pct:.0f}th  "
          f"({pct:.0f}% of UK policies are less detection-framed)")

    for label, hits in (("detection", s["detection_keywords"]),
                        ("education", s["education_keywords"])):
        fired = sorted(((v, k) for k, v in hits.items() if v), reverse=True)
        zero = [k for k, v in hits.items() if not v]
        print(f"\n  top {label} terms:")
        for v, k in fired[:args.top]:
            print(f"    {v:4d}  {k}")
        if not fired:
            print("    (none)")
        print(f"  {len(zero)}/{len(hits)} {label} terms never fired")


if __name__ == "__main__":
    main()
