---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T12:35:45Z'
agent: claude-code
session_id: 3b55343d-db1e-4924-97b5-fcad2277dbd8
continues_from: .gzkit/handoffs/20261018T080626Z-drydock-ro1-acts-a-to-e-landed.md
---

## Current State Summary

RO-1 act (f) is landed and pushed: e4136bd3d, the budget witness extended to every surface an agent loads (GHI #1249, closed fixed with the population variance against the baseline proof recorded as the disposition). RO-1's six acts (a) to (f) are all landed; the WP-16 effectiveness read per cut (GHI #1252) is the one RO-1 witness still open. Also this session: GHI #1257 filed for the three MX hardening guards that no runtime path calls (ttl_max_open_status, debt_aging_status, dangling_state_status; ADR-0.0.74 item 14), and the mx-session lock reaped at TTL at 2026-10-18T12:33:57Z by a gz obpi lock list call, leaving the safe-mode marker in place as predicted. Red witness for act (f): arb-red-commit-e4136bd3dc20-eb0a83fedb80444ca95eabf1ebbf7013, inconclusive, 14 killed, 0 survived, 14 inconclusive; the first cut arb-red-commit-8bf3007882ec-1c5a8fdc8df945d4a253151d3a489af7 was undriven on the unterminated-frontmatter guard and was repaired before push. Commits since the predecessor (04cd00591): 2e6b806c3 (insight and ledger sync), e4136bd3d (act f), bb432fb43 (ledger sync).

## Important Context

Safe mode stays open by operator ruling (.gzkit/mx.json mode safe, contract docs/governance/harbor-pilotage-candidate-2026-10-15.md). Releasing or reaping the mx-session lock never touches the marker: the lock is only the entry mutex (src/gzkit/commands/mx_cmd.py), the marker is the session truth, and only gz mx exit, which runs a full gz check, closes it. The hangar's own 24h TTL lapsed at 2026-10-18T08:37Z and raised no signal because ttl_max_open_status has no caller (GHI #1257); only normal_release_blocked is wired, at patch_release.py and closeout.py. A new gz mx enter would now find no lock, but it refuses while the marker exists. gz validate --instructions-files-budget now prints every total on each run (25 advisories on the current tree) and reads data/instructions_files_budget.json totals and injected_hook_text; scripts/session_orientation.py reads injected_hook_text and appends a warning to its own output when over. The first turn of a session receives both the orientation and the MX banner, each measured against the per-injection budget, not their sum. Root AGENTS.md's budget bullet names only the per-file budgets: true but incomplete, and it moves only by an operator ruling through the corpus. gz handoff create's section flags keep only their last value when repeated, so each section must be one multi-line value (insight scope gzkit.handoff.create-flags). Workflow fronts per the campaign: this session worked the drydock under the adr/obpi campaign front (RO-1) and the ghi triage front (filing #1257, closing #1249).

## Decisions Made

- [operator-ruled] Let the mx-session lock reap at TTL (verbatim: "Let the lock reap at TTL.").
- [operator-ruled] Keep safe mode open and continue the drydock (verbatim: "keep safemode open keep going with drydock"); booked with gz handoff decide proceed against the predecessor.
- [operator-ruled] The orientation measures its own size and the validator measures the MX banner (verbatim: "A: the orientation reads its budget from the JSON and checks itself at render; the validator measures the MX banner. Proceed with act (f)."); insight scope drydock-ro1f.
- [operator-ruled] File a GHI for the uncalled hardening guards (verbatim: "File a GHI through ghi-author for the three unwired MX hardening guards (ttl_max_open_status, debt_aging_status, dangling_state_status). Let the lock reap at TTL."); filed as GHI #1257.
- [operator-ruled] Close GHI #1249 with the baseline variance as the disposition (verbatim: "Close GHI #1249 through ghi-close, recording the population variance against the baseline proof as the disposition.").
- [agent-chose] New totals measure UTF-8 bytes, skill descriptions count chars of model-invoked skills by YAML parse, and nested AGENTS.md excludes .agents/, .claude/, src/gzkit/skills/ and src/gzkit/chores/; the baseline proof's 17-file nested set could not be reproduced by any exclusion rule.
- [agent-chose] An unparseable skill frontmatter is an advisory naming the file rather than a traceback, after the witness crashed on the baseline tag's gz-deps-upgrade.

## Immediate Next Steps

1. Assess GHI #1246 and #1252 against what RO-1 landed: #1246's description cut landed in act (c) and its rules narrative lift is RO-7 work; #1252 needs the per-stage WP-16 report series, which is RO-1's last open witness.
2. Operator: rule on GHI #1257's two open questions (does a hangar past its TTL block gz mx exit or only announce; how to treat the safe-mode session opened 2026-10-17 when the guard goes live), then fix it as fix(mx) (GHI #1257).
3. Session that specifies: RO-2, the identity seam, as the predecessors advised.
4. Operator: two offered follow-ups still await a ruling: a repair order to let a model correct AGENTS.md inside the drydock under a retention map, attestation and re-armed witnesses; and a WP-16-style measure of the content CMS's validators to size what to keep.

## Pending Work / Open Loops

- GHI #1257 (MX hardening guards uncalled), #1246, #1252 and #922 (nested AGENTS.md shape; weight is now measured) stay open.
- gz handoff create silently keeps only the last value of a repeated section flag; recorded as an insight, no GHI yet.
- ADVISEMENT_CHAR_BUDGET in src/gzkit/session_start.py (4000, the adopter-path truncation limit) still lives in code, not in the budget file.
- Carried: detect_claude_settings_drift misses SessionStart and SessionEnd; skill_contract.parse_frontmatter reads a block-scalar description as its first line; RO-5's repair tagging scheme undesigned; the orientation does not print the drydock's repair orders (GHI #1245); 136 docs carry absolute local paths; briefs 17 and 20 stay PENDING by R4.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0 and HEAD is at or after the sync commit carrying this handoff.
- uv run gz obpi lock list shows no active locks; the mx-session reaping record of 2026-10-18T12:33:57Z exists under .gzkit/locks/exchange/; .gzkit/mx.json still present.
- uv run gz validate --instructions-files-budget exits 0 and prints a line for rules, skill descriptions, agent definitions, nested AGENTS.md, personas and the MX banner.
- uv run python -m unittest tests.governance.test_audit_instructions_files_budget tests.scripts.test_session_orientation passes.
- gh issue view 1249 reads CLOSED; gh issue view 1257 reads OPEN.

## Evidence / Artifacts

- `data/instructions_files_budget.json` — totals and injected_hook_text.
- `src/gzkit/governance/trust_audits/instructions_files_budget.py` — the totals and banner witness.
- `scripts/session_orientation.py` — the self-check at render.
- `docs/governance/instructions-files-budget-history.md` — the 2026-10-18 entry with the baseline variance.
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` — the act (f) passage-log row.
- `.gzkit/insights/agent-insights.jsonl` — scopes gzkit.mx.hardening, drydock-ro1f and gzkit.handoff.create-flags.

## Settled Rulings

1588 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
