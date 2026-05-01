---
id: OBPI-0.26.0-02-references
parent: ADR-0.26.0-governance-library-module-absorption
item: 2
status: Completed
lane: heavy
date: 2026-03-21
paired_with: OBPI-0.25.0-30-references-pattern
---

# OBPI-0.26.0-02: References

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-02 — "Evaluate and absorb lib/references.py (797 lines) — cross-reference resolution and link management"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/references.py` (797 lines) and
determine: Absorb (opsdev is better) or Exclude (domain-specific). gzkit has
no equivalent module for cross-reference resolution and link management. The
opsdev module was anticipated to provide dedicated reference tracking for
resolving links between ADRs, OBPIs, artifacts, and governance documents.
This OBPI records the comparison outcome and decision rationale.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/references.py` (797 lines)
- **gzkit equivalent:** None

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any absorption outcome would
add or change a runtime module / CLI surface. Exclude outcomes inherit Heavy
because the decision is binding on future governance-library absorption.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Cross-reference resolution is a domain-agnostic governance primitive that any governance framework needs

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a generic link-resolution framework beyond governance needs

## Requirements (FAIL-CLOSED)

1. Read both implementations completely before recording a decision.
2. Document comparison across feature completeness, error handling,
   cross-platform robustness, and test coverage.
3. Record decision with rationale: Absorb or Exclude (no Confirm path — gzkit
   has no equivalent).
4. If Absorb: adapt to gzkit conventions (Pydantic, pathlib, UTF-8) and add
   tests under `tests/`.
5. If Exclude: document why the module is domain-specific, citing concrete
   evidence from the opsdev source.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` for Exclude outcomes (no code, no tests, no CLI change)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a
  governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — understand the 12-module absorption program and the subtraction test
- [x] Sibling OBPI brief pattern (e.g. `OBPI-0.0.16-04-backfill-and-ghi-closure.md`) — confirm canonical section headings and required structure
- [x] `src/gzkit/schemas/obpi.json` — required headers contract

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/references.py` (797 lines) — opsdev source under review
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Parent ADR Cross-Reference Matrix row for `references.py` reviewed: anticipates "Strong absorption candidate unless link semantics are ops-specific"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/references.py` read end-to-end (lines 1-797): docstring, module constants, hardcoded airline reference list, PDF citation extractor, APA renderer, rosetta-stone updater
- [x] gzkit surface check: `docs/references/`, `docs/REFERENCES.md`, `docs/ANNOTATED_BIBLIOGRAPHY.md`, `docs/airlineops_rosetta_stone.md` — all confirmed absent
- [x] gzkit dependency check: no `pypdf` in `pyproject.toml`
- [x] gzkit's actual governance cross-referencing reviewed: `src/gzkit/traceability.py`, `src/gzkit/governance/trust_audits.py`, `src/gzkit/commands/adr_autolink.py` — none overlap with PDF-citation generation

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Exclude` decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior, the brief names
  `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.26.0-02-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`. **Decision: Exclude** — see
  `## Decision` below.
- [x] REQ-0.26.0-02-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between opsdev and gzkit.
  See `## Comparison` (dimension-by-dimension table) and `## Decision`
  (five-point ops-specific semantics enumeration).
- [x] REQ-0.26.0-02-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. **N/A — Exclude
  outcome.** The Absorb path was not taken; this REQ is vacuously satisfied.
- [x] REQ-0.26.0-02-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is ops-specific or otherwise not fit for gzkit. See `## Decision`
  — the five ops-specific semantics (filesystem contract, airline-domain data,
  discipline-specific dependency, literature-management purpose, naming
  collision) each cite the opsdev module line-range that demonstrates the
  ops-specific character.
- [x] REQ-0.26.0-02-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. **N/A.** Exclude outcome with zero code changes under
  `src/gzkit/`, zero new CLI verbs, zero generated-surface change — nothing
  operator-visible changes, so Gate 4 behavioral proof is not required.

## Comparison

### opsdev module surface (observed by reading the file)

`../airlineops/src/opsdev/lib/references.py` (797 lines) is an
academic-bibliography and APA-citation generator. Concrete anchors:

- **Module docstring** (lines 1-21): "References index builder and APA
  citation generator (internalized). Source:
  scripts/generate_references_index.py, scripts/generate_apa_citations.py."
  The module name "references" is short for "academic references", not
  "cross-references between governance artifacts".
- **Module-level filesystem constants** (lines 44-54): `REF_DIR =
  docs/references/`, `MANIFEST = docs/references/_rename_manifest.json`,
  `INDEX_MD = docs/references/index.md`, `BIB_MD =
  docs/references/ANNOTATED_BIBLIOGRAPHY.md`, `REFERENCES_MD =
  docs/REFERENCES.md`, `ROSETTA_MD = docs/airlineops_rosetta_stone.md`.
  Every anchor points at an academic-PDF / airline-research surface.
- **Hardcoded airline reference list** (lines 56-63): `ROSETTA_REFERENCES_LIST`
  contains Belobaba/Odoni/Barnhart *The Global Airline Industry* (2015),
  Bazargan *Airline Operations and Scheduling* (2016), Abdelghany & Abdelghany
  *Airline Network Planning and Scheduling* (2018), Littlewood *Forecasting
  and Control of Passenger Bookings* (AGIFORS 1972), Talluri & van Ryzin
  *Theory and Practice of Revenue Management* (Springer 2004), and Barnhart
  airline-scheduling OR literature. Pure airline-domain content.
- **PDF-citation extractor** (lines 617-670): `build_citation(pdf: Path)` opens
  a PDF with `pypdf.PdfReader`, extracts title/authors/year/journal/volume/
  issue/pages/DOI from metadata and text heuristics, returns a `Citation`
  dataclass. Lines 249-319 render `Citation.apa_markdown()` — APA-style
  bibliographic output.
- **Top-level run functions**: `run()` (lines 207-224) regenerates
  `docs/references/index.md`; `run_apa_citations()` (lines 731-760) scans
  `docs/references/*.pdf` and injects APA markdown into `docs/REFERENCES.md`
  between `<!-- BEGIN AUTO APA -->` / `<!-- END AUTO APA -->` markers;
  `run_rosetta_refs()` (lines 782-797) writes the hardcoded airline
  reference list into `docs/airlineops_rosetta_stone.md`.

### gzkit equivalent surface

None exists, and none is planned:

- `docs/references/` — **absent** (`test -d docs/references` → false)
- `docs/REFERENCES.md` — **absent** (`test -f` → false)
- `docs/ANNOTATED_BIBLIOGRAPHY.md` — **absent**
- `docs/airlineops_rosetta_stone.md` — **absent** (airline-specific)
- No `pypdf` dependency in `pyproject.toml`; no APA/bibliography code in
  `src/gzkit/**` (the `rg` matches for "reference" in gzkit are all about
  skill-surface audits, ADR governance cross-validation, or manifest
  references — none are PDF/bibliography infrastructure)

The brief's OBJECTIVE anticipated "dedicated reference tracking for resolving
links between ADRs, OBPIs, artifacts, and governance documents." That
anticipation was based on the filename alone. The module's actual content is
academic-literature citation management, which is not the same capability.
gzkit's equivalent functions for governance-artifact cross-referencing live
in `src/gzkit/traceability.py`, `src/gzkit/governance/trust_audits.py`, and
the ADR autolink / @covers tooling — none of which overlap with PDF-citation
generation.

### Dimension-by-dimension comparison

| Dimension | opsdev `lib/references.py` | gzkit equivalent | Verdict |
|-----------|----------------------------|------------------|---------|
| Feature completeness | Full APA-citation generation, PDF-index builder, bibliography cross-linking, rosetta-stone refresh — all scoped to academic airline literature | None — gzkit has no academic-bibliography surface | **Not comparable** — opsdev feature set serves a domain gzkit does not operate in |
| Error handling | `pypdf` errors silently fall back to filename stubs; JSON parse errors on the rename manifest silently return empty dict (lines 89-91) | N/A | No meaningful comparison — no gzkit equivalent to error-handle |
| Cross-platform robustness | Uses `pathlib.Path` and `encoding="utf-8"`; mostly cross-platform-safe | N/A | Would need minor hardening if absorbed, but moot |
| Test coverage | Not examined in plan — module is ops-only | N/A | N/A |
| Fit with gzkit conventions | Requires `pypdf` dep, airline-ref literals, `docs/references/` surface | gzkit does not carry any of these | **Negative** — absorbing inflates gzkit's scope with airline-research infrastructure |

### Naming-collision note

The OBPI brief template was authored from the 12-module checklist in the
parent ADR before the module bodies were read. The filename "references"
suggested governance cross-reference resolution. The actual module is an
academic-bibliography generator. This is recorded here so future absorption
work does not repeat the mistake of inferring module purpose from filename.

## Decision

**Exclude.** `../airlineops/src/opsdev/lib/references.py` is domain-specific
airline-research-literature infrastructure. It fails the subtraction test
(`opsdev − gzkit = pure ops domain`) on every dimension the brief requires:

1. **Filesystem contract is domain-specific.** Module-level constants
   (references.py:44-54) hardcode `docs/references/`,
   `docs/ANNOTATED_BIBLIOGRAPHY.md`, `docs/REFERENCES.md`, and
   `docs/airlineops_rosetta_stone.md` — none of which exist in gzkit and none
   of which gzkit plans to acquire.
2. **Content is airline-domain data.** `ROSETTA_REFERENCES_LIST`
   (references.py:56-63) hardcodes six airline operations-research and
   revenue-management texts. Absorbing this module would inject airline
   content into a governance toolkit.
3. **Dependency is discipline-specific.** The module carries `pypdf` solely
   to extract APA metadata from academic PDFs (references.py:31-34, 617-670).
   gzkit has no other use for `pypdf`, and introducing a dependency that
   serves zero gzkit operators would force the 40% coverage floor and lint
   rules onto code nobody in gzkit will exercise.
4. **Functional purpose is literature management, not artefact linkage.**
   `build_citation`, `render_apa_section`, `update_references_apa`,
   `crosslink_bibliography`, and `run_rosetta_refs` operate on academic
   literature. gzkit's governance cross-referencing (ADR → OBPI → artefact)
   lives in `src/gzkit/traceability.py`, `src/gzkit/governance/trust_audits.py`,
   and `src/gzkit/commands/adr_autolink.py` — none of which overlap with
   PDF-citation generation.
5. **Naming collision, not behavioral overlap.** The brief's OBJECTIVE
   anticipated generic governance reference resolution because the filename
   says "references". The module's docstring (lines 1-21) and implementation
   both make clear the name is short for "academic references / bibliography",
   not "cross-references between governance artifacts". Surface-level name
   collision with no behavioral overlap.

No code lands under `src/gzkit/` for this OBPI. No new tests. No new CLI
surface. No operator-visible behavior change.

### Implementation Summary


- Outcome: Exclude — no absorption, no code under src/gzkit/, no test additions, no CLI surface change
- Files changed: brief-only (docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md) — recorded Decision, Comparison, five-point rationale, REQ evidence, completion checklist; fixed three briefs/ to obpis/ path drifts in Verification section; restructured sections to satisfy obpi.json schema
- Gates resolved: Gate 1 ADR intent recorded; Gate 2 baseline quality green (lint, typecheck, OBPI-scoped tests, covers parity, documents+surfaces+brief-headings validation); Gate 3 brief is the Docs deliverable; Gate 4 N/A with rationale (zero operator-visible behavior change); Gate 5 human attested
- REQ coverage: REQ-01 decision recorded (Exclude); REQ-02 rationale cites concrete dimension-by-dimension differences; REQ-03 vacuous (Absorb path not taken); REQ-04 five-point ops-specific-semantics enumeration with opsdev line anchors; REQ-05 Gate 4 N/A rationale present
- Subtraction test: opsdev minus gzkit equals pure ops domain — holds decisively

### Key Proof


Decision Exclude; proof is that the opsdev module cannot function without airline-research surfaces gzkit does not have. Observable:

- `test -d docs/references` returns absent; `test -f docs/REFERENCES.md` returns absent; `test -f docs/ANNOTATED_BIBLIOGRAPHY.md` returns absent — none of the module-level filesystem constants at references.py:44-54 resolve in gzkit.
- `rg -n 'Belobaba|Bazargan|Abdelghany|Littlewood|Talluri' ../airlineops/src/opsdev/lib/references.py` matches lines 57-62 — the hardcoded ROSETTA_REFERENCES_LIST is six airline operations-research and revenue-management texts; absorbing would inject airline content into a governance toolkit.
- `rg -n 'pypdf' pyproject.toml` returns no matches — gzkit has no academic-PDF dependency, and the module needs pypdf solely to extract APA metadata (references.py:31-34, 617-670).
- `rg -n 'Exclude' <brief>` matches multiple lines including Decision: Exclude and the five-point rationale — the brief records the decision in both frontmatter-lowercase form and body prose.

ARB receipts: lint arb-ruff-3d48bc2412d041c2834eb2b58fbb9761 (exit 0); types arb-step-typecheck-18c1c51391b34b5e9455bfc40598f85f (exit 0). Covers parity: gz covers OBPI-0.26.0-02-references --json returned total_reqs=0 uncovered_reqs=0 (doc-only REQs). Documents+surfaces+brief-headings: 3/3 scopes pass.

## Verification

Concrete, reproducible commands that verify this OBPI's acceptance criteria.
The REQ-01/REQ-04/REQ-05 patterns are OBPI-specific (they grep this brief for
decision text and Gate 4 rationale).

```bash
# Baseline quality gates (OBPI-scoped)
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.26.0-02-references
uv run gz covers OBPI-0.26.0-02-references --json
uv run gz validate --documents --surfaces --brief-headings

test -f ../airlineops/src/opsdev/lib/references.py
# Expected: opsdev source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — parent ADR-0.26.0 authored; this
  OBPI brief under `obpis/` records the comparison scope
- [x] **Gate 2 (TDD):** Tests pass — baseline `uv run gz lint`, `uv run gz
  typecheck`, and `uv run gz test --obpi OBPI-0.26.0-02-references` all
  green (no new code to test for an Exclude outcome)
- [x] **Gate 3 (Docs):** Decision rationale completed — see `## Comparison`
  and `## Decision` sections above, with observed evidence anchors from
  the opsdev module
- [x] **Gate 4 (BDD):** `N/A` recorded with rationale — Exclude outcome
  with zero operator-visible behavior change (no new CLI verbs, no
  generated-surface change, no code under `src/gzkit/`), so behavioral
  proof is not required
- [ ] **Gate 5 (Human):** Attestation recorded — pending ceremony at
  Stage 4 of the OBPI pipeline (Heavy-lane parent ADR requires human
  attestation)

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Exclude decision for ../airlineops/src/opsdev/lib/references.py (797 lines): module is airline-research-literature infrastructure (REF_DIR=docs/references/, hardcoded ROSETTA_REFERENCES_LIST of Belobaba/Bazargan/Abdelghany/Littlewood/Talluri airline OR texts at lines 57-62, pypdf-driven APA citation extraction at lines 617-670) and fails the subtraction test on all five dimensions (filesystem contract, airline-domain data, discipline-specific dependency, literature-management purpose, naming collision); gzkit has no docs/references/, no docs/REFERENCES.md, no docs/ANNOTATED_BIBLIOGRAPHY.md, no pypdf dep, and gzkit's governance cross-referencing already lives in src/gzkit/traceability.py, governance/trust_audits.py, commands/adr_autolink.py. No code landed under src/gzkit/; no new tests; Gate 4 N/A. Receipts: lint arb-ruff-3d48bc2412d041c2834eb2b58fbb9761; types arb-step-typecheck-18c1c51391b34b5e9455bfc40598f85f.
- Date: 2026-04-24

### Closing Argument

The brief asked: is `../airlineops/src/opsdev/lib/references.py` a generic
governance primitive gzkit should own, or ops-specific content that should
stay in opsdev? The answer resolves on observation, not interpretation.

The module's filesystem contract (`docs/references/`,
`docs/ANNOTATED_BIBLIOGRAPHY.md`, `docs/REFERENCES.md`,
`docs/airlineops_rosetta_stone.md`) anchors exclusively to academic and
airline-research surfaces that gzkit does not have. Its embedded data
(`ROSETTA_REFERENCES_LIST` — six airline OR / revenue-management texts) is
pure airline-domain content. Its dependency (`pypdf`) serves only academic
PDF metadata extraction, a capability no gzkit operator needs. Its functional
signature (`build_citation`, `render_apa_section`, `update_references_apa`,
`crosslink_bibliography`, `run_rosetta_refs`) generates bibliographic output
for academic literature, not cross-references between governance artefacts.

gzkit already owns governance cross-referencing through
`src/gzkit/traceability.py`, `src/gzkit/governance/trust_audits.py`, and the
ADR autolink / @covers tooling. The opsdev module does not compete with or
improve those surfaces — it operates on a different domain entirely.

The OBPI brief's original anticipation of "dedicated reference tracking for
resolving links between ADRs, OBPIs, artifacts, and governance documents"
was inferred from the filename. Reading the module refutes that inference:
"references" here means "academic references / bibliography", not
"cross-references". Naming collision, not capability overlap.

**Decision: Exclude.** The subtraction test holds — the module belongs in
opsdev because its entire surface area is airline-domain. No code lands in
gzkit. No tests added. No CLI change. No operator-visible behavior change.
The brief itself is the deliverable; Gate 5 human attestation closes the
unit.
