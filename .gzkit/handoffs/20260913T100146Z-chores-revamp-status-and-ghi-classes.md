---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-13T10:01:46Z'
agent: claude-code
session_id: edd8e9ad-30da-4e2d-a24a-da2b89654f14
continues_from: .gzkit/handoffs/20260913T090956Z-chore-authority-sync-and-rung-conformance.md
---

## Current State Summary

Session edd8e9ad resumed `20260913T090956Z-chore-authority-sync-and-rung-conformance.md` (Fresh; every claim verified — origin level, no locks, GHI states as stated, named tests 29/29, distribution exit 0). Ruling booked with `gz handoff decide`: proceed on #999 step 4 then #1004; #1006, #936 and the R&D skill design set aside.

Landed and pushed to main (HEAD `2910a30a8`, level with origin, clean tree):
- `16caf8392` — GHI #999 step 4: `src/gzkit/chores/README.md` states what a chore is, the admission criterion, the five classes, the four rungs and the declaration requirement; `tests/governance/test_chore_readme_class_contract.py` holds the class/rung tables to the code. #999 stays open for steps 5–6.
- `2910a30a8` — GHI #1004 CLOSED: `gz handoff decide` prints `<decision> — <handoff> (session <id>) recorded` for all four decisions; help, refusals, docstrings, `handoff-decide.md`, `handoff-authorize.md` and the operator runbook no longer describe the retired gate. #805's witness `RetiredGateProseTests` widened (more spellings, now scans `docs/user`) — #1004 was #805 recurring.

Operator asked mid-session why every implementation run produces new GHIs. Answered with a class grouping of the 50 open GHIs (see Important Context). No GHIs filed this session.

## Chores revamp — status at a glance

The operator reported the revamp's progress is hard to read from handoffs. Plan: `docs/governance/chore-class-system.md` § Implementation order (ratified 2026-09-12). Work orders: GHI #999 (steps 1, 3–6), GHI #936 (step 2). **No chore's behaviour has changed yet: `gz chores list` reports 40 of 40 chores carry no class declaration.**

| Step | Status |
|---|---|
| 1. Registry schema (class, rung, idempotent, staleness, remediation, nonAuthority, governingRule) | DONE `f1c9b0e59` |
| 2. `gz chores status` indicator + orientation announcement | NOT STARTED — #936, set aside at two resume rulings |
| 3. Rung-conformance validator (workflow step stages ≤ rung) | DONE `6615d0a18` |
| 4. README: what a chore is, classes, rungs, admission | DONE `16caf8392` |
| 5. Declare all 40 chores; fix self-contradictory and stop-at-data chores; calibrate control-surface five individually; flip undeclared → refusal | NOT STARTED — the step that changes chore behaviour |
| 6. Suppression prohibition as rule text with its witness | NOT STARTED |

Supporting fixes done: #1002 (CHORE.md cites JSON authorities, `e2d31cbac`), #1005 (surface-level files ship, `84d3e23c8`).

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system** — #1004 closed (`2910a30a8`). #1003 open for Movement D's ruling identity. #870 untouched. The operator finds the chores revamp hard to follow across per-session handoffs; this handoff carries a step table in Current State Summary for that reason.
- **ghi triage** — class grouping run (read-only, below); no rank deliverable produced, no GHIs filed or closed other than #1004.
- **adr/obpi campaign** — no OBPI work (IRON LAW), no locks. ADR-0.35.0 remains TOPMOST, untouched.
- **new R&D** — not worked; set aside.

### Why GHIs keep regenerating — class grouping of the 50 open GHIs (2026-09-13)
Read from each issue's `## Class of failure` section; grouping is agent judgment, counts exact. 85 GHIs filed since 2026-08-30; 26 of the 50 open were opened before 2026-09-01.
- **A. A witness covers less than its claim** (one member of a set, presence not content, a different domain) — 27: #803 #810 #799 #939 #851 #889 #894 #907 #921 #922 #926 #927 #956 #1006 #998 #983 #950 #996 #994 #808 #997 #936 #815 #919 #995 #969 #971.
- **B. One fact on many surfaces; a change reaches some** — 9: #1004 (now closed) #934 #943 #837 #978 #1003 #802 #818 #999.
- **C. One half built, the other not** (no reversal, no consumer, unwired parameter) — 14: #930 #611 #973 #594 #870 #807 #766 #813 #767 #804 #871 #832 #993 #968.
Reading: family A regenerates, and instance fixes feed it — each fix tends to add a witness scoped to the instance (#805 → #1004). Agent recommendation, NOT ruled: work family A as a class (every witness declares its population; one shared check compares declaration to the real population) under the campaign's Movement C `doctrine-declared-without-mechanism` box.

### Gotchas learned
- The stop hook lints dirty Python at turn end; `gz check` started before a lint fix will fail on it — re-stage and re-run.
- `gz validate --tautological-test-audit` refuses `assertTrue(path.is_dir())`; assert non-vacuity through content (e.g. the scanned list contains the file) instead.
- Rich wraps console output at 80 columns; compare rendered lines after whitespace normalisation.
- The verifier-pipe gate refuses `ruff`/`unittest` followed by another statement; read `$?` immediately or split commands.

## Decisions Made

- [operator-ruled] Resume ruling on `20260913T090956Z`: "#999 step 4, then #1004 (Recommended)" — #1006, #936 and the R&D skill design set aside for this session.
- [operator-ruled] Asked why every implementation run yields new GHIs, then: "Finish #1004, then class triage (Recommended)" — commit #1004, then a read-only class grouping of the open queue, no new filings.
- [agent-chose] Held the README's class and rung tables to `ChoreClass` and the audit's ladder order with a test, because the README restates code-owned values and #1002 measured exactly that shape drifting.
- [agent-chose] Widened #805's `RetiredGateProseTests` inside #1004 instead of filing a sibling GHI, since #1004 was #805 recurring through the witness's narrow phrase list and `src/`-only scope.
- [agent-chose] Replaced the handoff-decide manpage example with output captured from a scratch project, never booking a demo ruling into this repo's ledger.
- [agent-chose] Did the class grouping by reading each GHI's Class of failure section from the `ghi-triage` Step 1 fetch; the skill ranks by severity and has no class view, so no rank deliverable was rendered.

## Immediate Next Steps

1. Put the next chores-revamp move to the operator (asked at session end, declined before an answer — not ruled): step 5 declarations (agent recommendation), step 2 `gz chores status` (GHI #936), or pause the revamp.
2. If step 5: read GHI #997 and GHI #808 first, clear GHI #1006 (8 unresolvable `gz` chains in 4 chores) alongside, calibrate the control-surface five with the operator one at a time, then flip an undeclared chore from warning to refusal.
3. Put the family-A recommendation to the operator: work "a witness covers less than its claim" (27 of 50 open GHIs) as one class under the Movement C box rather than by instance.
4. Set-aside items awaiting operator initiation: GHI #1006, GHI #936, the R&D skill design.

## Pending Work / Open Loops

- GHI #999 steps 5–6: per-chore declarations with a stage on every workflow step, the absence→refusal flip, and the suppression rule with its witness.
- GHI #936 (step 2, status verb) — set aside.
- GHI #1006 — chore docs outside the cli-alignment scan — set aside this session.
- GHI #997 and GHI #808 are open against chores that step 5 must declare.
- Stale proofs: `control-surface-permission-consent-drift` and `control-surface-skill-rule-reachability` fail their freshness criterion; their audits need re-running before `gz chores run` goes green.
- complexity-reduction-xenon's post-cluster mode waits on the `.gzkit/rules/pythonic.md` threshold ruling.
- Mutation evidence gaps, disclosed: the stageless and unknown-stage guards in `audit_chore_rung_conformance` are observed only as crashes when removed.
- `RetiredGateProseTests` is still a phrase list: it catches the spellings it names, never a new one (stated limit, family A).
- GHI #1003 stays open until Movement D's typed ruling event; GHI #870 and GHI #810 untouched.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
gh issue view 999 --json state,title
gh issue view 1004 --json state,title
gh issue view 936 --json state,title
gh issue view 1006 --json state,title
uv run gz chores list
uv run -m unittest tests.governance.test_chore_readme_class_contract tests.test_handoff_cli tests.governance.test_handoff_resume_gate
uv run gz handoff rulings --search "then #1004"
```

Expected at authoring: 0 0; no active locks; #999, #936, #1006 OPEN; #1004 CLOSED; `gz chores list` reports 40 of 40 chores undeclared; tests green; the resume ruling found. Re-run rather than trust these.

## Evidence / Artifacts

- `src/gzkit/chores/README.md`, `.gzkit/chores/README.md` — What a Chore Is, The Five Classes, The Four Rungs (GHI #999 step 4).
- `tests/governance/test_chore_readme_class_contract.py` — README tables held to `ChoreClass` and the rung ladder.
- `docs/governance/chore-class-system.md` — step 4 recorded as landed.
- `src/gzkit/commands/handoff.py`, `src/gzkit/cli/parser_handoff.py`, `src/gzkit/events.py`, `src/gzkit/session_start.py` — retired-gate prose removed (GHI #1004).
- `docs/user/manpages/handoff-decide.md`, `docs/user/manpages/handoff-authorize.md`, `docs/user/runbook.md` — decide documented as a record that gates nothing.
- `tests/test_handoff_cli.py` (`TestHandoffDecideRendering`), `tests/governance/test_handoff_resume_gate.py` (`RetiredGateProseTests` widened).
- Commits `16caf8392`, `2910a30a8`; GHI #999 comment on step 4; GHI #1004 closure comment.

## Settled Rulings

836 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
