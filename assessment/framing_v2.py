"""Six-dimension framing scorer.

Extends the two-dimension (detection/education) instrument of Illingworth (2026)
in three ways, each justified empirically in assessment/README.md:

  detection    misconduct policing            (retained verbatim from the UK study)
  compliance   regulatory obligation          (new: the register that carries force
                                               in a regulator-issued instrument)
  provision    what the institution supplies  (the ~90% of the UK "education" signal)
  agency       what the student decides       (the ~10%, split out so it cannot be
                                               masked by provision language)
  ethics       normative principle language   (split out: saying "ethical" often is
                                               not the same as being about learning)
  datafication learner as data object         (surveillance by analytics rather than
                                               by misconduct detection)
"""
import csv, re
from collections import OrderedDict

DIMENSIONS = ["detection", "compliance", "provision", "agency", "ethics", "datafication"]


def load_vocab(path):
    v = OrderedDict((d, []) for d in DIMENSIONS)
    for row in csv.DictReader(open(path)):
        v[row["frame"]].append(row["keyword"])
    return v


def count_terms(text, terms):
    low = text.lower()
    return {t: len(re.findall(r"\b" + re.escape(t) + r"\b", low)) for t in terms}


def _decollide(hits, vocab):
    """Subtract cross-dimension double counts.

    "at-risk" (datafication) also matches "risk" (compliance); "learning
    analytics" (datafication) also matches "learning" (provision). Left alone,
    one phrase would score in two dimensions and distort the very ratios this
    instrument exists to measure. Nesting WITHIN a dimension (e.g. "critical
    thinking" also matching "critical") is left intact, matching the behaviour
    of the original UK instrument.
    """
    flat = [(t, d) for d, ts in vocab.items() for t in ts]
    for long_t, long_d in flat:
        n = hits[long_d].get(long_t, 0)
        if not n:
            continue
        for short_t, short_d in flat:
            if short_d != long_d and short_t != long_t and \
               re.search(r"\b" + re.escape(short_t) + r"\b", long_t):
                hits[short_d][short_t] = max(0, hits[short_d][short_t] - n)
    return hits


def score(text, vocab):
    wc = len(text.split())
    hits = {d: count_terms(text, terms) for d, terms in vocab.items()}
    hits = _decollide(hits, vocab)
    raw = {d: sum(h.values()) for d, h in hits.items()}
    per1k = {d: round(raw[d] / wc * 1000, 2) if wc else 0.0 for d in raw}

    def safe(n, d):
        return n / d if d else 0.0

    indices = {
        # of the developmental language, how much positions the student as decider
        "agency_share": safe(raw["agency"], raw["agency"] + raw["provision"]),
        # the UK study's axis, rebuilt: policing vs everything developmental
        "detection_ratio": safe(raw["detection"],
                                raw["detection"] + raw["provision"] + raw["agency"]),
        # what the UK binary could not see: total obligation vs total development
        "enforcement_ratio": safe(raw["detection"] + raw["compliance"],
                                  raw["detection"] + raw["compliance"]
                                  + raw["provision"] + raw["agency"]),
        # principle language as a share of all framing
        "ethics_share": safe(raw["ethics"], sum(raw.values())),
    }
    return {"word_count": wc, "raw": raw, "per1k": per1k,
            "hits": hits, "indices": indices}


def overlap_report(vocab):
    """Cross-dimension substring containment causes one phrase to score twice."""
    flat = [(t, d) for d, ts in vocab.items() for t in ts]
    out = []
    for t, d in flat:
        for t2, d2 in flat:
            if t != t2 and d != d2 and re.search(r"\b" + re.escape(t) + r"\b", t2):
                out.append((t2, d2, t, d))
    return out
