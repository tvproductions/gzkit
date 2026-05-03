# AUDIT PLAN — ADR-0.0.25-obpi-completion-req-coverage-gate

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.25-obpi-completion-req-coverage-gate |
| ADR Title | OBPI Completion REQ-Coverage Gate |
| SemVer | 0.0.25 |
| Kind / Lane | foundation / heavy |
| ADR Dir | `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/` |
| Audit Date | 2026-05-03 |
| Auditor | main-session (agent-relayed) |

## Purpose

Validate that ADR-0.0.25 ships a fail-closed REQ-coverage gate at OBPI brief
completion (and the mirrored ADR-close gate), with the documented
ledger-recorded operator override path, and BDD/runbook coverage. Move the
ADR from `Completed` → `Validated` after producing reproducible proof and
demonstrating the gate's value on a live runtime surface.

**Audit trigger:** Phase 2 validation — Phase 1 closeout already attested
(`Jeffry`, 2026-05-03), all three OBPIs `attested_completed`, REQ-coverage
already at 15/15 per `gz adr audit-check`.

## Claims extracted from ADR § Decision

1. `gz obpi complete` parses the closing brief's `## Acceptance Criteria`
   for REQ-IDs, locates `@covers(REQ-…)`-decorated tests, runs them
   scoped, and refuses completion (exit 3) on heavy/foundation when any
   REQ has zero passing covered tests.
2. `--accept-uncovered=REQ-X.Y.Z-NN-MM` (repeatable, paired with
   `--accept-uncovered-reason`) waives a gap, recording an
   `obpi_completion_uncovered_accept` ledger event; heavy/foundation
   waivers require interactive TTY + `ACCEPT` confirmation (or
   `--attestor-present` with active pipeline marker).
3. `gz adr emit-receipt … --event closed` mirrors the gate: an ADR
   cannot close while any of its OBPIs has an unwaived REQ gap.
4. `gz obpi complete` help text + AGENTS.md § OBPI Acceptance Protocol
   reflect the new contract.
5. BDD scenarios in `features/obpi_completion_coverage_gate.feature`
   cover the gate firing, the override path, and the interactive-
   confirmation requirement.

## Planned checks

| # | Check | Command / Method | Expected signal |
|---|-------|------------------|-----------------|
| 1 | Ledger proof exists | `uv run gz adr audit-check ADR-0.0.25` | `PASS All linked OBPIs … completed`; coverage 15/15 |
| 2 | Lifecycle pre-state | `uv run gz adr report ADR-0.0.25` | Lifecycle = `Completed`, Closeout = `attested` |
| 3 | Scoped REQ-coverage tests pass | `uv run -m unittest -q tests.commands.test_obpi_complete_coverage_gate tests.commands.test_adr_emit_receipt_coverage_gate tests.governance.test_req_coverage` | All tests pass, no failures |
| 4 | CLI surface exposes override | `uv run gz obpi complete --help` | `--accept-uncovered`, `--accept-uncovered-reason` flags present |
| 5 | ADR-close mirror surface | `uv run gz adr emit-receipt --help` | `--event {completed,validated,closed}` enum present |
| 6 | BDD scenarios run | `uv run -m behave features/obpi_completion_coverage_gate.feature` | All scenarios pass |
| 7 | Docs build | `uv run mkdocs build -q` | Build clean |
| 8 | Governance CLI audit | `uv run gz cli audit` | CLI cross-coverage 100% |
| 9 | Ledger event presence | `grep -c obpi_completion_uncovered_accept .gzkit/ledger.jsonl` | ≥ 1 (override path exercised) |

## Risk focus

- **Override-path corruption risk** — `--accept-uncovered` is a load-bearing
  escape hatch. The audit must confirm (a) the help text exposes both flags
  with the 1:1 pairing requirement, (b) at least one ledger event of shape
  `obpi_completion_uncovered_accept` exists with operator name + REQ-ID +
  rationale fields, and (c) heavy/foundation override requires the TTY-or-
  marker confirmation discipline (asserted by scoped tests).
- **Mirror-surface drift risk** — the ADR-level mirror in
  `gz adr emit-receipt --event closed` was the second OBPI's deliverable;
  the audit must confirm the `closed` event is in the parser enum and
  the mirror logic appears in `src/gzkit/commands/adr_audit.py`.
- **Doc-drift risk** — AGENTS.md § OBPI Acceptance Protocol must name the
  REQ-coverage gate by its canonical surface (`gz obpi complete` REQ-coverage
  gate ADR-0.0.25), not as an undocumented implementation detail.

## Acceptance criteria

- All planned checks executed; results recorded in `audit/AUDIT.md` with
  ✓/✗/⚠ symbols.
- Proof logs saved under `audit/proofs/` and referenced from `audit/AUDIT.md`.
- Feature Demonstration section in `audit/AUDIT.md` shows the gate's
  delivered capabilities exercised on the live `gz` runtime.
- Validation receipt emitted via the agent-relayed `audit-begin / emit /
  audit-end` ceremony after operator's verbal `accept audit` ack.
- `uv run gz adr report ADR-0.0.25` shows Lifecycle = `Validated` after
  receipt emission.
