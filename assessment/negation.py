"""Negation scoping for the v2 and regulation 5 instruments.

Keyword counting cannot tell "the institution does not rely on detection tools"
from "the institution relies on detection tools". This module finds rejection clauses, where
the institution declines, denies or sets aside a practice, and marks keyword
hits inside them. The method follows NegEx: find a cue, then extend its scope
to the end of the clause.

Prohibitions are deliberately not cues. "Students must not use AI" and "not
permitted" are enforcement, and several are detection terms in their own right.
An imperative "Do not use..." addressed to students is a prohibition too, so a
cue on "do not" needs a subject before it. Negated hits are reported alongside
the raw counts, never silently removed. The published v1 instrument does not
use this module: it must reproduce Illingworth (2026) exactly.
"""
import re

CUES = re.compile(
    r"(?<=\w )(?:does|do|did|will|would|shall)\s+not\s+"
    r"(?:rely|use|employ|depend|endorse|require|treat|prescribe|impose)\b"
    r"|\brather than\b|\binstead of\b|\bnot intended (?:as|to)\b"
    r"|\b(?:is|are)\s+not\s+(?:a|an|intended)\b"
    r"|\bwithout (?:relying|resorting|recourse)\b|\bno longer\b"
    r"|\bnot (?:as )?(?:the )?(?:primary|sole)\b",
    re.I)
CONDITIONAL = re.compile(r"\b(?:if|when|where|unless|whether)\b(?:\W+\w+){0,4}\W*$", re.I)
CLAUSE_END = re.compile(r"[.;:!?]|\bbut\b|\bhowever\b|\bthough\b", re.I)
MAX_SCOPE = 110  # characters, roughly fifteen words


def negated_spans(text):
    """Character spans of rejection clauses in text."""
    spans = []
    for m in CUES.finditer(text):
        if CONDITIONAL.search(text[max(0, m.start() - 40):m.start()]):
            continue  # "if you are not the author..." is a condition, not a rejection
        end = CLAUSE_END.search(text, m.end())
        stop = min(end.start() if end else len(text), m.end() + MAX_SCOPE)
        spans.append((m.start(), stop))
    return spans


def in_spans(pos, spans):
    return any(a <= pos < b for a, b in spans)
