# ADR-pool.svfr-quick-adhoc

- **Status:** Pool
- **Lane:** Heavy
- **Date:** 2026-04-05
- **Origin:** GSD v1 comparative analysis — quick mode adaptation

## Intent

Provide a ceremony-lite execution path for bounded ad-hoc tasks that would otherwise
skip governance entirely. The current pipeline requires a full ADR → OBPI → implement
→ attest cycle for every change. For small, well-understood tasks (bug fixes, config
tweaks, dependency bumps, documentation patches), this overhead discourages governance
participation — operators either skip the pipeline or batch unrelated changes into
existing OBPIs to avoid the ceremony cost.

SVFR (Special VFR) already solves the "Heavy work with Lite ceremony" problem at the
OBPI level — self-close with deferred human review at ADR closeout. This pool ADR
extends that principle to ad-hoc work: bounded tasks get SVFR clearance under a
standing maintenance ADR, preserving the ledger trail without the full ceremony cost.

## Target Scope

### Standing Maintenance ADR

A persistent ADR (e.g., `ADR-M.0.0-maintenance`) that serves as the parent for
all quick/ad-hoc OBPIs. This ADR:

- Is created once per project via `gz bootstrap` or `gz init`
- Has `## Execution Mode: Exception (SVFR)` permanently granted
- Has no fixed checklist — OBPIs are added dynamically as quick tasks arise
- Undergoes periodic human review (weekly/monthly) rather than per-OBPI attestation

### Quick Execution Command

`gz quick "<description>"` as a single-command workflow:

1. **Auto-creates** a minimal OBPI brief under the maintenance ADR
   - Slug derived from description
   - Allowed paths inferred from the description + codebase analysis (or `--paths` flag)
   - Lane inherited from maintenance ADR (SVFR)
2. **Claims** the OBPI lock automatically
3. **Executes** the standard pipeline (implement → verify → present) with SVFR self-close
4. **Commits** atomically with OBPI ID in the commit message
5. **Releases** the lock and records ledger events

### Scope Escalation

If a quick task grows beyond its initial scope:

- `gz quick --escalate` promotes the ad-hoc OBPI to a proper ADR
- Existing ledger events transfer to the new ADR
- Human reviews the escalation and confirms the new scope
- Prevents scope creep hidden behind quick mode

### Flags

- `gz quick "<desc>"` — full auto: create, implement, self-close
- `gz quick "<desc>" --dry-run` — show what would be created, don't execute
- `gz quick "<desc>" --paths src/foo,tests/foo` — explicit path scope
- `gz quick --escalate OBPI-M.0.0-nn` — promote to full ADR
- `gz quick --log` — list recent quick OBPIs under the maintenance ADR

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- Quick mode does not bypass the ledger — every action is recorded.
- Quick mode does not bypass tests — Gate 2 (TDD) still runs.
- Quick mode is not a license for large changes — scope escalation is mandatory when
  the task outgrows its initial brief.
- No replacement for the full ADR pipeline — quick mode is for bounded tasks only.

## Dependencies

- **Prerequisite:** SVFR execution mode (ADR-0.12.0, ADR-0.13.0 — already implemented)
- **Prerequisite:** OBPI lock mechanism (already implemented via `gz-obpi-lock`)
- **Complements:** ADR-pool.agent-execution-intelligence CAP-22 (`gz next` could route to `gz quick` when the task is ad-hoc)
- **Complements:** ADR-pool.atomic-obpi-commits (quick tasks produce atomic commits)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Standing maintenance ADR pattern is validated — confirm it doesn't create a
   governance blind spot where large changes hide behind quick mode.
3. Scope escalation mechanism is defined with clear thresholds (line count? file count?
   human judgment?).
4. SVFR self-close behavior for ad-hoc OBPIs is confirmed compatible with existing
   pipeline runtime.
5. Periodic review cadence for the maintenance ADR is established.

## Inspired By

- [GSD](https://github.com/gsd-build/get-shit-done) `/gsd-quick` — ad-hoc task execution that skips the full phase ceremony but preserves atomic commits and state tracking. Flags: `--discuss`, `--research`, `--full`, `--validate`.
- Aviation Special VFR — fly visual rules in controlled airspace when conditions and clearance allow. The pilot (operator) still files a flight plan (ledger events) but doesn't need the full IFR ceremony.

## Notes

- The maintenance ADR is a governance innovation — it's the first ADR type that doesn't
  have a fixed scope at creation time. This needs careful design to prevent it from
  becoming a dumping ground that circumvents governance.
- Consider: maximum OBPI count or age limit on the maintenance ADR before requiring
  a new one, to keep review scope manageable.
- Consider: `gz quick` could default to Lite lane unless `--heavy` is specified,
  since most ad-hoc tasks are internal changes.
- Risk: if quick mode is too easy, operators may prefer it over proper ADRs for work
  that deserves full ceremony. The escalation mechanism and periodic review are the
  primary mitigations.
- GSD's quick mode lives in `.planning/quick/` — gzkit's equivalent would be the
  maintenance ADR's `obpis/` directory, keeping all artifacts in the standard location.
