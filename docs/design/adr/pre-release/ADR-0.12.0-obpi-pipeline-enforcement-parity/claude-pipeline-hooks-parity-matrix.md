# ADR-0.12.0 Claude Pipeline Hooks Parity Matrix

## Metadata

- Date: 2026-03-12
- Canonical source: `../airlineops/.claude/hooks/` and `../airlineops/.claude/skills/gz-plan-audit/SKILL.md`
- Extraction target: `.claude/hooks/`, `.claude/plans/`, `.gzkit/skills/`
- Parent ADR: `ADR-0.12.0-obpi-pipeline-enforcement-parity`
- Intake owner: `OBPI-0.12.0-01-canonical-hook-inventory-and-parity-contract`

## Contract Summary

This matrix replaces the generic "future plan-mode lifecycle ADR" placeholder
from `ADR-0.9.0` with an explicit parity contract for the blocking AirlineOps
pipeline-enforcement chain.

The key hidden dependency is not another hook. It is the receipt generator that
produces `.claude/plans/.plan-audit-receipt.json`. In AirlineOps that surface
comes from `gz-plan-audit`; in gzkit it is now tracked explicitly as
`OBPI-0.12.0-07`.

## Canonical Hook Mapping

| Canonical Artifact | Current gzkit Status | gzkit Target | Trigger / Contract | Owner OBPI | Notes |
| --- | --- | --- | --- | --- | --- |
| `plan-audit-gate.py` | Ported (inactive) | `.claude/hooks/plan-audit-gate.py` | `ExitPlanMode` hard gate; consumes `.claude/plans/.plan-audit-receipt.json` | `OBPI-0.12.0-02` | Hook script is ported; registration and ordering still land in `OBPI-0.12.0-06` |
| `pipeline-router.py` | Ported (inactive) | `.claude/hooks/pipeline-router.py` | plan-exit routing; reads receipt and directs agent to `gz-obpi-pipeline` | `OBPI-0.12.0-03` | Supports PASS-only routing and silent no-op when receipt is absent or not `PASS`; registration still lands in `OBPI-0.12.0-06` |
| `pipeline-gate.py` | Ported (inactive) | `.claude/hooks/pipeline-gate.py` | `Write|Edit` block for `src/` and `tests/`; consumes active pipeline marker | `OBPI-0.12.0-04` | Honors per-OBPI marker first, legacy marker second, and blocks only when a PASS receipt exists without a matching marker; registration still lands in `OBPI-0.12.0-06` |
| `pipeline-completion-reminder.py` | Ported (inactive) | `.claude/hooks/pipeline-completion-reminder.py` | pre-commit / pre-push reminder before incomplete pipeline state leaves local repo | `OBPI-0.12.0-05` | Non-blocking warning surface; generated locally but registration still lands in `OBPI-0.12.0-06` |
| Hook registration / ordering | Missing | `.claude/settings.json` and `.claude/hooks/README.md` | correct registration order relative to existing router/validator hooks | `OBPI-0.12.0-06` | Must document actual runtime, not aspirational parity |

## Prerequisite Surfaces

| Surface | Current gzkit Status | gzkit Target | Contract | Owner OBPI | Notes |
| --- | --- | --- | --- | --- | --- |
| `gz-plan-audit` skill | Ported | `.gzkit/skills/gz-plan-audit/SKILL.md` plus mirrors | audits ADR ↔ OBPI ↔ plan alignment and writes receipt | `OBPI-0.12.0-07` | Canonical skill is ported; operator-invoked today, hook enforcement still pending |
| Plan-audit receipt | Skill-defined | `.claude/plans/.plan-audit-receipt.json` | fields: `obpi_id`, `timestamp`, `verdict`, `plan_file`, `gaps_found` | `OBPI-0.12.0-07` | Contract is ported through the skill; hook and router enforcement still land in later OBPIs |
| Active pipeline marker | Ported (skill contract) | `.claude/plans/.pipeline-active-{OBPI-ID}.json` | per-OBPI marker created by pipeline Stage 1 | `OBPI-0.12.0-03` | Stage 1 now dual-writes the legacy fallback `.pipeline-active.json` for compatibility-only consumers |
| Lock surface | Missing | future native surface | concurrency / shared-scope coordination | follow-on ADR | Out of scope for `ADR-0.12.0`; fail closed until designed |

## Ordering Contract

1. `gz-plan-audit` produces the receipt.
2. `plan-audit-gate.py` blocks plan exit without a valid receipt.
3. `pipeline-router.py` routes only after a PASS receipt exists.
4. `gz-obpi-pipeline` creates the active pipeline marker.
5. `pipeline-gate.py` blocks `src/` and `tests/` writes until that marker exists.
6. `pipeline-completion-reminder.py` warns before commit/push while the marker
   still represents incomplete governance state.
7. `OBPI-0.12.0-06` wires the hook chain into `.claude/settings.json` in the
   correct order.

## Fail-Closed Rules

- Missing `gz-plan-audit` parity is a blocker, not a reason to weaken the
  gate/router contract.
- Missing active-marker parity is a blocker for write-time gating, not a reason
  to allow unrestricted `src/` / `tests/` edits.
- `.claude/hooks/README.md` and the pipeline skill must stay honest about what
  is implemented versus only contracted.
- No hook in this ADR may silently reinterpret the AirlineOps contract into a
  reminder-only substitute where canon blocks.

## Relation To ADR-0.9.0

`ADR-0.9.0` correctly deferred these hooks because gzkit lacked the plan-mode
and receipt infrastructure at the time. `ADR-0.12.0` supersedes that generic
deferral for the pipeline-enforcement tranche only; the `ADR-0.9.0` intake
matrix remains the historical record of the original defer decision.
