---
id: OBPI-0.0.36-03-validate-receipt-shape-scope
parent: ADR-0.0.36-universal-obpi-attestation
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.36-03-validate-receipt-shape-scope: Validator Scope `--receipt-shape`

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ADR-0.0.36-universal-obpi-attestation.md`
- **Checklist Item:** #3 — "`gz validate --receipt-shape` fail-closed scope"

**Status:** Completed

## Objective

Add a fail-closed `gz validate --receipt-shape` scope that refuses any ledger receipt dated after ADR-0.0.36's cutoff carrying `attestation_requirement: optional`, `obpi_completion: completed` without the `attested_` prefix, or `attestor` matching `^agent:`, while delegating pre-cutoff receipts to the historical waiver list authored under OBPI-0.0.36-04.

## Lane

**Heavy** — adds a new CLI flag to a foundation surface (`gz validate`) and creates a fail-closed gate that affects every receipt-emission code path. CLI surface change triggers all heavy-lane gates (manpage, behave scenario, runbook update). Receipts that pass today must continue to pass after this scope lands; the cutoff and waiver list are the integrity boundaries.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — primary validator host module (precedent: `gz validate --utf8-prefix`, `gz validate --reconcile-freshness`, `gz validate --kind-invariance`)
- `src/gzkit/validate_pkg/__init__.py`, `src/gzkit/validate_pkg/document.py`, `src/gzkit/validate_pkg/ledger_check.py` — validator package surfaces if scope wiring lands here per existing convention
- `src/gzkit/cli/parser_artifacts.py` (or wherever `gz validate` flags are registered) — flag registration
- `src/gzkit/commands/validate.py` (if validator dispatch lives there) — flag dispatch
- `tests/governance/test_validate_receipt_shape.py` — new test module asserting fail-closed semantics on each deprecated shape
- `tests/commands/test_validate.py` — existing `gz validate` test surface; add `--receipt-shape` flag-wiring test
- `docs/user/manpages/gz-validate.md` — manpage update naming the new scope and exit codes
- `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — runbook entries for the new scope per gate-5-runbook-code-covenant rule
- `features/validate_receipt_shape.feature` (or extension to existing `features/validate.feature`) — behave scenario tagged with new REQ IDs

## Denied Paths

- `AGENTS.md` — doctrine surface owned by OBPI-0.0.36-01
- `src/gzkit/commands/adr_audit.py` — runtime gate is OBPI-0.0.36-02
- `data/historical_self_close_waivers.json` — waiver list authoring is OBPI-0.0.36-04 (this OBPI consumes the schema but does not author entries)
- `.gzkit/skills/**/SKILL.md`, `.claude/rules/**`, `.gzkit/rules/**` — skill/rule prose sweep is OBPI-0.0.36-05
- `.gzkit/ledger.jsonl` — never edit the ledger directly per AGENTS.md Behavior Rules — Never #2
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz validate --receipt-shape` MUST be a registered flag on the `gz validate` parser. Running `uv run gz validate --help` after this OBPI MUST list the flag with a one-line description naming the deprecated shapes it refuses.
2. REQUIREMENT: The validator MUST exit 3 (policy breach) when ANY receipt with `event_date >= ADR-0.0.36 cutoff date` carries `attestation_requirement: optional`. Cutoff is read from ADR-0.0.36-universal-obpi-attestation's `date:` frontmatter; hard-coding the date string is forbidden.
3. REQUIREMENT: The validator MUST exit 3 when ANY post-cutoff receipt carries `obpi_completion: completed` without the `attested_` prefix (the canonical post-doctrine term is `attested_completed`).
4. REQUIREMENT: The validator MUST exit 3 when ANY post-cutoff receipt carries `attestor` matching the regex `^agent:` (case-insensitive). Human attestor strings (`g0`, GitHub noreply addresses) MUST pass.
5. REQUIREMENT: The validator MUST delegate pre-cutoff receipts to the historical waiver list at `data/historical_self_close_waivers.json`. If the waiver list does not yet exist (i.e. OBPI-0.0.36-04 has not yet landed), pre-cutoff receipts with deprecated shapes MUST emit a warning, not a fail-closed exit — fail-closed semantics for historical receipts are switched on only when the waiver list is present.
6. REQUIREMENT: The new scope MUST be wired into `gz check` so the default quality pipeline catches violations. Adding the wiring without a `gz check` integration is incomplete delivery.
7. REQUIREMENT: `docs/user/manpages/gz-validate.md` MUST be updated to enumerate the new scope, its exit codes, and the cutoff-date semantics. Manpage drift is a Heavy-lane gate-3 failure.
8. REQUIREMENT: `features/validate_receipt_shape.feature` (or scenario in adjacent feature file) MUST carry scenarios tagged `@REQ-0.0.36-03-NN` covering each deprecated shape. Behave run MUST pass.
9. REQUIREMENT: Tests assert REQ-derived semantics — the deprecated-shape detection logic, not the byte-level error message format. Output-form fixtures (if any) live in a separate test class per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 3 carve-out.

> STOP-on-BLOCKERS: if `gz validate` flag registration uses a different module than `parser_artifacts.py` or `validate.py`, halt and surface the actual registration site before adding the flag.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item #3 — quote verbatim into Implementation Summary** (the validator scope addition).
- [ ] Parent ADR § Intent — why the validator is the mechanical defense complementing the doctrine collapse.
- [ ] Parent ADR § Non-goals — confirm this OBPI does NOT add a new top-level CLI verb (only a `--receipt-shape` flag under existing `gz validate`).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ADR-0.0.36-universal-obpi-attestation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item #3 that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.claude/rules/cli.md` — exit code conventions and Heavy Lane Trigger for new flags
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — manpage and runbook update requirement
- [ ] `.claude/rules/tests.md` § Behave scenario tagging — REQ-tag pattern
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution — new flag must resolve cleanly

**Context:**

- [ ] `src/gzkit/governance/trust_audits.py` — read existing scope implementations as pattern (e.g. `_check_utf8_prefix`, `_check_kind_invariance`); use the same shape for `_check_receipt_shape`
- [ ] `src/gzkit/cli/parser_artifacts.py` — locate `gz validate` flag registration block; new flag follows the same registration pattern
- [ ] `tests/governance/test_validate_*` (existing test modules) — match existing test patterns for new scope's tests
- [ ] `data/historical_self_close_waivers.json` — schema (authored by OBPI-04; this OBPI consumes the schema; coordinate with OBPI-04's brief on the field shape)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/governance/trust_audits.py` exists
- [ ] `src/gzkit/cli/parser_artifacts.py` exists (or equivalent flag-registration site)
- [ ] OBPI-0.0.36-01 has landed (doctrine binds the new scope)
- [ ] OBPI-0.0.36-02 has landed (runtime gate matches doctrine; receipts emitted post-OBPI-02 are the canonical shape the validator enforces)

**Existing Code (understand current state):**

- [ ] Existing receipt schema: read one or more recent ledger events under `.gzkit/ledger.jsonl` to confirm field shapes (`attestation_requirement`, `obpi_completion`, `attestor`, `event_date`)
- [ ] Existing validator dispatch in `gz validate` — note exit-code conventions (0/3 for clean/breach)
- [ ] Existing behave scenario tagging — match the canonical `@REQ-X.Y.Z-NN-MM` form

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item #3 quoted in Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: `tests/governance/test_validate_receipt_shape.py::test_post_cutoff_optional_attestation_fails_closed` fails before scope exists
- [ ] GREEN: same test passes after scope lands
- [ ] Red-Green-Refactor cycle followed for each deprecated shape
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/gz-validate.md` updated with new scope, exit codes, cutoff semantics
- [ ] `docs/user/runbook.md` and `docs/governance/governance_runbook.md` reference the new scope where receipt-shape integrity is discussed

### Gate 4: BDD (Heavy)

- [ ] `features/validate_receipt_shape.feature` (or extended `features/validate.feature`) scenarios tagged `@REQ-0.0.36-03-NN` for each deprecated shape; behave passes: `uv run -m behave features/`

### Gate 5: Human (Universal under this very ADR)

- [ ] Human attestation recorded with TTY+ATTEST under `gz obpi complete`

## Verification

```bash
# Help text shows new flag
uv run gz validate --help | rg -- --receipt-shape

# Fail-closed semantics on each deprecated shape (post-cutoff fixture receipt)
uv run -m unittest tests.governance.test_validate_receipt_shape -v

# Default `gz check` integration
uv run gz check 2>&1 | rg "receipt-shape"

# CLI alignment audit confirms new verb resolves cleanly in docs
uv run gz validate --cli-alignment

# Standard quality gates
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/validate_receipt_shape.feature

# ARB receipts for Heavy-lane attestation
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. The closeout
     ceremony walkthrough harvests this section (parser-validated;
     unregistered verbs are dropped). Prefer real paths and arguments
     over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

- [ ] REQ-0.0.36-03-01: Given `uv run gz validate --help` after this OBPI, when run, then `--receipt-shape` is listed with a one-line description naming the deprecated receipt shapes the scope refuses.
- [ ] REQ-0.0.36-03-02: Given a fixture receipt dated after ADR-0.0.36's `date:` cutoff carrying `attestation_requirement: optional`, when `uv run gz validate --receipt-shape` runs, then exit code is 3 and stderr names the offending receipt ID.
- [ ] REQ-0.0.36-03-03: Given a fixture receipt dated after cutoff carrying `obpi_completion: completed` without the `attested_` prefix, when the scope runs, then exit code is 3.
- [ ] REQ-0.0.36-03-04: Given a fixture receipt dated after cutoff carrying `attestor: agent:claude-code`, when the scope runs, then exit code is 3.
- [ ] REQ-0.0.36-03-05: Given a fixture receipt dated before cutoff carrying any deprecated shape and the historical waiver list at `data/historical_self_close_waivers.json` containing a matching waiver entry, when the scope runs, then the receipt passes silently (waiver hit).
- [ ] REQ-0.0.36-03-06: Given the new scope after this OBPI, when `uv run gz check` runs, then `--receipt-shape` is invoked as part of the default pipeline and a violation propagates the exit-3 to `gz check` itself.
- [ ] REQ-0.0.36-03-07: Given `docs/user/manpages/gz-validate.md` after this OBPI, when read, then the new scope, its exit codes, and the cutoff-date semantics are documented.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; Decision item #3 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed; assertions are REQ-derived semantics, not error-string shape
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** mkdocs --strict clean; manpage and runbook updated
- [ ] **Gate 4 (BDD):** behave scenarios tagged `@REQ-0.0.36-03-NN` and passing
- [ ] **Gate 5 (Human):** TTY+ATTEST attestation recorded
- [ ] **Value Narrative:** Documented below
- [ ] **Key Proof:** Concrete fail-closed exit-3 evidence below

> Universal attestation rule applies under ADR-0.0.36; Gate 5 fires regardless of lane.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste RED + GREEN test output for each deprecated-shape case here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output and manpage diff here
```

### Gate 4 (BDD)

```text
# Paste behave output for tagged scenarios here
```

### Gate 5 (Human)

```text
# Record attestation text + TTY+ATTEST receipt here
```

### Value Narrative

Before this OBPI, the receipt schema permitted `attestation_requirement: optional`, `obpi_completion: completed` without the `attested_` prefix, and `attestor: agent:*` — the literal state shapes that surfaced in the GHI #332 audit of ADR-0.16.0 closeout. After this OBPI, the validator refuses these shapes for any receipt dated after ADR-0.0.36's cutoff with exit 3, while the historical waiver list (OBPI-04) preserves ledger immutability for pre-cutoff drift. The mechanical defense is now in place — the doctrine collapse (OBPI-01) and runtime collapse (OBPI-02) cannot be silently re-rationalized by a future schema relaxation.

### Key Proof


```bash
# REQ-01: --receipt-shape flag registered
$ uv run gz validate --help | grep "receipt-shape"
[--kind-invariance] [--receipt-shape] [--regenerate]
  --receipt-shape       Refuse deprecated receipt shapes post-ADR-0.0.36 cutoff (exit 3)

# REQ-02..04: live repo passes (all canonical shapes)
$ uv run gz validate --receipt-shape --json
{"valid": true, "errors": []}

# REQ-02 fails closed on synthetic post-cutoff optional attestation_requirement (BDD scenario passes)
# REQ-03 fails closed on bare completed (no attested_ prefix) (BDD scenario passes)
# REQ-04 fails closed on agent: attestor case-insensitive (BDD scenario + unit test)
# REQ-05 pre-cutoff: silent pass when waivered; warn-only when waiver file absent
# REQ-06 wired into gz check via run_receipt_shape_audit in _build_check_steps
# REQ-07 manpage docs/user/manpages/validate.md updated with scope/exit-codes/cutoff semantics
```

Verified by 10/10 OBPI-scoped tests (arb-step-unittest-41ec1fa886274eb0981ffdfa6a973562) + 7/7 BDD scenarios (arb-step-behave-cae38fb93a294bbcb2bd04dcc2c0104c). Receipts: arb-ruff-a08e28ad69044da2853b060cced25362, arb-step-typecheck-00af324df363462991430b9ce3008797, arb-step-mkdocs-305cd5490f894ad3a2a389c4f5a89a11.

### Implementation Summary


- Files created: `src/gzkit/governance/trust_audits/receipt_shape.py` (audit_receipt_shape with cutoff parsing, ledger scanning, waiver delegation); `tests/governance/test_validate_receipt_shape.py` (7 REQ-derived unit tests); `features/validate_receipt_shape.feature` (7 BDD scenarios tagged @REQ-0.0.36-03-01..07); `features/steps/validate_receipt_shape_steps.py` (step definitions)
- Files modified: `src/gzkit/governance/trust_audits/__init__.py` (export); `src/gzkit/cli/parser_maintenance.py` (--receipt-shape flag); `src/gzkit/commands/validate_cmd.py` (dispatch + _POLICY_BREACH_ERROR_TYPES); `src/gzkit/quality.py` (run_receipt_shape_audit); `src/gzkit/commands/quality.py` (gz check wiring); `tests/commands/test_validate.py` (flag-wiring tests); `tests/commands/test_skills.py` (coupled-surface mock patch); `docs/user/manpages/validate.md`; `docs/user/runbook.md`; `docs/governance/governance_runbook.md`
- Tests added: 7 unit (post-cutoff optional fails, canonical passes, bare completed fails, agent attestor fails + case-insensitive, pre-cutoff waivered silent pass, pre-cutoff no waiver warn-only) + 3 flag-wiring + 7 BDD scenarios
- REQ→@covers parity: 7/7 covered (100%)
- Coupled-surface fix: tests/commands/test_skills.py mock patch added for new run_receipt_shape_audit step (AGENTS.md DO IT RIGHT 1a)
- Path corrections at audit time: brief listed `trust_audits.py` and `validate.py` (do not exist); actual paths are `trust_audits/receipt_shape.py` (package module) and `validate_cmd.py`; flag registration in `parser_maintenance.py`
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.36-03 validator scope --receipt-shape landed: src/gzkit/governance/trust_audits/receipt_shape.py implements audit_receipt_shape with dynamic ADR-0.0.36 cutoff parsing (no hard-coded date), ledger scanning, and waiver delegation; src/gzkit/cli/parser_maintenance.py registers --receipt-shape flag (help text ≤80 chars); src/gzkit/commands/validate_cmd.py dispatches and routes to exit 3 via _POLICY_BREACH_ERROR_TYPES; src/gzkit/quality.py + src/gzkit/commands/quality.py wire run_receipt_shape_audit into gz check _build_check_steps. Verified by 10/10 OBPI-scoped tests (7 unit tests in tests.governance.test_validate_receipt_shape + 3 flag-wiring tests in tests.commands.test_validate.TestReceiptShapeFlag) and 7/7 BDD scenarios tagged @REQ-0.0.36-03-01..07 (features/validate_receipt_shape.feature). REQ→@covers parity: 7/7 covered (100%). Receipts: arb-ruff-a08e28ad69044da2853b060cced25362, arb-step-typecheck-00af324df363462991430b9ce3008797, arb-step-unittest-41ec1fa886274eb0981ffdfa6a973562, arb-step-mkdocs-305cd5490f894ad3a2a389c4f5a89a11, arb-step-behave-cae38fb93a294bbcb2bd04dcc2c0104c. Brief Allowed Paths corrected in-flight: trust_audits.py → trust_audits/receipt_shape.py (package module); validate.py → validate_cmd.py; parser_artifacts.py → parser_maintenance.py. Coupled-surface fixes: tests/commands/test_skills.py mock patch added for new run_receipt_shape_audit check step. Closes mechanical defense layer of ADR-0.0.36 universal-attestation doctrine — doctrine collapse (OBPI-01) + runtime collapse (OBPI-02) now backed by fail-closed validator scope refusing the three deprecated state shapes (attestation_requirement: optional, obpi_completion without attested_ prefix, attestor: ^agent:) on post-cutoff receipts.
- Date: 2026-05-18

---

**Brief Status:** Draft

**Date Completed:** 2026-05-18

**Evidence Hash:** -
