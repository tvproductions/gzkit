---
id: ADR-pool.context-package-registry
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.context-package-registry: Context Package Registry

## Status

Pool

## Intent

Create a governed registry for installable or loadable context packages:
documentation bundles, skills, rules, examples, templates, and vendor-specific
control-surface fragments that agents can consume without treating arbitrary
markdown as trusted instruction.

Tessl and other spec-oriented systems make context and documentation packages a
first-class product surface. gzkit already has skills, generated control
surfaces, docs, rules, and vendor mirrors, but it lacks a package-level contract
that says what a context bundle contains, where it came from, how it was
validated, and which trust boundary it crosses.

**Target promotion kind:** feature candidate, with possible foundation doctrine
dependency if package trust tiers become identity-shaping.

**Comparator signals:** Tessl context/spec registry, BMAD method packaging, GSD
multi-runtime install flows, Compound Engineering plugin patterns.

## Decision

When promoted, define a `gzkit.context_package` registry and validation surface.
Candidate command shape:

```bash
gz context package list
gz context package inspect <id>
gz context package validate <path-or-id>
gz context package install <id> --vendor codex|claude|copilot|...
```

Each package record should include:

- `id`, `version`, `owner`, `source`
- `contents`: skills, rules, docs, templates, examples, command docs
- `trust_tier`: canon, generated mirror, vendor adapter, external reference
- `provenance`: source commit, generation command, receipt IDs
- `allowed_load_contexts`: session start, skill invocation, command help,
  research reference, operator prompt only
- `validation`: schema checks, injection scan, link checks, mirror sync status
- `exports`: vendor-specific rendered files with generated-file warnings

The registry should make context portable without weakening instruction
authority. External packages are references until promoted or explicitly
installed through a validated pathway.

## Alternatives Considered

- **Treat skills as the only package surface.** Rejected. Skills are executable
  workflow instructions; context packages also include docs, examples, rules,
  templates, and vendor adapters.
- **Let vendor directories be the registry.** Rejected. Vendor mirrors are
  rendered outputs, not source-of-truth packages.
- **Adopt an external package manager.** Rejected. gzkit needs repo-owned
  provenance, injection scanning, and lane-aware trust semantics.
- **Keep context loading ad hoc.** Rejected. Ad hoc context loading is one of the
  primary places prompt injection and doctrine drift can enter.

## Promotion Triggers

- Agent surfaces need portable installation across Codex, Claude, Copilot, or
  other vendors.
- Skills/rules/docs need versioned packages with provenance.
- Comparator intake identifies a reusable context bundle that should become
  governed rather than copied into prose.

## Related Destinations

- `ADR-pool.skill-control-surface-contract`
- `ADR-pool.vendor-capability-matrix`
- `ADR-pool.content-injection-scanning`
- `ADR-pool.research-skill-composition`
- `ADR-0.0.32-canonical-surface-packaging`
- `ADR-0.44.0-vendor-alignment-codex`

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
