---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-04T00:12:36Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: ececdaf1-3c3d-4f6c-98f5-62562647485e
continues_from: .gzkit/handoffs/20261003T234832Z-obpi-10-trial-implemented-two-blockers-before-rulings.md
---

## Current State Summary

This session resumed the predecessor handoff, checked its claims against live state, and did not work its advised steps: the operator's ruling was booked as hold. At the operator's direction the session then took a gate-by-gate read of which gates have caught something a plain test run would have missed, saved it as a dated record with a tally script, and synced it as commit 304680d1b. OBPI-0.35.0-10 is unchanged from the predecessor: implemented, tests green, not complete, not attested, and its lock is still held by claude-code-a0f543a5. No source, test, rule, skill or hook file was edited, and no control surface was disabled. One defect insight was recorded, about the verifier-pipe-gate hook refusing help calls.

## Important Context

What the read found, in short; the record holds the table and its limits. Three things have a recorded history of catching defects that green tests missed: the plain checks (lint, typecheck, unit suite, behave, strict docs build), the cross-vendor Codex adversary, and the operator's own directed audits. Brief reconcile, the ADR evaluation, both airlock doors, enforcement-claim verification, audit generation and the plan audit show either no non-pass at all, non-passes about their own paperwork, or no verdict history. The spec reviewer is mixed and the quality reviewer is low yield. Eleven completions recorded as attested were later repudiated, and no repudiation reason names a gate as what found it. Hooks and the gz validate scopes have no failure history in the ledger, so their catches could not be counted. The counts come from the tally script; the judgment of what each non-pass caught is one agent's reading of truncated finding text and is labelled as such in the record. Variances found when the predecessor's claims were checked: its claims about sync, lock, status, tests, the retention validator and the two failing precomplete checks all verified. It understated one thing: the acceptance record has no reviews at all, so every one of the ten proofs carries the blocker 'lacks accepted adversarial review', not only REQ-0.35.0-10-10. Whether the human-review operation of gz obpi acceptance discharges that blocker was not verified. The plan-audit receipt also lists scope collisions with sibling OBPIs 0.30.0-03, 0.27.0-03 and 0.39.0-03, which the predecessor did not mention. By code reading only, gz obpi complete does not consult the plan-audit receipt; the FAIL check is in the pipeline launch command. The support-citation misparse behind REQ-0.35.0-10-10 is the same defect an insight of 2026-09-25 recorded against OBPI-0.35.0-14. Operator statements this session, verbatim, recorded as concerns and not as rulings: "the real story is the shameful bloat that the obpi-0.35.0-10 revealed. gzkit is a shambles." and "I am tempted to disable almost all control surfaces and use combinations of goal and loop. it is abysmal. direly so." The operator has not ruled to disable anything. Workflow fronts (source: the campaign plan, Workflow fronts section). Handoff system: the resume was run and booked as hold, and this handoff was written; the lineage walk hit its depth bound and the ancestors were not read this session. GHI triage: not run. ADR/OBPI campaign: OBPI-0.35.0-10 on hold as above; the landed count of ADR-0.35.0 did not change and is read from gz adr status. New R&D: not touched; the gate-value record is a measurement, not an R&D run.

## Decisions Made

- [operator-ruled] Take the gate-by-gate read instead of the predecessor's advised steps (verbatim: "do the gate-by-gate read - I am tempted to disable almost all control surfaces and use combinations of goal and loop. it is abysmal. direly so.").
- [operator-ruled] Save the gate-by-gate read as a record (verbatim: "save it").
- [operator-ruled] Sync the saved record (verbatim: "git sync").
- [operator-ruled] Write a handoff and sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] Booked the gate-read ruling on the predecessor handoff under the decision category hold; the category is the agent's reading, the words are the operator's.
- [agent-chose] Saved the read as a directory holding a record and a tally script, following the layout of the 2026-10-03 run-cost evidence; the operator asked only that it be saved.
- [agent-chose] Corrected three statements between the spoken read and the saved record: the red-commit witness is marked unclear, not untrustworthy; the repudiations are attributed as their reasons state; and the completions are described as recorded complete, since one carried an attestation never given.
- [agent-chose] Left OBPI-0.35.0-10, its brief, its proofs and its lock untouched.
- [agent-chose] Did not read the 552 improvement insights or the 19 ancestor handoffs.

## Immediate Next Steps

1. Show the operator the table in the gate-value record and ask for a ruling on the apparatus: which control surfaces to keep, which to disable, and whether the kept core is the plain checks, one Codex adversary pass on the diff and the human attestation. Disable nothing without that ruling.
2. Ask the operator whether to close OBPI-0.35.0-10-classification-reader-and-ownership or let it lapse. Its lock was claimed at 2026-10-03T12:35Z with a 24 hour TTL, so a session starting after 2026-10-04T12:35Z will find it expired and reapable. Closing it needs the operator's rulings on the REQ-0.35.0-10-10 witness wording and on the plan audit, then the human-review judgment and the attestation in the operator's own words; never author either.
3. Before step 2's human-review, confirm from code or a run whether the human-review operation of gz obpi acceptance clears the 'lacks accepted adversarial review' blocker that all ten proofs carry.
4. Ask the operator how to reconcile the six scorecard rows whose class disagrees with their corpus entry: reclassify the corpus entries or rescore the rows.
5. If the OBPI is completed, re-run the run-cost script for session a0f543a5-5dc2-41ff-949b-f036f79ce0a1 and add the trial's figures to the run-cost evidence README beside the baseline.

## Pending Work / Open Loops

Not measured by the read and still open: the token cost of the Codex adversary; the catches of the hooks and of the gz validate scopes, which leave no failure history; and the 552 improvement insights. Unreviewed by the operator, carried from the predecessor: mandatory source attribution on every scorecard row, the disagreement-as-advisory reading, the 31 hand-mapped rows, and the requote of Local Agent Rules row 8. An independent reviewer session on the OBPI-0.35.0-10 diff was suggested two sessions ago and has not been run. The brief's evidence sections are unfilled. The gz-obpi-pipeline skill is unedited and the operator has not ruled on what changes. The six findings the predecessor recorded as insights are unrepaired. The predecessor's other open loops stand as written there.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after the sync. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. uv run gz obpi lock list: expect one ACTIVE lock held by claude-code-a0f543a5 until 2026-10-04T12:35Z, and no active lock once a later session has reaped it. uv run gz obpi precomplete OBPI-0.35.0-10-classification-reader-and-ownership: expect exit 3 with plan_audit_receipt and adversarial_validation failing. uv run gz obpi acceptance OBPI-0.35.0-10-classification-reader-and-ownership status --stage stage4 --json: expect ready false, an empty reviews list and twelve blockers; a changed input digest means the proofs must be re-run. uv run python docs/governance/gate-value-read-2026-10-03-evidence/gate_value_tallies.py: expect JSON whose plain-check, reviewer and verdict counts match the record, allowing for rows added since. uv run -m unittest tests.governance.test_bullet_retention: expect 52 tests OK. uv run gz validate --bullet-retention: expect exit 0 with six advisory lines.

## Evidence / Artifacts

Files written this session: `docs/governance/gate-value-read-2026-10-03-evidence/README.md`, `docs/governance/gate-value-read-2026-10-03-evidence/gate_value_tallies.py`, `.gzkit/insights/agent-insights.jsonl`. Commit 304680d1b carries the record, the script and two ledger rows. Read and cited: `docs/governance/gate-witness-audit-2026-09-30.md`, `docs/governance/obpi-run-cost-2026-10-03-evidence/README.md`, `.gzkit/ledger.jsonl`. Predecessor: `.gzkit/handoffs/20261003T234832Z-obpi-10-trial-implemented-two-blockers-before-rulings.md`, whose resume decision is booked as hold with the operator's words under session ececdaf1-3c3d-4f6c-98f5-62562647485e.

## Settled Rulings

1298 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
