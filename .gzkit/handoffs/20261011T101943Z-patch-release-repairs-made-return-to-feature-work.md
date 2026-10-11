---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-11T10:19:43Z'
agent: claude-code
session_id: 24f0562f-2e6d-46b4-978a-a506149330a6
continues_from: .gzkit/handoffs/20261011T095245Z-v0-34-9-released-return-to-feature-work.md
---

## Current State Summary

After v0.34.9 was released the operator ordered the two patch-release defects fixed; both are in commit 19cc94d9d. `gz patch release` now releases a version that is already ahead of its tag and does not bump it again, so the hand-over from `gz closeout` runs through the verb, and the release body is the newest version block whether or not a rule closes it. main is even with origin and clean after this handoff's sync. Nothing is in flight. Everything else is as `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` and the two previous handoffs say.

## Important Context

Read `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` first; the operator's state, the workflow fronts and the mechanics are in the handoff of 2026-10-11T09:21Z and unchanged. One correction to the previous handoff: it said the full ceremony's body extraction would have published 41 versions. That was wrong. The full ceremony authors its own entry closed by a rule before extracting, so its body was always one entry; the claim came from running the function against a hand-written notes file. The extraction was made independent of the rule anyway, because the new in-flight path can meet a hand-written entry. The fix has not been exercised on a real minor release; the first one will be v0.35.0.

## Decisions Made

- [operator-ruled] The two patch-release defects are fixed directly (verbatim: "fix the two patch release defects, then git sync").
- [agent-chose] Read a declared version ahead of the latest tag as a release in flight, with no new flag and no change to the JSON fields; a newest tag that is not a version keeps the ordinary bump.
- [agent-chose] Split three helpers out of the command when the complexity hook refused the first commit, and added five tests when the falsifiability run reported four undriven lines, both before anything was pushed.

## Immediate Next Steps

1. Show the operator `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` and take their ruling on what to draw next. Execute nothing before it.
2. If the operator returns to feature work: `ADR-0.35.0` item 15, `OBPI-0.35.0-15-pipeline-run-position`, which the operator initiates through gz-obpi-pipeline. Confirm the landed count with `uv run gz adr status ADR-0.35.0` first.
3. Put an open maintenance ruling only when the operator asks for one, and one at a time.

## Pending Work / Open Loops

- Everything in the Pending Work of the handoff of 2026-10-11T09:21Z stands, except: GHI #997 [settled] is closed, v0.34.9 is released, and both patch-release repairs are made.
- The in-flight path of `gz patch release` is covered by unit tests only until v0.35.0 closes.
- The v0.34.9 release notes still list the already-bumped path under Known issues; that entry is a dated record and the next release's notes will carry the fix.

## Verification Checklist

- `git status -sb` and `git log --oneline -4`: main even with origin, clean; 19cc94d9d is the fix.
- `uv run -m unittest tests.adr.test_patch_release_in_flight`: 13 tests pass.
- `uv run gz patch release --dry-run`: prints `0.34.9 -> 0.34.10 (proposed)` while v0.34.9 is the newest tag and no version is in flight.
- `uv run gz skill audit`: exit 0; `gz-patch-release` is 1.13.0.

## Evidence / Artifacts

- `src/gzkit/commands/patch_release.py`
- `src/gzkit/commands/ceremony_steps.py`
- `tests/adr/test_patch_release_in_flight.py`
- `tests/commands/test_ceremony_release_handover.py`
- `docs/user/manpages/patch-release.md`
- `.gzkit/skills/gz-patch-release/SKILL.md`
- `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md`
- Commit 19cc94d9d; falsifiability receipt arb-red-commit-19cc94d9d881-ef5b4ea872c84adc9802d1fb71fd80d5 (inconclusive about the run: 12 hunks killed, none survived, the rest ungradable).

## Settled Rulings

1459 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
