---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-27T09:32:32Z'
agent: claude-code
session_id: c2190695-4a85-407d-957f-4984a2e3c958
continues_from:
- .gzkit/handoffs/20261027T084150Z-cosmic-ray-canary-provenance.md
- .gzkit/handoffs/20261027T085646Z-session-exit-bookmark.md
- .gzkit/handoffs/20261027T092346Z-session-exit-bookmark.md
---

## Current State Summary

Resumed 20261027T084150Z-cosmic-ray-canary-provenance.md and folded the two mechanical exit bookmarks (sessions e8912233 and fea5e6a2), whose work sat staged but uncommitted. Landed it as three separate acts: b2010522e (dependency-currency becomes a daily repair chore and deps are brought current: Python 3.14.10, pydantic 2.14.1, coverage 7.17.0, ruff 0.17.3, uv.lock, plus the ty 0.0.92 fixes), a37cc8afa (the prefer_lsp PreToolUse hook, the CLAUDE.md line and the template lines, and the exec-form test fix), and 88e10748f (docs/rnd/subagent-folding.md, diamond 1 in progress with sources gathered and no disposition map yet). canonical_history.json was split by hunk so each commit carries only its own hashes. Pre-commit passed on all three. Safe mode is still open, and the mx-session lock is still held.

## Important Context

Safe mode is open: the slow alarms are off and lint plus the fast static checks are on. Each act is one commit with a Task: trailer (docs/governance/safe-mode-doctrine.md item 5). MX debt has aged past 240h. The 2026-10-27 insight records that gz check --full fails 9 tests on surfaces these sessions did not touch: the unittest lockstep test, which the mx alarm wrapper changed; the mx-mode.md version against the Coverage Ledger; gz release pressure unresolved at docs/governance/harbor-ro4-release.md:22; the competitor-radar-currency CHORE.md lane and steps shape; and the 91-char --model-class-only help line. Each of those belongs on the punch list before gz mx exit. No ruling is recorded for the prefer_lsp hook. The operator authorized committing it as staged work.

## Decisions Made

- [operator-ruled] Fold the bookmarks, commit the staged work in separate acts, then pick an R&D run (verbatim: "Fold the two bookmarks into a new authored handoff. Then commit the staged work through git-sync in separate commits (deps and chore, LSP hook, R&D doc), because safe mode wants one commit per act. After that, pick between the subagent-folding R&D and the contractor-kit R&D.").
- [agent-chose] Split canonical_history.json by hunk: the templates/claude.md hash went with the LSP commit and the chore hashes went with the deps commit.
- [agent-chose] Committed agent-insights.jsonl with the deps act because it carries that act's ruling. The ledger and the bookmarks ride with this handoff's git-sync.

## Immediate Next Steps

1. The operator picks between the subagent-folding R&D (docs/rnd/subagent-folding.md, sources gathered, decision on subject recorded) and the contractor-kit R&D (docs/rnd/contractor-kit.md), both through gz-rnd.
2. Then the mode contract's syntax: candidate Python affordances for code controls, after reading the census and the seven chore --self-test arms (carried).
3. Before gz mx exit, enter the 9 gz check --full failures on the MX punch list, each with its own recovery.
4. After gz mx exit, offer the Cosmic Ray route: the 2026-08-22 decline versus the 2026-10-27 words, and an ADR versus a recorded STDLIB-FIRST exception (carried).
5. Remind the operator to turn off cowork-plugin-management via /plugin (carried).

## Pending Work / Open Loops

- GHI #1273 (MX-system review): carry the 2026-10-26 trap table, the report-only ruling, the full-lint-in-safe-mode ruling, and the GZKIT_MX_FULL_STRENGTH=1 observation.
- The 9 gz check --full failures (insight 2026-10-27T09:11Z) are not yet on the punch list.
- 31 chores are overdue. dependency-currency now runs daily, so it comes due tomorrow.

## Verification Checklist

- git log --oneline -4 shows 88e10748f, a37cc8afa and b2010522e on top of 0269e4faa.
- git rev-list --left-right --count origin/main...HEAD reads 0 0 after this handoff's git-sync.
- uv run gz obpi lock list shows mx-session ACTIVE.
- uv run gz chores show dependency-currency shows rung repair, periodDays 1.

## Evidence / Artifacts

- `.claude/hooks/prefer_lsp.py`
- `.gzkit/chores/dependency-currency/CHORE.md`
- `docs/rnd/subagent-folding.md`
- `docs/rnd/contractor-kit.md`
- `.gzkit/insights/agent-insights.jsonl`
- `src/gzkit/canonical_history.json`

## Settled Rulings

1767 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
