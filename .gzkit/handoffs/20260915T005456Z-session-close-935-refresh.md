---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-15T00:54:56Z'
agent: claude-code
session_id: 863d2b33
continues_from: 20260915T001007Z-chore-scan-record-935-and-fronts.md
---

## Current State Summary

Refresh of `20260915T001007Z-chore-scan-record-935-and-fronts.md` at session close; nothing changed after it except its own sync commit `17bfc4315`. Session 863d2b33 resumed `20260914T231625Z-chores-status-936-and-fronts.md` (ruling booked: proceed, option (a); (b), (c), (d) set aside). It fixed the reopened GHI #935 interval-gate deadlock in `7e306e4cb`, synced it to origin/main, and closed #935 with evidence.

- The elapsed-time gate in `scripts/check_proof_freshness.py` and `gz chores status` now date a chore that declares `staleness.artifacts` by that scan record's last change, never by `CHORE-LOG.md`. The PASS-block witness was circular, because the gate is a criterion of the run that writes PASS blocks. It was also bypassable, because a bare run inside the period pushed the clock back.
- `staleness.artifacts` is repo-relative, elapsed-time only, and refuses `CHORE-LOG.md`, directories and globs. An uncommitted edit reads as now; a deleted record never does. A gated elapsed-time chore with no declared record is refused with exit 1.
- Declared for the two gated chores: permission-consent-drift reads `proofs/summary.md`, and frontier-model-card-currency step 5 now writes `proofs/scan-record.md` (chore 1.3.0).
- An independent spec review returned PASS-WITH-NOTES. Its directory/glob hole was fixed in the same commit. Mutation sweep: 8 of 8 killed, conclusive. `gz check` exit 0.

At authoring: HEAD `17bfc4315`, level with origin/main, clean tree, no OBPI locks. Board re-read: 36 overdue, 1 due, 3 unmeasured, 0 paused, 0 current.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** unchanged.
- **ghi triage:** #935 closed (`7e306e4cb`). #934 is still open (frontier Mythos-tier drift). #1009, #1010, #1011 and #1008 are open; #983 and #894 still await rulings.
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 is still topmost.
- **new R&D:** not worked.

### Chores front state (verified this session)
- Board after the fix: 36 overdue, 1 due, 3 unmeasured, 0 paused, 0 current. frontier-model-card-currency moved from current to overdue by design: no scan record exists until its next scan writes `proofs/scan-record.md`. Its last real scan (2026-09-02, routed to #934) predates the record, and seeding one would fabricate a record.
- The permission-consent-drift gate exits 3 (last scan 2026-08-09). Recovery is its steps 1-5, which rewrite the dated `summary.md`, then `gz chores run`. It also lacks `proofs/settings-patch.md`, which its acceptance requires.
- New insight `chores/staleness-gate-class-fit` (plus a count correction): § Indicator, not gate lets only the Currency class gate, yet the conformance-class permission-consent-drift chore gates on elapsed time and five coherence chores gate on content-delta proof freshness.

### Gotchas carried
- `gzkit.mutation_witness` needs `-v` in the test command, and a test that prints to stdout mid-run breaks its parser. Capture that output in the test fixture.
- The tautological-test audit in `gz check` refuses a test that reads a repo file with `read_text` and asserts on its content.
- The verifier-pipe gate refuses a unittest run piped into `tail`. Write to a log and read the exit status immediately.
- Registry JSON edits were textual insertions, to keep the file's escapes and layout.

## Decisions Made

- [agent-chose] Refreshed rather than amended: the predecessor's two operator rulings (the resume ruling and "Declare it (Recommended)") are already booked in `.gzkit/handoffs/rulings.jsonl` and carried by `continues_from`, so they are not restated here (GHI #1003).
- [agent-chose] Newest change among declared records dates the scan, not every record: an identically regenerated file makes no commit, so requiring every record to change would re-create a deadlock.
- [agent-chose] Did not seed `scan-record.md` for frontier-model-card-currency; the chore reads overdue until a genuine scan writes it.

## Immediate Next Steps

1. Put the next move to the operator with the standing fronts as live options: (a) the frontier-model-card-currency scan, an operator-initiated chore run that writes `proofs/scan-record.md` and re-checks the drift #934 tracks; (b) the 36-overdue board, where the operator decides which chores to declare `staleness.paused` and whether to recalibrate `quality-check`/`memory-hygiene`; (c) a ruling on insight `chores/staleness-gate-class-fit`; (d) R&D skill design per `20260912T235557Z` step 4; (e) a short direct fix: #1010 or #1008.
2. If (a): follow `.gzkit/chores/frontier-model-card-currency/CHORE.md` steps 1-5, then run `uv run gz chores run frontier-model-card-currency` and commit the record with the log.
3. If (b): run `uv run gz chores status` for the live board. Pausing a chore is a registry declaration edit, synced via `gz agent sync control-surfaces`.
4. If (e): #1010's contract says `--json` stdout carries only JSON. `configure_logging` in `src/gzkit/cli/logging.py` is defined but never called.

## Pending Work / Open Loops

- GHI #934 (frontier drift), #1009 (accumulated-work counters), #1010 (structlog stdout), #1011 (CHORE.md drift), #997 and #808 (chores); #983 and #894 (presence, ruling-gated); #969 open by ruling; #968 open; #1008 open, unselected.
- Insights awaiting operator calibration: `chores/staleness-gate-class-fit`, `chores/staleness-signal-fit`, `cli/manpage-flag-claims`.
- permission-consent-drift lacks `proofs/settings-patch.md`, so its run still fails after a scan until step 5 writes the patch.
- R&D: skill design session, campaign R&D-front amendment text, `.out-of-scope/` ratification.
- Carried: `src/gzkit/commands/obpi_stages.py` BASELINE_VERIFICATION prescribes `uv run -m unittest -q` rather than the canonical step; three live justify-binding violations; 83 enforcement claims population-undeclared and 55 exemption-undeclared.

## Verification Checklist

```bash
git status -sb
git rev-list --left-right --count origin/main...HEAD
gh issue view 935 --json state
uv run gz obpi lock list
uv run python scripts/check_proof_freshness.py control-surface-permission-consent-drift
uv run python scripts/check_proof_freshness.py frontier-model-card-currency
uv run gz chores status
uv run -m unittest tests.governance.test_scan_interval_gate tests.commands.test_chores_staleness tests.commands.test_chores_status tests.commands.test_chores_declaration
uv run gz handoff rulings --search "Declare it"
```
Expected: level with origin/main; #935 CLOSED; no active locks; both gates exit 3 (no recent scan record); the board renders and exits 0; tests green; the witness ruling in the store. Re-run rather than trust.

## Evidence / Artifacts

- `.gzkit/handoffs/20260915T001007Z-chore-scan-record-935-and-fronts.md` (predecessor).
- `scripts/check_proof_freshness.py`, `src/gzkit/commands/chores_staleness.py`, `src/gzkit/commands/chores_declaration.py`, `src/gzkit/commands/chores_status_cmd.py`.
- `.gzkit/chores/registry.json`, `.gzkit/chores/README.md`, `.gzkit/chores/frontier-model-card-currency/CHORE.md`, `.gzkit/chores/control-surface-permission-consent-drift/CHORE.md`, and their `src/gzkit/chores/` mirrors.
- `tests/governance/test_scan_interval_gate.py`, `tests/commands/test_chores_staleness.py`, `tests/commands/test_chores_status.py`, `tests/commands/test_chores_declaration.py`.
- `docs/governance/chore-class-system.md`, `docs/user/manpages/chores-status.md`, `docs/user/manpages/chores.md`.
- `artifacts/receipts/arb-ruff-b3737d9ec2ed4fb29b05b9f0835e8a9d.json`, `artifacts/receipts/arb-step-unittest-c2c3f0bf656343d9aeb18362a72624b6.json`.
- Commits `7e306e4cb` and `17bfc4315`; GHI #935 contract-amendment and close comments.

## Settled Rulings

867 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
