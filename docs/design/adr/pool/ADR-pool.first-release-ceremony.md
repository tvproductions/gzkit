---
id: ADR-pool.first-release-ceremony
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.first-release-ceremony: First-Release Ceremony (Pre-release → v0.1.0/v1.0.0)

## Status

Pool

## Intent

`gz-patch-release` (ADR-0.0.15) handles patch releases on a project that
already has a versioned release history. It does not cover the *first*
release — the moment a pre-release project crosses to v0.1.0 (or v1.0.0).
The first-release transition has different mechanics than a patch:

- **Changelog seeding** — no prior `CHANGELOG.md` to compare against; the
  diff-from-last-tag heuristic the patch ceremony depends on has no
  baseline.
- **Version-floor doctrine** — choosing v0.0.1 vs. v0.1.0 vs. v1.0.0 is a
  governance judgment call (operator-attested), not a mechanical bump.
  No skill currently surfaces the decision tree.
- **PyPI registration** — first-time package upload requires PyPI account
  + project namespace claim + trust-publisher provisioning; subsequent
  releases reuse the trust publisher transparently.
- **GitHub repository release setup** — release workflow installation,
  tag protection rules, and PyPI trust-publisher GitHub Actions wiring
  are one-time configuration the patch ceremony assumes pre-exists.

Surfaced under GHI #430 during authoring of
`docs/user/storybook/from-init-to-first-attested-release.md`. Loop 0 in
`docs/user/runbook.md` (added under GHI #428) Stage 8 currently points at
`/gz-patch-release`, which cannot deliver for a brand-new project — the
storybook arc loses cohesion at exactly the moment the system promises
to deliver its value.

## Decision

Pool. Carries the architectural intent for first-release ceremony as a
distinct surface from `gz-patch-release`. Promotion (foundation or
feature) decomposes the intent into briefs along the four mechanical
axes named above:

- Version-floor doctrine (governance rule + attestation matrix)
- Changelog seeding (CLI surface or template + first-tag baseline)
- PyPI registration (skill or runbook + trust-publisher provisioning)
- GitHub release setup (workflow scaffolding + tag protection)

Each axis is a candidate brief; whether they land as one foundation ADR
(doctrine + ceremony) plus one feature ADR (CLI/skill surface) or as a
single feature ADR with four briefs is a promotion-time call grounded
in `docs/governance/GovZero/obpi-decomposition-matrix.md`.

## Alternatives Considered

- **Extend `gz-patch-release` with first-release detection** — rejected
  at pool-authoring time as premature; conflates two ceremonies whose
  governance posture differs (first release is a one-time foundation
  event; patch release is a recurring feature event). Promotion may
  revisit this if decomposition shows the surface overlap dominates.
- **Runbook-only entry** — rejected because the GHI's named concerns
  (version-floor doctrine, attestation matrix for the first tag) are
  governance decisions, not procedure. Runbook prose without a
  doctrine-bearing ADR leaves the operator without an attestable
  decision path.
- **Defer until the first downstream consumer reaches v0.1.0** —
  rejected because the storybook arc already promises end-to-end
  coherence; the absence is doctrine drift surfaced now, not a future
  problem.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

Routing receipt: GHI #430 (closed `superseded` against this pool ADR
2026-05-10).

Related:
- ADR-0.0.15 (GHI-Driven Patch Release Ceremony) — sibling ceremony for
  recurring patch releases
- ADR-pool.release-hardening — 1.0.0 quality-gating posture (distinct
  from procedural ceremony; release-hardening answers "is the project
  ready", this ADR answers "what is the procedure")
- `docs/user/storybook/from-init-to-first-attested-release.md` § Stage 8
- `docs/user/runbook.md` § Loop 0 Stage 8 (Release)

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
