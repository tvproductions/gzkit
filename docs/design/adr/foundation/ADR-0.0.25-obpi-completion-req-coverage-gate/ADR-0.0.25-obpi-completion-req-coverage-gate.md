---
id: ADR-0.0.25-obpi-completion-req-coverage-gate
status: Draft
kind: foundation
semver: 0.0.25
lane: heavy
parent:
date: 2026-04-25
---

# ADR-0.0.25-obpi-completion-req-coverage-gate: OBPI Completion REQ-Coverage Gate

## Persona

`main-session` + `implementer`. Heavy-lane runtime contract change tightening
what `Completed` means at OBPI brief level. Methodical TDD discipline; tests
assert REQ-derived semantics, not strings.

## Intent

Refuse `gz obpi complete` (and the ADR-level analogue `gz adr emit-receipt
--event closed`) when any REQ in the closing brief's `## Acceptance Criteria`
section lacks a passing `@covers`-decorated test. Today, `gz obpi complete`
emits a completion receipt as long as the attestation block is well-formed
and (post-ADR-0.0.24) the ARB receipts resolve. It does not assert that the
brief's REQs are individually covered by passing tests.

The GPT-5.5 Apollo § 9.2 finding — 29% lying about completing an Impossible
Coding Task — has a direct gzkit analogue: an agent can complete an OBPI
whose acceptance criteria include REQs that no passing test exercises. The
brief renders `Completed`; the audit-check surface (`gz adr audit-check`)
flags the gap later, post-attestation, when the cost of repair is higher.

This ADR redefines what `Completed` means at brief level: a brief is
completable iff every REQ has at least one passing covered test (or an
explicit, ledger-recorded waiver).

## Decision

1. Add a pre-emission check inside `gz obpi complete`:
   - Parse the brief's `## Acceptance Criteria` section for REQ-IDs.
   - For each REQ, search `tests/**` for `@covers(REQ-<id>)` decorators.
   - For each covered test, run `unittest` on it (scoped, fast) and assert
     pass.
   - If any REQ has zero covered tests, or any covered test fails, refuse
     completion with exit 3 and a structured message naming the gap.
2. Add `--accept-uncovered=REQ-X.Y.Z-NN-MM` (repeatable) override flag:
   - Each acceptance is recorded in the ledger as an
     `obpi-completion-uncovered-accept` event with operator name, brief
     ID, REQ ID, and rationale string.
   - Heavy/foundation briefs require an interactive TTY + `ACCEPT`
     confirmation per the same authenticity discipline as
     `_enforce_human_attestation_authenticity`.
3. Mirror the same gate in `gz adr emit-receipt … --event closed`: an ADR
   cannot close while any of its OBPIs has an unwaived REQ gap.
4. Update `gz obpi complete` help text and the OBPI Acceptance Protocol in
   AGENTS.md to reflect the new contract.
5. Backstop in BDD: add scenario coverage proving the gate fires, the
   override path records correctly, and the override requires interactive
   confirmation in heavy/foundation contexts.

## Consequences

### Positive

- Closes the "completed-with-uncovered-REQs" vector at the brief layer
  rather than catching it post-attestation in `gz adr audit-check`.
- Operator override remains available, but each override is now ledger-
  visible and operator-attributed — no silent skipping.
- Aligns brief-level Gate 2 (TDD) with brief-level completion: today
  Gate 2 verifies tests pass globally; this ADR verifies the brief's
  own REQs are individually covered.

### Negative

- A brief whose REQ language is broader than any single test legitimately
  covers will be blocked until either the test scope expands or the REQ
  is split. This is a forcing function, not a defect — narrow REQs that
  produce narrow tests is the desired authoring discipline.
- The `--accept-uncovered` override is a load-bearing escape hatch; if
  agents adopt it routinely (rather than as the documented rare exception),
  the gate's value erodes. Mitigated by the ledger-record-and-audit
  protocol — `gz validate --uncovered-accept-rate` can later flag elevated
  override usage as an advisory signal.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 0
- Dimension Total: 5
- Baseline Range: 3-4
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.25-01: Implement the REQ-coverage gate in `gz obpi complete` (parse acceptance criteria, locate `@covers`, run scoped unittest, fail-closed on heavy/foundation)
- [ ] OBPI-0.0.25-02: Implement the `--accept-uncovered=<REQ>` override path with ledger event recording and TTY+`ACCEPT` confirmation discipline; mirror the gate in `gz adr emit-receipt --event closed`
- [ ] OBPI-0.0.25-03: BDD scenarios in `features/` covering the gate firing, the override path, and the interactive-confirmation requirement; update AGENTS.md § OBPI Acceptance Protocol

## Q&A Transcript

Authored from a system-card review session (2026-04-25). External evidence:
GPT-5.5 Apollo § 9.2 (29% Impossible Coding Task lie rate) is the named
analogue at the model layer. gzkit's brief-level analogue is "completed
with uncovered REQs" — currently caught post-hoc by `gz adr audit-check`,
not pre-completion. This ADR moves the check from post-attestation to
pre-emission.

## Evidence

- [ ] Gate logic: `src/gzkit/commands/obpi.py`, `src/gzkit/commands/adr_emit_receipt.py`
- [ ] Override path: ledger event schema in `src/gzkit/governance/`
- [ ] Tests: `tests/commands/test_obpi_complete_coverage_gate.py`
- [ ] BDD: `features/obpi_completion_coverage_gate.feature`
- [ ] Docs: AGENTS.md § OBPI Acceptance Protocol; `docs/user/runbook.md`

## Alternatives Considered

1. **Continue relying on `gz adr audit-check` post-completion** — rejected.
   Post-hoc audit catches the gap, but only after attestation is recorded
   and only at ADR closeout granularity. The cost of repair (re-attestation,
   GHI authoring, brief re-open) is higher than the cost of pre-emission
   refusal. Per AGENTS.md § DO IT RIGHT 6c, the more-thorough fix is
   preferred when the narrow-fix rationale is "smaller diff."
2. **Run the full test suite at completion time instead of REQ-scoped
   tests** — rejected. The full suite already runs at Gate 2 and via
   `gz check`; the gap this ADR closes is REQ-specific coverage, which
   the global test pass cannot verify on its own. Scoped check is faster
   and produces the right signal.
3. **Make the gate advisory (warn, do not fail-closed)** — rejected for
   heavy/foundation. The Apollo 29% lie rate plus Opus 4.7 § 2.3.6.4
   "Dishonest when caught" both demonstrate that advisory discipline at
   completion time is insufficient at the current frontier. Lite-lane
   non-foundation completions remain advisory (consistent with the
   existing § Lane Rules covenant).

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.25 | Pending | | | |
