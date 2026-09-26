---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-26T06:41:48Z'
agent: claude-code
session_id: a7415691-3d6e-47eb-b95f-517f613ab40c
continues_from: .gzkit/handoffs/20260926T061354Z-ghis-1098-1099-fixed-review-age-scoped.md
---

## Current State Summary

This part of the session followed the ghis-1098-1099 handoff: two skill reviews and one GHI filed and fixed, all pushed. origin/main is level with HEAD 19a90b413. gz-ontology (0.1.1) and gz-tidy (1.1.2) were reviewed and re-stamped in 1ea283613. Every gz-ontology claim held on the live tree. gz-tidy had two stale claims: a '200-line' CLAUDE.md budget, where the authority is the per-file character budget in data/instructions_files_budget.json, and a mirror-parity check naming only .claude/skills. The review found that gz tidy --fix bypassed the canonical sync preflight; it was filed as GHI #1100 and fixed in 19a90b413. Every command that propagates canon now routes through src/gzkit/commands/sync_guard.py: gz agent sync, gz tidy --fix (full path: preflight, sync, post-sync audit), gz init repair (preflight, and refusal comes after the repair summary) and gz init --force (preflight before its first sync). #1100 was closed with evidence. No OBPI work was initiated and no lock is held.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-09-20.md § Workflow fronts. This part touched the ghi triage front (#1100 filed and fixed) and skill maintenance. It did not touch the adr/obpi or new R&D fronts. The pre-push Skill audit still blocks on any skill whose last_reviewed passes 90 days. The next expiries are gz-insights-remember (last_reviewed 2026-07-13, blocks after 2026-10-11), gz-init (2026-07-15, after 2026-10-13), gz-adr-emit-receipt (2026-07-18, after 2026-10-16) and gz-check-config-paths (2026-07-25, after 2026-10-23). A skill review bumps skill-version and sets last_reviewed to today in the same edit, then runs gz agent sync control-surfaces. A skill test may locate a section by the first occurrence of its heading text (tests.test_foundation_triage_skill did), so a review edit must not repeat a heading phrase earlier in the body. Dry runs of gz init and gz agent sync do not run the preflight, so a dry run can list Would sync paths that the real run refuses. The skill-authoring rule treats generic rationalization and red-flag rows as parsimony findings, and trimming them is the operator's call; gz-tidy's tables were left unchanged.

## Decisions Made

- [operator-ruled] Verbatim: "review gz-ontology and gz-tidy" (1ea283613).
- [operator-ruled] Verbatim: "file a ghi for the tidy --fix bypass" (GHI #1100).
- [operator-ruled] Verbatim: "fix 1100" (19a90b413).
- [agent-chose] #1100 puts the refusal in a new module, src/gzkit/commands/sync_guard.py, rather than in tidy.py, so init_cmd does not import the tidy command module.
- [agent-chose] #1100 gives gz tidy --fix the full agent-sync path (preflight, sync, post-sync audit), and gz init repair the preflight only. Repair reports every write it made before the refusal, so GHI #1098's guarantee holds.
- [agent-chose] #1100 extends the guard to gz init --force, because --force keeps local canonical skills and so can meet corrupt canon.
- [agent-chose] The gz-tidy review corrected only factual claims; its generic rationalization and red-flag rows were left for the operator to rule on.

## Immediate Next Steps

1. Ask the operator which work to take up next. In ascending ADR order the lowest open work is ADR-0.35.0, whose closeout was blocked on OBPIs 07, 08, 10, 11, 12 and 13 at this session's start. Only the operator initiates OBPI work such as OBPI-0.35.0-07.
2. Before 2026-10-11, review gz-insights-remember, then gz-init (before 2026-10-13), gz-adr-emit-receipt (before 2026-10-16) and gz-check-config-paths (before 2026-10-23). Otherwise the pre-push Skill audit blocks every push.
3. Put to the operator whether to trim gz-tidy's rationalization and red-flag rows that name no failure observed in this repository (.gzkit/rules/skill-authoring.md § Parsimony clause 5).
4. On the first commit that changes an ADR, OBPI, PRD or constitution doc, AGENTS.md or CLAUDE.md outside the Edit tool, confirm the post-commit.legacy recorder prints recorded N and that the row persists in .gzkit/ledger.jsonl. This is the live witness for GHI #1092 [settled].

## Pending Work / Open Loops

The live-use confirmations from the prior handoff are still outstanding: reviewers return one importable envelope at the next real Stage-2 or Step-4b round (GHI #1095 [settled]), and the brief Demo runs in a copy at the next present-evidence run (GHI #1093 [settled]). Open GHIs carried forward and not worked: #1091, #1028, #894 and #611. Two discovery insights from an earlier session still await selection: gz obpi verify-packet replays transcripts in the live checkout, and the pre-push gate reports concurrent-session writes as its own modification. The tidy --fix insight recorded in 1ea283613 is now discharged by GHI #1100 [settled]. Dry-run preflight is out of #1100 [settled]'s scope: gz init --dry-run and gz agent sync --dry-run can list Would sync paths that a real run refuses. OBPI-0.35.0-07's land must call enforce_retention (BI-10) and owns the partial-IO sidecar exposure.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run gz skill audit
uv run -m unittest tests.commands.test_sync_preflight_guard tests.commands.test_init_repair_announces_writes tests.test_configured_path_consumers
gh issue view 1100 --json state
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing

## Evidence / Artifacts

- `.gzkit/skills/gz-ontology/SKILL.md`
- `.gzkit/skills/gz-tidy/SKILL.md`
- `src/gzkit/commands/sync_guard.py`
- `src/gzkit/commands/tidy.py`
- `src/gzkit/commands/init_cmd.py`
- `docs/user/manpages/tidy.md`
- `docs/user/manpages/init.md`
- `tests/commands/test_sync_preflight_guard.py`
- `artifacts/receipts/arb-step-unittest-b21aaf56a05046a5b7a66d4530b2e266.json`
- Commits: 1ea283613 (skill reviews), 19a90b413 (GHI #1100)

## Settled Rulings

1077 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
