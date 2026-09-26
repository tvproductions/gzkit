---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-26T06:13:54Z'
agent: claude-code
session_id: a7415691-3d6e-47eb-b95f-517f613ab40c
continues_from: .gzkit/handoffs/20260926T012130Z-ghis-1092-1093-fixed-req9-corrected.md
---

## Current State Summary

This session resumed the GHI 1092/1093 handoff and fixed two GHIs, both pushed and closed with evidence. origin/main is level with HEAD c605cc277. GHI #1098 (gz init repair) was fixed in 9bb08e2a2. The dry run itself was the writer: repair ran the skill and chore scaffolders with skip_existing=not dry_run, so --dry-run rewrote canonical skills and dropped their airlineops-parity-scan routing rows. The real repair then mirrored that damage through an unreported sync_all. Repair now announces every write and skips the sync when nothing would change (the new plan_sync_changes). While #1098 was being verified, the unit suite went red on the date alone: gz-foundation-triage passed its 90-day review limit. It was reviewed and re-stamped in 65cb75abf; a wording fix in 691c52da0 un-broke a test that finds the first mention of Step 2. GHI #1099 was filed for the class and fixed in c605cc277. Review age is now judged only by gz skill audit and Gate 3; sync (preflight and post-sync audit) never refuses on it. audit_skills takes a today parameter through a frozen ReviewWindow, and review_clock() is the one machine-clock read. No OBPI work was initiated and no lock is held.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-09-20.md § Workflow fronts. This session touched the handoff front (resume and ruling booking), the ghi triage front (#1098 and #1099 fixed and closed) and the adr/obpi front (read only: ADR-0.35.0 closeout was verified blocked on OBPIs 07, 08, 10, 11, 12 and 13 at session start, and was not re-checked at close). It did not touch the new R&D front. The other session that held the working tree last time committed and pushed its AGENTS.md and ieee work (e5b3edff0, d131fa684) during this session, so the tree was clean at close. gz init repair is safe on this repository again. The GHI #1092 commit-locus recorder only watches PRD, constitution, ADR and OBPI docs plus AGENTS.md and CLAUDE.md (GOVERNANCE_PATTERNS in src/gzkit/hooks/core.py). No commit this session touched those, so its silence was correct and its live witness is still outstanding. The review-age check still blocks the pre-push gz check through the Skill audit step. gz-ontology (last_reviewed 2026-07-06) expires on 2026-10-04 and gz-tidy (2026-07-12) on 2026-10-10; after that the push gate fails until each is reviewed and re-stamped. A skill edit needs a skill-version bump and last_reviewed set to today in the same edit, followed by gz agent sync control-surfaces. The far-clock harness used to check #1099 lives only in the session scratchpad; it patched review_clock in-process, so subprocess-spawned tests were outside it.

## Decisions Made

- [operator-ruled] Handoff ruling on next work, verbatim: "Direct-fix GHI #1098 (Recommended)".
- [operator-ruled] Stale gz-foundation-triage review blocking the push, verbatim: "Review + bump, file GHI (Recommended)" (65cb75abf, GHI #1099 filed).
- [operator-ruled] Verbatim: "fix 1099".
- [operator-ruled] GHI #1099 sync policy, verbatim: "Audit only, sync stops (Recommended)". Sync no longer refuses on review age; gz skill audit and Gate 3 still block.
- [agent-chose] #1098 reports sync writes by rendering sync_all into the capture sink and comparing bytes with disk (plan_sync_changes), rather than listing every touched path (plan_sync_all), so a synced tree plans nothing.
- [agent-chose] #1098 dry run names mirrors of not-yet-scaffolded artifacts only through its Would scaffold line; a full simulation would need scaffolders to write through the sink. The limit is documented in the init manpage.
- [agent-chose] #1099 removed the duplicate constant sync_skills.DEFAULT_MAX_REVIEW_AGE_DAYS and its roster row; the roster is shrink-only, so removal is the permitted direction.
- [agent-chose] #1099 pins test_skills to the oldest shipped last_reviewed, so every shipped review has age zero or less, instead of a global test pin that would break real-clock-relative review tests.

## Immediate Next Steps

1. Ask the operator which work to take up next. In ascending ADR order the lowest open work is ADR-0.35.0, whose closeout was blocked on OBPIs 07, 08, 10, 11, 12 and 13 at this session's start. Only the operator initiates OBPI work such as OBPI-0.35.0-07.
2. Before 2026-10-04, review gz-ontology and re-stamp it, and gz-tidy before 2026-10-10. Otherwise the pre-push Skill audit step blocks every push.
3. On the first commit that changes an ADR, OBPI, PRD or constitution doc, AGENTS.md or CLAUDE.md outside the Edit tool, confirm the post-commit.legacy recorder prints recorded N and that the row persists in .gzkit/ledger.jsonl. This is the live witness for GHI #1092 [settled].
4. At the next real Stage-2 or Step-4b review round, confirm that reviewers return one importable envelope with no formatting repair (GHI #1095 [settled]). At the next present-evidence run, confirm the Demo ran in a copy (GHI #1093 [settled]).

## Pending Work / Open Loops

Open GHIs carried from the prior handoff and not worked this session: #1091 (compression losses family), #1028 (Stage-4 4a/4b loop), #894 (ruling on OBPI-08's launch row) and #611 (append-only corrective-action primitive). Two discovery insights from the prior session still await a selection decision: gz obpi verify-packet replays packet transcripts in the live checkout, and the pre-push gate reports writes by a concurrent session as its own modification. #1098 [settled]'s close comment names one untested cause: a missing chores registry.json is announced through missing_surface_files, but no test deletes it. #1099 [settled]'s class check did not reach tests that spawn gz as a subprocess, which read the real clock. OBPI-0.35.0-07's land must call enforce_retention (BI-10) and owns the partial-IO sidecar exposure. The Layer-2 retention digest remains deferred on the security surface.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
uv run gz skill audit
uv run -m unittest tests.commands.test_init_repair_announces_writes tests.commands.test_review_age_scope tests.test_skills_audit tests.test_sync
gh issue view 1098 --json state
gh issue view 1099 --json state

## Evidence / Artifacts

- `src/gzkit/commands/init_cmd.py`
- `src/gzkit/validate_pkg/sync_parity.py`
- `src/gzkit/chores/__init__.py`
- `docs/user/manpages/init.md`
- `tests/commands/test_init_repair_announces_writes.py`
- `.gzkit/skills/gz-foundation-triage/SKILL.md`
- `src/gzkit/skills_audit.py`
- `src/gzkit/sync_skill_validation.py`
- `src/gzkit/commands/tidy.py`
- `docs/user/manpages/agent-sync-control-surfaces.md`
- `data/module_constant_grandfather.json`
- `tests/commands/common.py`
- `tests/commands/test_review_age_scope.py`
- `artifacts/receipts/arb-step-unittest-92da4bfbd4fe437b907c57a97fafee6f.json`
- `artifacts/receipts/arb-step-unittest-839ea0bb56bd4d3a95da98c5e7ae3b07.json`
- Commits: 9bb08e2a2 (GHI #1098), 65cb75abf and 691c52da0 (gz-foundation-triage review), 61d012cce (ledger), c605cc277 (GHI #1099)

## Settled Rulings

1074 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
