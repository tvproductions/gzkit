---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-21T23:55:11Z"
agent: claude-code
obpi_id: OBPI-0.0.74-11-mx-gz-level-vocabulary
session_id:
continues_from: .gzkit/handoffs/20260621T225721Z-adr-0-0-74-leveled-substrate-bcd-shipped.md
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-21T23:55:11Z -->

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

**OBPI-0.0.74-11-mx-gz-level-vocabulary is COMPLETE (attested_completed, attestor g0).**
This session implemented the first leveled-substrate build under the Magna Carta
campaign (Movement I). The `GZ_<LEVEL>` severity vocabulary landed at
`src/gzkit/mx/levels.py` STDLIB-FIRST: the ladder reuses Python `logging`
constants (CRITICAL 50 / ERROR 40 / WARNING 30 / INFO 20 / DEBUG 10) plus
`NOTICE = 25` (the rung Python omits — the agent-fidelity / V.I.B.E.S. drift
band), `GROUNDING_THRESHOLD = ERROR`, and `grounds(level)` returning True iff
effective severity `>= ERROR`. Five unit tests in `tests/mx/test_levels.py`
(TestLadderReusesStdlib x2, TestGroundingThreshold x3) pass 5/5.

The full `uv run gz obpi pipeline` ran end to end: plan-audit PASS, lock claimed,
brief reconciled, TDD RED then GREEN, Stage 3 all-green, Stage 4 operator
attestation ("attest completed"), Stage 5 atomic completion via the kind-aware
`gz obpi complete` chokepoint.

**Last lock-event timestamp:** `obpi_lock_claimed` at 2026-06-21T23:07:13.703486+00:00
(agent claude-code-3d7c7b6b). **Last commit SHA at handoff creation:** `7d3d5898`.
**Branch state:** `main`, with the completion's governance edits (brief update +
ledger receipt) uncommitted at handoff time; Stage 5 git-sync commits them.

## Important Context

- **The substrate is now 3/13 on ADR-0.0.74** (OBPI-01/02/11 attested). OBPI-11
  (the vocabulary foundation) was the right first pull because OBPI-12/03/14 all
  consume it.
- **Two gate-friction items surfaced in Stage 5 (both benign, both logged as an
  improvement insight):** (1) `gz obpi precomplete`'s `behave_req_coverage` check
  flagged all 3 REQs — the tracked Movement II item 3 defect (`obpi_precomplete.py`
  is NOT REQ-kind-aware while `obpi_complete.py` IS, GHI #636). Completion routed
  via the kind-aware chokepoint per skill doctrine; the chokepoint accepted all
  coverage. (2) Brief reconcile reported allowlist=1 drift post-implementation;
  the operator-attested (g0) amendment ADDED `src/gzkit/mx/__init__.py` to the
  allowlist via the reconcile engine's new-submodule coupled-surface heuristic —
  `__init__.py` was NOT actually modified (git diff empty). Harmless permissive
  over-declaration.
- **OBPI-11 deliberately did NOT modify `checkpoint.py`.** REQ-11-03 is a
  STRUCTURAL-FENCE whose proof channel is the parent ADR § Boundary Invariants #2
  (audited at ADR closeout), not a per-OBPI code edit. The actual checkpoint
  leveled-severity wiring is OBPI-12's deliverable.
- **No `__init__.py` export of `levels` was added.** The test imports
  `from gzkit.mx import levels` (submodule import), which resolves without an
  `__init__` re-export. Adding one was explicitly rejected as gold-plating.

## Decisions Made

- **Decision:** Route OBPI-11 completion through `gz obpi complete` despite the
  precomplete `behave_req_coverage` failure.
  **Rationale:** the failure is the known stale non-kind-aware precomplete check
  (Movement II item 3); the skill names precomplete the bypassable pre-flight and
  `gz obpi complete` the kind-aware chokepoint. The chokepoint accepted REQ-11-01/02
  (@covers) and REQ-11-03 (fence).
  **Alternatives rejected:** editing `obpi_precomplete.py` inside the OBPI-11
  pipeline (outside its allowlist — cross-brief scope violation).

- **Decision:** Apply the operator-attested brief reconcile amendment.
  **Rationale:** the post-implementation allowlist drift had to clear for the
  completion reconcile-freshness gate; the engine's amendment is permissive and
  clearly provenanced.
  **Alternatives rejected:** `--accept-stale-reconciliation` override (the drift
  was a genuine engine determination, not a false positive to wave through).

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator, await authorization before acting. -->

1. **Implement OBPI-0.0.74-12 (`mx-gates-as-sensors` / disposition handler)** — the
   next dependency-order pull: it consumes the `GZ_<LEVEL>` vocabulary and wires
   the level to AOG/advisory disposition (ADR BI#2). Run
   `uv run gz obpi pipeline OBPI-0.0.74-12` after plan-audit.
2. **Then OBPI-0.0.74-03 (`mx-gate5-invariants`)** — the never-relax floor +
   grader-gaming as the 5th member; consumes the vocabulary's grounding semantics.
3. **Discharge Movement II item 3 (GHI-direct fix):** make `obpi_precomplete.py`'s
   behave-coverage check REQ-kind-aware (mirror `obpi_complete.py` / GHI #636) so
   the pre-flight stops false-flagging BEHAVIOR-with-@covers and STRUCTURAL-FENCE
   REQs. Clean direct-fix per AGENTS.md § Defect-fix routing.

## Pending Work / Open Loops

- **ADR-0.0.74 is 3/13 complete.** Remaining: OBPI-03/04/05/06/07/08/09/12/13/14
  (item 10 withdrawn-hidden). The substrate build is the bulk of remaining work.
- **Movement II item 3 defect** (`obpi_precomplete.py` not REQ-kind-aware) is
  logged in `.gzkit/insights/agent-insights.jsonl` and named above — awaiting the
  direct fix.
- **Reconcile-engine over-reach** (adds a package `__init__.py` it cannot prove
  was modified) noted in the same insight as a lower-priority observation.
- **`ADR-0.29.0-precise-auth`** still in the feature list, not yet dropped to pool
  — release bookkeeping for the eventual `0.29.0` MX release.

## Verification Checklist

- [ ] `uv run gz obpi status OBPI-0.0.74-11-mx-gz-level-vocabulary` shows attested_completed
- [ ] `uv run gz adr status ADR-0.0.74` shows 3/13
- [ ] `git branch --show-current` is `main`; tree clean after Stage 5 git-sync
- [ ] `uv run -m unittest tests.mx.test_levels -v` passes 5/5
- [ ] `uv run gz obpi lock list` shows no lock for OBPI-0.0.74-11 (released this session)

## Evidence / Artifacts

- `src/gzkit/mx/levels.py` — the `GZ_<LEVEL>` vocabulary (ladder + NOTICE=25, GROUNDING_THRESHOLD=ERROR, grounds())
- `tests/mx/test_levels.py` — 5 unit tests (stdlib-equality ladder, NOTICE drift rung, grounding boundary)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-11-mx-gz-level-vocabulary.md` — the completed brief (evidence sections + attestation written)
- `.claude/plans/OBPI-0.0.74-11-mx-gz-level-vocabulary.md` — the approved plan
- `.claude/plans/.plan-audit-receipt-OBPI-0.0.74-11-mx-gz-level-vocabulary.json` — plan-audit PASS receipt
- `.gzkit/insights/agent-insights.jsonl` — improvement insight for the two Stage-5 gate-friction items

## Environment State

Platform win32; Python 3.13; `uv run` throughout. Branch `main` (operator
directive: no feature branches). HEAD `7d3d5898` at handoff creation; Stage 5
git-sync advances it. Lock claimed 2026-06-21T23:07:13Z, released this session
after this handoff (token-block coupling: handoff precedes release).
