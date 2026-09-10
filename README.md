# AI policy assessment instruments

Three instruments for assessing institutional AI policies, built to apply
Illingworth's UK method in a Mauritian regulatory context.

| Instrument | Question it answers |
|---|---|
| **v1** — detection vs education | How does this policy compare with 96 UK institutions? |
| **v2** — six dimensions | What does the detection/education binary hide? |
| **reg 5** — conformance screening | Does this policy discharge the Mauritian statutory duties? |

No policy documents are included in this repository. See *Documents* below.

## Why a v2 was needed

Illingworth's published instrument scores policies on two axes, detection and
education. Applied to a regulator-issued document, two problems surfaced.

**It cannot see obligation.** Of the 34 detection terms, 27 never fire in the
HEC Mauritius guidelines — no *misconduct*, *penalty*, *Turnitin*, *sanction*.
That document's force is carried by `shall`, `compliance`, `regulations`,
`oversight`, `monitoring`, `audits`, `corrective`, `directives`. The instrument
reads a statutory instrument as gentle.

**"Education" conflates provision with agency.** Across the 96 UK policies,
**90.3%** of education-keyword hits are provision words — what the institution
supplies (*learning* 690, *guidance* 555, *support* 484). Only **9.7%** position
the student as a decider, and **25 of 96 policies contain zero agency terms**.
In 176,000 words of UK policy, `student voice` appears 3 times, `co-creation` 4,
`empower` 6.

Separating those makes the study's own qualitative finding measurable. Aston
University scores 0.06 on the published measure — apparently among the most
education-framed policies in Britain — and on the six-dimension instrument is
60% obligation language with zero agency terms.

## The six dimensions

`detection` (misconduct policing) · `compliance` (regulatory obligation) ·
`provision` (what the institution supplies) · `agency` (what the student
decides) · `ethics` (principle language) · `datafication` (learner as data
object).

Agency is reported twice: raw, and as `agency_share_strict`, which excludes
`discretion`, `judgement` and `agency` — terms that mean staff authority, not
student agency, in assessment regulations.

Hits inside rejection clauses ("does not rely on detection tools", "rather than
surveillance") are reported separately: `detection_ratio_adj` and
`enforcement_ratio_adj` set them aside. Prohibitions ("must not use AI") still
count as enforcement. v1 is unchanged.

## Regulation 5 conformance

The Higher Education (Use of Artificial Intelligence) Regulations 2026
(GN No. 39 of 2026, Government Gazette of Mauritius No. 25 of 11 April 2026)
place eleven duties on every Mauritian higher education institution.
`assessment/reg5/` decomposes them into **52 separately testable elements**.

This is a **screening instrument**, reliable in one direction only: where no
indicator fires, an element is almost certainly unaddressed; finding the word
"monitor" does not establish that a monitoring mechanism exists. Use
`--adjudication out.csv` to produce an assessor worksheet with evidence attached.

Calibration: 96% on the HEC guidelines (ceiling test), mean 36% across the 96 UK
policies written without reference to these regulations (negative control).

## Setup

The UK corpus is a separate CC BY 4.0 repository. Clone it alongside:

```bash
git clone https://github.com/sam-illingworth/uk-university-ai-policies.git
```

Then:

```bash
python3 assessment/validate.py       # reproduces the published UK results
python3 assessment/validate_v2.py    # v2 against the 96 UK policies
python3 assessment/validate_reg5.py  # reg 5 screening, negative control
```

To assess a policy (plain text):

```bash
python3 assessment/assess.py policy.txt --name "My Institution"
python3 assessment/score_reg5.py policy.txt --evidence --adjudication work.csv
```

Full method, calibration and limitations: [`assessment/README.md`](assessment/README.md).

## Documents

This repository contains **no policy documents**. The institutional policies
assessed with these instruments are not ours to redistribute, and the HEC
guidelines PDF carries a notice against reproduction. Sources:

- **UK corpus (96 policies, CC BY 4.0)** — https://github.com/sam-illingworth/uk-university-ai-policies
- **HEPI Policy Note 71** — Illingworth, S. (2026) *What UK university AI policies actually do: A study of 96 institutions*, HEPI, May 2026
- **Regulations 2026** — Government Gazette of Mauritius No. 25 of 11 April 2026
- **HEC guidelines** — Higher Education Commission, Mauritius

## Attribution and licence

The v2 vocabulary is a **derivative** of the keyword vocabularies published in
the UK corpus repository under CC BY 4.0. Of its 177 terms, **77 are inherited**
from that source:

| Dimension | Inherited | Total |
|---|---|---|
| detection | 34 | 34 |
| provision | 27 | 34 |
| agency | 12 | 26 |
| ethics | 4 | 28 |
| compliance | 0 | 37 |
| datafication | 0 | 18 |

Changes made: the two-way detection/education split was reorganised into six
dimensions; the education vocabulary was divided into provision, agency and
ethics; compliance and datafication were added.

- **Vocabularies and specifications** (`assessment/vocab/`, `assessment/reg5/`) —
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), attributing
  Illingworth (2026) as above. Statutory text in `reg5/obligations.csv` is
  reproduced from the Government Gazette.
- **Code** (`assessment/*.py`) — MIT, see `LICENSE`.

## How this was produced

The instruments were built with Claude Code, an AI coding agent made by
Anthropic. Study design, document selection and interpretive judgement are the
authors'. This mirrors the disclosure in Policy Note 71, and for the same
reason: the automated parts are reproducible, the judgements are contestable,
and a reader should know which is which.
