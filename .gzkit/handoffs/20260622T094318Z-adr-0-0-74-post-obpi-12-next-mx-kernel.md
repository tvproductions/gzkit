---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-22T09:43:18Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: b45762eb
session_id:
continues_from: .gzkit/handoffs/20260622T092915Z-obpi-0-0-74-12-mx-gates-as-sensors-completed.md
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-22T09:43:18Z -->

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

Session completed **OBPI-0.0.74-12-mx-gates-as-sensors** (Heavy lane,
ATTESTED COMPLETED, operator `g0`, 2026-06-22) end-to-end through the
gz-obpi-pipeline, synced to `main`. The one disposition handler
(`src/gzkit/mx/disposition.py`) and the `checkpoint.resolve()` level→route wire
are live; the operator's V.I.B.E.S.-management-band refinement of the sub-ERROR
matrix rows is encoded in both `disposition.py` and the ADR-0.0.74 matrix.

**Magna Carta updated this session:** Movement I item 1 (`GZ_<LEVEL>` substrate +
gates-as-sensors + one disposition handler) is checked off in
`docs/governance/build-to-1.0-campaign-2026-06-20.md` — OBPI-0.0.74-11 (levels
vocabulary) + OBPI-0.0.74-12 (disposition handler + wire) both ATTESTED
COMPLETED. The check carries an explicit caveat: the *mechanism* (substrate,
handler, AOG/advisory wire, BI#2) is built, but migrating each live guard to emit
`GZ_<LEVEL>` through the checkpoint remains (OBPI-0.0.74-09, retire staging flags).

No active OBPI lock. Tree is clean except the in-flight campaign edit (this
handoff's git-sync will commit it). Branch `main`, synced.

## Important Context

- **Movement I is partially built.** Item 1 (substrate/sensors/handler) done.
  Item 2 (MX lean kernel + hardening → release `0.29.0`) and item 3 (the
  enforcement-claim meta-validator) are open. The "substrate" in the topmost
  sequencing line = item 1 + item 3; item 3 (meta-validator) is still unbuilt, so
  the substrate is not yet whole.
- **ADR-0.0.74 OBPI ledger:** 01, 02, 11, 12 complete (5 incl. marker). Open:
  03 (gate5_invariants formal set), 04 (mx enter), 05 (mx exit hard-gate), 06
  (log auto-assemble), 07 (awareness hook), 08 (skill+agent), 09 (retire staging
  flags), 13 (proxy-reality detector), 14 (MX hardening). Item 10 (doc-type
  taxonomy) is CUT per the campaign.
- **The campaign Queue is the daily driver**, not the ADR OBPI order. Movement I
  item 2 ("MX lean kernel + hardening") maps to a cluster of these OBPIs:
  enter/exit/status (04/05), the floor (03), ledger↔marker binding, no-force
  exit, TTL/max-open, no-normal-release-while-MX-open, live exit negative-controls,
  ledger debt-aging, dangling-state detector. The campaign also carries a
  standing fix for ADR-0.0.74's stub (non-live) fidelity assertions.
- **Green-floor inheritance rule:** no movement opens while `uv run gz check` is
  red. Verify before pulling new Movement I work.
- **disposition.py is pure** — it imports only `gzkit.mx.levels`; the
  checkpoint→disposition import direction is load-bearing (never reverse).

## Decisions Made

- **Decision:** Check off Movement I item 1 with a precise scope annotation rather
  than leaving it open or claiming blanket completion.
  **Rationale:** The item's own parenthetical scopes it to "the level→AOG/advisory
  wire; BI#2 built for real" — which OBPI-11+12 deliver. The per-guard migration
  is a distinct thread (OBPI-09), named in the annotation so the check is honest.
  **Alternatives rejected:** Leaving it unchecked (understates real, attested
  progress); checking it bare (overstates — would imply every guard is already a
  sensor, which OBPI-09 has not yet done).
- **Decision:** Treat the campaign checkbox update as the "Living: items check off
  with command evidence" mechanism, not an amendment.
  **Rationale:** § Authority & amendment distinguishes living check-offs (body,
  evidence-backed) from amendments (operator-ratified, appended to § Archive). A
  checkbox flip is the former.
  **Alternatives rejected:** Appending an Archive amendment block (reserved for
  doctrine changes, not progress check-offs).

## Immediate Next Steps

<!-- ADVISORY ONLY — propose to operator, do not execute without authorization. -->

1. **Confirm green floor:** run `uv run gz check` and verify it passes before
   opening new Movement I work (campaign green-floor inheritance rule).
2. **Pull Movement I item 2 — the MX lean kernel.** Decide with the operator which
   OBPI starts the enter/status/exit cluster (likely OBPI-0.0.74-04 `mx-enter`,
   then 05 `mx-exit-hard-gate`, with 03 `gate5_invariants` formal set as the floor
   they enforce). `uv run gz adr status ADR-0.0.74 --json` for the live OBPI grid.
3. **Or pull Movement I item 3 — the enforcement-claim meta-validator** (§5's
   mechanism, "the floor's teeth"). This is the cross-cutting primitive the MX exit
   gate and the antibody both depend on; sequencing it before the MX kernel may be
   the higher-leverage order — surface the tradeoff to the operator.
4. **Address the campaign's standing fix:** repair ADR-0.0.74's stub (non-live)
   fidelity assertions — scope this as its own GHI/OBPI when the kernel work
   reaches it.

## Pending Work / Open Loops

- **Movement I incomplete:** item 2 (MX kernel → `0.29.0` release) and item 3
  (meta-validator) open. `0.29.0` does not release until the MX lean kernel lands.
- **OBPI-0.0.74-09** (retire staging flags) is the guard-migration thread that
  completes "gates-as-sensors" in the per-guard sense — named in the item-1
  annotation, not yet scheduled.
- **V.I.B.E.S.-band routing** (NOTICE drain / INFO track / DEBUG steer) has named
  semantics but no mechanical dispatcher; the NOTICE "Chores drain" lands with the
  debt-aging / hardening OBPIs.
- Last published release: **0.28.1**. Next minor (`0.29.0`) is gated on the MX
  feature landing.

## Verification Checklist

- [ ] `uv run gz check` passes (green floor before new movement)
- [ ] `uv run gz obpi lock list` shows no active lock
- [ ] `git branch --show-current` == `main`, tree clean and synced
- [ ] `uv run gz adr status ADR-0.0.74 --json` shows 01/02/11/12 completed
- [ ] Campaign Movement I item 1 shows `[x]` in
      `docs/governance/build-to-1.0-campaign-2026-06-20.md`

## Evidence / Artifacts

- `docs/governance/build-to-1.0-campaign-2026-06-20.md` — Movement I item 1
  checked off with scope annotation (this session's Magna Carta update)
- `src/gzkit/mx/disposition.py` — the one level→route matrix handler (V.I.B.E.S.
  band encoded)
- `src/gzkit/mx/checkpoint.py` — `resolve()` level→route/AOG/advisory wire
- `tests/mx/test_disposition.py` — 5 tests, green
- `.gzkit/handoffs/20260622T092915Z-obpi-0-0-74-12-mx-gates-as-sensors-completed.md`
  — the OBPI-12 completion handoff (predecessor in this chain)
- `.gzkit/insights/agent-insights.jsonl` — `improvement` insight for the operator's
  V.I.B.E.S.-band refinement

## Environment State

Python 3.13+ via uv; gzkit on branch `main`, synced to `origin/main`. No feature
branch (operator directive). No active pipeline markers or OBPI locks. Last
published release 0.28.1; next minor `0.29.0` reserved for the MX feature.
