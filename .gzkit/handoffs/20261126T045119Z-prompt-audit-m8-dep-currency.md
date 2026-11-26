---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-26T04:51:19Z'
agent: claude-code
session_id: f5662052-93e0-4409-b50d-56df74e1acfc
continues_from: .gzkit/handoffs/20261125T130106Z-prompt-audit-m2-m7.md
---

## Current State Summary

Session f5662052 resumed from 20261125T130106Z-prompt-audit-m2-m7.md and walked prompt-audit M8. M8 grew into a chain of dependency-currency work, all on main and pushed, from 0a89f1e2c to 4cb19d021.

Closed, each confirmed by an independent reviewer subagent:
- #1368 (M8): gz-tech-debt-review cites the dependency-currency chore for currency grading, its probe observes only, and a fence test refuses a restated age (0a89f1e2c, 66049bb1f; CONFIRMED 7177380382).
- #1333: gz-deps-upgrade step 4a moves hook revs and Actions pins; the governed run moved them; local hooks declare language: unsupported (CONFIRMED 7182821413).

- #1369: dependency-currency's criteria now witness currency. check_currency.py --scan-record and --currency come first, a daily workflow calls them, and the shared staleness reader dates only records on disk.
  - Commits: 274e498ca, a68d248d7, 51b77411c, 4e54d06c7.
  - Reviews: NOT CONFIRMED 7180316153, NOT CONFIRMED 7182822126, CONFIRMED 7182944075.

Chore run 605be5480 (operator: "run the chore after the review"):
- 27 pins brought current; all six criteria pass; the board reads current.
- Drift report at .gzkit/chores/dependency-currency/proofs/drift-report.md.
- Full unit tier green at arb-step-unittest-f10e98029338484fa82bc179d216e198 (14323 tests).

Failures on main that predated this session, found by the full sweep and fixed:
- a4d6d1418: orientation text over its 4000 B budget.
- d4742c500: docs/rnd sources sealed for cli-alignment.
- 4cb19d021: the Windows-only ruff path assertion.

Filed, not worked: #1370, #1371, #1372.

M9 is next. The operator said: "ok, close them after the review, then M9".

## Important Context

Safe mode is still open (docs/governance/harbor-pilotage-candidate-2026-10-15.md):
- Every act is one commit with a Task: trailer.
- The advisory-scorecard and tautology guards are demoted. A rule version bump must be re-scored by hand in the Coverage Ledger of docs/governance/advisory-rules-audit.md. That was missed again this session, and amended before push in a4d6d1418.

Shift turnover, reviewed 2026-11-26:
- `gz wp tag show --all`: "No tag has been issued."
- `gz wp runs`: "No work package is in flight."
- `gz obpi lock list`: only mx-session, LEASE EXPIRED at 1682 of 1440 minutes. Renewal is the operator's call through gz-mx.
- The buy-back record is not built.

Mechanics learned:
- pre-commit refuses a commit while .pre-commit-config.yaml has unstaged edits. To split acts, use `git stash push --keep-index`, commit, then pop.
- canonical_history.json takes one hunk per changed canonical file. Stage a single act's hunk with `git apply --cached`.
- `gz agent sync` does not keep a chore script's executable bit in the src/gzkit copy. Run chmod +x after sync.
- `pre-commit autoupdate` can downgrade: it proposed gitleaks v8.30.1 to v8.30.0. The currency criterion names the real release.
- The per-change gz check does not run the full unit tier. Run `gz check --full` or the ARB unittest step before saying CI is green; main's CI had been red since f07865e87 on tests gz check never runs.
- Prose-reading fence tests (the M4, M7 and M8 witnesses) fail the demoted tautology audit at `gz mx exit`. #1370 decides their form.
- A search is not a read: #1368 was first filed claiming ">5y aging policy" existed nowhere, but it is the live STDLIB-FIRST adoption signal. Corrected on the issue and recorded as an insight.

## Decisions Made

- [operator-ruled] M8 started (verbatim: "proceed with M8").
- [operator-ruled] M8's reach: the skill fix in #1368, and the chore's currency-blind criteria as a second GHI (verbatim: "Skill fix + 2nd GHI (Recommended)").
- [operator-ruled] The five-year STDLIB-FIRST adoption signal is separate from currency grading; the debt review stops grading it (verbatim: "Separate them (Recommended)").
- [operator-ruled] Prose-reading witness tests are committed as built, and their form is decided under #1370 (verbatim: "Commit, file class GHI (Recommended)").
- [operator-ruled] dependency-currency gets both a scan-record gate and a currency criterion over every inventoried surface (verbatim: "do both - we need 'full monty' deps check, not 'lite'").
- [operator-ruled] A dependency behind upstream passes only via a `held: GHI #N` marker for a release that cannot be installed, and only while that GHI is open; a gate-red bump is repaired forward (verbatim: "Only uninstallable (Recommended)").
- [operator-ruled] The gates' automatic caller is a daily scheduled workflow (verbatim: "Daily CI workflow (Recommended)", then "try again" after the permission denial).
- [operator-ruled] The chore is run once the review is in (verbatim: "run the chore after the review").
- [operator-ruled] docs/rnd/<run>/sources/ are sealed records, exempt from cli-alignment (verbatim: "Exempt docs/rnd sources (Recommended)").
- [operator-ruled] gzkit's hooks move to language: unsupported, and gz init's template stays on system until an adopter pre-commit floor exists, tracked in #1372 (verbatim: "Switch repo, keep init (Recommended)").
- [operator-ruled] #1369 and #1333 close after review, then M9 (verbatim: "ok, close them after the review, then M9").
- [agent-chose] build_pins reads pyproject.toml through stdlib tomllib, not a line scan.
- [agent-chose] The orientation budget was met by a compress-and-merge pass over three lines, keeping WARNING, the verb and --abandon.
- [agent-chose] Unpushed commits were amended to fold in the falsifiability-driven tests, so one arb red run covers every hunk.
- [agent-chose] The Windows ruff path test was fixed directly without a GHI, under defect-fix routing (two lines, one surface, found in flight).

## Immediate Next Steps

1. Confirm CI on 4cb19d021: check (ubuntu-latest) and check (windows-latest) should both pass. full-strength-report stays red on the demoted hangar debt (#1262).
2. M9, per the operator ("ok, close them after the review, then M9"): gz-tidy lines 123 and 132 contradict its own lines 38-43 and tidy.py:104, which exits 3 on a breach (GHI #1124 [settled]). File through ghi-author, repair the canonical .gzkit/skills/gz-tidy, sweep by concept, review independently, close, then stop and report.
3. The mx-session lease is expired (1682 of 1440 minutes). Put renewal, or the hangar's exit, to the operator through gz-mx.
4. M10 onward in map order from the Revised mechanism map in docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md, stopping after each.

## Pending Work / Open Loops

- #1370: the form of the M4, M7 and M8 witness tests (a gz validate scope, or a declared tautology-audit exemption). It carries #1368 [settled]'s fence gaps and #1367's widening.
- #1371: no validator byte-checks the src/gzkit package copies against canon (probed: a drifted chore, rule and skill copy all passed).
- #1372: the gz init template stays on language: system until an adopter pre-commit floor exists.
- Carried from the prior handoff:
  - #1361, #1363 and #1365, filed but not worked.
  - Check whether #1346 absorbs M25, M28 and M40 before working them.
  - M32 needs the operator's attestation words.
  - Leftovers: M11, M13, M14 and M24.
  - After the audit: the conceptual-model R&D frontier, the DDD-discipline R&D run, two stale worktrees under .claude/worktrees, and the frontier-model-card-currency chore.
- #1369 [settled]'s out-of-contract observations: pre-release ordering and the whole-day scan period are recorded in CHORE.md § Known Gaps; a hold above `- repo:` fails closed.

## Verification Checklist

- `gh issue view 1369 --json state`: CLOSED.
- `gh run list --limit 6`: CI on 4cb19d021.
- `uv run python .gzkit/chores/dependency-currency/check_currency.py --currency` and `--scan-record`: both should exit 0 while the drift report is within its 1-day period. Expect red after a day until the chore runs again.
- `uv run gz chores status | grep dependency-currency`: current.
- `uv run -m unittest tests.chores.test_dependency_currency_gate`: 57 tests.
- `uv run gz obpi lock list`: the mx-session lease state.
- `git rev-list --left-right --count origin/main...HEAD`: 0 0.

## Evidence / Artifacts

- `.gzkit/chores/dependency-currency/check_currency.py`
- `.gzkit/chores/dependency-currency/CHORE.md`
- `.gzkit/chores/dependency-currency/proofs/drift-report.md`
- `.github/workflows/dependency-currency.yml`
- `tests/chores/test_dependency_currency_gate.py`
- `tests/policy/test_dependency_currency_cites_the_chore.py`
- `src/gzkit/commands/chores_staleness.py`
- `src/gzkit/governance/trust_audits/cli.py`
- `.gzkit/skills/gz-tech-debt-review/SKILL.md`
- `.gzkit/skills/gz-deps-upgrade/SKILL.md`
- `scripts/session_orientation.py`
- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md`

## Settled Rulings

2571 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
