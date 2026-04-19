---
id: OBPI-0.0.19-05-docs-bdd-closeout
parent: ADR-0.0.19
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.19-05-docs-bdd-closeout: Docs, BDD, and Heavy-lane closeout

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md`
- **Checklist Item:** #5 — Docs + BDD + Heavy-lane closeout. Manpage, command doc, runbook entries, governance runbook note; BDD scenarios covering all invocation paths + failure modes; Gate 5 attestation with ARB receipts for lint/typecheck/tests/coverage/mkdocs and human `gz attest`.

**Status:** Draft

## Objective

Close out the ADR with the documentation covenant and BDD acceptance coverage. This OBPI ships: (a) a command manpage at `docs/user/manpages/gz-justify.md`; (b) a command doc at `docs/user/commands/justify.md`; (c) runbook entries in `docs/user/runbook.md` for operator flows (invoke on GHI, invoke on OBPI, invoke with `--draft`, validate filled scaffold); (d) a governance-runbook note in `docs/governance/governance_runbook.md` describing when `gz-justify` suggestions appear in `gz-adr-evaluate` and `gz-obpi-pipeline`; (e) BDD scenarios at `features/justify.feature` covering every invocation path and every failure mode with step definitions at `features/steps/justify_steps.py`; (f) Heavy-lane Gate 5 attestation package at ADR-level closeout: ARB receipts for lint/typecheck/tests/coverage/mkdocs plus human `gz attest`.

## Lane

**Heavy** — Delivers the Gate 3 (docs), Gate 4 (BDD), and Gate 5 (human attestation) evidence required for Heavy-lane closeout per `.gzkit/rules/gate5-runbook-code-covenant.md`.

> Heavy is reserved for command/API/schema/runtime-contract changes.

## Allowed Paths

- `docs/user/manpages/gz-justify.md` — new manpage
- `docs/user/commands/justify.md` — new command doc
- `docs/user/runbook.md` — extend with operator flow section; no other sections modified
- `docs/governance/governance_runbook.md` — extend with governance-flow note about upstream suggestions
- `docs/user/commands/index.md` (or equivalent command index) — add justify entry if index file exists; verify via Glob before editing
- `features/justify.feature` — new BDD feature file
- `features/steps/justify_steps.py` — new step definitions
- `tests/cli/test_justify_manpage.py` — assert manpage exists and covers required sections (usage, options, exit codes, examples)
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-CLOSEOUT-FORM.md` — updated to reflect all gates complete before `gz attest`
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md` — Evidence section extended with closeout commands and receipt IDs
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/EVALUATION_SCORECARD.md` — refresh if re-evaluation is warranted at closeout

## Denied Paths

- `src/gzkit/justify/**`, `src/gzkit/commands/justify_cmd.py`, `src/gzkit/cli/parser_artifacts.py` — implementation is locked by OBPI-01/02/03
- `.gzkit/skills/**` — skill authoring is owned by OBPI-04; this OBPI does not alter skill bodies
- `.claude/skills/**`, `.github/skills/**` — regenerated mirrors
- Any file mutation outside Allowed Paths
- New third-party dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `docs/user/manpages/gz-justify.md` covers the required manpage sections: NAME, SYNOPSIS, DESCRIPTION, OPTIONS (all flags from OBPI-02 + the `validate` subverb's flags from OBPI-03), EXIT STATUS (0/1/2 with meanings), EXAMPLES (at least three: GHI invocation, OBPI invocation with `--save`, `validate` invocation), SEE ALSO (at minimum: `gz-adr-evaluate`, `gz-obpi-pipeline`). Lines ≤80 chars per CLI doctrine.
2. REQUIREMENT: `docs/user/commands/justify.md` follows the structure of other command docs in the same directory (identify an exemplar via Glob and mirror its heading layout). Contains: overview, usage, anchor types table, flag table, exit-code table, operator-flow example, troubleshooting note for `--draft-slug` required.
3. REQUIREMENT: `docs/user/runbook.md` is extended with a new section describing when an operator should invoke justify, the three anchor types, and the validate flow. The section integrates with the existing runbook narrative; it is NOT a standalone appendix.
4. REQUIREMENT: `docs/governance/governance_runbook.md` is extended with a governance-flow note explaining that `gz-adr-evaluate` low-score output suggests `justify`, and that `gz-obpi-pipeline` at Stage 1→2 suggests `justify` when confidence is low. Cites Prime Directive invariant 11.
5. REQUIREMENT: `features/justify.feature` contains Gherkin scenarios covering: (a) invoke on GHI with mocked `gh`; (b) invoke on OBPI against a fixture brief; (c) invoke with `--draft` + `--draft-slug` + `--save`; (d) reject ADR anchor with exit 1; (e) reject `--draft` + `--save` without `--draft-slug`; (f) `validate` on complete fixture exits 0; (g) `validate` on incomplete fixture exits 1 with unfilled ordinals; (h) `validate` on malformed fixture exits 2. Each scenario tagged with a `@REQ-0.0.19-05-<NN>` identifier per `.gzkit/rules/tests.md`.
6. REQUIREMENT: `features/steps/justify_steps.py` implements every Given/When/Then from the feature file. Step definitions mock `gh` and filesystem where appropriate but exercise the real CLI subcommand end-to-end (per the two-runner contract in `.gzkit/rules/tests.md`).
7. REQUIREMENT: `uv run mkdocs build --strict` exits 0 after all doc changes.
8. REQUIREMENT: `uv run behave features/justify.feature` exits 0 with all scenarios passing.
9. REQUIREMENT: `uv run gz cli audit` exits 0 with `justify` and `justify validate` covered across manpage, command doc, and index.
10. REQUIREMENT: Before attestation, the following ARB receipts are recorded in the ADR's Evidence section: `arb-ruff-*`, `arb-step-typecheck-*`, `arb-step-unittest-*`, `arb-step-coverage-*`, `arb-step-mkdocs-*`. Receipt IDs are quoted inline per `.gzkit/rules/attestation-enrichment.md`.
11. REQUIREMENT: `uv run gz adr audit-check ADR-0.0.19` exits 0 before attestation.
12. REQUIREMENT: Human attestation via `uv run gz closeout ADR-0.0.19` and `uv run gz attest ADR-0.0.19 --status completed` completes successfully, with attestation text matching the pattern from `.gzkit/rules/attestation-enrichment.md` (user's verbatim words + em-dash enrichment citing concrete session facts).
13. REQUIREMENT: The ADR Attestation Block table in `ADR-0.0.19-pre-execution-reasoning-walkthrough.md` is updated with: term `0.0.19`, status `Completed`, attestor name, date, and the user-verbatim reason.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.gzkit/rules/gate5-runbook-code-covenant.md` — three-layer documentation model, Gate 5 attestation requirement
- [ ] `.gzkit/rules/cli.md` — manpage requirements (Heavy-lane trigger for CLI contract changes)
- [ ] `.gzkit/rules/attestation-enrichment.md` — canonical invocations for ARB receipts; attestation pattern
- [ ] `.gzkit/rules/tests.md` — `@REQ-*` scenario tagging convention for behave
- [ ] Parent ADR — full context

**Context:**

- [ ] OBPI-01 through OBPI-04 completed and merged
- [ ] Existing manpage exemplar: `docs/user/manpages/gz-validate.md` or `gz-gates.md` (Glob to pick one)
- [ ] Existing command-doc exemplar: `docs/user/commands/validate.md` or similar (Glob to pick one)
- [ ] Existing BDD exemplar: `features/gates.feature` or similar for scenario structure
- [ ] Existing runbook: `docs/user/runbook.md` to find the right insertion point

**Prerequisites (check existence, STOP if missing):**

- [ ] All four prior OBPIs in this ADR are complete and merged
- [ ] `uv run gz adr audit-check ADR-0.0.19` is reachable (command exists)
- [ ] `docs/user/manpages/` has at least one existing manpage file (verify via Glob)
- [ ] `features/` has at least one existing `.feature` file (verify via Glob — confirmed)
- [ ] `uv run gz closeout` and `uv run gz attest` commands exist

**Existing Code (understand current state):**

- [ ] Sample manpage for layout: read one existing `docs/user/manpages/*.md`
- [ ] Sample command doc: read one existing `docs/user/commands/*.md`
- [ ] Sample BDD feature + steps: read one existing `features/*.feature` + matching `features/steps/*.py`
- [ ] `docs/user/runbook.md` — identify the operator-flow section where justify belongs

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief REQ-IDs, not from implementation
- [ ] `tests/cli/test_justify_manpage.py` exists and passes

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`
- [ ] Markdown lint clean on all new/modified docs

### Gate 3: Docs (Heavy only)

- [ ] `uv run mkdocs build --strict` exits 0
- [ ] `uv run gz cli audit` exits 0 with justify coverage across all three surfaces (manpage, command doc, index)
- [ ] Runbook entries reviewed for narrative integration (not standalone appendix)

### Gate 4: BDD (Heavy only)

- [ ] `uv run behave features/justify.feature` exits 0
- [ ] All eight scenarios from REQ-05 pass
- [ ] Each scenario carries a `@REQ-0.0.19-05-<NN>` tag

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded via `gz closeout ADR-0.0.19` and `gz attest ADR-0.0.19 --status completed`
- [ ] ARB receipts cited in attestation text

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb coverage run -m unittest discover -s tests -t .
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# Docs + manpage coverage
test -f docs/user/manpages/gz-justify.md
test -f docs/user/commands/justify.md
uv run gz cli audit

# BDD
uv run gz arb step --name behave-justify -- uv run -m behave features/justify.feature

# ADR audit + closeout
uv run gz adr audit-check ADR-0.0.19
uv run gz closeout ADR-0.0.19 --dry-run
uv run gz attest ADR-0.0.19 --status completed
uv run gz audit ADR-0.0.19
```

## Acceptance Criteria

- [ ] REQ-0.0.19-05-01: Given `docs/user/manpages/gz-justify.md` after this OBPI lands, when the file is parsed, then it contains the required manpage sections (NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT STATUS, EXAMPLES, SEE ALSO) with at least three examples and documented exit codes 0/1/2.
- [ ] REQ-0.0.19-05-02: Given `docs/user/commands/justify.md`, when compared to the command-doc exemplar, then it uses the same heading layout and includes the anchor-types table, flag table, and exit-code table required by REQ-02.
- [ ] REQ-0.0.19-05-03: Given `docs/user/runbook.md` after extension, when scanned, then it contains a new operator-flow section describing the three anchor types and the validate flow, integrated into the existing narrative (not a standalone appendix).
- [ ] REQ-0.0.19-05-04: Given `docs/governance/governance_runbook.md` after extension, when scanned, then it contains the governance-flow note citing Prime Directive invariant 11 and naming both upstream skills (`gz-adr-evaluate`, `gz-obpi-pipeline`).
- [ ] REQ-0.0.19-05-05: Given `features/justify.feature`, when parsed by behave, then it contains exactly the eight scenarios specified in REQ-05, each tagged with a unique `@REQ-0.0.19-05-<NN>` identifier.
- [ ] REQ-0.0.19-05-06: Given `uv run -m behave features/justify.feature`, when it runs, then exit code is 0 and all eight scenarios pass.
- [ ] REQ-0.0.19-05-07: Given `uv run mkdocs build --strict`, when it runs after all doc changes, then exit code is 0 with no warnings.
- [ ] REQ-0.0.19-05-08: Given `uv run gz cli audit`, when it runs, then exit code is 0 with justify (both parent verb and validate subverb) covered across manpage, command doc, and index.
- [ ] REQ-0.0.19-05-09: Given the ADR at closeout time, when ARB-wrapped canonical QA commands run (lint, typecheck, unittest, coverage, mkdocs), then five corresponding receipts exist under `artifacts/receipts/` and their IDs are quoted inline in the ADR's Evidence section.
- [ ] REQ-0.0.19-05-10: Given `uv run gz adr audit-check ADR-0.0.19`, when it runs, then exit code is 0 and all OBPI acceptance evidence is present.
- [ ] REQ-0.0.19-05-11: Given `uv run gz closeout ADR-0.0.19`, then `uv run gz attest ADR-0.0.19 --status completed` with an attestation string that contains the operator's verbatim words followed by an em-dash and session-grounded enrichment per `.gzkit/rules/attestation-enrichment.md`, when executed, then both commands exit 0.
- [ ] REQ-0.0.19-05-12: Given the ADR's Attestation Block table after closeout, when read, then the row for term `0.0.19` shows status `Completed`, a real attestor name, the ISO-date, and the reason string.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed on the manpage test
- [ ] **Code Quality:** Lint, format, type checks clean; markdown-lint clean
- [ ] **Gate 3 (Docs):** mkdocs build strict, cli audit clean
- [ ] **Gate 4 (BDD):** all eight scenarios pass
- [ ] **Gate 5 (Human):** attestation recorded with ARB receipt IDs
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste manpage-test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs build strict output and gz cli audit output
```

### Gate 4 (BDD)

```text
# Paste behave output showing 8 scenarios passing
```

### Gate 5 (Human)

```text
# Record attestation text with ARB receipt IDs here
```

### Value Narrative

**Before:** Implementation and skill wiring complete from OBPI-01 through OBPI-04, but Gate 3/4/5 evidence missing — Heavy-lane ceremony incomplete and the ADR cannot be closed out.

**After:** The full runbook-code covenant is satisfied: operators have documentation (manpage, command doc, runbook), BDD scenarios pin operator-facing behavior, and a human attestation with ARB receipt citations records the final sign-off. ADR-0.0.19 moves from Draft to Completed.

### Key Proof

```bash
# Paste a short excerpt from gz-justify.md manpage (SYNOPSIS + one example)
# Paste behave summary line (e.g. "8 scenarios passed, 0 failed")
# Paste the final attestation reason string with ARB receipt IDs
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when recorded at closeout
- Attestation: substantive attestation text with ARB receipt IDs
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
