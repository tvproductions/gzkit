# Changelog

All notable changes to gzkit are recorded here. This is the *exhaustive,
developer-facing* record of every user-visible change; the curated
*why-it-matters* narrative for each release lives in
[`RELEASE_NOTES.md`](RELEASE_NOTES.md). The two are distinct artifacts and never
collapse into each other.

Format adapted from the [Good Docs Project changelog
template](https://www.thegooddocsproject.dev/template/changelog). Versions follow
Semantic Versioning; dates use the ISO `YYYY-MM-DD` format. Because gzkit commits
to `main` and tracks work by GitHub Issue (GHI), **every entry cites its
`GHI #N`** in place of the upstream template's pull-request link. Each version's
entries are the derived projection of the GHIs closed since the previous tag.

Canonical shape: `.gzkit/templates/changelog.md`. Discipline: `.gzkit/rules/changelog-release-notes.md`.

## [Unreleased]

### Added

- Good Docs Project changelog and release-notes template discipline: canonical templates (`.gzkit/templates/changelog.md`, `.gzkit/templates/release_notes.md`), a `paths:`-scoped rule binding both files, and this changelog surface (GHI #685)

### Fixed

- `gz handoff` documents no longer emit a trailing blank line that tripped the end-of-file-fixer hook (GHI #684)
- Stage-4 present-evidence no longer counts proven SUPPORT REQs as attestability blockers, so coverage accounting reflects only genuinely uncovered BEHAVIOR requirements (GHI #683)
- Airlock exit-side ledger booking is now failure-atomic, so a partial transit can no longer leave an inconsistent L2 record (GHI #679)
