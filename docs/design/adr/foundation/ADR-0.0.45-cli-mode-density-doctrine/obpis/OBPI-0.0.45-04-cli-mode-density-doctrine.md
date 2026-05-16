---
id: OBPI-0.0.45-04-cli-mode-density-doctrine
parent: ADR-0.0.45-cli-mode-density-doctrine
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.45-04-cli-mode-density-doctrine: Cli Mode Density Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`
- **Checklist Item:** #4 - "OBPI-0.0.45-04: **cli-surface-and-cutover** — `gz validate audit cli-flag-density`, `gz validate audit suite-density`, `gz validate suite density`; suite wiring (`default`/`surface-fidelity`/`cheap-fidelity`) pending ≤100ms perf measurement; recalibration receipt emission/read paths; manpage; folds in #471's noun-verb refactor (parser cutover + ~481-file sweep)."

**Status:** Draft

## Objective

**cli-surface-and-cutover** — `gz validate audit cli-flag-density`, `gz validate audit suite-density`, `gz validate suite density`; suite wiring (`default`/`surface-fidelity`/`cheap-fidelity`) pending ≤100ms perf measurement; recalibration receipt emission/read paths; manpage; folds in #471's noun-verb refactor (parser cutover + ~481-file sweep).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md` — parent ADR for intent and scope (read-only)
- `.pre-commit-config.yaml` — hook contents change from `gz validate --bullet-retention ...` to `gz validate suite cheap-fidelity`
- `src/gzkit/cli/parser_validate.py` — parser refactor to noun-verb subverbs (folds in #471 cutover)
- `src/gzkit/cli/**` — sweep of ~99 `--<scope>` references across CLI parser modules
- `src/gzkit/**` — sweep of remaining ~99 `--<scope>` references across the codebase
- `docs/**` — sweep of doc references to `--<scope>` form
- `tests/**` — sweep of test references and CLI test updates
- `data/validate_audits.json` — register `cli-flag-density` and `suite-density` audit entries
- `data/validate_suites.json` — wire `default`/`surface-fidelity`/`cheap-fidelity` suites pending perf measurement
- `src/gzkit/ledger.py` — add `cli_flag_density_recalibrated` and `suite_density_recalibrated` receipt schemas to the existing ledger event registry
- `docs/user/manpages/gz-validate-suite.md` — net-new manpage created by this OBPI
- `docs/user/manpages/gz-validate-audit.md` — net-new manpage created by this OBPI
- `tests/cli/test_validate_suite_audit.py` — net-new CLI unit tests created by this OBPI

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## OBPI creates these files

- `docs/user/manpages/gz-validate-suite.md`
- `docs/user/manpages/gz-validate-audit.md`
- `tests/cli/test_validate_suite_audit.py`
- `src/gzkit/cli/parser_validate.py`
- `data/validate_suites.json`
- `data/validate_audits.json`

## Requirements (FAIL-CLOSED)

1. REQ-0.0.45-04-01: New CLI subverbs `gz validate suite <name>` and `gz validate audit <name>` are registered in `src/gzkit/cli/parser_validate.py`; their help text follows clig.dev conventions and exits 0 on `--help`.
1. REQ-0.0.45-04-02: `gz validate audit cli-flag-density` invokes the OBPI-0.0.45-02 validator; `gz validate audit suite-density` invokes the OBPI-0.0.45-03 validator; `gz validate suite density` runs both as a named composite.
1. REQ-0.0.45-04-03: Wall-clock perf of `cli-flag-density` + `suite-density` on the current gzkit corpus is measured and recorded in the OBPI evidence. If combined runtime exceeds 100ms, both audits are wired into `default` and `surface-fidelity` only — not `cheap-fidelity` — and the perf measurement justifies the routing decision.
1. REQ-0.0.45-04-04: Noun-verb refactor (folded from GHI #471): every `--<scope>` reference across the codebase (~99 occurrences across ~481 files) is rewritten to the noun-verb form in the same commit; `.pre-commit-config.yaml` changes from `gz validate --bullet-retention --surface-weight --pointer-anchors` to `gz validate suite cheap-fidelity` atomically.
1. REQ-0.0.45-04-05: Recalibration receipts `cli_flag_density_recalibrated` and `suite_density_recalibrated` have Pydantic models with `extra="forbid"`; emission path lives in the validator runners; read path lives in the audit functions and is the only consumer.
1. REQ-0.0.45-04-06: Manpages at `docs/user/manpages/gz-validate-suite.md` and `docs/user/manpages/gz-validate-audit.md` exist with description, usage, options, exit codes, and at least one example each per `.claude/rules/cli.md` § Help Text Requirements.
1. REQ-0.0.45-04-07: CLI unit tests at `tests/cli/test_validate_suite_audit.py` cover `--help`, audit invocation, suite invocation, exit codes (0 / 1 / 2 / 3), and the perf-measurement assertion against the 100ms budget.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/cli/parser_validate.py`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Test patterns: `tests/governance/test_cli_density_validators.py`
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md
test -f src/gzkit/cli/parser_validate.py
test -f src/gzkit/governance/trust_audits/cli_density_models.py
test -f src/gzkit/governance/trust_audits/cli_flag_density.py
test -f src/gzkit/governance/trust_audits/suite_density.py
uv run -m unittest tests/governance/test_cli_density_validators.py -v
uv run -m unittest tests/governance/test_cli_density_models.py -v
uv run -m unittest tests/cli/test_validate_suite_audit.py -v
uv run -m behave features/cli_mode_density.feature
test -f features/steps/cli_mode_density_steps.py
```

## Demo

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

- [ ] REQ-0.0.45-04-01: Given the parser_validate module, when invoked with `--help`, then `gz validate suite` and `gz validate audit` are documented subverbs exiting 0.
- [ ] REQ-0.0.45-04-02: Given `gz validate audit cli-flag-density` and `gz validate audit suite-density`, when invoked, then they call the OBPI-02 / OBPI-03 validators respectively; `gz validate suite density` runs both as a named composite.
- [ ] REQ-0.0.45-04-03: Given the gzkit corpus, when the perf measurement runs, then wall-clock is recorded in OBPI evidence and the suite-wiring decision (cheap-fidelity inclusion or exclusion) is justified against the 100ms budget.
- [ ] REQ-0.0.45-04-04: Given the noun-verb cutover commit, when applied, then no remaining `--<scope>` references survive (verified by `rg`); `.pre-commit-config.yaml` calls `gz validate suite cheap-fidelity`.
- [ ] REQ-0.0.45-04-05: Given a recalibration event, when emitted, then the receipt validates against the Pydantic `extra="forbid"` model; the read path consumes only that schema.
- [ ] REQ-0.0.45-04-06: Given `docs/user/manpages/gz-validate-suite.md` and `gz-validate-audit.md`, when reviewed, then both contain description, usage, options, exit codes, and at least one example.
- [ ] REQ-0.0.45-04-07: Given the CLI unit tests, when run under unittest, then they assert `--help` exit 0, audit / suite invocation behavior, exit code mapping (0/1/2/3), and the perf assertion against the 100ms budget.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
