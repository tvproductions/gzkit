# AUDIT PLAN (Gate-5) — ADR-0.0.14

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.14 |
| ADR Title | Deterministic OBPI Commands |
| SemVer | 0.0.14 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands |
| Audit Date | 2026-04-06 |
| Auditor(s) | agent:claude-opus-4-6 |

## Purpose

Confirm ADR-0.0.14 implementation is complete by validating its claims with reproducible CLI evidence.

**Audit Trigger:** Post-implementation Gate-5 validation for lifecycle promotion to Validated.

## Scope & Inputs

**Primary contract surfaces:**

- `gz obpi lock claim` — Claim an OBPI work lock with TTL
- `gz obpi lock release` — Release a claimed lock
- `gz obpi lock check` — Check lock status for an OBPI
- `gz obpi lock list` — List all active locks with stale-reaping
- `gz obpi complete` — Atomic OBPI completion transaction
- Lock data layer: `src/gzkit/lock_manager.py`
- Command implementations: `src/gzkit/commands/obpi_lock.py`, `src/gzkit/commands/obpi_complete.py`

**Skill surfaces (migration verified):**

- `.claude/skills/gz-obpi-lock/SKILL.md` — Delegates to `gz obpi lock` subcommands
- `.claude/skills/gz-obpi-pipeline/SKILL.md` — Delegates to `gz obpi lock` and `gz obpi complete`

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.14` | PASS — all OBPIs completed | Pending |
| Lock claim/release cycle | `gz obpi lock claim` / `release` / `check` | Atomic lock lifecycle | Pending |
| Lock list with stale-reaping | `gz obpi lock list` | Lists active, reaps expired | Pending |
| Complete command help | `gz obpi complete -h` | Shows full interface | Pending |
| Skill migration — no direct writes | `grep` for Write tool in skills | Zero matches to governance paths | Pending |
| Unit tests | `uv run -m unittest -q` | All pass | Pending |
| Docs build | `uv run mkdocs build -q` | Build clean | Pending |
| Gates | `uv run gz gates --adr ADR-0.0.14` | All gates pass | Pending |

## Risk Focus

- **Atomic rollback:** `gz obpi complete` claims all-or-nothing semantics — failure mid-transaction must not leave partial artifacts.
- **TTL enforcement:** Lock expiration and stale-reaping must be deterministic.
- **Skill migration completeness:** Skills must not retain any direct Write tool calls to governance paths.

## Findings Placeholder

Will be captured in `AUDIT.md` — do not populate here beyond structural notes.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with checkmarks.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- ADR lifecycle updated to Validated after attestation.
- No edits to accepted ADR prose.

## Attestation Placeholder

Human will complete in `AUDIT.md` with final summary.
