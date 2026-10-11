---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-11T09:52:45Z'
agent: claude-code
session_id: 24f0562f-2e6d-46b4-978a-a506149330a6
continues_from: .gzkit/handoffs/20261011T092143Z-maintenance-closed-map-written-return-to-feature-work.md
---

## Current State Summary

v0.34.9 is released. After the previous handoff the operator ordered the patch release; the gz-patch-release ceremony ran from discovery to publication on 2026-10-11. 26 issues were discovered since v0.34.8: 19 qualified and are in the notes, 3 landed fixes under trackers that stay open, and 4 stay out. The release commit is 0efb147ec, the tag v0.34.9 is on main, the GitHub release exists and the publish workflow for the tag concluded success. main is even with origin and clean after this handoff's sync. Nothing is in flight. Everything else is as the previous handoff and `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` say.

## Important Context

Read `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` first, then the previous handoff, which carries the operator's state, the workflow fronts and the mechanics; none of that changed. Two facts are new. First, the previous handoff's advised step 3 (the patch release) is done and must not be advised again. Second, `gz patch release --full` was not used and should not be until it is repaired: its body extraction would have published 41 versions as the release body (insight `patch-release/full-path-body-is-cumulative`). The skill path, which slices the newest block, is the one that works.

## Decisions Made

- [operator-ruled] The v0.34.9 release notes are approved as drafted, and GHI #1154, #1155 and #1185 are still-open trackers for this release, described only by what landed (verbatim: "approved, then git sync").
- [agent-chose] Added one upgrade-note sentence to the notes after approval, restating that the flags named in #1163 and #1166 are removed; it is disclosed in the entry's Gate Evidence.
- [agent-chose] Left #1167, #1169, #1182 and #1168 out of the notes and the changelog, on the v0.34.8 precedent: help text, a docstring, a data file and a script, with no shipped source change.

## Immediate Next Steps

1. Show the operator `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` and take their ruling on what to draw next. Execute nothing before it.
2. If the operator returns to feature work: `ADR-0.35.0` item 15, `OBPI-0.35.0-15-pipeline-run-position`, which the operator initiates through gz-obpi-pipeline. Confirm the landed count with `uv run gz adr status ADR-0.35.0` first.
3. Put an open maintenance ruling only when the operator asks for one, and one at a time.
4. Before v0.35.0 closes, the operator will need to initiate two repairs to `gz patch release`: a path for an already-bumped version, and the body extraction of its full path.

## Pending Work / Open Loops

- Everything in the previous handoff's Pending Work stands, except that GHI #997 [settled] is closed and the patch release is done.
- GHI #1154, #1155 and #1185 remain open with partial landings shipped in v0.34.9.
- Insights with no go, added since: `patch-release/full-path-body-is-cumulative`.

## Verification Checklist

- `git status -sb` and `git log --oneline -4`: main even with origin, clean; 0efb147ec is the release commit.
- `git tag --points-at 0efb147ec`: v0.34.9.
- `gh release list --limit 2`: v0.34.9 is Latest.
- `gh run list --workflow release.yml --limit 1`: the v0.34.9 run completed with success.
- `uv run gz validate --changelog`: exit 0.
- `uv run gz adr status ADR-0.35.0`: 10 of 20, item 9 repudiated.

## Evidence / Artifacts

- `RELEASE_NOTES.md` (the v0.34.9 entry)
- `CHANGELOG.md` (the v0.34.9 block, 22 issue entries)
- `docs/releases/PATCH-v0.34.9.md`
- `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md`
- `.gzkit/handoffs/20261011T092143Z-maintenance-closed-map-written-return-to-feature-work.md`
- Commit 0efb147ec (release: v0.34.9); release https://github.com/tvproductions/gzkit/releases/tag/v0.34.9

## Settled Rulings

1458 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
