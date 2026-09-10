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
from negation import negated_spans, in_spans
from textnorm import normalise
from collections import OrderedDict

DIMENSIONS = ["detection", "compliance", "provision", "agency", "ethics", "datafication"]

# Mean student self-determination in a student-facing AI policy but staff
# authority in assessment regulations: "at the discretion of the assessment
# board", "academic judgement", even "a person/agency external to the
# institution". agency_share_strict excludes them; report it alongside the raw
# figure for any document that contains assessment or examination rules.
AMBIGUOUS_AGENCY = frozenset({"discretion", "judgement", "agency"})

# Dimensions whose terms name institutional practices. A hit inside a rejection
# clause ("does not rely on detection tools") is reported as negated.
NEGATABLE = ("detection", "compliance", "datafication")


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
    text = normalise(text)
    wc = len(text.split())
    hits = {d: count_terms(text, terms) for d, terms in vocab.items()}
    hits = _decollide(hits, vocab)
    raw = {d: sum(h.values()) for d, h in hits.items()}
    per1k = {d: round(raw[d] / wc * 1000, 2) if wc else 0.0 for d in raw}

    def safe(n, d):
        return n / d if d else 0.0

    strict_agency = raw["agency"] - sum(hits["agency"].get(t, 0) for t in AMBIGUOUS_AGENCY)
    low = text.lower()
    spans = negated_spans(low)
    negated = {d: 0 for d in DIMENSIONS}
    negated_hits = []
    for d in NEGATABLE:
        for t in vocab[d]:
            for m in re.finditer(r"\b" + re.escape(t) + r"\b", low):
                if in_spans(m.start(), spans):
                    negated[d] += 1
                    negated_hits.append((d, t, m.start()))
    adj = {d: max(0, raw[d] - negated[d]) for d in raw}
    indices = {
        # of the developmental language, how much positions the student as decider
        "agency_share": safe(raw["agency"], raw["agency"] + raw["provision"]),
        # the same, without the role-ambiguous terms
        "agency_share_strict": safe(strict_agency, strict_agency + raw["provision"]),
        # the UK study's axis, rebuilt: policing vs everything developmental
        "detection_ratio": safe(raw["detection"],
                                raw["detection"] + raw["provision"] + raw["agency"]),
        # what the UK binary could not see: total obligation vs total development
        "enforcement_ratio": safe(raw["detection"] + raw["compliance"],
                                  raw["detection"] + raw["compliance"]
                                  + raw["provision"] + raw["agency"]),
        # principle language as a share of all framing
        "ethics_share": safe(raw["ethics"], sum(raw.values())),
        # the same two ratios with hits inside rejection clauses set aside
        "detection_ratio_adj": safe(adj["detection"],
                                    adj["detection"] + raw["provision"] + raw["agency"]),
        "enforcement_ratio_adj": safe(adj["detection"] + adj["compliance"],
                                      adj["detection"] + adj["compliance"]
                                      + raw["provision"] + raw["agency"]),
    }
    return {"word_count": wc, "raw": raw, "per1k": per1k,
            "hits": hits, "indices": indices,
            "negated": negated, "negated_hits": negated_hits}


def overlap_report(vocab):
    """Cross-dimension substring containment causes one phrase to score twice."""
    flat = [(t, d) for d, ts in vocab.items() for t in ts]
    out = []
    for t, d in flat:
        for t2, d2 in flat:
            if t != t2 and d != d2 and re.search(r"\b" + re.escape(t) + r"\b", t2):
                out.append((t2, d2, t, d))
    return out
