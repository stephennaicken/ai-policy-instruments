"""Reimplementation of the framing analysis from Illingworth (2026),
uk-university-ai-policies. Counts detection vs education keywords in a
policy text and returns the framing ratio and category.

Validated to reproduce analysis/framing_analysis.csv for all 96 UK policies.
"""
import csv, re, sys

csv.field_size_limit(sys.maxsize)


def load_vocab(path):
    detection, education = [], []
    for row in csv.DictReader(open(path)):
        (detection if row["frame"] == "detection" else education).append(row["keyword"])
    return detection, education


def count_terms(text, terms):
    """Whole-word, case-insensitive count of each term."""
    low = text.lower()
    return {t: len(re.findall(r"\b" + re.escape(t) + r"\b", low)) for t in terms}


def word_count(text):
    return len(text.split())


def categorise(ratio):
    if ratio < 0.4:
        return "Education-dominant"
    if ratio <= 0.6:
        return "Balanced"
    return "Detection-dominant"


def score(text, detection, education):
    d = count_terms(text, detection)
    e = count_terms(text, education)
    d_raw, e_raw = sum(d.values()), sum(e.values())
    wc = word_count(text)
    total = d_raw + e_raw
    ratio = d_raw / total if total else 0.0
    return {
        "word_count": wc,
        "detection_raw": d_raw,
        "education_raw": e_raw,
        "detection_per_1k": round(d_raw / wc * 1000, 2) if wc else 0.0,
        "education_per_1k": round(e_raw / wc * 1000, 2) if wc else 0.0,
        "detection_keywords": d,
        "education_keywords": e,
        "framing_ratio": ratio,
        "frame_category": categorise(ratio),
    }
