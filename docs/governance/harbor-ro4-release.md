<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-4 specification — release detached from the ADR

**2026-10-25. Status: specified; every open question ruled the same day.** Operator: **g0**. Repair order RO-4 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving version. Sequenced after RO-5 ([its specification](harbor-ro5-work-packages.md)), because the Release Package ships work packages.

## Already ruled in the record

- Operator, 2026-10-16: *"adrs are not releases"*. 2026-10-17: *"We're not sunsetting ADRs. They've got to stop driving release"*.
- R2 (2026-10-17): *"Gate 5 stays per work package with a release attestation on top"*. R3: *"the Release Package is the plan and the ledger release record the shipped claim, `gz-release` subsumes `gz-patch-release`"*.
- Q-08 (`ieee/OPEN-QUESTIONS.md`, ruled 2026-09-22): *"`version_sync` stops deriving the package version from an ADR identifier. The missing `kind` guard is repairable immediately and independently"*.
- Q-10 (ruled 2026-09-22): the release record is *"a ledger release record: an L2 event asserting the approved content of a version"*.
- Requirements model § 7: *"The release target is Release Package membership, mutable through a `gz` verb that books a ledger event; a slip changes membership and nothing else. `released_in` derives from the ledger release record and never changes"*; *"The Release Package says which outcomes advance in a version"*; *"No version appears in any outcome, work package or REQ id"*.

## Rulings of 2026-10-25

1. **A Release Package lives in `data/catalog/releases.json`, edited only through `gz` verbs** (selection *"A"*) that book each membership change to the ledger. This amends the contract's § The Release Package, which named one Markdown document per version under `docs/design/releases/`.

2. **One `release_recorded` event for every release** (selection *"A"*): the version, its Release Package members and the R2 release attestation. Past `patch_release_event` rows stay as history, read as the same claim; none are written after.
3. **`gz closeout` is keyed to a Release Package, settled by the row** (*"`gz closeout` keyed to a Release Package"*, witness *"a dry-run closeout keyed to an empty Release Package"*): `gz closeout <version>` is the release ceremony, ending in `release_recorded`; per-package Gate 5 lives in the work-package close (RO-5 ruling 5); the `gz-release` skill drives it and subsumes `gz-patch-release` (R3).

4. **The version is the operator's, with a floor and a recommendation** (operator: *"A & C together"*): the operator sets it on the Release Package; the verb refuses a number below what the members require (any delivery outcome needs at least a minor bump; only `runtime`-eligible repairs allow a patch); `gz release pressure` recommends. This replaces `check_version_sync`'s ADR-derived target. **Semver rule** (operator, verbatim: *"release packages drive semver and semver rules. prd drives major, release package drives minor, ghi pressure drives patch. confirm."*): a major bump requires a PRD version change and nothing else allows one (as `GovZero/releases/README.md:41` already holds); a minor bump is a Release Package of delivery work; a patch is driven by GHI pressure over `runtime` repairs. `gz release pressure` reads GHIs and recommends a patch only (operator, verbatim: *"let the gz pressure tool work with ghis for patch..."*); a minor comes from a Release Package and a major from the PRD, neither from the pressure reading.
5. **RO-4 carries GHI #1248**, the pressure verb and its data file included, as a consequence of ruling 4 (and RO-5 ruling 2: a repair order carries its issues).

6. **Members are work packages and their issues** (selection *"A"*): delivery and repair packages; legacy ADR work is not a member and is not backfilled.
7. **The `release_package.md` template retires, settled by rulings 1 and 6:** the package is a catalog record, not a document, and its members are packages, not REQ states (model § 7).

## Tranches (for the contractor)

The contractor stops and waits on every structural question; the names of new verbs and events are among them.

1. **Store and events.** `data/catalog/releases.json` and its schema (version, members, state); the membership verb booking each change to the ledger; `release_recorded` (ruling 2) with the version, members and release attestation.
2. **Version.** `version_sync` stops deriving from the ADR id (`version_sync.py:18`, Q-08) and `closeout.py:557-563` stops bumping from it; the floor rule (ruling 4); `gz release pressure` and its data file (GHI #1248).
3. **Closeout.** `gz closeout <version>` (ruling 3), its dry run against an empty Release Package, the release attestation (R2), ending in `release_recorded`.
4. **Skills and canon.** `gz-release` subsuming `gz-patch-release` (R3); `gz validate --version-release` reading release records; the ADR-as-carrier text retired with retention maps in `GovZero/releases/README.md`, `GovZero/adr-lifecycle.md` and the sibling `patch-release.md`, `minor-release.md` and `major-release.md`; the template retired (ruling 7).

## Restoration (RO-4's punch-list lines)

Each tranche adds a § Punch list line for what it disconnects, reroutes or changes: at least the tests of `version_sync` and `closeout`, the `--version-release` audit and its manifests, and the `gz-patch-release` flow until `gz-release` replaces it. RO-4 closes when those lines are cleared.

## Witness

`gz validate --version-release`; a dry-run `gz closeout` keyed to an empty Release Package (the row's).

## Current state (research of 2026-10-25)

Nothing of RO-4 has landed. `version_sync.py:18` derives the version from the ADR id and `closeout.py:557-563` bumps it; `patch_release_event` (`ledger_events.py:919`) is the only release event; `gz closeout` is keyed to the ADR (`closeout.py:665`); `gz validate --version-release` reads pyproject, tags and manifests; GHI #1248 is open; the ADR-as-carrier text stands in `GovZero/releases/README.md:39-43` and `GovZero/adr-lifecycle.md:227-277`.
