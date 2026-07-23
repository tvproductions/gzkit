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

## v0.33.1 (2026-07-23)

### Added

- Good Docs Project changelog and release-notes template discipline: canonical templates (`.gzkit/templates/changelog.md`, `.gzkit/templates/release_notes.md`), a `paths:`-scoped rule binding both files, and this changelog surface (GHI #685)
- Validator firing when a child OBPI declares a `[STRUCTURAL-FENCE]` REQ but the parent ADR lacks the `## Boundary Invariants` section that kind's proof channel requires (GHI #538)
- Mechanical resume authorization gate: a resuming agent must book explicit operator authorization before its first mutating action, replacing the prose-only banner (GHI #574)
- Enrollment-completeness enumeration wiring the gate5-floor and grader-gaming enforcement-claim sources into the single production-discovery seam (GHI #648)
- `gz cli audit` check that manpage flag descriptions agree with the parser (required vs optional, defaults, choices, env fallbacks), not merely that a flag is mentioned (GHI #693)
- `rendition_fingerprint` provenance field and fail-closed gate detecting committed-rendition byte drift past its Gate-5 attestation (GHI #694)
- Manifest-aware `kind` guard at the `register-adrs`/`init` ledger ingress refusing a hand-placed `kind: foundation` ADR absent from the grandfather roster (GHI #706)
- `gz git-sync` pre-staging guard refusing `git add -A` when the index already holds `src/**`/`tests/**` paths (GHI #708)

### Fixed

- `gz handoff` documents no longer emit a trailing blank line that tripped the end-of-file-fixer hook (GHI #684)
- Stage-4 present-evidence no longer counts proven SUPPORT REQs as attestability blockers, so coverage accounting reflects only genuinely uncovered BEHAVIOR requirements (GHI #683)
- Airlock exit-side ledger booking is now failure-atomic, so a partial transit can no longer leave an inconsistent L2 record (GHI #679)
- Reconciled 233 orphaned `obpi_created` ledger events across 24 feature ADRs (0.27.0–0.51.0) that asserted OBPI briefs never authored on disk (GHI #584)
- `Ledger.append` is now failure-atomic (serialize-then-single-write, truncate-on-failure) with pinned UTF-8, so an interrupted write can no longer corrupt the JSONL ledger (GHI #687)
- Bound the two `continues_from` pointer resolvers so they can no longer silently desync and wrongly archive or skip a live chain link (GHI #689)
- Handoff validator now requires section population, not mere heading presence, rejecting hollow handoffs (GHI #692)
- Handoff format preserves every authored next step, operator ruling, and decision attribution across the session boundary (GHI #696)
- Handoff `adr_id` is now optional, so handoffs carry continuity for any unit of work, not only ADR-scoped work (GHI #709)
- Documented the brief-reconcile existence-vs-liveness blind spot and routed its cure to the event-registry collapse rather than entrenching a new validator dimension (GHI #581)
- brief-reconcile `req_count` dimension recognizes the REQ taxonomy and checked acceptance-criteria boxes, ending the false-positive drift that blocked pipeline Stage 1→2 entry (GHI #664)
- `gz brief reconcile --apply` re-measures drift after writing amendments and fails closed on residual drift instead of certifying the pre-mutation state (GHI #677)
- `reconcile_brief` no longer existence-checks terminal (completed/attested) briefs against the current tree (GHI #707)
- CLI color decision honors `FORCE_COLOR=0`/`NO_COLOR`, so `gz test` and `gz git-sync --test` pass regardless of ambient `FORCE_COLOR` (GHI #663)
- Acceptance-criteria REQ parser tolerates bold kind tags (`**[BEHAVIOR]**`), so decorated REQs are no longer dropped from coverage (GHI #700)
- `gz validate` no longer silently drops the six solo-only scopes when combined with another scope under a false all-passed (GHI #704)
- Repointed the `governance-core` workflow order off the deprecated `gz gates` verb onto `gz closeout`, and stopped false completion-block reports for unrelated complete OBPIs (GHI #705)
- `gz adr audit-check` covers-backfill scan excludes withdrawn OBPIs' REQs, unblocking closeout of ADRs that withdraw OBPIs whose `@covers` tests remain in the tree (GHI #695)
- Hardened enforcement-floor negative controls: expected exit codes, banned empty-directory fixtures, decomposed composite claims, subprocess NCs pointed at the working tree (GHI #699)
- `gz plan audit` honors the brief's `**CREATE**` markers and `gz brief reconcile` skips glob prerequisites, so first-implementation OBPIs no longer deadlock (GHI #626)
- Resolved duplicate invariant-tier corpus entries for the "Correction vs enhancement" directive that made AGENTS.md recomposition unsatisfiable (GHI #635)
- Closed the `gz content remember` footgun with a guarded, orchestrated capture→compose→commit canon-landing flow across all consumers (GHI #654)
- Replaced the ADR-0.0.37 canon→AGENTS.md derivation facade with a content-coherence gate that fails closed unless the committed rendition contains every corpus invariant-tier entry verbatim (GHI #623)
