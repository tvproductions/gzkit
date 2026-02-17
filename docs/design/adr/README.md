# ADR Structure and Migration Notes

This document captures the current ADR layout, migration rules, and settled decisions after the February 17, 2026 docs restructure.

## Canonical Layout (Current)

```
docs/design/adr/
├── foundation/
│   └── ADR-0.0.z-{slug}/
│       ├── ADR-0.0.z-{slug}.md
│       ├── ADR-CLOSEOUT-FORM.md (optional by workflow)
│       ├── obpis/
│       └── audit/ (optional)
├── pre-release/
│   └── ADR-0.y.z-{slug}/
│       ├── ADR-0.y.z-{slug}.md
│       ├── ADR-CLOSEOUT-FORM.md (optional by workflow)
│       ├── obpis/
│       └── audit/ (optional)
├── <major>.0/              # post-1.0 releases, e.g. 1.0/, 2.0/, ...
│   └── ADR-<major>.y.z-{slug}/
└── pool/
    └── ADR-pool.{slug}.md
```

## Rules Locked by Restructure

1. `ADR package folder` is the canonical unit for location and linking (not `adr-0.x.x` series folders).
2. `OBPI` is the operational unit of completion, and OBPIs live inside each ADR package under `obpis/`.
3. Pool entries remain proposal-only and do not receive OBPI files while still in `docs/design/adr/pool/`.
4. Foundation and pre-release semantics are explicit top-level buckets:
   - Foundation: `ADR-0.0.z`
   - Pre-release: `ADR-0.y.z` where `y > 0`
5. Release sequencing after pre-release follows major buckets (`1.0/`, `2.0/`, ...) containing ADRs like `ADR-1.y.z-*`.
6. `docs/design/obpis/` is deprecated for new work. New OBPIs must be ADR-local under `.../obpis/`.

## Migration Guidance

When moving or promoting ADRs:

1. Move the full ADR package directory, not individual files.
2. Update all internal and external links that reference the old location.
3. Remove obsolete empty directories created by old series patterns.
4. Keep metadata (`id`, `parent`, `promoted_from`) unchanged unless decision lineage changed.

## Lessons Learned

1. Folder taxonomy should match operational practice, not historical grouping convenience.
2. Series-level folders (`adr-0.2.x`) caused link churn and ambiguous ownership when only one ADR package existed.
3. Promoting pool work is clearer when destination is a concrete ADR package path.
4. Documentation drift appears quickly if path contracts are implied instead of explicitly documented.

## Decisions (2026-02-17)

1. `docs/design/obpis/` is formally deprecated for authoring. ADR-local `obpis/` is canonical.
2. Lint now includes a hard ADR path-contract check that fails on legacy series-folder link forms (`adr-*.x` paths).
3. Release buckets are numeric major/minor directories: `1.0/`, `2.0/`, ...
4. This restructure is documentation and operations alignment work; no separate pool ADR closeout is required.
