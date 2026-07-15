# Plan — OBPI-0.0.65-04-orientation-single-location-scan

**Parent ADR:** ADR-0.0.65-handoff-system-consolidation (foundation, heavy)
**OBPI:** OBPI-0.0.65-04-orientation-single-location-scan

## Context

ADR-0.0.65 § Decision item 4 ("Align the orientation reader with the resolved
canonical location"). OBPI-01 canonized `.gzkit/handoffs/` as the single write
location and migrated the 24 per-ADR handoffs (verified: `find docs/design/adr
-name "*.md" -path "*/handoffs/*"` returns 0). With the per-ADR sources now
empty, the GHI #529 dual-scan union in `_candidate_handoff_dirs()` is dead
weight — the OBPI-04 prerequisite (OBPI-01 `attested_completed`) is met.

`_candidate_handoff_dirs(repo_root)` currently returns
`[.gzkit/handoffs] + sorted(adr_root.glob("**/handoffs"))`. Collapse it to a
single-element list.

## Files (brief allowlist)

- `scripts/session_orientation.py` — collapse `_candidate_handoff_dirs()`; delete
  the ADR-glob dual-scan; remove both `GHI #529` markers and the `docs/design/adr`
  path reference (REQ-04-03 file-wide check).
- `tests/scripts/test_session_orientation.py` — replace the dual-scan test with
  single-scan assertions; add REQ-derived `@covers` tests.

## Decision: the two GHI #529 markers are distinct

Commit `2ab33914` bundled two fixes under GHI #529:
- **fix #1 — dual-scan** (`_candidate_handoff_dirs` ADR-glob): DELETE entirely.
- **fix #2 — frontmatter filter** (`_looks_like_handoff`): KEEP the behavior
  (`.gzkit/handoffs/AGENTS.md` still needs excluding under a single scan). Drop
  only the bare `GHI #529` token from its docstring to satisfy REQ-04-03's
  file-wide substring check; preserve the behavioral rationale prose.

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **REQ-0.0.65-04-01** — `_candidate_handoff_dirs()` returns a length-1 sequence
   containing exactly `Path(".gzkit/handoffs")` resolved against repo root,
   regardless of whether `docs/design/adr/**/handoffs/` dirs exist.
   - RED: test asserting `len(dirs) == 1` and `dirs[0] == repo_root/".gzkit"/"handoffs"`
     even when an ADR-package `handoffs/` dir is present. Watch it fail (currently
     returns 2 when an ADR handoffs dir exists).
   - GREEN: collapse the function body to `return [repo_root / ".gzkit" / "handoffs"]`.
2. **REQ-0.0.65-04-02** — orientation reports the newest `.gzkit/handoffs/` entry
   correctly (AGENTS.md filter still excludes non-handoffs).
   - RED: repurpose/keep the newest-wins test scoped to `.gzkit/handoffs/` only.
   - GREEN: already satisfied by step 1's collapse; confirm green.
3. **REQ-0.0.65-04-03** — `scripts/session_orientation.py` contains zero
   `docs/design/adr` references and zero `GHI #529` references.
   - RED: file-read substring test asserting neither literal appears. Watch it
     fail (both currently present).
   - GREEN: remove line 160-162 ADR-glob; drop `GHI #529` from both docstrings
     (rewrite `_looks_like_handoff` docstring to keep the AGENTS.md-filter
     rationale without the marker token).
4. REFACTOR: tidy the collapsed docstring; confirm `collect_handoff` loop over the
   single dir is clean. Delete the now-dead `test_discovers_adr_package_handoffs_and_unions_with_gzkit`
   dual-scan test.

## Verification (shell-less, per brief)

- `uv run gz validate --documents`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run -m unittest tests.scripts.test_session_orientation`
- `uv run -m unittest tests.governance.test_orientation_freshness`

## Notes

- Output shape / char budget / section ordering must stay stable (Requirement 6):
  the collapse is internal to dir enumeration; `collect_handoff` and `render`
  are untouched behaviorally.
- Denied paths honored: no SKILL.md, no handoff_api.py, no CLI parser surface.

## Plan-Before-Exploration Disclosures (Step 6a)

1. **Destination-in-mind:** Before writing this plan I had already concluded the
   fix is a one-line collapse of `_candidate_handoff_dirs` to
   `[repo_root/".gzkit"/"handoffs"]` plus marker removal — the brief and code
   made the shape obvious. Disclosed rather than reconstructed.
2. **Rejected alternatives:** (a) Keeping `_candidate_handoff_dirs` as a helper
   returning one element vs. inlining the single path into `collect_handoff` —
   kept the helper to minimize `collect_handoff` diff and preserve the existing
   test seam. (b) Removing `_looks_like_handoff`'s GHI #529 provenance entirely
   vs. rephrasing to keep the rationale — chose rephrase-keep-behavior, since the
   AGENTS.md filter is still live and only the marker token conflicts with REQ-03.
