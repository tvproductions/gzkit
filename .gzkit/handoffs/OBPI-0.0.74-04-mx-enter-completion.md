---
mode: CREATE
adr_id: ADR-0.0.74
obpi_id: OBPI-0.0.74-04-mx-enter
branch: main
timestamp: "2026-06-25T11:30:00+00:00"
agent: claude-code-ce4198e6
session_id: ce4198e6-757c-44d1-a384-f05a7d471066
last_lock_event_timestamp: "2026-06-25T10:52:43.259516+00:00"
last_commit_sha: a658abdbb16ee6f45a71fdfcbaf6ebe9e2c7a61f
---

# OBPI-0.0.74-04-mx-enter Completion Handoff

## Current State Summary

`gz mx enter` landed and is operator-attested complete (g0, "attest completed").
ADR-0.0.74 Decision item #4: the operator opens the Maintenance Hangar door — the
tool sets the marker, writes one `mx_session_opened` ledger event, captures the
inspection scope, acquires the `lock_manager` token rail (`mx-session`), and fails
closed on empty/whitespace reason or attestor and on an already-active marker. The
agent can never open the hangar autonomously.

## Important Context

- Prereqs OBPI-01 (marker) and OBPI-02 (checkpoint) were already Completed; this
  OBPI is the door that writes them.
- `mx_session_opened` event builder is module-local in `mx_cmd.py` because
  `ledger_events.py` is outside this brief's allowlist (deliberate constraint).
- Brief allowlist was under-declared for standard new-command surfaces; in-flight
  amendments (all operator-attested at Stage 4): `config/doc-coverage.json`,
  `src/gzkit/governance/trust_audits/cli.py` (`_NO_SKILL_VERBS` waiver),
  `docs/user/manpages/mx-enter.md` (per-subcommand manpage the CLI audit requires),
  and both runbooks.
- Process note: the RGR red on first pass was an import error; assertion-level red
  verified retroactively via a stub negative control. The RGR discipline was then
  adopted into the `gz-obpi-pipeline` skill (v6.23.0) this session.

## Decisions Made

- SUPPORT REQ-04-05 proof channel is `gz validate --cli-alignment` exit 0 +
  `artifact_edited` event; the validator side is green, the ledger event writes at
  git-sync (correct sequencing, not a gap).
- Lock identity is the singleton `mx-session` key on the existing lock_manager rail
  (not a hand-rolled lock), satisfying REQ-04-04.

## Immediate Next Steps

- Stage 5 sync #1 (governance edits), reconcile, ADR status refresh, sync #2.

## Pending Work / Open Loops

- Remaining ADR-0.0.74 OBPIs per the Build-to-1.0 campaign: OBPI-05 (mx exit hard
  gate), OBPI-06/07/08 (log, awareness hook, skill+rule), and the leveled-substrate
  / meta-validator organs (11–20). The `gz-mx` skill that will wield `gz mx enter`
  is a later ADR-0.0.74 deliverable (waiver recorded in `_NO_SKILL_VERBS`).

## Verification Checklist

- Full suite 6502/6502 (`arb-step-unittest-b001fce829804af6aa93a3e9711d8397`)
- Lint clean (`arb-ruff-d21c2a32b0b24830a8cfd18999298a9f`)
- Typecheck clean (`arb-step-typecheck-d2cb9df116844a6db9b9bf7b6e7492e6`)
- Docs build clean (`arb-step-mkdocs-45e84a7ca174443bb60f6ead1e930051`)
- CLI audit 111/111; `gz validate --documents` clean; precomplete 8/8 READY

## Evidence / Artifacts

- Brief: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-04-mx-enter.md`
- Created: `src/gzkit/commands/mx_cmd.py`, `docs/user/manpages/mx.md`,
  `docs/user/manpages/mx-enter.md`, `tests/commands/test_mx_enter.py`
- Stage-4b adversary verdict: REFUTED-WITH-CAVEATS (both caveats resolved at Stage 5)
