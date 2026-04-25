---
id: OBPI-0.0.28-03-threshold-validator
parent: ADR-0.0.28
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.28-03-threshold-validator: gz validate --complexity-thresholds

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/ADR-0.0.28-complexity-threshold-doctrine.md`
- **Checklist Item:** #3 — "`gz validate --complexity-thresholds` validator (`src/gzkit/governance/trust_audits.py`) — fail-closes on unmapped bands, missing block band, missing percentile + absolute pairing, trigger-semantic outside enum, unparseable citation; integrates into `gz validate --all` and `gz check`; manpage + runbook updates"

**Status:** Draft

## Objective

Implement `validate_complexity_thresholds` in `src/gzkit/governance/trust_audits.py`, register the `gz validate --complexity-thresholds` flag, and integrate the new validator into `gz validate --all` and `gz check`. The validator runs OBPI-02's `load_threshold_table`, asserts every metric in the canonical list has a `block` band, asserts every band's percentile + absolute pairing is well-formed, and asserts the citation tuple parses against OBPI-0.0.27-05's `parse_citation`. Manpage and runbook updates land in the same patch per the gate5-runbook-code-covenant.

## Lane

**Heavy** — New CLI flag is a contract change per `.gzkit/rules/cli.md`; new validator is a Mechanical-class rule audit per `AGENTS.md` § Governance doctrine surfaces. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — add `validate_complexity_thresholds` (function-size discipline: split helpers as needed)
- `src/gzkit/cli/parser_artifacts.py` — register `--complexity-thresholds` flag on `gz validate`
- `src/gzkit/commands/validate.py` (or wherever the validate dispatcher lives) — wire the flag to the new validator and into `--all` aggregation
- `tests/governance/test_complexity_thresholds_validator.py` — REQ-derived assertions
- `features/complexity_thresholds.feature` — BDD scenarios tagged with REQ IDs
- `docs/user/manpages/gz-validate.md` — manpage section for the new flag
- `docs/user/runbook.md` — runbook entry under "Complexity doctrine surfaces"
- `docs/governance/advisory-rules-audit.md` — promote OBPI-01's scorecard entry to "promoted/Mechanical" with this validator as the enforcement artifact
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-03-threshold-validator.md` — this brief's evidence section only

## Denied Paths

- `.gzkit/rules/complexity-thresholds.md` — rule file is OBPI-01 (consumed here, not edited)
- `src/gzkit/complexity/thresholds.py` — loader is OBPI-02 (consumed here, not edited)
- `src/gzkit/complexity/citation.py` — citation parser is OBPI-0.0.27-05 (consumed here, not edited)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `validate_complexity_thresholds` calls OBPI-02's `load_threshold_table(Path(".gzkit/rules/complexity-thresholds.md"))`. A `ValidationError` from the loader is treated as a validator failure (exit 3) with the underlying error text propagated to operator-facing diagnostic output.
2. REQUIREMENT: After loader success, the validator asserts each canonical metric (the twelve metrics from ADR-0.0.27 OBPI-03) has at least one band; missing metric coverage fails closed (exit 3) with a named-error message listing the missing metrics.
3. REQUIREMENT: For each band, the validator asserts `corpus_percentile ∈ {50, 75, 90, 95, 99}` AND `absolute_number > 0`; violations fail closed.
4. REQUIREMENT: Each metric MUST have a `block` band (re-asserted at validator level even though the loader enforces it — the validator is the gate-time defense against a future loader regression).
5. REQUIREMENT: The validator calls OBPI-0.0.27-05's `parse_citation` against the loaded `ThresholdTable.citation` field; a parse failure fails closed.
6. REQUIREMENT: When the rule body declares the bootstrap-absolutes carve-out section (per OBPI-01's first-distillation cold-start handling), the validator skips portability checks against bootstrap rows but logs a "bootstrap-mode" warning to operator-facing diagnostic. The carve-out is one-shot — when the bootstrap section is removed, the validator runs the full portability check.
7. REQUIREMENT: The CLI flag `--complexity-thresholds` is registered on `gz validate` and integrates into both `gz validate --all` and `gz check`. A speculative-citation escape marker (per the precedent in `.claude/rules/governance-core.md`) is honored.
8. REQUIREMENT: The exit-code map per `.claude/rules/cli.md` § Exit Codes: 0 success, 3 policy breach. The validator never exits 1 or 2 for complexity-doctrine breaches; system errors (file unreadable, schema file missing) exit 2.
9. REQUIREMENT: Tests cover: well-formed table validates clean (exit 0); rule body with metric missing block band fails (exit 3, named error); rule body with band carrying percentile=80 (off-enum) fails; rule body with citation that does not parse fails; rule body with all twelve metrics covered + bootstrap section skips portability and emits the bootstrap-mode warning; integration into `gz validate --all` fires the validator; the `gz check` aggregate path includes it. Each test decorated with `@covers(REQ-0.0.28-03-NN)`.
10. REQUIREMENT: A behave scenario file `features/complexity_thresholds.feature` covers four canonical failure paths with scenarios tagged `@REQ-0.0.28-03-{02..05}`.
11. REQUIREMENT: Manpage `docs/user/manpages/gz-validate.md` adds a section for `--complexity-thresholds` documenting purpose, exit codes, and at least one example invocation per `.gzkit/rules/cli.md` § Help Text Requirements. Runbook `docs/user/runbook.md` adds an entry under "Complexity doctrine surfaces" prescribing the verb for the operator moment "verify the threshold table is well-formed".
12. REQUIREMENT: Function-size discipline (≤ 50-line functions); the validator decomposes into named helpers (loader invocation, metric coverage check, band shape check, citation check, bootstrap-mode handling).
13. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures simulating valid + invalid rule bodies.
14. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, manpage, runbook, or commit messages.

> STOP-on-BLOCKERS: if OBPI-02's `load_threshold_table` is not present or OBPI-0.0.27-05's `parse_citation` is not importable, STOP — both are consumer dependencies of this validator.

## Discovery Checklist

- [ ] OBPI-0.0.28-02 loader (`src/gzkit/complexity/thresholds.py`)
- [ ] OBPI-0.0.27-05 citation parser (`src/gzkit/complexity/citation.py`)
- [ ] OBPI-0.0.28-01 rule body — concrete artifact for the validator's resolution checks
- [ ] `src/gzkit/governance/trust_audits.py` — existing validator patterns (e.g. `validate_brief_headings`, `validate_advisory_scorecard`, `validate_complexity_doctrine_links`)
- [ ] `.gzkit/rules/cli.md` — exit-code map (3 = policy breach)
- [ ] `.claude/rules/governance-core.md` — speculative-marker precedent
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — manpage + runbook in same patch

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits respected

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage section for `--complexity-thresholds`
- [ ] Runbook entry under "Complexity doctrine surfaces"

### Gate 4: BDD (Heavy)
- [ ] `features/complexity_thresholds.feature` covers four canonical failure paths; scenarios tagged `@REQ-0.0.28-03-{02..05}`

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --complexity-thresholds
uv run gz validate --all
uv run gz check
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_complexity_thresholds_validator.py -v
uv run -m behave features/complexity_thresholds.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.28-03-01: Given a well-formed threshold rule body, when `gz validate --complexity-thresholds` runs, then exit 0.
- [ ] REQ-0.0.28-03-02: Given a rule body where any metric lacks a `block` band, when the validator runs, then exit 3 with a named error listing the metric.
- [ ] REQ-0.0.28-03-03: Given a band with `corpus_percentile=80` (off the {50,75,90,95,99} enum), when the validator runs, then exit 3 with a named error.
- [ ] REQ-0.0.28-03-04: Given a citation tuple that does not parse against `parse_citation`, when the validator runs, then exit 3 with a named error.
- [ ] REQ-0.0.28-03-05: Given a rule body declaring the bootstrap-absolutes carve-out section, when the validator runs, then portability checks against bootstrap rows are skipped and a "bootstrap-mode" warning is emitted to operator-facing output.
- [ ] REQ-0.0.28-03-06: Given `gz validate --all` and `gz check`, when invoked, then the new validator fires as part of the aggregate run.
- [ ] REQ-0.0.28-03-07: Given the manpage `docs/user/manpages/gz-validate.md`, when read, then the `--complexity-thresholds` section is present with at least one example invocation; the runbook entry exists under "Complexity doctrine surfaces".

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

<!-- Problem before: an unmapped band introduced by a new distillation could land in `.gzkit/rules/complexity-thresholds.md` silently and surface only at the next operator session, possibly months later — by which time the advisor (ADR-0.0.29) and authoring-guidance (ADR-0.0.30) had been operating against a malformed table. Capability now: every threshold rule body is mechanically validated at gate time; broken bands, missing block bands, off-enum percentiles, or unparseable citations fail-close at `gz check`, surfacing the defect before merge. -->

### Key Proof

<!-- Paste the validator output for the four canonical failure paths and the integration into `gz check`. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why fail-closed at validator time beats best-effort at runtime (the cluster's downstream consumers must not silently operate against a malformed table), why integrating into `gz check` closes the "validator exists but never runs" failure class, and why this OBPI is the cluster's gate-time defense — without it, every other invariant in 0.0.28 is exposed to silent drift. -->

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
