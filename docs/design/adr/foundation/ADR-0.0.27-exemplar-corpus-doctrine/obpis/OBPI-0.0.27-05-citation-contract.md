---
id: OBPI-0.0.27-05-citation-contract
parent: ADR-0.0.27
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.27-05-citation-contract: Citation Contract

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #5 — "Citation contract specifying how downstream foundation ADRs cite the corpus (percentile + absolute-number pairing for portability across refresh)"

**Status:** Draft

## Objective

Specify the canonical citation form by which downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) reference the distilled-characteristics document, codify the percentile + absolute-number pairing requirement so that boundaries remain portable across corpus refresh, and provide the parser surface that OBPI-07's link-integrity validator consumes.

## Lane

**Heavy** — Citation contract is a binding doctrinal surface consumed by three downstream foundation ADRs and the link-integrity validator. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/rules/complexity-doctrine.md` — extension only: add the "Citation contract" section formalizing the citation tuple, percentile + absolute pairing, and refresh-portability rule (rule-version bump per `.gzkit/rules/skill-surface-sync.md`)
- `.claude/rules/complexity-doctrine.md`, `.agents/rules/complexity-doctrine.md`, `.github/instructions/complexity-doctrine.md` — vendor mirrors via `gz agent sync control-surfaces`
- `src/gzkit/complexity/citation.py` — citation tuple parser + portability checker (consumed by OBPI-07)
- `src/gzkit/schemas/complexity_citation.json` — JSON Schema for the citation tuple
- `tests/complexity/test_citation.py` — REQ-derived assertions on parser, schema, portability rule
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

## Denied Paths

- `data/exemplar_corpus.json` — corpus is OBPI-02
- `src/gzkit/complexity/measurement.py` — measurement is OBPI-03
- `docs/governance/complexity/distilled-characteristics-*.md` — distillation outputs are OBPI-04
- `.gzkit/skills/gz-complexity-distill/**` — skill is OBPI-06
- `src/gzkit/governance/trust_audits.py` — link validator is OBPI-07
- ADR-0.0.28 / 0.0.29 / 0.0.30 files — those ADRs cite this contract in their own briefs, not here
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The "Citation contract" section in `.gzkit/rules/complexity-doctrine.md` defines the canonical citation tuple as `(distilled_characteristics_path, section_anchor, corpus_revision)` and forbids citation of raw distributions or the corpus directly.
2. REQUIREMENT: The section codifies the percentile + absolute-number pairing rule: every cited boundary appears as both a percentile-of-corpus AND the absolute-number-at-that-percentile (e.g. "p90 = CC 12"), so that downstream ADRs remain readable across corpus refresh even when absolute numbers shift.
3. REQUIREMENT: The section codifies the corpus-refresh portability rule: when a citing ADR references `(file, anchor, corpus_revision=N)` and a new distillation lands at `corpus_revision=N+1`, the citation remains valid until the citing ADR is amended; the link-integrity validator (OBPI-07) flags out-of-date references but does not auto-rewrite them.
4. REQUIREMENT: `src/gzkit/complexity/citation.py` exposes `parse_citation(text: str) -> Citation` and `is_portable(citation: Citation, current_revision: int) -> bool` (Pydantic frozen `Citation` model) consumed by OBPI-07.
5. REQUIREMENT: The citation tuple JSON Schema at `src/gzkit/schemas/complexity_citation.json` is `extra="forbid"` equivalent and validates: `distilled_characteristics_path` is a relative path under `docs/governance/complexity/`; `section_anchor` is a slugified anchor string; `corpus_revision` is a positive integer.
6. REQUIREMENT: Tests cover: parser accepts canonical tuple shape; parser rejects citations that omit any of the three fields; portability returns true within current revision; portability returns false when revision is older than the supported window (parameterized in the rule); rule body parsing detects the citation contract section; vendor-mirror sync produces empty diff. Each test decorated with `@covers(REQ-0.0.27-05-NN)`.
7. REQUIREMENT: The rule-version marker in `.gzkit/rules/complexity-doctrine.md` is bumped to reflect this OBPI's amendment (e.g. `0.1.0` → `0.2.0`); both the body-level `<!-- rule-version: ... -->` HTML comment and the visible block quote update together.
8. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures.
9. REQUIREMENT: NEVER include the operator's personal email in rule body, schema, code, or fixtures.

> STOP-on-BLOCKERS: if OBPI-04 has not produced the first distilled-characteristics document, STOP — the citation contract has no concrete artifact to bind against.

## Discovery Checklist

- [ ] OBPI-01 rule file (`.gzkit/rules/complexity-doctrine.md`) for the existing structure to extend
- [ ] OBPI-04 first distilled-characteristics document for the "Citation form" reference section
- [ ] `.gzkit/rules/skill-surface-sync.md` — rule-version bump discipline + body-marker convention
- [ ] AGENTS.md § Attestation — citation discipline as the model for binding (receipt IDs ↔ corpus revisions are isomorphic)

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean (rule body renders)

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: rule + parser scope; downstream-citation BDD lands at OBPI-07's link validator

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # diff empty
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/test_citation.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.27-05-01: Given the rule body, when the "Citation contract" section is parsed, then the canonical tuple `(distilled_characteristics_path, section_anchor, corpus_revision)` is named and the prohibition on raw-distribution citation is explicit.
- [ ] REQ-0.0.27-05-02: Given the rule body, when the "Percentile + absolute pairing" rule is parsed, then both forms are required for every cited boundary.
- [ ] REQ-0.0.27-05-03: Given a citation tuple in canonical form, when `parse_citation` runs, then a frozen `Citation` model is returned.
- [ ] REQ-0.0.27-05-04: Given a citation missing any of the three fields, when `parse_citation` runs, then a `ValidationError` is raised.
- [ ] REQ-0.0.27-05-05: Given a citation with `corpus_revision=N` and a current revision `N`, when `is_portable` runs, then it returns true; given `corpus_revision` older than the supported window, it returns false.
- [ ] REQ-0.0.27-05-06: Given the rule file, when the rule-version marker is parsed, then the body comment and the visible block quote agree on the bumped version.
- [ ] REQ-0.0.27-05-07: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then all four mirrors produce identical content and the post-sync diff is empty.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict clean
- [ ] Gate 4: BDD waiver registered
- [ ] Gate 5: TTY + `ATTEST` captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)
```text
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.27-05
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: downstream foundation ADRs would cite numeric thresholds in narrative form, exposing them to silent drift across corpus refresh. Capability now: a canonical citation tuple with percentile + absolute pairing makes references portable across refresh, and the parser surface gives OBPI-07's link validator a mechanical check against the rule. -->

### Key Proof

<!-- Paste a sample citation in canonical form (e.g. `(docs/governance/complexity/distilled-characteristics-2026-04-25.md, #cc-distribution, 1)`) and the diff hunk for the rule-version bump. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why the percentile + absolute pairing is the load-bearing portability invariant (corpus refresh shifts absolute numbers but preserves percentile semantics), why a parser-backed citation closes the silent-drift class at the OBPI-07 layer, and why citation discipline is the same shape as ARB receipt-ID discipline (claims without observable evidence are post-hoc reasoning pathways). -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires TTY + ATTEST)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
