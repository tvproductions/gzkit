# Changelog

All notable changes to {project_name} are recorded here. This is the
*exhaustive, developer-facing* record of every user-visible change; the curated
*why-it-matters* narrative for each release lives in `RELEASE_NOTES.md`. The two
are distinct artifacts and never collapse into each other.

Format adapted from the [Good Docs Project changelog
template](https://www.thegooddocsproject.dev/template/changelog). Versions follow
Semantic Versioning; dates use the ISO `YYYY-MM-DD` format. Because {project_name}
commits to `main` and tracks work by GitHub Issue (GHI), **every entry cites its
`GHI #N`** in place of the upstream template's pull-request link. Each version's
entries are the derived projection of the GHIs closed since the previous tag.

<!--
Per-version block shape follows. Prepend the newest version at the top. Omit any
category with no entries. Early in a project's life, only Added / Changed / Fixed
may be needed; expand to the full set as the product matures.
-->

## {version} ({date})

### Release highlights

<!-- 1-2 sentences on the most important changes this release. -->
- {highlight}

### Added

<!-- New capabilities. Emphasize the problem solved or the benefit. -->
- {added_entry} (GHI #{ghi})

### Changed

<!-- Changes to existing behavior (error messages, load times, defaults). -->
- {changed_entry} (GHI #{ghi})

### Deprecated

<!-- Soon-to-be-removed capabilities; name the recommended alternative. -->
- {deprecated_entry} (GHI #{ghi})

### Fixed

<!-- Bug fixes; describe the user-visible benefit, not the implementation. -->
- {fixed_entry} (GHI #{ghi})

### Security

<!-- Vulnerability fixes; cite CVE IDs and impact where applicable. -->
- {security_entry} (GHI #{ghi})

### Breaking changes

<!-- Incompatible changes requiring user action; include upgrade steps. -->
- {breaking_entry} (GHI #{ghi})
