---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-18T07:22:45Z'
agent: claude-code
session_id: 8cb3c061-3787-4ff9-81da-3dcd93c5a8c0
continues_from: .gzkit/handoffs/20261118T005747Z-rp12-o3-task3-repaired-reviewed.md
---

## Current State Summary

RP-12 O3 task 4 is half built: its rulings, the dispatch's end, and the clearance authorized (writer and verb) are committed; the clear (writer and verb), the docs pass and the independent review remain. The operator ruled the predecessor handoff "proceed" (booked by gz handoff decide under this session). CI on a38024152 was green. The planning pass checked task 4 against the code and put four open questions one at a time, ruled as rulings 137 to 140, written onto the RP-12 page:
- 5c9ba7087: rulings 137 to 140 (out-of-position clear books an order block; clearance refused while the hanging dispatch is live; refusal 1 compares dispatch ids and the subagents that claimed them; a position found is off, advisory, recording or on), and ruling 136 added to the page's status line.
- b854b1c0c: dispatch_ended, booked by the stamp hook on SubagentStop from the stopping subagent's own transcript (ruling 115); SubagentStop is a generated, gzkit-owned settings phase.
- b6721ca4c: record_tag_clearance and dispatch_over, the tag_clearance_authorized event with its schema, corpus and probe.
- 941954f21: the speculative-verb marker on rulings 137 to 140, a defect the full unit tier caught that the per-change gz check missed.
- 9060059d9: gz wp tag authorize with its seven obligations, a behave scenario, the show view's clearance line and field, recaptured manpage examples, ruling 104's line at 38.
Pushed through 941954f21 (CI green on it); 9060059d9 rides this handoff's sync. The full unit tier passed at 9060059d9's tree (gz test exit 0).

## Important Context

- Safe mode (drydock) is open; MX session 57346836, lease renewed 2026-11-18T00:02Z for 24h; gz obpi lock list read the mx-session lock alone, active, 440 of 1440 minutes, held by claude-code-b5ddbaec. Every act is one commit with Task: TASK-rnd-repair-work-organization.
- Shift turnover: no tag is hung, issued or authorized in the live repository, no work package commenced, no finding awaits buy-back; every tag act ran in temporary test projects. Read: gz obpi lock list and the contract's list of discrepancies.
- Run uv run gz test (the full unit tier) before calling an act done: the per-change gz check missed tests/governance/test_cli_alignment_scope.py, which refuses a doc naming an unregistered gz verb unless the preceding line carries the gz-validate-skip command-shape marker. Read gz test's own exit code; an appended echo masked it once this session.
- Rulings 137, 139 and 140 still carry that marker because gz wp tag clear is not registered; remove each when the clear verb lands. Ruling 138's marker is gone.
- _EventBase overrides model_dump and ignores exclude; compare events by popping ts, as the hang tests do.
- The commit hook books mx_contract_amended when docs/governance/harbor-pilotage-candidate-2026-10-15.md (the safe-mode contract) changes; the row rides the next commit.
- Manpage EXAMPLES were captured by scratchpad scripts subclassing tests.commands.test_wp_tag._HungTagCase (the hang fixture's setUp, lifted this session) and invoking gz's main in-process, every example of a page from one run.
- gz check now reports three demoted guards (Tautological debt, Validate default scopes, tautological test audit), not the predecessor's four.

## Decisions Made

- [operator-ruled] Ruling on the predecessor handoff, booked by gz handoff decide (verbatim: "proceed").
- [operator-ruled] Ruling 137, an out-of-position clear books an order block written by the runtime and leaves the tag hung (by selection: "A: book an order block (Rec.)").
- [operator-ruled] Ruling 138, clearance refused while the hanging dispatch is live (by selection: "A: refuse while live (Rec.)").
- [operator-ruled] Ruling 139, refusal 1 compares dispatch ids and the subagents that claimed them (by selection: "A: ids and claiming agents (Rec.)").
- [operator-ruled] Ruling 140, a position found is off, advisory, recording or on (by selection: "A: hung positions + on (Rec.)").
- [operator-ruled] Push the four commits through 941954f21 (verbatim: "push now").
- [operator-ruled] Write a fresh handoff and git sync (verbatim: "write handoff, git sync").
- [agent-chose] Did not put the order states for clearance to the operator: rulings 59, 132 and 135 settle them (commenced, unblocked, a stopped order included).
- [agent-chose] SubagentStop reads the dispatch line from agent_transcript_path, as the SubagentStop probe record states, not from claim rows, since a foreground claim is booked after SubagentStop.
- [agent-chose] dispatch_over reads an end before a void when both name the dispatch.
- [agent-chose] Fixed in flight the marker-not-on refusal shared by every tag verb, which ended "then issue the tag" whatever the act.
- [agent-chose] Recaptured the whole show manpage EXAMPLES in one run rather than hand-editing observed output.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's id.
2. Read CI on the synced HEAD (gh run list --workflow CI --limit 1); if check is red, repair it first.
3. Build the clear writer in src/gzkit/mx/tag_out.py: record_tag_clear on a tag whose clearance is authorized, the stamped call of a live Restoration dispatch on the tag's commenced, unblocked order; refusal 1 by dispatch id and by any subagent that claimed both the hanging and the clearing dispatch (ruling 139); --position-found from off, advisory, recording or on (ruling 140); a position other than the hung one books one work_package_blocked on the order, its reason and decision written by the runtime, exit 3, the tag still hung (ruling 137); a cleared tag reads closed (ruling 129). Tests in tests/test_tag_out.py, then the commit witness.
4. Build gz wp tag clear with its seven obligations, a behave scenario, the show view's clear, ruling 104's count, and the markers on rulings 137, 139 and 140 removed.
5. The docs pass (the kit's Mode Contract rows for authorize, clear and the SubagentStop end; witness floor rows 1 and 6), then an independent review of task 4 before pushing; then O3 tasks 5, 6 and 7.

## Pending Work / Open Loops

- The tag clear is not built: refusal 1 and ruling 137's block are unwitnessed until it lands.
- The check-then-append races of the tag issue, hang and clearance are stated as limits; no refusal holds two concurrent writers apart.
- A killed subagent fires no SubagentStop; its dispatch reads live until the coordinator voids it (ruling 118), and a harness without the hook, Codex among them, leaves every dispatch live (ruling 115's limit).
- Ruling 104's RP-11 line holds 38 untagged held tests, cleared when RP-11's intake admits REQs, before gz mx exit.
- The IDE's newer ty reports unresolved-attribute renamed to missing-attribute at 15 ignore comments; the pinned ty 0.0.92 does not; it belongs to the next ty upgrade.
- Carried: gz mx renew books no expiry for a lease that lapsed mid-session (O3 task 6); GHI #1266 (canaries leave the kernel checker unmutated); the MX session's advisory debt; open siblings #1314 and #1316.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.
- uv run gz test passes (13,918 tests at 941954f21; more at 9060059d9).
- uv run -m unittest tests.test_tag_out tests.test_dispatch_stamp_hook tests.commands.test_wp_tag tests.test_hooks tests.test_ledger_producer_probe passes.
- uv run gz validate --hexagon-tests reports 76 findings, 38 tests, the count ruling 104's line carries.
- uv run gz validate --cli-alignment --skill-alignment passes.
- uv run gz handoff rulings --search "book an order block" returns ruling 137.
- uv run gz obpi lock list shows the mx-session lock alone.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-contractor-kit.md` (rulings 137 to 140)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (ruling 104's line at 38)
- `src/gzkit/dispatch_stamp.py`
- `src/gzkit/hooks/claude.py`
- `src/gzkit/hooks/scripts/dispatch.py`
- `src/gzkit/work_package_run.py`
- `src/gzkit/mx/tag_out.py`
- `src/gzkit/commands/wp_tag.py`
- `src/gzkit/cli/parser_wp_tag.py`
- `src/gzkit/events.py`
- `tests/test_dispatch_stamp_hook.py`
- `tests/test_tag_out.py`
- `tests/commands/test_wp_tag.py`
- `docs/user/manpages/wp-tag-authorize.md`
- `docs/user/manpages/wp-tag-show.md`
- `.gzkit/skills/gz-wp/SKILL.md`

## Settled Rulings

2316 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
