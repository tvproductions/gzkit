---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-10-29T05:39:48Z'
agent: claude-code
session_id: 2e2e493b-472b-4c61-addf-78ede287b7bf
continues_from: .gzkit/handoffs/20261029T052527Z-ro9-tranches-5-6-landed-tranche-7-in-flight.md
---

## Current State Summary

The RO-9 tranche 7 work in progress the predecessor handoff described as uncommitted is now committed and pushed as b5d6335cf on the operator's word (verbatim: "commit now"), and the working tree is clean. That commit carries the uv-built gz init skeleton, gz init --project-type lib|package|app, the adopter baseline seeded at init, and gzkit's own Astral-discipline baseline emptied. The pre-push gz check and the whole-tree lint passed, and origin/main is level with HEAD. Committing also required grouping the skeleton's layout arguments into a frozen ProjectSkeleton model (PLR0913) and a _present helper for the init status lines, which lowered two cognitive-complexity baseline rows and surrendered one Ruff baseline row.

## Important Context

This checkpoint supersedes two lines of the predecessor handoff: tranche 7 is no longer uncommitted, and the warning not to run gz git-sync no longer applies because the tree is clean. Everything else in the predecessor stands: safe mode open, WP-01-astral-toolchain held and commenced with both issues closed, and the shift-turnover statement. scaffold_project_skeleton now takes (project_root, ProjectSkeleton, *, dry_run); ProjectSkeleton lives in src/gzkit/commands/init_cmd.py.

## Decisions Made

- [operator-ruled] Commit tranche 7's work in progress as a checkpoint before it is finished (verbatim: "commit now").
- [agent-chose] Grouped the skeleton's name, source_root, tests_root and project_type into a frozen ProjectSkeleton model rather than suppress PLR0913.

## Immediate Next Steps

1. Finish RO-9 tranche 7 on top of b5d6335cf: tests for each --project-type, no authors field, the ruff and ty dev group, the CI workflow, a seeded baseline holding an existing project's debt, and a non-src source_root; the init manpage row and examples for --project-type; adopter docs on uv tool install and uvx only (docs/user/manpages/init.md lines 143 and 347, docs/user/manpages/upgrade.md line 66, docs/examples/guide-releasing.md line 10); a behave scenario in features/init.feature; gz cli audit; gz arb red --commit on the commits.
2. Record tranche 7 in docs/governance/harbor-ro9-astral-toolchain.md and the passage log, sync, and confirm CI is green; RO-9 closes when the baseline is empty and gz check --full passes on every CI platform.
3. Run gz wp accept on WP-01-astral-toolchain and bring the operator the Gate 5 close (gz wp close).
4. Ask the operator to review the supply-chain-audit and supply-chain-audit-ignored canaries through gz canary review.

## Pending Work / Open Loops

- Tranche 7's remaining items are the work of next step 1.
- The two supply-chain canaries carry no operator review yet.
- docs/design/cli-standards-v3.md still states a 3.13 Python floor in its scaffold example and stack table.
- The MX hangar's advisory debt keeps aging; close it through the gz-mx skill when the drydock work is done.

## Verification Checklist

- git status --short prints nothing, and git log --oneline -1 shows b5d6335cf.
- uv run -m unittest tests.commands.test_init tests.governance.test_astral_discipline passes.
- uv run gz validate --astral-discipline passes with no rows in data/astral_discipline_baseline.json.
- git rev-list --left-right --count origin/main...HEAD prints 0 0.

## Evidence / Artifacts

- `src/gzkit/commands/init_cmd.py` — the uv-built skeleton and ProjectSkeleton.
- `src/gzkit/governance/trust_audits/astral_discipline.py` — seed_discipline_baseline.
- `data/astral_discipline_baseline.json` — empty.
- `.gzkit/handoffs/20261029T052527Z-ro9-tranches-5-6-landed-tranche-7-in-flight.md` — the predecessor this checkpoint corrects.

## Settled Rulings

1810 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
