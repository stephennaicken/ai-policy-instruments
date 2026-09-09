"""Run all three instruments over one policy document.

  1. UK v1      Illingworth (2026) as published: detection vs education
  2. v2         six dimensions, splitting provision from agency
  3. reg 5      conformance screening against the Mauritian regulations

Usage: python3 assessment/assess.py <policy.txt> [--name NAME] [--adjudication OUT.csv]
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(script, args):
    print("\n" + "=" * 78)
    subprocess.run([PY, os.path.join(HERE, script)] + args, check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--name", default=None)
    ap.add_argument("--adjudication", default=None)
    a = ap.parse_args()
    name = a.name or os.path.basename(a.path)
    base = [a.path, "--name", name]

    print(f"\nThree-instrument assessment of: {name}")
    print("  1. UK v1  — the published instrument, for comparability with the 96")
    print("  2. v2     — six dimensions, for what the binary hides")
    print("  3. reg 5  — conformance screening, for what the regulator requires")

    run("score_policy.py", base)
    run("score_v2.py", base)
    run("score_reg5.py", base + (["--adjudication", a.adjudication] if a.adjudication else []))

    print("\n" + "=" * 78)
    print("Reminder: all three are screening instruments over word patterns.")
    print("None establishes adequacy. The qualitative framework in")
    print("uk-university-ai-policies/analysis/coding-framework.md remains the arbiter.")


if __name__ == "__main__":
    main()
