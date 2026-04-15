---
id: OBPI-0.41.0-04-tdd-runbook-and-manpage
parent: ADR-0.41.0
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.41.0-04: `gz tdd` Runbook, Manpage, and Rule Updates

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-0.41.0-tdd-emission-and-graph-rot-remediation.md`
- **Checklist Item:** #4 — "Runbook, manpage, and docs for gz tdd + tests.md rule update"

**Status:** Draft

## Objective

Document the `gz tdd` subcommand family in the operator runbook, create a canonical manpage at `docs/user/manpages/tdd.md` and a command doc at `docs/user/commands/tdd.md`, and update `.gzkit/rules/tests.md` so the Red-Green-Refactor section cites `gz tdd red` / `gz tdd green` as the canonical verification path. This OBPI is the *documentation* layer — Gate 3 for the ADR.

## Lane

**Heavy** — documentation that governs operator behavior around TDD discipline. Heavy because `.gzkit/rules/tests.md` is a binding rule.

## Allowed Paths

- `docs/user/commands/tdd.md` — new command doc
- `docs/user/manpages/tdd.md` — new manpage
- `docs/user/runbook.md` — add TDD section
- `.gzkit/rules/tests.md` — update Red-Green-Refactor section
- `mkdocs.yml` — register new docs in navigation (if required)
- `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/obpis/OBPI-0.41.0-04-tdd-runbook-and-manpage.md` — this brief

## Denied Paths

- `src/gzkit/commands/tdd.py` — OBPI-02 owns implementation
- `src/gzkit/templates/agents.md` — AGENTS.md updates stay minimal here; tests.md carries the binding rule
- `.claude/rules/tests.md` — generated mirror, updated via `gz agent sync`
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. `docs/user/commands/tdd.md` documents `gz tdd red`, `gz tdd green`, and `gz tdd chain` with description, usage, exit codes, and at least two examples.
2. `docs/user/manpages/tdd.md` follows the existing manpage template (see `docs/user/manpages/closeout.md` for pattern) and documents the same surface plus the verification semantics (how failure_kind is classified, what "RED fails for the right reason" means).
3. `docs/user/runbook.md` gains a section titled "TDD Cycle with Verified Emission" that walks an operator through a RED→GREEN cycle for one REQ, from test authoring through event emission and `gz tdd chain` verification.
4. `.gzkit/rules/tests.md` Red-Green-Refactor section is updated to cite `gz tdd red` and `gz tdd green` as the canonical way to produce verifiable evidence. The existing per-TASK discipline remains; the addition is the citation path and the example.
5. `uv run mkdocs build --strict` passes.
6. `uv run gz validate --surfaces` passes after `gz agent sync control-surfaces` regenerates the mirrored rule.
7. `uv run gz cli audit` passes — the new `gz tdd` commands appear in the manpage index.

## Discovery Checklist

**Governance:**

- [ ] `.gzkit/rules/gate5-runbook-code-covenant.md` — documentation-is-first-class rule
- [ ] `.gzkit/rules/tests.md` — current Red-Green-Refactor section

**Context:**

- [ ] OBPI-0.41.0-02 must be complete — the CLI surface must exist before the manpage describes it
- [ ] `docs/user/manpages/closeout.md` — structural precedent for a manpage with verification semantics
- [ ] `docs/user/runbook.md` — where the new section lands

**Prerequisites:**

- [ ] OBPIs 01, 02, 03 Completed

**Existing code:**

- [ ] `gz cli audit` enforces manpage coverage — review the existing check before adding new manpages.

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded

### Gate 2: TDD

- [ ] Per-REQ RGR cycle — each doc REQ has a test in `tests/test_cli_audit.py` or equivalent that asserts the doc surface exists with expected headings

### Gate 3: Docs (Heavy)

- [ ] `uv run mkdocs build --strict` passes
- [ ] `uv run gz validate --documents` passes
- [ ] `uv run gz cli audit` passes

### Gate 4: BDD (Heavy)

- [ ] No new BDD scope

### Gate 5: Human (Heavy)

- [ ] Attestation at ADR closeout

## Verification

```bash
uv run gz lint
uv run gz validate --documents --surfaces
uv run mkdocs build --strict
uv run gz cli audit
uv run -m unittest tests.test_cli_audit -v
```

## Acceptance Criteria

- [ ] REQ-0.41.0-04-01: Given `docs/user/commands/tdd.md`, when read, then it contains description, usage, exit codes, and at least two examples for each of `gz tdd red/green/chain`.
- [ ] REQ-0.41.0-04-02: Given `docs/user/manpages/tdd.md`, when read, then it documents failure_kind classification and the "top stack frame in tests/" verification rule from OBPI-02 REQ 02-03.
- [ ] REQ-0.41.0-04-03: Given `docs/user/runbook.md`, when read, then it contains a "TDD Cycle with Verified Emission" section with a step-by-step worked example (write test → red → implement → green → chain).
- [ ] REQ-0.41.0-04-04: Given `.gzkit/rules/tests.md`, when read, then the Red-Green-Refactor section cites `gz tdd red` and `gz tdd green` as the canonical verification path with a worked example.
- [ ] REQ-0.41.0-04-05: Given `uv run mkdocs build --strict`, when invoked, then the build passes with the new doc files registered.
- [ ] REQ-0.41.0-04-06: Given `uv run gz cli audit`, when invoked, then `gz tdd red/green/chain` appear in the manpage index and no coverage gaps are reported.
- [ ] REQ-0.41.0-04-07: Given `uv run gz agent sync control-surfaces` followed by `uv run gz validate --surfaces`, when invoked, then no drift is reported for `.claude/rules/tests.md`.

## Completion Checklist

- [ ] Gate 1/2/3/4/5 recorded
- [ ] Docs build passes
- [ ] Evidence filled

## Evidence

### Value Narrative

Before this OBPI: `gz tdd` exists as code (OBPI-02) but has no operator-facing documentation. Agents can call it but can't learn it from the runbook. After: the runbook walks a real TDD cycle end-to-end, the manpage documents the verification semantics, and the rule cites the canonical path so agents reading `.gzkit/rules/tests.md` know exactly what tool to use.

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: at ADR closeout
- Date: n/a

---

**Brief Status:** Draft

**Date Completed:** -
