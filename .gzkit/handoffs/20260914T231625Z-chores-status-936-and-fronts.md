---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-14T23:16:25Z'
agent: claude-code
session_id: 863d2b33
continues_from: .gzkit/handoffs/20260914T115538Z-cited-approvals-994-and-fronts.md
---

## Current State Summary

Session 863d2b33 resumed `20260914T115538Z-cited-approvals-994-and-fronts.md` (ruling booked: proceed, option (a), with (b) and (c) set aside). It fixed GHI #936 (chores-revamp step 2) in `5d39afd99`, synced it, and closed the issue with evidence.

- `gz chores status [--json]` reports every chore as overdue, due, unmeasured, paused or current without running any chore, and exits 0 in every band. Session orientation calls it out-of-process and shows `## Chores due or overdue` only when a chore is due or overdue.
- `staleness.surfaces` is now part of the chore declaration: required for content-delta chores and refused for any other signal. All 30 content-delta chores declare it, each read from its CHORE.md and the commands its criteria run. `scripts/check_proof_freshness.py` lost its own five-chore surface map and reads the declaration instead.
- Board at landing: 35 overdue, 1 due, 3 unmeasured (accumulated-work), 0 paused, 1 current.
- An independent spec review returned PASS-WITH-NOTES. Its one blocking item was not a contract violation, but it led to a real defect in #935's remedy, and #935 is reopened.
- Found along the way and filed: #1009 (accumulated-work counters), #1010 (structlog writes to stdout and corrupts `--json`), #1011 (4 CHORE.md files name things that do not exist). #935 reopened (the interval gate cannot be cleared by running the chore). Two insights recorded.

At authoring: HEAD `5d39afd99`, level with origin/main, no OBPI locks.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** unchanged. This resume put the standing fronts to the operator as live options, as the prior insight asked.
- **ghi triage:** #936 closed (`5d39afd99`). Opened #1009, #1010 and #1011. Reopened #935. #983 and #894 are still waiting on rulings; #1008 is still unselected.
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 is still topmost.
- **new R&D:** not worked. The step-4 skill design from `20260912T235557Z` and the R&D-front amendment text are still undone.

### Chores front state (verified this session)
- Revamp steps 1-6 have all landed; step 2 is `5d39afd99`. The 35-overdue board is the full-red case `docs/governance/chore-class-system.md` § Graded bands predicted. `staleness.paused` is the operator's lever for it, and no chore is paused today.
- **#935 deadlock (live):** criterion 1 of an elapsed-time chore only passes when the newest PASS block is within `periodDays`. `gz chores run` writes a PASS block only when every criterion passes, and a FAIL block never counts. So once a chore is past its period, running it cannot clear it. `control-surface-permission-consent-drift` is in that state now (36d against a 30d period). `frontier-model-card-currency` reaches it on 2026-10-12.
- Signal fit, recorded as insight `chores/staleness-signal-fit`: `quality-check` surfaces cover nearly the whole repo, so it is always due. `memory-hygiene`'s real subject (the agent memory directory) sits outside the repo, so its declared surfaces cover only its invariant-coherence arm. Changing either signal is the operator's calibration.

### Gotchas carried
- The verifier-pipe gate refuses `ruff format .` followed by another statement. Run it alone and read `$?` immediately afterwards.
- Registry JSON must be rewritten with `ensure_ascii=True`. The file uses `§` and `—` escapes, and writing it without that setting rewrites 20 lines.
- In the package-fallback path, a structlog resolver log reaches stdout ahead of the JSON (#1010). Inside this repo the project overlay resolves first, so orientation is unaffected.
- `.claude/agents/*.md` bodies are hand-maintained. `gz agent sync control-surfaces` renders only `.codex/agents/*.toml`.

## Decisions Made

- [operator-ruled] Resume ruling on `20260914T115538Z`: "(a) Chores step 2 (Recommended)". R&D skill design and the next presence/family-A member set aside.
- [operator-ruled] GHI #936 unmeasured-chore handling: "Declare content-delta (Recommended)". Add `staleness.surfaces`, declare it for all 30 content-delta chores in this fix, report accumulated-work as an explicit `unmeasured` band, and file a GHI for counters (#1009). Two alternatives were set aside: an unmeasured band plus a GHI for the 28, and keeping the surface map in the script.
- [agent-chose] Status verb exits 0 in every band. Canon already settles this: step 2 of the implementation order says "Announces; never gates".
- [agent-chose] The content-delta run witness is the CHORE-LOG PASS block, not a proof commit date. 25 of 30 chores keep no proof except the log, and the log's commit date moves on a FAIL run.
- [agent-chose] Reopened #935 instead of filing a new GHI. The interval-gate deadlock is a regression in #935's own remedy.
- [agent-chose] Declared broad surfaces for `quality-check` and partial ones for `memory-hygiene` as the ruling required, and flagged both for signal recalibration by insight rather than changing either signal.

## Immediate Next Steps

1. Put the next move to the operator with the standing fronts as live options: (a) #935, the interval-gate deadlock repair, which is live on `control-surface-permission-consent-drift` and needs a witness-shape reading; (b) the 35-overdue board, where the operator decides which chores to declare `staleness.paused` and whether to recalibrate `quality-check`/`memory-hygiene` to elapsed-time; (c) R&D skill design per `20260912T235557Z` step 4 plus the campaign R&D-front amendment; (d) a short direct fix: #1010 (structlog stdout) or #1008.
2. If (a): read `scripts/check_proof_freshness.py` `_check_scan_interval`, `src/gzkit/commands/chores.py` `chores_run`, and the #935 reopen comment's closure contract first.
3. If (b): run `uv run gz chores status` for the live board. Pausing a chore is a registry declaration edit under the chore class system, and it syncs via `gz agent sync control-surfaces`.
4. If (d): #1010's contract says `--json` stdout carries only JSON. `configure_logging` in `src/gzkit/cli/logging.py` is defined but never called.

## Pending Work / Open Loops

- GHI #935 (reopened: interval-gate deadlock), #1009 (accumulated-work counters), #1010 (structlog stdout), #1011 (CHORE.md drift), #997, #808 (chores); #983, #894 (presence, ruling-gated); #969 open by ruling; #968 open; #1008 open, unselected.
- Insights awaiting operator calibration: `chores/staleness-signal-fit`; `cli/manpage-flag-claims` (`gz cli audit` does not check flag claims inside group manpages).
- R&D: skill design session, campaign R&D-front amendment text, `.out-of-scope/` ratification.
- Carried: `src/gzkit/commands/obpi_stages.py` BASELINE_VERIFICATION prescribes `uv run -m unittest -q` rather than the canonical step; three live justify-binding violations; 83 enforcement claims population-undeclared, 55 exemption-undeclared.

## Verification Checklist

```bash
git status -sb
git rev-list --left-right --count origin/main...HEAD
gh issue view 936 --json state
gh issue view 935 --json state
uv run gz obpi lock list
uv run gz chores status
uv run python scripts/check_proof_freshness.py control-surface-permission-consent-drift
uv run -m unittest tests.commands.test_chores_staleness tests.commands.test_chores_status tests.commands.test_chores_declaration
uv run gz handoff rulings --search "Declare content-delta"
```
Expected: level with origin/main; #936 CLOSED; #935 OPEN; no active locks; the board renders and exits 0; the permission-consent-drift gate exits 3 (the deadlock that #935 reopens); tests green; the #936 ruling in the store. Re-run rather than trust.

## Evidence / Artifacts

- `.gzkit/handoffs/20260914T115538Z-cited-approvals-994-and-fronts.md` (predecessor).
- `src/gzkit/commands/chores_staleness.py`, `src/gzkit/commands/chores_status_cmd.py`, `src/gzkit/commands/chores_declaration.py`, `scripts/check_proof_freshness.py`, `scripts/session_orientation.py`.
- `.gzkit/chores/registry.json`, `.gzkit/chores/README.md`, `.gzkit/rules/chores.md`, `.gzkit/skills/gz-chore-runner/SKILL.md`.
- `tests/commands/test_chores_staleness.py`, `tests/commands/test_chores_status.py`, `tests/governance/test_scan_interval_gate.py`, `features/chores_status.feature`.
- `docs/user/manpages/chores-status.md`, `docs/governance/chore-class-system.md`.
- `artifacts/receipts/arb-ruff-8eefc6dfc35b4d8a8499254502033349.json`, `artifacts/receipts/arb-step-unittest-62957f0a2a624062ae0786e46ff5a48d.json`.
- Commit `5d39afd99`; GHI #936 close comment and correction; GHI #935 reopen comment.

## Settled Rulings

863 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
