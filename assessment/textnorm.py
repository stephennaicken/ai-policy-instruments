"""Text normalisation shared by the v2 and regulation 5 instruments.

Text extracted from PDFs breaks lines mid-phrase, so "academic\\nintegrity"
would not match the term "academic integrity". Both instruments collapse runs
of whitespace to a single space before matching. A hyphen at a line break
("over-\\n   reliance") is kept and the line joined ("over-reliance").

The v1 instrument deliberately does not normalise. Illingworth (2026) counted
the scraped text as it stood, and normalising would change 12 more of the 96
published results. v1 exists to reproduce those results exactly.
"""
import re

_HYPHEN_BREAK = re.compile(r"-[ \t]*\n\s*")
_WHITESPACE = re.compile(r"\s+")


def normalise(text):
    return _WHITESPACE.sub(" ", _HYPHEN_BREAK.sub("-", text))
