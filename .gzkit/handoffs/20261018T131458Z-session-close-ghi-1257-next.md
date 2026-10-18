---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T13:14:58Z'
agent: claude-code
session_id: 3b55343d-db1e-4924-97b5-fcad2277dbd8
continues_from: .gzkit/handoffs/20261018T130848Z-ghi-1257-handed-to-fresh-session.md
---

## Current State Summary

Session close. Everything this session landed is pushed: e4136bd3d RO-1 act (f), the budget witness over every loaded surface (GHI #1249 closed fixed); 0a7ee68ff gz handoff create section flags repeat instead of keeping the last value; GHI #1257 filed for the three uncalled MX hardening guards, ruled and handed to a fresh session by the checkpoint 20261018T130848Z-ghi-1257-handed-to-fresh-session.md. Since that checkpoint, one commit (372910b26) carried the operator's realization that the OBPI-named skills will likely become work-package skills, recorded as insight scope drydock-ro7-skill-recut and as a planning comment on GHI #1250. Safe mode stays open; no locks are held; the mx-session lock was reaped at 2026-10-18T12:33:57Z.

## Important Context

GHI #1257 ruling (operator, "agree"): a hangar past its TTL announces but never blocks gz mx exit, and the safe-mode session opened 2026-10-17 gets no exemption. The fix wires ttl_max_open_status, debt_aging_status and dangling_state_status (src/gzkit/mx/hardening.py) into the default gz check through a new gz validate scope and into the session-start orientation as a line, with tests that fail when a call site is removed. checkpoint.resolve needs no guard-name registration; inside the hangar every level below CRITICAL routes ADVISORY, so today the scope prints two advisories (TTL and debt aging) and grounds nothing. Leveled-audit template: src/gzkit/governance/trust_audits/rendition_freshness.py. Surfaces a default scope registers on, read from --wheel-path-literals: the audit module and its export in src/gzkit/governance/trust_audits/__init__.py; src/gzkit/cli/parser_maintenance.py (flag and set_defaults); src/gzkit/commands/validate_cmd.py (scope table and check_* map); src/gzkit/quality.py and src/gzkit/commands/quality.py (wrapper, step map, step list); data/check_scope_membership.json; tests/cli/test_validate_registry_parity.py; a negative control in _qc_negative_controls.py with its entry point in _qc_nc_entrypoints.py; a row in _qc_claim_exemptions.py; then decide, by reading the rosters' rules, whether data/guard_canary_grandfather.json, data/population_control_grandfather.json and data/waiver_identity_baseline.json take the scope or it gets its own canary; docs/user/manpages/validate.md section and row; a Coverage Ledger row in docs/governance/advisory-rules-audit.md; REQ-0.0.74-14-01/03/04 evidence repaired at the surface (ADR-0.0.74 is Completed). The skill re-cut is planning only: RO-7's merge plan (GHI #1250) maps each gz-obpi-* skill by function after RO-5 lands work packages and task cards; it changes no current workflow. Workflow fronts per the campaign: drydock under the adr/obpi front; ghi triage front for #1249, #1250 and #1257.

## Decisions Made

- [operator-ruled] Plan the OBPI-skill re-cut without stopping the workflow (verbatim: "just plan for it, don't stop your workflow, it is just a realization"); recorded as insight scope drydock-ro7-skill-recut and on GHI #1250.

## Immediate Next Steps

1. Fresh session: fix GHI #1257 per the ruling and the surface list in Important Context, as one fix(mx) commit citing GHI #1257, RED tests first, then gz check, gz arb red --commit, and the close through ghi-close.
2. Assess GHI #1246 and #1252 against what RO-1 landed; #1252 holds until the RO-7 cuts start, by the operator's agreement.
3. Session that specifies: RO-2, the identity seam.
4. Operator: two offered follow-ups still await a ruling: a repair order to let a model correct AGENTS.md inside the drydock, and a WP-16-style measure of the content CMS's validators.

## Pending Work / Open Loops

- GHI #1257, #1246, #1250, #1252 and #922 stay open.
- ADVISEMENT_CHAR_BUDGET in src/gzkit/session_start.py still lives in code, not in the budget file.
- Carried: detect_claude_settings_drift misses SessionStart and SessionEnd; skill_contract.parse_frontmatter reads a block-scalar description as its first line; RO-5's tagging scheme undesigned; GHI #1245; absolute local paths in 136 docs; briefs 17 and 20 PENDING by R4.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- The session orientation's account section reports zero commits since this handoff.
- uv run gz handoff rulings --search 'just plan for it' returns the realization ruling.
- gh issue view 1257 reads OPEN; gh issue view 1249 reads CLOSED.

## Evidence / Artifacts

- `src/gzkit/mx/hardening.py` — the three uncalled guards.
- `src/gzkit/governance/trust_audits/rendition_freshness.py` — the leveled-audit template.
- `src/gzkit/cli/parser_handoff.py` — the repeatable section flags.
- `.gzkit/insights/agent-insights.jsonl` — scopes drydock-ro7-skill-recut, drydock-session-2026-10-18, gzkit.mx.hardening.

## Settled Rulings

1591 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
