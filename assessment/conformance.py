"""Conformance screening against Higher Education (Use of Artificial
Intelligence) Regulations 2026 (GN No. 39 of 2026), regulation 5.

WHAT THIS IS. Regulation 5 places eleven duties on every Mauritian HEI. This
instrument decomposes them into 52 separately testable elements, searches an
institutional policy for language discharging each, and returns the evidence.

WHAT THIS IS NOT. It cannot judge adequacy. Finding the word "monitor" does not
establish that a monitoring mechanism exists. The instrument is reliable in one
direction only: where no indicator fires anywhere in a policy, that element is
almost certainly not addressed. Treat hits as *candidate evidence for an
assessor to adjudicate*, and misses as *gaps to investigate*.

Elements marked inter_alia=1 come from lists the regulation introduces with
"inter alia" or "including but not limited to". Those lists are explicitly
non-exhaustive, so a miss is weaker evidence of breach than a miss on a
free-standing duty.
"""
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
REG5 = os.path.join(HERE, "reg5")


def load_spec():
    obligations = list(csv.DictReader(open(os.path.join(REG5, "obligations.csv"))))
    elements = list(csv.DictReader(open(os.path.join(REG5, "elements.csv"))))
    for e in elements:
        e["inter_alia"] = e["inter_alia"] == "1"
        e["pattern"] = re.compile(e["indicators"], re.I)
    return obligations, elements


def _norm(text):
    return re.sub(r"\s+", " ", text)


def evidence(text, pattern, limit=3, window=100):
    out = []
    for m in pattern.finditer(text):
        a, b = max(0, m.start() - window), min(len(text), m.end() + window)
        out.append(("..." if a else "") + text[a:b].strip() + ("..." if b < len(text) else ""))
        if len(out) >= limit:
            break
    return out


def band(covered, total):
    if total == 0:
        return "n/a"
    f = covered / total
    if f == 0:
        return "Absent"
    if f < 0.5:
        return "Partial"
    if f < 1.0:
        return "Substantial"
    return "Full"


def assess(text, obligations=None, elements=None, limit=3):
    if obligations is None:
        obligations, elements = load_spec()
    t = _norm(text)
    results, by_ob = [], {}
    for e in elements:
        hits = len(e["pattern"].findall(t))
        r = {"element_id": e["element_id"], "obligation": e["obligation"],
             "element": e["element"], "inter_alia": e["inter_alia"],
             "hits": hits, "status": "present" if hits else "ABSENT",
             "evidence": evidence(t, e["pattern"], limit) if hits else []}
        results.append(r)
        by_ob.setdefault(e["obligation"], []).append(r)

    summary = []
    for o in obligations:
        rs = by_ob.get(o["obligation"], [])
        cov = sum(1 for r in rs if r["hits"])
        core = [r for r in rs if not r["inter_alia"]]
        core_cov = sum(1 for r in core if r["hits"])
        summary.append({
            "obligation": o["obligation"], "title": o["title"],
            "covered": cov, "total": len(rs),
            "core_covered": core_cov, "core_total": len(core),
            "band": band(cov, len(rs)),
            "missing": [r["element"] for r in rs if not r["hits"]],
            "missing_core": [r["element"] for r in rs if not r["hits"] and not r["inter_alia"]],
        })
    total_cov = sum(s["covered"] for s in summary)
    total_all = sum(s["total"] for s in summary)
    return {"summary": summary, "elements": results,
            "covered": total_cov, "total": total_all,
            "coverage": total_cov / total_all if total_all else 0.0}
