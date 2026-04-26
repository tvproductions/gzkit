---
id: OBPI-0.0.35-04-kind-invariance-validator
parent: ADR-0.0.35-foundation-feature-invariance-test
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.35-04-kind-invariance-validator: `gz validate --kind-invariance` Validator Scope

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.35-foundation-feature-invariance-test/ADR-0.0.35-foundation-feature-invariance-test.md`
- **Checklist Item:** #4 — "`gz validate --kind-invariance` validator scope — author validator in `src/gzkit/governance/trust_audits.py` enumerating every `kind: foundation` ADR under `docs/design/adr/foundation/**` and asserting each carries the Why-foundation-tier section non-empty; wire into `gz check`; REQ-derived unit tests asserting section-presence semantics; manpage and runbook updates per `.claude/rules/gate5-runbook-code-covenant.md`; behave scenario tagged with the new REQ-IDs. Heavy-lane CLI surface change. Depends on OBPI-03."

**Status:** Draft

## Objective

Ship the `gz validate --kind-invariance` validator scope as a new heavy-lane CLI surface: enumerate every `kind: foundation` ADR under `docs/design/adr/foundation/**`, parse each ADR body, and assert it carries the `## Why foundation tier?` section with substantive non-placeholder content. Register the flag in the `gz validate` argparse surface (`src/gzkit/cli/parser_maintenance.py`); wire the new scope into the default `gz check` pipeline so kind-invariance drift fails the pre-commit/pre-merge gate. Author REQ-derived unit tests asserting section-presence semantics and substantive-content semantics. Add a behave scenario tagged with the new REQ-IDs covering the operator flow. Update `docs/user/manpages/gz-validate.md` and `docs/user/runbook.md` per the runbook-code covenant.

## Lane

**Heavy** — New CLI surface (`--kind-invariance` flag and scope), new public contract (validator semantics adopters can rely on). Heavy-lane gate covenant applies: Gate 1 (ADR), Gate 2 (TDD), Gate 3 (Docs build), Gate 4 (BDD scenario), Gate 5 (Human attestation). Foundation-kind brief-level attestation also fires (parent ADR-0.0.35 is foundation-kind).

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — validator scope implementation (or wherever foundation-related validators live; confirm during discovery)
- `src/gzkit/cli/parser_maintenance.py` — `--kind-invariance` flag registration in the `gz validate` argparse subparser
- `src/gzkit/commands/validate_cmd.py` — dispatch of the new scope into the validator function
- `src/gzkit/commands/check.py` — integration of the new scope into the default `gz check` pipeline (path subject to discovery; may live elsewhere)
- `tests/governance/test_kind_invariance.py` — new unit-test module for the scope (REQ-derived semantics)
- `tests/commands/test_validate.py` — additions covering the `--kind-invariance` flag wiring (registration, dispatch, exit codes)
- `features/kind_invariance.feature` — new behave scenario file (or addition to an existing governance feature) with `@REQ-0.0.35-04-NN` tags
- `docs/user/manpages/gz-validate.md` — manpage update reflecting the new scope
- `docs/user/runbook.md` — cross-reference at the kind-invariance verification section
- `data/behave_coverage_waivers.json` — only if a justified waiver is needed; default expectation is full BDD coverage

## Denied Paths

- `docs/user/concepts/foundation-feature-invariance-test.md` — OBPI-01 deliverable; do not edit
- `.gzkit/skills/**` — OBPI-02 scope
- `src/gzkit/templates/adr.md` — OBPI-03 scope
- `src/gzkit/commands/plan.py` — OBPI-03 scope (renderer logic for the section, not the validator)
- All ADR/OBPI files except this brief
- `docs/design/adr/foundation/**` — the validator reads these as inputs; it does not modify them
- `.gzkit/ledger.jsonl` — modified only via `gz` commands

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT — flag registered.** `gz validate --kind-invariance` MUST be a registered argparse flag with `dest="check_kind_invariance"` (or named consistently with adjacent flags). `gz validate --help` MUST list it with a one-line description.
2. **REQUIREMENT — validator enumerates foundation ADRs.** The scope function MUST glob every `docs/design/adr/foundation/ADR-*/ADR-*.md` (the on-disk canonical ADR file in each package), parse frontmatter, and select only those with `kind: foundation`. ADRs under `docs/design/adr/pre-release/`, `docs/design/adr/pool/`, or any other directory are out of this scope's purview.
3. **REQUIREMENT — section-heading match is byte-identical.** The validator MUST match the section header exactly as `## Why foundation tier?` (sentence case, single space after `##`, trailing question mark). Any case-insensitive or fuzzy match is a defect — the byte-identical match is the structural defense per OBPI-03 REQ-01.
4. **REQUIREMENT — substantive-content check uses the placeholder helper.** Section-body content MUST be checked against the same `_is_placeholder` helper the OBPI authored-readiness validator uses (`src/gzkit/hooks/obpi.py`) — empty body, "TBD"/"TODO"/"To be filled" markers, or "paste here"-style placeholders fail the check. Reuse the existing helper; do not author a parallel.
5. **REQUIREMENT — exit codes per the standard 4-code map.** Per `.claude/rules/cli.md`: exit 0 (all foundation ADRs pass), exit 3 (one or more foundation ADRs fail the check — policy breach). Exit 1 (user error: malformed ADR file) and exit 2 (system error: I/O) per the standard map.
6. **REQUIREMENT — wired into `gz check`.** The default `gz check` pipeline MUST invoke `--kind-invariance` so kind-invariance drift fails pre-commit/pre-merge gates. Per `.claude/rules/governance-core.md` § Proof commands.
7. **REQUIREMENT — REQ-derived unit tests assert semantics.** Per `.gzkit/rules/tests.md` § Tests assert semantics, not strings: tests assert section-presence behavior (foundation ADR with section passes; foundation ADR without section fails; feature ADR is not enumerated regardless of section presence) and substantive-content behavior (placeholder-only body fails; substantive body passes). Tests must NOT pin a specific expected error string.
8. **REQUIREMENT — REQ-IDs decorate every test.** Each test MUST carry `@covers(REQ-0.0.35-04-NN)` decoration linking it to the brief's acceptance criteria. Per `.claude/rules/tests.md` § TASK-Driven Workflow.
9. **REQUIREMENT — behave scenario tagged.** A scenario under `features/` MUST be tagged with `@REQ-0.0.35-04-NN` for at least one of the brief's REQs, exercising the operator-facing CLI flow per `.gzkit/rules/tests.md` § Behave scenario tagging.
10. **REQUIREMENT — manpage updated.** `docs/user/manpages/gz-validate.md` MUST list `--kind-invariance` in flags table and have at least one example invocation per `.claude/rules/cli.md` § Help Text Requirements.
11. **REQUIREMENT — runbook cross-reference.** `docs/user/runbook.md` MUST add a verification line at the kind-classification or quality-checks section.
12. **REQUIREMENT — ARB receipts cited in attestation.** Per AGENTS.md § Attestation lane behavior (heavy-lane = fail-closed on missing receipts): the closeout attestation MUST cite `arb-step-unittest-*`, `arb-ruff-*`, `arb-step-typecheck-*`, `arb-step-coverage-*`, `arb-step-mkdocs-*` receipts captured during this OBPI's verification.
13. **REQUIREMENT — substantiveness floor matches OBPI-03 prompts.** A foundation ADR with the section heading present but only the OBPI-03 author-prompts (unfilled) MUST fail the substantive-content check — author-prompts contain placeholder phrasing the helper recognizes. A foundation ADR with operator-filled answers passes. Walking this through against a fixture is part of the test surface.
14. **NEVER — pin a specific error string in tests.** Per `.gzkit/rules/tests.md` Invariant 6f: assertion derives from REQ semantics, not currently-observed bytes. *"Foundation ADR X failed kind-invariance check"* is a substring; *"the validator surfaces a foundation-ADR-keyed failure for the missing-section case"* is the semantic.
15. **NEVER — degrade enumeration to "first foundation ADR found".** The validator runs against every foundation ADR; partial enumeration would silently let drift accumulate.
16. **NEVER — exempt this OBPI's parent ADR (ADR-0.0.35) from the check.** ADR-0.0.35 is foundation-kind and gains the section under OBPI-03's backfill rule for in-flight foundation work — when this OBPI lands, ADR-0.0.35 itself must pass the check. (Existing other foundation ADRs are out-of-scope per OBPI-03 REQ-06; their drift is tracked as a separate sweep.)

> STOP-on-BLOCKERS: if the `## Why foundation tier?` heading is not yet in `src/gzkit/templates/adr.md` (OBPI-03 not landed), the validator has nothing to validate against. Print BLOCKERS and halt.
> ALSO STOP: if `docs/user/concepts/foundation-feature-invariance-test.md` (OBPI-01) is missing — the manpage and runbook updates link to it.

## Discovery Checklist

**Parent ADR (read first; order pinned per GHI #321):**

- [ ] Quote ADR-0.0.35 § Decision item #6 (Why-foundation-tier becomes load-bearing) and § Consequences positive #4 (validator closes the convention mechanically) verbatim into Implementation Summary.
- [ ] Read ADR-0.0.35 § Intent and § Decision § "Why-foundation-tier section becomes load-bearing".

> **STOP:** If you cannot quote ADR-0.0.35 § Decision item #6 verbatim, STOP and re-read.

**Sibling rule reference:**

- [ ] Read `.claude/rules/cli.md` § Exit Codes, § Flag Conventions, § Adding CLI Features § New Flag.
- [ ] Read `.gzkit/rules/tests.md` § Tests assert semantics, not strings, § TASK-Driven Workflow, § Behave scenario tagging end-to-end.
- [ ] Read `.claude/rules/gate5-runbook-code-covenant.md` end-to-end.
- [ ] Read `AGENTS.md` § Attestation § Lane behavior (heavy-lane fail-closed on missing receipts).
- [ ] Read OBPI-03 brief — confirm the exact section heading authored there (must match the validator anchor byte-identically).

**OBPI dependency check:**

- [ ] OBPI-03 has landed: `src/gzkit/templates/adr.md` contains `## Why foundation tier?`.
- [ ] OBPI-01 has landed: `docs/user/concepts/foundation-feature-invariance-test.md` exists.

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/governance/trust_audits.py` exists (or alternative validator-scope home identified).
- [ ] `src/gzkit/cli/parser_maintenance.py` lines 270-460 contain the `gz validate` argparse setup.
- [ ] `src/gzkit/commands/validate_cmd.py` contains the dispatch.
- [ ] `gz check` resolves to a registered command.
- [ ] `behave` runner is resolvable: `uv run -m behave --version` exits 0.

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits.py` — read at least three existing validator scopes end-to-end (`adr_status_fresh`, `frontmatter`, `taxonomy`) to confirm the scope-function signature, error-collection pattern, and exit-code contract. Mirror the conventions.
- [ ] `src/gzkit/hooks/obpi.py` § `_is_placeholder` and `_has_substantive_section` — these are the reuse target for substantive-content checking.
- [ ] `src/gzkit/cli/parser_maintenance.py` lines 270-460 — read existing `--documents`, `--frontmatter`, `--taxonomy`, `--surfaces` flag registrations; mirror the `dest=` and `action=` pattern.
- [ ] `src/gzkit/commands/validate_cmd.py` — read the dispatch logic that maps a parsed `--<flag>` to the corresponding scope function.
- [ ] `src/gzkit/commands/check.py` (or wherever `gz check` is implemented) — read the pipeline that fans out to validator scopes; identify the insertion point for the new scope.
- [ ] `tests/governance/test_*.py` — read the test conventions used by adjacent validator-scope tests (assertion shape, fixture pattern, REQ-decorator usage).
- [ ] `features/*.feature` — locate an adjacent governance feature file; confirm the scenario tagging pattern (`@REQ-X.Y.Z-NN-MM` per scenario).
- [ ] `docs/user/manpages/gz-validate.md` — read end-to-end; locate flag-table and examples sections for insertion.
- [ ] `docs/user/runbook.md` — locate quality-checks or kind-classification section for cross-reference.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR § Decision item #6 quoted

### Gate 2: TDD (Red-Green-Refactor)

Heavy-lane code path. RGR cycle is mandatory:

- [ ] **Red 1 (enumeration):** Test asserting the validator selects only `kind: foundation` ADRs; run; observe RED for the right reason.
- [ ] **Green 1:** Implement enumeration; pass.
- [ ] **Red 2 (section-presence):** Test with foundation-fixture-without-section; observe RED.
- [ ] **Green 2:** Implement section-presence check; pass.
- [ ] **Red 3 (substantive-content):** Test with foundation-fixture-with-placeholder-only-section; observe RED.
- [ ] **Green 3:** Implement substantive-content check; pass.
- [ ] **Red 4 (CLI integration):** Test asserting `gz validate --kind-invariance` flag dispatch; observe RED.
- [ ] **Green 4:** Wire the flag in `parser_maintenance.py` and `validate_cmd.py`; pass.
- [ ] **Refactor:** Tighten if duplication accrued.
- [ ] All tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`
- [ ] Coverage floor preserved: `uv run gz arb coverage run -m unittest discover -s tests -t .`

### Gate 3: Docs (Heavy required)

- [ ] `docs/user/manpages/gz-validate.md` updated with `--kind-invariance` flag and example
- [ ] `docs/user/runbook.md` cross-reference added
- [ ] `uv run mkdocs build --strict` exits 0

### Gate 4: BDD (Heavy required)

- [ ] At least one scenario under `features/` tagged `@REQ-0.0.35-04-NN` exercising `gz validate --kind-invariance`
- [ ] `uv run -m behave features/` covering the new scenario passes

### Gate 5: Human (Heavy + Foundation-kind required)

- [ ] Both heavy-lane and foundation-kind attestation requirements apply (either alone is sufficient; both fire here).
- [ ] Operator confirms the validator semantics, exit codes, and section-heading byte-identical match.
- [ ] Operator runs `gz validate --kind-invariance` and pastes observed output into the closeout commit body per `.claude/rules/tool-skill-runbook-alignment.md` § Commit-message discipline.

## Verification

```bash
# Flag registered
uv run gz validate --help | grep "kind-invariance"

# Validator runs clean against current foundation-ADR population (post-OBPI-03 backfill of ADR-0.0.35 itself)
uv run gz validate --kind-invariance

# Validator catches drift on a fixture foundation ADR with section missing
# (test surface; not a real ADR mutation)

# `gz check` includes the new scope
uv run gz check 2>&1 | grep -i "kind-invariance" || echo "Verify integration manually"

# Tests pass with REQ coverage
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz adr audit-check ADR-0.0.35-foundation-feature-invariance-test

# REQ-IDs covered
uv run gz covers ADR-0.0.35-foundation-feature-invariance-test

# Behave scenario passes
uv run -m behave features/kind_invariance.feature

# Behave REQ-tag validation
uv run gz validate --behave-req-tags

# Heavy-lane ARB receipts captured
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb coverage run -m unittest discover -s tests -t .
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Acceptance Criteria

- [ ] **REQ-0.0.35-04-01:** Given the `gz validate` argparse surface, when `gz validate --help` is invoked, then `--kind-invariance` is listed with a one-line description.
- [ ] **REQ-0.0.35-04-02:** Given a foundation-kind ADR carrying a substantive `## Why foundation tier?` section, when `gz validate --kind-invariance` runs, then it reports the ADR as passing and exits 0.
- [ ] **REQ-0.0.35-04-03:** Given a foundation-kind ADR with the `## Why foundation tier?` heading absent, when `gz validate --kind-invariance` runs, then it reports the ADR as failing and exits 3.
- [ ] **REQ-0.0.35-04-04:** Given a foundation-kind ADR with the `## Why foundation tier?` heading present but only placeholder text in the body, when `gz validate --kind-invariance` runs, then it reports the ADR as failing the substantive-content check and exits 3.
- [ ] **REQ-0.0.35-04-05:** Given a feature-kind ADR with no `## Why foundation tier?` section, when `gz validate --kind-invariance` runs, then the feature ADR is not enumerated and its absence of the section does not fail the check.
- [ ] **REQ-0.0.35-04-06:** Given the default `gz check` pipeline, when invoked, then it includes the `--kind-invariance` scope and fails the gate when any foundation ADR fails the check.
- [ ] **REQ-0.0.35-04-07:** Given the test surface, when run, then every test for this scope is decorated with `@covers(REQ-0.0.35-04-NN)` and `gz adr audit-check ADR-0.0.35-foundation-feature-invariance-test` reports REQ coverage closed.
- [ ] **REQ-0.0.35-04-08:** Given `features/`, when scenarios are enumerated, then at least one scenario carries `@REQ-0.0.35-04-NN` exercising the `gz validate --kind-invariance` operator flow, and `gz validate --behave-req-tags` reports the brief's REQs covered post-completion.
- [ ] **REQ-0.0.35-04-09:** Given `docs/user/manpages/gz-validate.md`, when read, then `--kind-invariance` is documented in the flags table and at least one example invocation is shown.
- [ ] **REQ-0.0.35-04-10:** Given `docs/user/runbook.md`, when read, then a cross-reference to the kind-invariance verification step is present.
- [ ] **REQ-0.0.35-04-11:** Given the closeout commit body, when inspected, then it cites ARB receipts for lint, typecheck, unit tests, coverage, and mkdocs strict per AGENTS.md § Attestation heavy-lane fail-closed rule.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent § Decision quoted
- [ ] **Gate 2 (TDD):** RED-GREEN-REFACTOR cycle followed across enumeration, section-presence, substantive-content, and CLI-integration increments; all tests passing
- [ ] **Code Quality:** Lint, format, typecheck clean; coverage floor preserved
- [ ] **Gate 3 (Docs):** Manpage and runbook updated; mkdocs strict clean
- [ ] **Gate 4 (BDD):** Behave scenario tagged with REQ-IDs and passing; `gz validate --behave-req-tags` clean
- [ ] **Gate 5 (Human):** Heavy-lane + foundation-kind brief-level attestation recorded; operator pasted observed CLI output into closeout commit
- [ ] **Value Narrative:** Recorded below
- [ ] **Key Proof:** `gz validate --kind-invariance` invoked against current foundation-ADR population with observed output pasted in evidence
- [ ] **OBPI Acceptance:** Evidence section populated with all five ARB receipt IDs

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste RED output for each of the four increments and GREEN output for each here
```

### Code Quality

```text
# Paste lint, format, typecheck, coverage output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output here
```

### Gate 4 (BDD)

```text
# Paste behave scenario output here
```

### Gate 5 (Human)

```text
# Record heavy-lane + foundation-kind brief-level attestation text here
# (operator-pasted observed CLI output for `gz validate --kind-invariance` against current foundation-ADR population)
```

### Value Narrative

Before this OBPI: the Why-foundation-tier convention authored under OBPI-03 is honor-system. Newly-scaffolded foundation ADRs land the section pre-populated, but nothing prevents an author from emptying it, paraphrasing the heading into drift, or skipping the substantive answer. After this OBPI: `gz validate --kind-invariance` enumerates every foundation ADR on every `gz check` invocation, fails closed on missing or placeholder-only `## Why foundation tier?` sections, and surfaces drift the moment it appears. The convention transitions from honor-system to structural — the doctrine ADR ships its own enforcement, closing the smell that triggered the OBPI re-decomposition.

### Key Proof

Output of `uv run gz validate --kind-invariance` invoked against the current foundation-ADR population, pasted with one passing case (ADR-0.0.35 itself, post-OBPI-03 backfill) and one constructed-failure case (a fixture foundation ADR with placeholder body) — both with their exit codes named.

### Implementation Summary

- Files created/modified: `src/gzkit/governance/trust_audits.py` (new validator scope), `src/gzkit/cli/parser_maintenance.py` (flag registration), `src/gzkit/commands/validate_cmd.py` (dispatch), `src/gzkit/commands/check.py` or equivalent (pipeline integration), `tests/governance/test_kind_invariance.py` (new), `tests/commands/test_validate.py` (additions), `features/kind_invariance.feature` (new or existing-feature addition), `docs/user/manpages/gz-validate.md`, `docs/user/runbook.md`
- Tests added: REQ-derived semantics tests for enumeration, section-presence, substantive-content, and CLI dispatch — exact test names TBD by implementer; each `@covers(REQ-0.0.35-04-NN)`-decorated
- ARB receipts: `arb-step-unittest-*`, `arb-ruff-*`, `arb-step-typecheck-*`, `arb-step-coverage-*`, `arb-step-mkdocs-*` (cited in attestation)
- Date completed: -
- Attestation status: -
- Defects noted: -

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` — required (heavy-lane + foundation-kind parent)
- Attestation: -
- Date: -

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
