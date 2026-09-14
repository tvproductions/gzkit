---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-14T02:55:15Z'
agent: claude-code
session_id: 863d2b33-90f9-4eb6-9472-5d4b9f153523
continues_from: .gzkit/handoffs/20260913T150226Z-chores-step6-suppression-and-smoke-tier.md
---

## Current State Summary

Session 863d2b33 resumed `20260913T150226Z-chores-step6-suppression-and-smoke-tier.md` (Fresh; every claim verified). Resume ruling booked with `gz handoff decide`: proceed on (c) family-A inventory; (a) chores step 2 (GHI #936) and (b) test-isolation-compliance set aside.

Done:
- Read-only family-A inventory of 47 open and 72 recently closed GHIs, grouped into five shapes: population, presence, channel, cap-not-reduction, verdict. 26 open members.
- Full-body read of the 10 population-shape issues. Only #851 fit a shared population mechanism cleanly: #921, #922, #939 and #799 sit under ADR-0.35.0 briefs (IRON LAW); #956 already has its roster; #950 is over-inclusion (family C); #926 and #927 have no declared set.
- Filed GHI #1007 (class). Landed `1edf9dc1b`, pushed (sync `a2895ffb7`, origin level): a three-state `population` argument on `@enforces`, a per-member runner requiring each finding to name its member, `gz validate --population-controls` as its own `gz check` step with a shrink-only list of 83, and #851's delivery witness covering every declared hook type with severity by type. `gz init` installs the declared list.
- Closed GHI #1007 and GHI #851 with evidence. Mutation sweeps 11/11 killed; `gz check` exit 0.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** no change. GHI #1003, #870 untouched.
- **ghi triage:** family-A inventory drafted (in conversation, not committed); #1007 filed and closed, #851 closed. Queue now 45 open.
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 TOPMOST, 7/13. Its OBPI-10, -11 and -12 own the family-A members #939, #922 and #921 respectively.
- **new R&D:** not worked.

### Family-A shapes and the remaining open members
- Presence (5): #889 #996 #994 #983 #894. Candidate class fix: a required present-but-false negative control for claims whose subject is an artifact.
- Channel (7): exit status #969 #971 #995 (plus #889 consumer side); neighbouring domain #907 #815 #803 #997 (no single mechanism; rule text).
- Cap not reduction (2): #808 #998. Verdict (2): #919 #936.
- Population leftovers: #926 and #927 need posture rulings; #810 is rules-arm work under the promotion freeze.

### Gotchas learned
- `run_enforcement_floor_audit` also runs in the pre-push guard (`src/gzkit/hooks/guards.py`) in every project, so the floor must read nothing repo-only. Recorded as an insight.
- A negative control must not re-run `_ensure_production_claims_registered` per member; `test_enforcement_nc_discrimination` pins discovery to once. Inject the registry the way `_ep_exemption_controls` does.
- A population callable must not reuse the witness's own reader, or it narrows in step with the witness.
- The verifier-pipe hook blocks piping `ruff` into `tail`; run a script file or capture to a log.

## Decisions Made

- [operator-ruled] Resume ruling on `20260913T150226Z`: "(c) Family-A inventory (Recommended)". (a) and (b) set aside.
- [operator-ruled] First family-A shape: "1 Population (Recommended)".
- [operator-ruled] After the full-body read showed one clean fit: "Build the class fix (Recommended)".
- [operator-ruled] GHI #851 severity: "By hook type (Recommended)" — prepare-commit-msg and post-commit advisory, every other declared type fails closed.
- [operator-ruled] Population inventory placement: "Own gz check step (Recommended)" — a `gz validate --population-controls` scope, not an arm of the enforcement floor.
- [agent-chose] Covered #851's delivery arm with a new claim `session-green-gate-delivery` instead of repurposing `session-green-gate`, whose control plants a declaration defect that must stay covered.
- [agent-chose] The inventory's refuse control is proven per undeclared claim; its admit control declares population "none" and exempts "none" (verifier escape-claim pattern).
- [agent-chose] Seeded `data/population_control_grandfather.json` at all 83 undeclared claims measured on main, following the #797 seeding precedent.

## Immediate Next Steps

1. Put the next family-A shape to the operator: presence (5 open), exit-status contract (#969 #971 #995 and #889), or draining the 83-entry population list one gate at a time.
2. If presence: read #889 #996 #994 #983 #894 in full and check brief ownership (`grep -rln` over `docs/design/adr/*/*/obpis/*.md`) before proposing the present-but-false control.
3. Chores-revamp step 2 (GHI #936) and `test-isolation-compliance` remain set aside; offer them again only if the operator asks.

## Pending Work / Open Loops

- 83 enforcement claims disclosed as population-undeclared (`data/population_control_grandfather.json`); each drain reads one gate.
- Family-A open members listed in Important Context.
- GHI #936, #997, #808 open; test-isolation-compliance still fails on two slow tests.
- ADR-0.35.0-owned members #921 #922 #939 #799 wait on operator-initiated OBPI work.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
gh issue view 1007 --json state
gh issue view 851 --json state
uv run gz validate --population-controls
uv run -m unittest tests.governance.test_enforcement_population tests.governance.test_population_controls tests.governance.test_session_green_gate_delivery_control tests.test_session_green_gate_validator
uv run gz handoff rulings --search "Own gz check step"
```
Expected at authoring: `0 0` (the insights append may leave `.gzkit/insights/agent-insights.jsonl` uncommitted); #1007 and #851 CLOSED; scope prints 86 claims, 3 declared, 83 disclosed; tests green. Re-run rather than trust.

## Evidence / Artifacts

- `src/gzkit/enforcement.py` — `POPULATION_NONE`, `population` field, `_run_population_claim`, `production_enforcement_registry`.
- `src/gzkit/governance/trust_audits/population_controls.py`, `src/gzkit/governance/trust_audits/_qc_nc_population.py`, `src/gzkit/governance/trust_audits/_qc_claim_populations.py`, `src/gzkit/governance/trust_audits/_qc_nc_hooks.py`.
- `src/gzkit/governance/trust_audits/session_green_gate.py`, `src/gzkit/commands/init_cmd.py`.
- `data/population_control_grandfather.json`, `data/waiver_ratchet_registry.json`, `data/check_scope_membership.json`, `data/check_step_concurrency.json`.
- `tests/governance/test_enforcement_population.py`, `tests/governance/test_population_controls.py`, `tests/governance/test_session_green_gate_delivery_control.py`.
- `docs/user/manpages/validate.md`, `docs/user/manpages/init.md`, `docs/user/runbook.md`.
- Commits `1edf9dc1b`, `a2895ffb7`; GHI #1007 and #851 close comments.

## Settled Rulings

849 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
