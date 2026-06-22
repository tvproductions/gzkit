---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-22T09:29:15Z"
agent: claude-code
obpi_id: OBPI-0.0.74-12-mx-gates-as-sensors
last_lock_event_timestamp: "2026-06-22T08:14:57.579044+00:00"
last_commit_sha: 1cd7f61b
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-22T09:29:15Z -->

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

OBPI-0.0.74-12-mx-gates-as-sensors is **attested-complete** (Gate 5, operator
`g0`, "attest completed", 2026-06-22). It was driven end-to-end through the
gz-obpi-pipeline (Heavy lane). The one disposition handler landed at
`src/gzkit/mx/disposition.py`: a pure `Route` StrEnum + `route(level)` matrix.
`src/gzkit/mx/checkpoint.py` gained `resolve(guard_name, emitted_level,
project_root)` which pins gate5_invariants to CRITICAL, demotes non-floor levels
to `Route.ADVISORY` under an active marker, and otherwise delegates to
`disposition.route()`. `is_advisory()` is preserved unchanged. Tests
(`tests/mx/test_disposition.py`, 5 tests / 3 classes) are GREEN; lint, typecheck,
mkdocs all clean.

Mid-ceremony the operator refined the sub-ERROR matrix rows into the
**V.I.B.E.S.-management band** (NOTICE=escalation via arb/insights,
INFO=tracking incl. inherent model behavior that can only be influenced,
DEBUG=anti-vibing verbose steering). That refinement is now encoded in
`disposition.py` (Route enum docstring + comments) and the ADR-0.0.74 § Decision
item 12 matrix interpretive note. An `improvement` insight was appended to
`.gzkit/insights/agent-insights.jsonl`.

At handoff creation: `gz obpi complete` has run (atomic attestation + brief +
receipt). Remaining Stage-5 mechanics after this handoff: lock release, marker
cleanup, git-sync #1, reconcile, ADR status, git-sync #2.

## Important Context

- **Prerequisite topology:** `GATE5_INVARIANTS` lives in `checkpoint.py` (seeded
  by OBPI-02), NOT in a separate `invariants.py` — the brief's discovery
  checklist was corrected to reflect this during Stage 1 reconcile.
- **Import direction is load-bearing:** `checkpoint → disposition` (never the
  reverse). `disposition.py` imports only `gzkit.mx.levels`; it must stay free of
  marker/checkpoint state to remain a pure matrix.
- **Allowlist amendment:** `src/gzkit/mx/marker.py` and `src/gzkit/mx/__init__.py`
  were added to the brief allowlist as READ-ONLY fixture/package dependencies —
  the under-marker tests import `marker` for fixtures (matching the
  `test_checkpoint.py` convention). This cleared a brief-reconcile allowlist
  false-positive; neither file was modified.
- **NOTICE drain is semantics-only:** the V.I.B.E.S.-band routes are named and
  encoded, but the actual "Chores drain" / debt-aging machinery is built by later
  ADR-0.0.74 OBPIs, not this one.

## Decisions Made

- **Decision:** Encode the operator's V.I.B.E.S.-band semantics in
  `disposition.py` Route enum docstring/comments AND the canonical ADR matrix.
  **Rationale:** `disposition.py` is the single home of the matrix; the semantics
  would otherwise evaporate at conversation close. The ADR carries the design
  table, so the interpretive note belongs there too.
  **Alternatives rejected:** Inline comments only (overflowed ruff E501, and the
  meaning belongs in prose); leaving the semantics in conversation only (lost).
- **Decision:** Add marker.py/__init__.py to the allowlist as read-only deps
  rather than refactor the test or use an `--accept-*` override.
  **Rationale:** The test genuinely imports them; the honest fix is to make the
  brief reflect reality. Matches the established `test_checkpoint.py` fixture
  convention.
  **Alternatives rejected:** `--accept-stale-reconciliation` override (hides the
  real dependency); refactoring the fixture (forks a working convention).

## Immediate Next Steps

<!-- ADVISORY ONLY — propose to operator, do not execute without authorization. -->

1. **Continue the ADR-0.0.74 campaign sequence.** Per the Build-to-1.0 Magna
   Carta, the next campaign item after gates-as-sensors (item 12) is the
   **MX lean kernel + hardening** (item 14) toward release `0.29.0`, and the
   **enforcement-claim meta-validator**. Confirm with the operator which OBPI is
   pulled next (`uv run gz adr status ADR-0.0.74 --json` for remaining items).
2. **Wire the NOTICE drain** when its OBPI is reached — the V.I.B.E.S.-band
   semantics this OBPI named (`drift → Chores drain`) now await the actual
   drain/debt-aging machinery.
3. **Operationalize INFO/DEBUG routing** if/when the campaign calls for it — they
   are correct level definitions with named routes but no mechanical dispatcher
   yet.

## Pending Work / Open Loops

- ADR-0.0.74 remains in progress — item 12 is done; items 13 (proxy-reality
  detector) and 14 (MX hardening) plus the meta-validator are open per the
  campaign checklist.
- INFO → track and DEBUG → steering routes are vocabulary + named semantics
  without a mechanical routing channel (future work, not a defect).

## Verification Checklist

- [ ] `uv run gz obpi status OBPI-0.0.74-12-mx-gates-as-sensors` shows
      `ATTESTED COMPLETED`
- [ ] `uv run gz obpi lock list` shows no active lock for this OBPI (released
      after this handoff)
- [ ] `uv run -m unittest tests.mx.test_disposition -q` passes
- [ ] Branch matches: `git branch --show-current` == `main`
- [ ] `uv run gz covers OBPI-0.0.74-12-mx-gates-as-sensors --json` →
      `behavior_uncovered_reqs == 0`

## Evidence / Artifacts

- `src/gzkit/mx/disposition.py` — the one level→route matrix handler (Route
  StrEnum + `route()`); V.I.B.E.S.-band semantics in docstring/comments
- `src/gzkit/mx/checkpoint.py` — added `resolve()`; `is_advisory()` preserved
- `tests/mx/test_disposition.py` — 5 tests across 3 classes (matrix rows,
  sensor interface, under-marker demotion, gate5 CRITICAL pin)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — matrix interpretive note (V.I.B.E.S. band)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-12-mx-gates-as-sensors.md` — completed brief with attestation
- `.gzkit/insights/agent-insights.jsonl` — `improvement` insight for the operator refinement

## Environment State

Python 3.13+ via uv; gzkit on branch `main`. No feature branch (operator
directive). Pipeline markers
`.claude/plans/.pipeline-active-OBPI-0.0.74-12-mx-gates-as-sensors.json` and the
legacy `.pipeline-active.json` pending cleanup in the remaining Stage-5 steps.
