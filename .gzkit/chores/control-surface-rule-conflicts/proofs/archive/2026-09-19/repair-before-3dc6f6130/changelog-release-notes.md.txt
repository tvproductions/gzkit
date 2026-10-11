---
id: changelog-release-notes
paths:
  - "CHANGELOG.md"
  - "RELEASE_NOTES.md"
description: Release-documentation files follow the Good Docs Project templates, adapted to gzkit's GHI-tracked, commit-to-main reality
---

<!-- rule-version: 1.2.0 -->

# Changelog & Release Notes Discipline

> **Rule version:** `1.2.0` — scored for real under GHI #921 (2026-08-30). This rule sat in `data/advisory_scorecard_grandfather.json`, pinned at `1.1.0` against a version nobody recorded; the pin is stripped by any edit, so its clauses were re-read and its Coverage Ledger rows added or corrected in the same commit. Prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#changelog-release-notesmd). Binding rules unchanged.

> **Source of authority:** Good Docs Project templates —
> [changelog](https://www.thegooddocsproject.dev/template/changelog),
> [release-notes](https://www.thegooddocsproject.dev/template/release-notes).
> Canonical shapes: `.gzkit/templates/changelog.md`, `.gzkit/templates/release_notes.md`.
> Adopted under GHI #685.

## Two distinct artifacts (binding)

`CHANGELOG.md` and `RELEASE_NOTES.md` are **not the same thing** and never collapse into one another:

- **`CHANGELOG.md`** — the *exhaustive, developer-facing* record. Every user-visible change, sorted into fixed categories, terse. The **derived projection of GHIs closed since the previous tag**.
- **`RELEASE_NOTES.md`** — the *curated, reader-facing narrative*. Selective headlines, plain language, retains gzkit governance provenance (`### Gate Evidence`). Curates the *same* closed-GHI set the changelog derives from.

One source (closed GHIs), two projections. Never reshape one to imitate the other.

## Changelog rules (binding)

1. Conform to `.gzkit/templates/changelog.md`. Per-version sections, in order: Release highlights · Added · Changed · Deprecated · Fixed · Security · Breaking changes. Omit empty categories.
2. Semantic Versioning; ISO `YYYY-MM-DD` dates. Version header: `## {version} ({date})`.
3. **Every entry cites `GHI #N`.** gzkit commits to `main` and tracks by GHI, so GHIs replace the upstream template's PR/MR link. Never invent a PR link.
4. The changelog is a Layer-3 derived view: every user-visible GHI closed since the last tag MUST appear. Coverage is reconciled fail-closed at release time by `gz-patch-release` (which already enumerates closed-since-tag GHIs).

## Release-notes rules (binding)

1. Conform to `.gzkit/templates/release_notes.md`. Curate by reader impact; plain language; bug fixes in past tense, never opened with "Fixed the bug".
2. Retain the `### Gate Evidence` section — it traces the release to gate/attestation Layer-2 truth. Good Docs shape informs the narrative; it does not delete gzkit provenance.
3. Authored and updated through the `gz-patch-release` skill, not by hand.

## Enforcement

Teeth split by capability — a hermetic check cannot reach the network, so
coverage lives where the network access already is:

- **Structure (hermetic, offline):** `gz validate --changelog` fails closed on changelog shape — SemVer versions, ISO `YYYY-MM-DD` dates, category set, and one `GHI #N` citation per entry.
- **Coverage (release-time, networked):** `gz-patch-release` cross-checks that every closed-since-tag user-visible GHI appears before publish.
- **Release-notes:** conform to the template and are reviewed at release; structure and tone are judgment-class, attested at Gate 5 (no mechanical release-notes validator — the curated narrative is not machine-checkable).
- **Authoring procedure:** `.gzkit/skills/gz-patch-release/SKILL.md`.

> The `gz validate --changelog` structural scope is landed and runs standalone
> and at release-time (operator-chosen: not in the default `gz check`). The
> `gz-patch-release` coverage cross-check is the networked half.
