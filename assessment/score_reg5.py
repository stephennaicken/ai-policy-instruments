"""Screen an institutional AI policy against regulation 5 of the Higher
Education (Use of Artificial Intelligence) Regulations 2026.

Usage:
  python3 assessment/score_reg5.py <policy.txt> [--name NAME]
                                   [--evidence] [--adjudication out.csv]
"""
import argparse, csv, os, sys, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from conformance import load_spec, assess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--name", default=None)
    ap.add_argument("--evidence", action="store_true",
                    help="print supporting passages for each element found")
    ap.add_argument("--adjudication", metavar="OUT.csv",
                    help="write an assessor worksheet with evidence attached")
    a = ap.parse_args()

    text = open(a.path, encoding="utf-8", errors="replace").read()
    obs, els = load_spec()
    res = assess(text, obs, els)
    name = a.name or os.path.basename(a.path)

    print(f"\nRegulation 5 conformance screening — {name}")
    print(f"{len(text.split()):,} words | {res['covered']}/{res['total']} elements "
          f"show relevant language ({res['coverage']*100:.0f}%)")
    print("SCREENING ONLY: presence of language is not evidence of adequacy.\n")

    print(f"{'reg':6s} {'obligation':38s} {'elements':>9} {'band':>12}  gaps")
    for s in res["summary"]:
        gaps = ", ".join(s["missing_core"]) or ("—" if not s["missing"] else "(non-exhaustive only)")
        print(f"{s['obligation']:6s} {s['title'][:37]:38s} "
              f"{s['covered']:4d}/{s['total']:<4d} {s['band']:>12}  {gaps[:60]}")

    hard = [s for s in res["summary"] if s["missing_core"]]
    if hard:
        print("\nDuties with unaddressed core elements — these are the real gaps:")
        for s in hard:
            print(f"  {s['obligation']} {s['title']}")
            for m in s["missing_core"]:
                print(f"      no language found for: {m}")
    else:
        print("\nNo core element is entirely unaddressed.")

    soft = [(s["obligation"], m) for s in res["summary"] for m in s["missing"]
            if m not in s["missing_core"]]
    if soft:
        print("\nUnaddressed items from non-exhaustive ('inter alia') lists —")
        print("weaker evidence of breach, but worth a decision:")
        for o, m in soft:
            print(f"  {o}  {m}")

    if a.evidence:
        print("\n" + "=" * 70 + "\nEVIDENCE\n" + "=" * 70)
        for e in res["elements"]:
            if not e["evidence"]:
                continue
            print(f"\n{e['element_id']} [{e['obligation']}] {e['element']}  ({e['hits']} hits)")
            for ev in e["evidence"]:
                print(textwrap.fill(ev, 96, initial_indent="    ", subsequent_indent="    "))

    if a.adjudication:
        with open(a.adjudication, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["element_id", "obligation", "element", "non_exhaustive",
                        "screening", "hits", "evidence",
                        "assessor_rating_0_3", "assessor_note"])
            for e in res["elements"]:
                w.writerow([e["element_id"], e["obligation"], e["element"],
                            "yes" if e["inter_alia"] else "no", e["status"], e["hits"],
                            " || ".join(e["evidence"]), "", ""])
        print(f"\nAssessor worksheet written to {a.adjudication}")
        print("Rating scale: 0 absent · 1 mentioned · 2 addressed · 3 addressed with a "
              "specified mechanism, owner or process.")


if __name__ == "__main__":
    main()
