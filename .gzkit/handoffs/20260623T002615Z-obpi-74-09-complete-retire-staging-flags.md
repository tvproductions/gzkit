---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-23T00:26:15Z"
agent: claude-code
obpi_id: OBPI-0.0.74-09-mx-retire-staging-flags
last_lock_event_timestamp: "2026-06-22T23:31:54.719717+00:00"
last_commit_sha: d42698ce
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-23T00:26:15Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

## Current State Summary

OBPI-0.0.74-09-mx-retire-staging-flags is **attested-complete** (Gate 5
operator attestation "attest completed" by g0, recorded via `gz obpi complete`,
completion type `operator-verbatim-conversational`).

The two hand-set staging flags are gone: `_FRESHNESS_FAIL_CLOSED`
(`rendition_freshness.py`) and `_FLOOR_FAIL_CLOSED`
(`rendition_floor_coherence.py`) were deleted and both gates now resolve their
effective severity through the shared leveled MX checkpoint via
`_checkpoint.is_advisory("<guard-name>", root)` — advisory inside the hangar
(marker present), fail-closed at full strength outside.

Verification at completion: 23/23 scoped tests pass
(`arb-step-unittest-fdd6331d99df481baa170005ba047f45`), lint clean
(`arb-ruff-8c1128b368364fff9900b6d4f1e9c530`), typecheck clean
(`arb-step-typecheck-db8d74cd54834733848cb66121c6aa83`), docs clean
(`arb-step-mkdocs-87db927daa64446ba806b405da7edf60`), QC binding (negative
controls) passes — the gates genuinely bind after the rewire.

Pipeline state: pre-`gz obpi complete` steps done. Remaining Stage 5 steps:
lock release (this handoff is its precondition), pipeline-marker cleanup, two
git-sync cycles, and `gz obpi reconcile`.

## Important Context

**Expected consequence — pre-existing corpus drift now surfaced.** The staging
flags were hiding pre-existing `AGENTS.md` corpus drift: `AGENTS.md/codex` and
`AGENTS.md/claude` renditions have no provenance sidecar. With the flags gone,
`gz validate --rendition-freshness` and `--rendition-floor-coherence` are now
fail-closed outside the MX hangar, so `gz check` exits 1 on these two checks
(plus a pre-existing `Behave` failure unrelated to this OBPI). This is the
honest generalization the ADR intended — the drift was always there; the
staging flag suppressed it. This drift is NOT a regression introduced by this
OBPI.

**The checkpoint API consumed (not authored):** `gzkit.mx.checkpoint.is_advisory(guard_name, project_root)`
returns `True` when an MX marker is active and the guard is not a
gate5_invariant. This OBPI consumes it; OBPI-0.0.74-02/11 own it.

**Brief allowlist amendment:** the brief's original `**` glob Allowed Path was
replaced with the explicit brief file path, because the reconcile engine's
allowlist checker does a literal file-existence test with no glob guard (unlike
the discovery checker). The `**` always read as "missing on disk." Surgical
brief fix, not a code contortion.

## Decisions Made

- **Decision:** Wire severity via `checkpoint.is_advisory()` rather than
  `checkpoint.resolve()` with a `GZ_<LEVEL>` constant.
  **Rationale:** `is_advisory()` directly answers the bool the `closed` variable
  needs; these two gates do not otherwise emit a level constant.
  **Alternatives rejected:** (a) hard-default `fail_closed=True` without
  checkpoint — loses hangar advisory demotion, defeats the OBPI's purpose;
  (b) `resolve()` with a level constant — introduces a level these gates don't
  emit; (c) new `guard_level` parameter — speculative complexity.

- **Decision:** Delete the obsolete staging-test classes
  (`TestRenditionFreshnessWarnStaging`, `TestStagedWarn`) rather than retrofit
  them.
  **Rationale:** they tested the `_*_FAIL_CLOSED = False` warn-default behavior
  that the checkpoint supersedes; the new `TestCheckpointWiring*` classes encode
  the replacement semantics (no marker → fail-closed; marker → advisory).

- **Decision:** Replace the `**` glob allowed-path with the explicit brief file
  path (brief amendment) rather than override the reconcile gate.
  **Rationale:** the brief was right and the tool has a known glob-guard gap;
  fixing the brief surgically is cleaner than carrying an override.

## Immediate Next Steps

*(ADVISORY — present to operator, await authorization before acting.)*

1. **Follow-up: repair the pre-existing AGENTS.md corpus drift.** Enter MX mode
   (`gz mx enter`) and recompose/recommit `AGENTS.md/codex` and
   `AGENTS.md/claude` renditions with provenance sidecars
   (`gz content compose AGENTS.md --consumer <c>` then `gz content commit ...`),
   so `gz check` returns green outside the hangar. This is now visible because
   OBPI-09 landed; it is the natural next repair.
2. **Continue the ADR-0.0.74 checklist.** Per the Build-to-1.0 campaign, the
   remaining MX kernel items (OBPI-0.0.74-05 no-force exit, TTL/max-open,
   ledger↔marker binding, dangling-state detector, etc.) and the
   enforcement-claim meta-validator are the next propellants toward `0.29.0`.
3. **Address the pre-existing `Behave` failure** surfaced by `gz check`
   (unrelated to OBPI-09; the `adr_audit_covers_backfill.feature` scenario).

## Pending Work / Open Loops

- ADR-0.0.74 closeout will audit REQ-0.0.74-09-03 (STRUCTURAL-FENCE) against
  parent ADR § Boundary Invariants #2 ("the checkpoint is the single LEVELED
  severity authority … no per-gate hand-set staging flag survives anywhere in
  the codebase"). OBPI-09 contributes to that invariant; it is proven at the ADR
  closeout layer, not per-OBPI.
- Pre-existing corpus drift (`AGENTS.md/codex`, `AGENTS.md/claude`) — tracked in
  Immediate Next Step 1.
- Pre-existing `Behave` failure in `gz check` — tracked in Immediate Next Step 3.

## Verification Checklist

- [ ] `uv run gz obpi status OBPI-0.0.74-09-mx-retire-staging-flags` → ATTESTED COMPLETED
- [ ] `uv run -m unittest tests.governance.test_rendition_freshness tests.governance.test_rendition_floor_coherence` passes (23 tests)
- [ ] `uv run gz validate --qc-binding` passes (negative controls bind)
- [ ] `grep -rn "_FRESHNESS_FAIL_CLOSED\|_FLOOR_FAIL_CLOSED" src/` returns nothing
- [ ] Branch matches: `git branch --show-current` → main

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/rendition_freshness.py` — flag deleted, checkpoint wired
- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — flag deleted, checkpoint wired
- `tests/governance/test_rendition_freshness.py` — `TestCheckpointWiringFreshness` added; staging class removed
- `tests/governance/test_rendition_floor_coherence.py` — `TestCheckpointWiringFloor` added; staging class removed
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-09-mx-retire-staging-flags.md` — brief, status Completed, evidence sections populated
- `.claude/plans/retire-staging-flags-OBPI-0.0.74-09.md` — approved plan
- `.claude/plans/.plan-audit-receipt-OBPI-0.0.74-09-mx-retire-staging-flags.json` — PASS receipt

## Environment State

Python 3.13, uv-managed. No new dependencies introduced.
