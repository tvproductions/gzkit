# AUDIT PLAN (Gate-5) — ADR-0.0.68

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.68 |
| ADR Title | Green-Between-Sessions Gate |
| SemVer | 0.0.68 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate |
| Audit Date | 2026-06-09 |
| Auditor(s) | agent (pipeline-orchestrator persona), operator g0 (attestor) |

## Purpose

Confirm ADR-0.0.68 implementation is complete by validating its claims with
reproducible CLI evidence, and demonstrate the delivered capability
(COMPLETED → VALIDATED transition).

**Audit Trigger:** P2 of the restore-health convergence brief
(`ultraplan-brief.md` §4) — lock the green-between-sessions gate as a
validated floor; operator-authorized this session.

## Scope & Inputs

**Primary contract surfaces:**

- `uv run gz validate --session-green-gate` — fail-closed declaration validator (exit-3 contract)
- `uv run gz check` — default scope must include the "Session green gate" step (self-referential wiring)
- `.pre-commit-config.yaml` — `stages: [pre-push]` hook running `gz check` (OBPI-01)
- `docs/user/manpages/validate.md` — scope documentation; `docs/user/runbook.md` — install step
- `audit_session_green_gate` in `src/gzkit/governance/trust_audits/session_green_gate.py`

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Ledger proof complete | `uv run gz adr audit-check ADR-0.0.68` | PASS, exit 0, no blocking findings | Pending |
| Green path (declared hook satisfies floor) | `uv run gz validate --session-green-gate` | exit 0 | Pending |
| Red path fail-close (library surface) | `audit_session_green_gate(tmp)` on dirs missing/with-wrong hook | non-empty `ValidationError` list, type `session_green_gate` | Pending |
| Self-referential wiring | `_build_check_steps()` enumeration + live `uv run gz check` | "Session green gate" step present and green | Pending |
| Pre-push declaration (OBPI-01) | inspect `.pre-commit-config.yaml`; `pre-commit run --hook-stage pre-push --all-files` hook listing | `stages: [pre-push]` hook running `gz check` declared | Pending |
| Boundary Invariant (REQ-0.0.68-02-04, STRUCTURAL-FENCE) | inspect `session_green_gate.py` for hardcoded validator list | delegation only — no frozen scope enumeration | Pending |
| Docs build | `uv run mkdocs build --strict` (ARB receipt) | exit 0 | Pending |
| CLI doc coverage | `uv run gz cli audit` | exit 0, `--session-green-gate` covered | Pending |
| Unit suite | `uv run gz arb step --name unittest -- uv run -m unittest -q` | OK (receipt) | Pending |
| Independent spec review | `spec-reviewer` persona subagent | REQ coverage holds against fresh read | Pending |
| Independent quality review | `quality-reviewer` persona subagent | OBPIs cohere into the port | Pending |

## Risk Focus

- The audit-check covers-backfill false positive surfaced at ceremony start
  (cross-paired `git log -L` attribution) — remediated this session via direct
  fix `5b2a71ed` (blame re-anchor); re-verified PASS exit 0.
- Honest-scope boundary: the floor makes red un-persistable-undetected, NOT
  push-impossible-while-red (`--no-verify` is a documented escape) — audit
  verifies the declared contract, not a stronger one.
- 3 REQs without `@covers` are `[support]`/`[structural-fence]` kinds whose
  proof channels are ledger events + structural validators / parent-ADR
  Boundary Invariants (ADR-0.0.59) — advisory, not gaps.

## Findings Placeholder

Captured in `audit/AUDIT.md`.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- Value demonstration shows the gate working (green path, red path, wiring).
- No unresolved ✗ findings.

## Attestation Placeholder

Operator completes via verbal audit acceptance relayed to
`gz adr emit-receipt --event validated` (audit-begin/audit-end ceremony).
