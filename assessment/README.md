# Assessing our institution's AI policy

Applies the method from Illingworth (2026), *What UK University AI Policies
Actually Do* ([repo](https://github.com/sam-illingworth/uk-university-ai-policies),
cloned in `../uk-university-ai-policies`), to a non-UK institution.

The source repository is data and method only — it ships no code. These scripts
reimplement the computational half of the study.

## Files

| File | Purpose |
|---|---|
| `framing.py` | Keyword counting, framing ratio, frame category |
| `validate.py` | Checks the reimplementation against the published UK results |
| `score_policy.py` | Scores one policy text and places it in the UK distribution |

## Method as reimplemented

- Keywords are matched **case-insensitively on whole-word boundaries**.
- `framing_ratio = detection_raw / (detection_raw + education_raw)`
- Categories: `< 0.4` Education-dominant, `0.4–0.6` Balanced, `> 0.6` Detection-dominant.
  (Derived from the published data: education-dominant tops out at 0.386,
  balanced spans 0.400–0.545, detection-dominant starts at 0.669.)

## Validation

`python3 assessment/validate.py` compares all 96 published policies.

Word counts, detection counts, per-1k rates and frame categories reproduce
**exactly**. Across 7,392 keyword cells (96 policies x 77 terms) there is a
single discrepancy: Solent University's published `assessment design` count of 1
comes from the text "assessment design**s**", which whole-word matching does not
count. Every other multi-word and single-word term matches. We keep the
consistent whole-word rule; it moves that one policy's ratio from 0.188 to 0.190
and changes no category.

## Caveat for non-UK use

The vocabularies encode UK regulatory language (`turnitin`, `unauthorised`,
`academic integrity`, `contract cheating`). Applied unmodified outside the UK,
detection terms may under-fire and depress the ratio for reasons of dialect
rather than framing. Report the unmodified score for comparability against the
96, and an adapted-vocabulary score for validity — and check which terms never
fired before trusting either.

---

# v2: a six-dimension instrument

## Why the UK binary is not enough

The original instrument scores detection vs education. Two problems surfaced when
it was pointed at a regulator-issued document.

**1. It cannot see obligation.** Applied to the HEC Mauritius guidelines, 27 of
the 34 detection terms never fire. No *misconduct*, *penalty*, *Turnitin*,
*sanction*, *cheating* or *disciplinary*. The document's force is carried by
`shall`, `compliance`, `regulations`, `standards`, `oversight`, `monitoring`,
`audits`, `corrective`, `directives` — a register the instrument does not measure.
It therefore reads a statutory instrument as gentle.

**2. "Education" conflates provision with agency.** Across the 96 UK policies,
**90.3%** of education-keyword hits are provision words — what the institution
supplies (*learning* 690, *guidance* 555, *support* 484, *skills* 289). Only
**9.7%** position the student as a decider, and **25 of 96 policies contain zero
agency terms**. In the whole UK corpus, `student voice` occurs 3 times,
`co-creation` 4, `empower` 6, `agency` 9.

This means the study's headline finding — education vocabulary masking compliance
function — is reproducible from its own computational instrument, once provision
and agency are separated. The 86.5% education-dominant figure is largely a count
of institutions describing their own service provision.

## The six dimensions

| Dimension | Measures | Source |
|---|---|---|
| `detection` | Misconduct policing | Retained verbatim from the UK study |
| `compliance` | Regulatory obligation, oversight, audit, enforcement | New |
| `provision` | What the institution supplies | UK "education" minus agency/ethics |
| `agency` | What the student decides | Split out |
| `ethics` | Normative principle language | Split out |
| `datafication` | Learner as data object; analytics, profiling, at-risk | New |

`assessment/vocab/keyword-vocabularies-v2.csv` — 177 terms, same
`keyword,frame,rationale` schema as the UK file, no duplicate terms.

Derived indices: `agency_share` (agency / agency+provision), `detection_ratio`
(the UK axis rebuilt), `enforcement_ratio` (obligation vs development),
`ethics_share`.

Cross-dimension substring collisions (`at-risk`/`risk`, `learning
analytics`/`learning`) are de-collided so one phrase cannot score twice.
Nesting *within* a dimension is left intact to match the UK instrument.

## Validation

`python3 assessment/validate_v2.py` — applies v2 to the 96 UK policies it was
not built on. All dimensions vary meaningfully (compliance fires in 83/96, mean
5.32 per 1k, range 0–28.81), so the new dimensions are not Mauritius artefacts.

The instrument also catches policies the original mis-classifies. Aston
University scores 0.06 on the original ratio — apparently the most
education-framed policy in the sector — but has an `enforcement_ratio` of 0.60
and **zero** agency terms.

## Limitations

- **Circularity.** The `compliance` and `datafication` vocabularies were derived
  partly from the HEC document. Re-scoring with only terms independently attested
  in the UK corpus (>=10 occurrences) drops 19 of 37 compliance terms; HEC still
  scores at the 99th percentile and `enforcement_ratio` moves 0.542 -> 0.494. The
  compliance finding is robust. `agency` is unaffected, having been derived from
  the UK study.
- **`datafication` is under-validated.** Only 2 of its 18 terms clear the UK
  attestation threshold, and it is absent from 74 of 96 UK policies. UK AI
  policies simply do not discuss learning analytics. The dimension is real in the
  Mauritian material but cannot be calibrated against the UK corpus; treat its
  percentiles as indicative only.
- **Keyword counting is not reading.** These are framing indicators, not verdicts.
  The qualitative framework in `analysis/coding-framework.md` remains the arbiter.
- **`agency` is role-ambiguous on assessment regulations.** Three of its terms —
  `discretion`, `judgement`, `agency` — mean student self-determination in a
  student-facing AI policy but assessor authority in assessment regulations
  ("at the discretion of the assessment board", "academic judgement", and even
  "a person/agency external to the institution"). On one combined corpus of an
  AI policy plus assessment regulations they lift `agency_share` from 0.072 to
  0.171 — from the UK median to the 79th percentile. The scorer therefore
  reports `agency_share_strict`, which excludes them, alongside the raw figure,
  and marks them with `*` in its output. Use the strict figure for any document
  containing assessment or examination rules. A fourth term, `consulted`, was
  removed outright: in the 96 UK policies it appears three times and never
  means students were consulted, and in one institutional draft all three uses
  referred to colleagues or to records. It is replaced by student-specific
  phrases ("students were consulted", "consultation with students").

---

# Instrument 3: regulation 5 conformance screening

The two framing instruments characterise a document. This one asks a different
question: does an institutional policy discharge the eleven duties that
regulation 5 of the Higher Education (Use of Artificial Intelligence)
Regulations 2026 (GN No. 39 of 2026, in force 31 March 2026) places on every
Mauritian HEI?

## Design

`reg5/obligations.csv` holds the eleven duties with their statutory text.
`reg5/elements.csv` decomposes them into **52 separately testable elements** —
5(a) alone requires ethical use, academic integrity and governance to be covered
across teaching, learning, assessment, grading and research, so it is eight
elements, not one.

Elements carry an `inter_alia` flag. Where the regulation introduces a list with
"inter alia" or "including but not limited to", that list is explicitly
non-exhaustive and a miss is weaker evidence of breach. The output separates
these from core gaps.

## What it can and cannot tell you

It is reliable in one direction. Where no indicator fires anywhere in a policy,
that element is almost certainly not addressed. The converse does not hold:
finding the word "monitor" does not establish that a monitoring mechanism
exists. Hits are **candidate evidence for an assessor to adjudicate**.

`--adjudication out.csv` writes an assessor worksheet with the evidence attached
and a rating column: 0 absent · 1 mentioned · 2 addressed · 3 addressed with a
specified mechanism, owner or process. The screening narrows what a human reads;
it does not replace the reading.

## Calibration

| | element coverage |
|---|---|
| HEC guidelines (ceiling test — the regulator's own document) | 96% |
| 96 UK policies (negative control — written without reference to these regs) | mean 37%, median 35%, range 4–88% |

The UK gap profile is what a domain expert would predict: strongest on
disclosure and acknowledgement (5(f)), near-absent on equitable access (5(c)),
programme updating (5(e)) and corrective action (5(k)).

Every pattern was audited against its UK hit rate. One was genuinely broken:
"response to non-compliance" fired in 0 of 96 policies because it looked for
*non-compliance*, whereas UK policies say *breach of*, *in breach*, *contravene*
and *failure to comply* — broadened, it now fires in 17 of 96. Three
near-universal absences were checked against near-synonyms and confirmed real:
patents (1/96, though *intellectual property* appears 42 times),
explainability (`explainab` twice in 176,000 words) and dignity (twice).
Capturing groups were converted to non-capturing throughout, since `findall`
returns group contents rather than matches.

The protected-grounds element (`c6`) was wrong in both directions. It counted
"background research" as a protected ground, and it missed disability and
language provisions worded as "documented accommodations" and "non-native
speakers". It now ignores *background* when followed by research, reading and
similar words, and catches *accommodations*, *reasonable adjustment*,
*non-native*, *second language* and *English language learner*. That was the
instrument's first confirmed false negative: "absent" is strong evidence, not
proof.

## Running it

```
python3 assessment/score_reg5.py policy.txt --evidence --adjudication work.csv
python3 assessment/assess.py policy.txt --name "My University"   # all three
```

## Scope note

Regulation 5 binds institutions, not the Commission. Screening the HEC
guidelines against it is a ceiling test of the instrument, not an assessment of
the HEC — the Commission's own duties are in regulation 4.
