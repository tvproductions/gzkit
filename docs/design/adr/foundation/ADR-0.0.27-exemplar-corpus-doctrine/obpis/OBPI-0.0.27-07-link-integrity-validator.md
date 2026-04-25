---
id: OBPI-0.0.27-07-link-integrity-validator
parent: ADR-0.0.27
item: 7
lane: Heavy
status: Draft
---

# OBPI-0.0.27-07-link-integrity-validator: gz validate --complexity-doctrine-links

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #7 — "`gz validate --complexity-doctrine-links` validator (link-integrity scope; closes 2am-Scenario-2 failure mode)"

**Status:** Draft

## Objective

Implement `validate_complexity_doctrine_links` in `src/gzkit/governance/trust_audits.py` and register the corresponding `gz validate --complexity-doctrine-links` flag. The validator scans every citation in the four cluster ADRs (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) and any rule body referencing the distilled-characteristics corpus, parses each citation via OBPI-05's `parse_citation`, and fail-closes (exit 3) when the cited document does not exist or when the cited `corpus_revision` is older than the validator's portability window. Closes the 2am-Scenario-2 failure mode (operator follows an advisor diagnosis to a missing artifact).

## Lane

**Heavy** — New CLI flag is a contract change per `.gzkit/rules/cli.md`; new validator is a Mechanical-class rule audit per `AGENTS.md` § Governance doctrine surfaces. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — add `validate_complexity_doctrine_links` (function-size discipline: split helpers as needed)
- `src/gzkit/cli/parser_artifacts.py` — register `--complexity-doctrine-links` flag on `gz validate`
- `src/gzkit/commands/validate.py` (or wherever the validate command dispatcher lives) — wire the flag to the new validator
- `tests/governance/test_complexity_doctrine_links.py` — REQ-derived assertions
- `features/complexity_doctrine_links.feature` — BDD scenario tagged with REQ IDs
- `docs/user/manpages/gz-validate.md` — manpage section for the new flag (per `.gzkit/rules/gate5-runbook-code-covenant.md`)
- `docs/user/runbook.md` — runbook entry under "Governance doctrine surfaces"
- `docs/governance/advisory-rules-audit.md` — promote the OBPI-01 entry to "promoted/Mechanical" with this validator as the enforcement artifact
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

## Denied Paths

- `data/exemplar_corpus.json` — corpus is OBPI-02
- `src/gzkit/complexity/measurement.py` — measurement is OBPI-03
- `docs/governance/complexity/distilled-characteristics-*.md` — distillation outputs are OBPI-04
- `src/gzkit/complexity/citation.py` — parser is OBPI-05 (consumed here, not edited)
- `.gzkit/skills/gz-complexity-distill/**` — skill is OBPI-06
- ADR-0.0.28 / 0.0.29 / 0.0.30 ADR bodies (validator scans them; does not edit)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `validate_complexity_doctrine_links` enumerates the in-scope artifacts: ADR-0.0.27 / 0.0.28 / 0.0.29 / 0.0.30 ADR bodies + their OBPI briefs + `.gzkit/rules/complexity-doctrine.md` + any file matching `docs/governance/complexity/**/*.md`; for each file, extracts every citation that matches the canonical citation pattern from OBPI-05.
2. REQUIREMENT: For each extracted citation, the validator calls `parse_citation` (OBPI-05); a parse failure fails closed with exit 3 and a named error citing the file + line.
3. REQUIREMENT: For each parsed citation, the validator asserts the cited `distilled_characteristics_path` resolves to an existing file under `docs/governance/complexity/`. A missing file fails closed with exit 3 and a named error.
4. REQUIREMENT: For each parsed citation, the validator asserts the cited `section_anchor` resolves to a heading in the cited document. An unresolved anchor fails closed with exit 3.
5. REQUIREMENT: For each parsed citation, the validator calls `is_portable(citation, current_revision)`; a non-portable citation fails closed with exit 3 and a named error directing the operator to the doctrine-amendment-protocol pool stub (`ADR-pool.doctrine-amendment-protocol`).
6. REQUIREMENT: The CLI flag `--complexity-doctrine-links` is registered on `gz validate` and integrates into `gz validate --all` and `gz check` (so pre-commit / pre-merge gates fire automatically).
7. REQUIREMENT: A speculative-citation escape marker is supported (per the precedent in `.claude/rules/governance-core.md` § "Operator-doc verb resolution"): a comment-style marker on the line preceding a citation tells the validator to skip that citation (used when an ADR cites a planned-but-unlanded distillation document).
8. REQUIREMENT: Tests cover: well-formed citations resolve clean (exit 0); a missing distilled-characteristics file fails (exit 3); an unresolved section anchor fails (exit 3); a non-portable corpus_revision fails (exit 3); the speculative marker correctly skips a citation; integration into `gz validate --all` fires the validator; the `gz check` aggregate path includes it. Each test decorated with `@covers(REQ-0.0.27-07-NN)`.
9. REQUIREMENT: A behave scenario tagged `@REQ-0.0.27-07-{01..04}` covers the four canonical failure paths against fixture cluster ADRs.
10. REQUIREMENT: Manpage and runbook updates land in the same patch per `.gzkit/rules/gate5-runbook-code-covenant.md`.
11. REQUIREMENT: Function-size discipline per `.claude/rules/pythonic.md` (≤ 50-line functions); the validator is decomposed into named helpers (citation extraction, parsing, file resolution, anchor resolution, portability check).
12. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures simulate the cluster ADR layout.
13. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, manpage, runbook, or commit messages.

> STOP-on-BLOCKERS: if OBPI-05's `parse_citation` is not present, STOP — the validator depends on the parser surface.

## Discovery Checklist

- [ ] OBPI-05 parser surface (`src/gzkit/complexity/citation.py`)
- [ ] OBPI-04 first distilled-characteristics document — concrete artifact for the validator's resolution checks
- [ ] `src/gzkit/governance/trust_audits.py` — existing validator patterns (e.g. `validate_brief_headings`, `validate_advisory_scorecard`) for shape consistency
- [ ] `.gzkit/rules/cli.md` — exit-code map (3 = policy breach)
- [ ] `.claude/rules/governance-core.md` — speculative-marker precedent for skip semantics
- [ ] `docs/user/manpages/gz-validate.md` — manpage shape for the new flag

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits respected

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage section for `--complexity-doctrine-links` in `docs/user/manpages/gz-validate.md`
- [ ] Runbook entry under "Governance doctrine surfaces"

### Gate 4: BDD (Heavy)
- [ ] `features/complexity_doctrine_links.feature` covers the four canonical failure paths; scenarios tagged `@REQ-0.0.27-07-{01..04}`

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --complexity-doctrine-links
uv run gz validate --all  # integration check
uv run gz check
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_complexity_doctrine_links.py -v
uv run -m behave features/complexity_doctrine_links.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.27-07-01: Given a cluster ADR with a well-formed citation to an existing distilled-characteristics document, when `gz validate --complexity-doctrine-links` runs, then exit 0.
- [ ] REQ-0.0.27-07-02: Given a cluster ADR citing a distilled-characteristics file that does not exist on disk, when the validator runs, then exit 3 with a named error citing the file + line.
- [ ] REQ-0.0.27-07-03: Given a cluster ADR citing an unresolved section anchor in an existing distilled file, when the validator runs, then exit 3 with a named error citing the anchor.
- [ ] REQ-0.0.27-07-04: Given a cluster ADR citing a non-portable `corpus_revision`, when the validator runs, then exit 3 with a named error directing the operator to the doctrine-amendment-protocol pool stub.
- [ ] REQ-0.0.27-07-05: Given a citation preceded by the speculative-marker comment, when the validator runs, then that citation is skipped without affecting the exit code.
- [ ] REQ-0.0.27-07-06: Given `gz validate --all` and `gz check`, when invoked, then the new validator fires as part of the aggregate run.
- [ ] REQ-0.0.27-07-07: Given the manpage `docs/user/manpages/gz-validate.md`, when the operator reads it, then the `--complexity-doctrine-links` section is present with at least one example invocation.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean; size limits
- [ ] Gate 3: mkdocs --strict clean; manpage + runbook updated
- [ ] Gate 4: behave scenarios pass with REQ tags
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
# Paste mkdocs --strict output + manpage + runbook diff hunks
```

### Gate 4 (BDD)
```text
# Paste behave output for the four canonical failure paths
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: an operator at 2am following an advisor diagnosis could land on a citation pointing at a missing or stale distilled-characteristics document and lose the doctrine trail at the worst possible moment. Capability now: every citation in the cluster ADRs and the rule body is mechanically validated; broken or out-of-date references fail-close at gate time, surfacing the defect at next operator session rather than during a midnight diagnosis. -->

### Key Proof

<!-- Paste the validator output for the four canonical failure paths and the integration into `gz check`. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why fail-closed at validator time beats best-effort at runtime (the 2am operator cannot debug a silent broken citation), why integrating into `gz check` closes the "validator exists but never runs" failure class, and why this is the load-bearing closing OBPI of the cluster — without link integrity, every other invariant in 0.0.27 / 0.0.28 / 0.0.29 / 0.0.30 is exposed to silent drift. -->

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
