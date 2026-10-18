---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-10-18T13:08:48Z'
agent: claude-code
session_id: 3b55343d-db1e-4924-97b5-fcad2277dbd8
continues_from: .gzkit/handoffs/20261018T123545Z-drydock-ro1-act-f-landed.md
---

## Current State Summary

Since the predecessor handoff: 0a7ee68ff fixed gz handoff create so repeated section flags accumulate (red witness arb-red-commit-0a7ee68ffe2c-e73591306d0a4ec4bf3c39c5c6ff2b61, inconclusive, 0 survived); pushed. GHI #1257 (three MX hardening guards with no runtime caller) is ruled but not started; the operator handed it to a fresh session because it touches about fifteen registration surfaces. Safe mode stays open; no locks are held.

## Important Context

Ruling for GHI #1257, given as "agree" to this recommendation: a hangar past its TTL announces but never blocks gz mx exit (inside the hangar an ERROR is advisory by design, and exit already runs the full gz check), and the safe-mode session opened 2026-10-17 gets no exemption, so the warning fires as soon as the guards are wired. The fix wires ttl_max_open_status, debt_aging_status and dangling_state_status (src/gzkit/mx/hardening.py) into the default gz check through a new gz validate scope, and into the session-start orientation as a line, with tests that fail when a call site is removed. checkpoint.resolve needs no guard-name registration: inside the hangar every level below CRITICAL routes ADVISORY, so on today's tree the scope prints two advisories (TTL and debt aging, about 28h) and grounds nothing; over-max (two open sessions) emits CRITICAL and grounds even inside; dangling state grounds outside. Template for a leveled audit: src/gzkit/governance/trust_audits/rendition_freshness.py (grounds -> ValidationError, else emit_advisory). Surfaces a default scope registers on, read from --wheel-path-literals: the audit module and its export in src/gzkit/governance/trust_audits/__init__.py; the flag in src/gzkit/cli/parser_maintenance.py (add_argument and the set_defaults lambda); src/gzkit/commands/validate_cmd.py (the scope table and the check_* parameter map); src/gzkit/quality.py (a run_*_audit wrapper) and src/gzkit/commands/quality.py (the step-to-guard map and the step list); data/check_scope_membership.json; tests/cli/test_validate_registry_parity.py; a negative control in src/gzkit/governance/trust_audits/_qc_negative_controls.py with its entry point in _qc_nc_entrypoints.py; a row in _qc_claim_exemptions.py; then decide, by reading those rosters' rules rather than copying, whether data/guard_canary_grandfather.json, data/population_control_grandfather.json and data/waiver_identity_baseline.json take the new scope or the scope gets a canary of its own; a section and a table row in docs/user/manpages/validate.md; a Coverage Ledger row in docs/governance/advisory-rules-audit.md. The REQ-0.0.74-14-01/03/04 evidence is repaired at the surface per the attested-REQ rule, since ADR-0.0.74 is Completed.

## Decisions Made

- [operator-ruled] Fix the handoff flag defect now, GHI #1257 announces past TTL without blocking gz mx exit and does not exempt the open session, RO-2 in a fresh session, hold #1252 for RO-7 (verbatim: "agree"); insight scope drydock-session-2026-10-18.
- [operator-ruled] GHI #1257 goes to a fresh session (verbatim: "Hand GHI #1257 to a fresh session: write a checkpoint handoff carrying the ruling and the surface list, then stop here.").

## Immediate Next Steps

1. Fresh session: fix GHI #1257 per the ruling and the surface list in Important Context, as one fix(mx) commit citing GHI #1257, RED tests first, then gz check, gz arb red --commit, and the close through ghi-close.
2. Then, per the predecessor: assess GHI #1246 and #1252; RO-2 the identity seam in a specifying session; the two offered follow-ups awaiting the operator's ruling.

## Pending Work / Open Loops

- GHI #1257, #1246, #1252 and #922 stay open.
- ADVISEMENT_CHAR_BUDGET in src/gzkit/session_start.py still lives in code, not in the budget file.
- Carried from the predecessor: detect_claude_settings_drift misses SessionStart and SessionEnd; skill_contract.parse_frontmatter reads a block-scalar description as its first line; RO-5's tagging scheme undesigned; GHI #1245; absolute local paths in 136 docs; briefs 17 and 20 PENDING by R4.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run python -m unittest tests.test_handoff_cli passes, including TestHandoffCreateRepeatedSectionFlags.
- gh issue view 1257 reads OPEN.
- grep -rn ttl_max_open_status src scripts .claude/hooks shows only src/gzkit/mx/hardening.py until the fix lands.

## Evidence / Artifacts

- `src/gzkit/cli/parser_handoff.py` — the repeatable section flags.
- `docs/user/manpages/handoff-create.md` — the repeatable-flag note.
- `src/gzkit/mx/hardening.py` — the three uncalled guards.
- `src/gzkit/governance/trust_audits/rendition_freshness.py` — the leveled-audit template.

## Settled Rulings

1590 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
