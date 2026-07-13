# {project_name} Release Notes

The *curated, reader-facing* narrative for each release — the *why-it-matters*
companion to the exhaustive `CHANGELOG.md`. Release notes are selective, not
exhaustive: they headline the changes that matter to readers and tell the story
of a version. The two are distinct artifacts and never collapse into each other.

Format adapted from the [Good Docs Project release-notes
template](https://www.thegooddocsproject.dev/template/release-notes): curate by
user impact, write in plain language spanning technical and non-technical
readers. {project_name}'s governance provenance (gate evidence, attestation) is
**retained** as gzkit-specific sections — the Good Docs shape informs the
narrative; it never deletes the audit trail. Each release curates the *same*
closed-GHI set that `CHANGELOG.md` derives exhaustively.

<!--
Per-version block shape follows. Prepend the newest version at the top. Omit any
optional section with no content. Write present tense except bug fixes (past
tense); never open a bug fix with "Fixed the bug", and don't explain how a bug
was fixed.
-->

## {version} ({date})

**ADR:** {adr_id} — {adr_summary}

### Highlights

<!-- 1-2 sentences on the most important items this release (Good Docs
     "High-level summary"). Omit if readers get frequent off-cycle updates. -->
{highlights}

### Improvements

<!-- Curated new capabilities and enhancements (Good Docs "New Features" /
     "Improvements"), ordered by reader impact. Cite the driving GHI/OBPI. -->
{improvements}

### Bug fixes

<!-- Curated fixes, emphasizing the user benefit. Past tense. -->
{bug_fixes}

### Known issues

<!-- Unresolved issues affecting readers, with workarounds where available. -->
{known_issues}

### Deprecated

<!-- Capabilities being phased out; name the migration path and removal timeline. -->
{deprecated}

### Gate Evidence

<!-- gzkit governance provenance — RETAINED, not optional. Gates satisfied, lane,
     human attestation (attestor + date), receipt IDs, test counts. Traces the
     release to Layer-2 ledger truth. -->
{gate_evidence}
