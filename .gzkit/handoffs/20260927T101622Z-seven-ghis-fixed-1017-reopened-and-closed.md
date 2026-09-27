---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-27T10:16:22Z'
agent: claude-code
session_id: d8dc657d-0462-429c-a332-8e4009e3977b
continues_from: .gzkit/handoffs/20260927T072424Z-skills-reviewed-gz-how-built-nine-ghis-filed.md
---

## Current State Summary

This session resumed `20260927T072424Z-skills-reviewed-gz-how-built-nine-ghis-filed.md` (ruling booked with gz handoff decide, verbatim "fix 1115"; its steps on #1112 and ADR-0.35.0 OBPI work set aside). No OBPI work was initiated and no lock is held.

It opened on a red CI: the windows-latest leg failed test_non_executable_recorder_is_not_delivered, which asserted a POSIX exec-bit state Windows cannot hold; skipped on Windows (d9c099add), CI green on 96cc65a75. A pasted diagnosis blaming NCSurface.md was wrong: that is an advisory negative-control fixture, and rendition lineage passed.

Closed with evidence: #1115 brief-drift --apply refuses a sealed brief, exit 3 (c9a73bebe); #1017 reopened under a new gh-cli rule allowing `gh issue reopen` (5928cd60f), then fixed so commit-trailers reads every pushed commit, not HEAD (98bec10c1); #1111 skill docs pages quoting dropped skill text (6d900df98); #1116 brief-drift --apply --dry-run previews the exact amendment lines (0732235ca); #1117 validate Scopes Reference lists all registry scopes, with a test (0ffc98162); #1118 producers record slug ids, `gz validate --pending-renames` blocks gz check, 21 renames appended (ed2a97c4e, f0cc88e01); #1114 seven gzkit-only chores projectLocal, pythonic-design-pattern-detection runnable in adopters (e9dcb8a60). HEAD edc8bba47 level with origin/main before this handoff.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-09-20.md § Workflow fronts. This session worked the ghi triage front only; the adr/obpi front was not touched. ADR-0.35.0 remains 8/14 with closeout blocked on OBPIs 07, 08, 10, 11, 12, 13, and OBPI-0.35.0-08 reads in_progress in the ledger with no lock held.

New mechanisms other work will meet: `gz validate --pending-renames` is default tier and fails gz check while any bare-id event lacks an artifact_renamed row (repair is gz migrate-semver). `gz validate --commit-trailers` now checks every commit in @{upstream}..HEAD, so a src/tests commit without a Task: trailer fails pre-push even under a .gzkit sync commit. tests/governance/test_validate_scopes_reference.py fails when a new validate scope has no Scopes Reference row. tests/governance/test_shipped_chore_criteria.py fails when a shipped chore's criterion names src/gzkit/ or scripts/. slug_id_for in src/gzkit/ledger.py is the producer-side canonicalizer.

Seven chores are now projectLocal and live only under .gzkit/chores/; their scripts and two pre-commit hooks run from there. The verifier-pipe-gate hook refuses a verifier followed by another statement or pipe; run it alone and echo $? next. Never bundle a recursive delete into a setup command: the operator stopped one this session.

## Decisions Made

- [operator-ruled] Verbatim: "yes, commit and git-sync" (Windows exec-bit test skip, d9c099add).
- [operator-ruled] Verbatim: "fix 1115" (c9a73bebe).
- [operator-ruled] Verbatim: "yes, file the ghi"; route "Reopen #1017 (Recommended)"; allowlist "Add reopen to the rule (Recommended)" (5928cd60f).
- [operator-ruled] Verbatim: "fix 1017"; homing "Fix under #1017 (Recommended)", over OBPI-0.37.0-04's Denied Paths note (98bec10c1).
- [operator-ruled] Verbatim: "danger! why was this invoked? `rm -rf`" (course-correction, recorded as an improvement insight; the command was refused and never ran).
- [operator-ruled] Verbatim: "fix 1111" (6d900df98).
- [operator-ruled] Verbatim: "fix 1116" (0732235ca).
- [operator-ruled] Verbatim: "fix 1117" (0ffc98162).
- [operator-ruled] Verbatim: "fix 1118"; backlog "Append all 21 (Recommended)"; check "Block (default tier) (Recommended)" (ed2a97c4e, f0cc88e01).
- [operator-ruled] Verbatim: "fix 1114"; seven chores "Mark projectLocal (Recommended)"; pythonic "Ship it runnable (Recommended)" (e9dcb8a60).
- [agent-chose] #1115 refusal exits 3 (policy breach), not 1; --dry-run refused too so the preview predicts the refusal.
- [agent-chose] #1117 table kept hand-written and checked, not generated: the registry carries no purpose text.
- [agent-chose] #1118 canonicalizes from the stem of the file each producer already resolves (slug_id_for), not a disk walk; the justify-binding reader folds renames.
- [agent-chose] #1114 disclosed chore:control-surface-rule-conflicts in data/uncalled_gate_grandfather.json (baseline 39 to 40), matching memory-hygiene and pythonic.

## Immediate Next Steps

1. Ask the operator which of GHIs #1110, #1112 and #1113 to take up next; #1112 is the eight scaffold-template skills, reviewed with gz-skill-review two per commit.
2. Put to the operator the insight asking whether `gz obpi brief-drift --dry-run` should stop writing a brief_reconciled ledger event.
3. Ask whether OBPI work on ADR-0.35.0 resumes; only the operator initiates it. When OBPI-0.37.0-04 is next initiated, its Denied Paths note on HEAD-only trailer scanning needs an operator amendment (stale since 98bec10c1).
4. Put to the operator the open questions carried from the predecessor handoff: whether the scaffolding-settings layer needs its own ADR, the competitor-radar cadence, and the presenter insight that gz complexity advise prints No crossings detected after an all-attested run.

## Pending Work / Open Loops

Open GHIs from the prior batch: #1110 redundant no-skill waivers, #1112 eight template skills, #1113 chores run pinned tools through unpinned uvx. Related open: #1034 (gz-flighttest docs, same delivered-path class as #1114 [settled]), #1063 (validator scopes never invoked, the doctrine-declared-without-mechanism family), #907 (authorship witness narrower than its rule).

Insights recorded this session and awaiting operator rulings: dry-run brief-drift writes the ledger; OBPI-0.37.0-04's stale denial note; the rm -rf course-correction. d9c099add and 84ea8e435 remain in published history without Task: trailers and are recorded instances, not repairable without a force-push. Readers that match ledger ids by raw string were not swept beyond the justify-binding gate.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads 0 0 after the sync.
- `uv run gz check` passes on a fully staged tree.
- `uv run gz validate --pending-renames` and `uv run gz validate --distribution` each exit 0.
- `gh issue view <N> --json state` reads CLOSED for #1017, #1111, #1114, #1115, #1116, #1117 and #1118, and OPEN for #1110, #1112 and #1113.
- `uv run gz obpi lock list` shows no active locks.

## Evidence / Artifacts

- `src/gzkit/commands/brief_reconcile.py` (#1115, #1116)
- `src/gzkit/commands/validate_commit_trailers.py` and `tests/governance/test_commit_trailers_pushed_range.py` (#1017)
- `.gzkit/rules/gh-cli.md` (0.7.0, gh issue reopen)
- `tests/test_skill_manpage_coverage.py` (#1111)
- `docs/user/manpages/validate.md` and `tests/governance/test_validate_scopes_reference.py` (#1117)
- `src/gzkit/commands/validate_pending_renames.py`, `tests/governance/test_bare_id_producers.py` and `tests/governance/test_pending_renames.py` (#1118)
- `tests/governance/test_shipped_chore_criteria.py` and `.gzkit/chores/registry.json` (#1114)
- `tests/hooks/test_commit_locus_survives_precommit_stash.py` (Windows skip)

## Settled Rulings

1118 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
