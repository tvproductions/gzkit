---
mode: CREATE
adr_id: ADR-0.0.17
branch: main
timestamp: "2026-04-20T02:54:48Z"
agent: claude-code
obpi_id:
session_id:
continues_from:
---

## Current State Summary

v0.25.13 patch release shipped successfully to GitHub
(https://github.com/tvproductions/gzkit/releases/tag/v0.25.13). During
release ceremony, closed five GHIs (#242, #251, #252, #253, #255) and
landed an in-flight fix to `src/gzkit/validate_pkg/sync_parity.py` for a
macOS `/var` ↔ `/private/var` symlink defect that was blocking the
`gz git-sync` unittest hook. Post-release triage of open GHIs closed three
duplicates (#244, #245, #248 → #243). Ten open GHIs remain, sorted into
priority bands. Operator paused before executing the P1 direct-fix sweep.

## Important Context

- **Tag recovery on v0.25.12.** The email-scrub commit
  (`7939b30a chore(privacy): scrub email from briefs and ledger`) rewrote
  history. The `v0.25.12` tag was orphaned on commit `e3bd0e7b` (not
  reachable from `main`). Early this session it was force-retagged to
  `b7069aa2` (the main-reachable twin) and force-pushed. `git describe`
  now resolves cleanly.
- **Discovery doctrine.** `gz patch release` uses `git log v0.25.12..HEAD`
  walking GitHub-canonical closure keywords (`Closes|Fixes|Resolves #N`).
  Project uses `(GHI #N)` as a citation form, which is explicitly NOT a
  closure. Recent commits (#251/#252/#253 perf sweep) used citation form;
  GHIs had to be closed manually via `gh issue close` before the release
  narrative could be drafted, but even after closing, dry-run reported 0
  qualifying GHIs because no commit in-range carries closure keywords.
  Release still shipped on the operator-authored narrative; this is a
  known workflow gap and matches the doctrine recorded in the v0.25.11
  release notes for GHI #233.
- **Lock-glob dedup.** Four independent filings (#243, #244, #245, #248)
  all describe the exact same defect in
  `src/gzkit/commands/obpi_precomplete.py:174-200` — `_check_lock_held`
  globs `.gzkit/locks/*.json` but lock files live at
  `.gzkit/locks/obpi/<OBPI-ID>.lock.json`. Consolidated under #243.
- **Defect-fix routing.** Direct-fix vs OBPI ceremony decision governed
  by `.gzkit/rules/defect-fix-routing.md` thresholds: ≤10 source lines,
  single module, ≥3 recent `fix(...)` precedent commits, in-flight
  surface, unit-testable. All three P1/P2 trivial fixes below meet these
  thresholds.

## Decisions Made

- **Decision:** Force-retag v0.25.12 to `b7069aa2` (main-reachable twin
  of orphaned `e3bd0e7b`).
  **Rationale:** Only path to make `gz patch release` discovery work
  against a sensible commit range.
  **Alternatives rejected:** Cut v0.25.13 from the orphaned-tag baseline
  (would have shipped a bogus 43-GHI narrative); hold the release (no —
  real substance to ship).

- **Decision:** Close #251, #252, #253 on commit evidence, leave #237
  (meta-tracker) open.
  **Rationale:** User attested work done; commits surgically match GHI
  titles.
  **Alternatives rejected:** Close all four — #237 title says "Track …
  sweep" (intended to stay open until the batch lands).

- **Decision:** Close #244, #245, #248 as duplicates of #243.
  **Rationale:** Four identical bug reports; consolidation reduces
  triage noise.
  **Alternatives rejected:** Keep all four as separate line items.

- **Decision:** Route the `sync_parity.py` macOS symlink fix as an
  in-flight direct fix rather than opening a new GHI/OBPI.
  **Rationale:** ≤10 lines, single module, blocking my current workflow
  — canonical in-flight defect per Invariants 2/4 and
  `defect-fix-routing.md`. Shipped in the release commit.
  **Alternatives rejected:** File a GHI and hold the release; ship with
  the defect unfixed.

## Immediate Next Steps

1. **Fix #243 (lock_held shallow glob).** Edit
   `src/gzkit/commands/obpi_precomplete.py:174-200`; update
   `_check_lock_held` to glob `.gzkit/locks/**/*.json` (or specifically
   include `.gzkit/locks/obpi/`) so lock files created by
   `gz obpi lock claim` are discoverable. Add a unit test that writes a
   lock under the `obpi/` subdir and asserts `_check_lock_held` finds it.
   Commit: `fix(obpi-precomplete): recurse into locks/obpi/ subdir (GHI #243)`.

2. **Fix #246 (ADR schema regex).** Edit `src/gzkit/schemas/adr.json:16`;
   relax the `id` pattern from `^ADR-[0-9]+\.[0-9]+\.[0-9]+$` to accept
   the slug-suffixed form that `gz adr promote` writes
   (`^ADR-[0-9]+\.[0-9]+\.[0-9]+(-[a-z0-9-]+)?$`). Re-run
   `tests/commands/test_adr_promote.py::TestAdrPromoteTaxonomyRoundtrip`.
   Commit: `fix(schema): accept slug-suffixed ADR ids from gz adr promote (GHI #246)`.

3. **Fix #247 (sync_copilot_instructions skip).** Edit
   `src/gzkit/sync_surfaces.py:612-623`; hoist the copilot-instructions
   render out of the `if canonical_rules:` guard so template edits to
   `src/gzkit/templates/copilot.md` always propagate. Add a unit test
   verifying copilot sync fires without canonical rules present.
   Commit: `fix(sync): always sync copilot instructions from template (GHI #247)`.

4. **Validate + sync.** Run `uv run gz check`, `uv run gz validate
   --surfaces`, then `uv run gz git-sync --apply` to land all three
   fixes in a single clean sync.

5. **Reassess #241** (`gz adr promote` bullet parsing). If a scan of
   `src/gzkit/commands/promote.py` confirms ≤30 lines and single-module
   containment, take it direct; else route to OBPI ceremony.

## Pending Work / Open Loops

- **Release discovery workflow gap.** `gz patch release` cannot see
  GHIs closed via `gh issue close` without corresponding
  `Closes/Fixes/Resolves #N` commits in range. Narrative release notes
  had to be operator-authored for v0.25.13. Consider filing a GHI to
  either (a) teach discovery to consult GH closure state, or
  (b) document the authorial workaround in the `gz-patch-release` skill.

- **P3/P4 queue** — remaining after the P1/P2 sweep:
  - #249 (Heavy/Foundation bucketing residuals in `docs/governance/**`)
    — 8 locations, chore or Lite OBPI
  - #250 (closeout Step 5 skill/CLI prompt ambiguity) — direct fix
  - #238 (`gz validate --brief-headings` scope) — Heavy OBPI
  - #239 (`PostToolUse ruff --no-fix` hook) — settings-surface OBPI
  - #240 (wire gz-justify into Stage 0 as pre-reflex) — pipeline OBPI

- **Meta-tracker #237** stays open until the 2026-04-19 pool amendment
  sweep lands.

## Verification Checklist

- [ ] `uv run -m unittest -q` passes (baseline clean at resume time)
- [ ] `git branch --show-current` returns `main`
- [ ] `git status` shows clean working tree
- [ ] `git describe --tags HEAD` resolves to `v0.25.13-N-g<sha>`
- [ ] `gh issue list --state open` shows 10 open GHIs (237, 238, 239, 240, 241, 243, 246, 247, 249, 250)
- [ ] `uv run gz patch release --dry-run` reports tag `v0.25.13`

## Evidence / Artifacts

- `RELEASE_NOTES.md` — v0.25.13 narrative entry
- `docs/releases/PATCH-v0.25.13.md` — patch release manifest
- `src/gzkit/validate_pkg/sync_parity.py` — macOS symlink fix landed this session
- `src/gzkit/commands/obpi_precomplete.py` — file targeted by #243 fix
- `src/gzkit/schemas/adr.json` — file targeted by #246 fix
- `src/gzkit/sync_surfaces.py` — file targeted by #247 fix
- `.claude/rules/defect-fix-routing.md` — routing thresholds for P1/P2 direct fixes

## Environment State

- Python 3.14.3 (via uv) — note: slightly ahead of declared 3.13+ floor
- Platform: darwin 25.4.0 (macOS)
- Tests: unittest suite at ~17s post-#253 perf work
