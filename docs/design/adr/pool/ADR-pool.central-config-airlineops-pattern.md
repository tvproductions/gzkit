---
id: ADR-pool.central-config-airlineops-pattern
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.central-config-airlineops-pattern: Central Config — AirlineOps Pattern

## Status

Pool

## Intent

Adopt a strong central-config pattern modeled after AirlineOps. gzkit
currently lacks a single canonical config surface: configuration is
distributed across at least seven locations today —

- `pyproject.toml [tool.<gzkit-key>]` for build-time and a small handful
  of runtime settings
- `.gzkit/manifest.json` for surface tracking
- `.gzkit/personas/*.md` frontmatter for persona-level traits
- `data/*.json` registries (security_surfaces, behave_coverage_waivers,
  chores_layout_waivers, flags, eval_feedback_thresholds, audit_thresholds,
  authoring_hint, advisor_archetype_rules, etc.)
- `.claude/settings.json` for Claude Code harness wiring
- `.claude/settings.local.json` for per-operator preferences
- Per-skill / per-rule frontmatter `paths:` and `description:` declarations

There is no single place an operator (or agent) can consult to answer
"what does gzkit consider configured for this project?" or change a
project-wide setting without hunting through seven file types. The
ADR-0.0.32 expansion to all harness surfaces surfaced this gap directly:
adding a `CORE_PERSONAS` registry, `CORE_TEMPLATES` registry, etc.,
multiplies the per-surface registry shape without a coordinating central
config surface to compose them.

AirlineOps' pattern (per operator framing, 2026-05-11) provides a strong
central-config seam that gzkit should adopt: a single canonical config
file (likely `.gzkit/config.yaml` or `.gzkit/config.toml`) that names
every project-level setting with explicit schema, and the per-surface
registries become typed views into that config rather than independent
config-shape definitions.

### Two-tier requirement — tunable config vs invariant registry (refinement, 2026-06-22)

The central-config shape gzkit needs is **not** a straight port of
AirlineOps'. AirlineOps' config is **mutable by design**: a three-layer
`defaults → settings → settings.local` deep-merge, and — critically — it
enforces **no programmatic immutability**. Its "invariant" values (Paths,
governance enums) are immutable only by *documentation convention*,
guarded by nothing at runtime.

gzkit's anti-vibing posture demands a second tier AirlineOps lacks. The
forcing example: OBPI-0.0.74-03 landed `GATE5_INVARIANTS` (the never-relax
floor) as a five-member frozenset at `src/gzkit/mx/invariants.py`, joining
`levels.py`, `disposition.py`, 20+ scattered frozensets, and ~30
`data/*.json` registries — textbook config sprawl that argues *for* central
config. But ADR-0.0.74 § Decision item 3 made it "a code constant
(**not** config)" deliberately, and § Risks #5 names why: the marker is a
skeleton-key surface, so the never-relax floor must be **un-relaxable at
runtime**. Relocating it into AirlineOps-style mutable config would make it
*more* tamperable — re-opening the surface ADR-0.0.74 closed.

Therefore gzkit's central config must distinguish two tiers:

- **Tunable config** — operator/project settings safe to override
  (lane defaults, template selection, thresholds, paths). AirlineOps'
  layered-merge pattern fits directly.
- **Invariant registry** — security-critical never-override values
  (the never-relax floor; integrity-class guards; PII/secrets surfaces).
  Centralized, schema-validated, and discoverable (the central-config
  win), but **programmatically tamper-proof, not runtime-tunable** — a
  layered override of an invariant-tier value must fail closed, not merge.
  `GATE5_INVARIANTS` is the canonical member of this tier.

This refinement does not change the park-then-promote decision below; it
constrains the schema the promoted ADR must design. A central config that
offers only AirlineOps' single mutable tier would be undersized for
gzkit's invariant surfaces on day one.

## Decision

Park until ADR-0.0.32 closeout completes (so the canonical-routing
invariant is fully landed and the surface inventory is stable; central
config that doesn't enumerate every canonical surface will be undersized
on day one). At that point, evaluate promotion:

- If a fifth `CORE_<SURFACE>` registry is added to gzkit (beyond skills /
  rules / personas / templates / chores), promotion is overdue — adding
  another registry without central composition multiplies fragmentation.
- If operator-facing per-surface config questions ("how do I override the
  default lane / kind / template for ADR creation?") start surfacing
  defects, promotion is urgent.
- If a configuration change crosses three or more of the seven config
  locations to land coherently, promotion is justified by coordination
  cost alone.
- If a second security-critical invariant-tier constant lands scattered
  (a new never-override set beyond `GATE5_INVARIANTS`), promotion is
  justified on safety, not just coordination — the invariant tier is the
  surface where sprawl is most dangerous, because a value that should be
  un-relaxable hidden among ordinary constants is a skeleton-key-by-
  obscurity risk (see § Two-tier requirement).

The cost of premature promotion: any central-config schema designed
before ADR-0.0.32 closeout would have to enumerate surfaces (skills,
rules, personas, templates, chores) that are still being established;
schema churn during enumeration is the dominant failure mode. The cost
of late promotion: per-surface registry shapes harden into a permanent
de-facto config surface that's harder to unify than a clean greenfield
schema would have been. The balance: closeout-then-promote sequencing.

## Alternatives Considered

**A. Promote now and build central config concurrently with the
ADR-0.0.32 OBPIs.** Rejected because central config that doesn't yet know
about personas/templates/chores (still being established by OBPIs 09-13)
would have to be retrofitted three times during the same release cycle.
Schema churn during enumeration is the dominant failure mode.

**B. Embed a stronger config layer inside `pyproject.toml [tool.gzkit]`
without a new top-level config file.** Considered; deferred. `pyproject.toml`
mixes build, distribution, project metadata, and tool config — making it
the central config surface multiplies its concerns. AirlineOps' pattern
(per operator framing) uses a dedicated config file, which gzkit should
emulate.

**C. Treat configuration fragmentation as a permanent feature.** Rejected
on the operator framing ("we should adopt that soon, the adr is exposing
that"). Fragmentation is a known cost; the operator has named it.

**D. Adopt cookiecutter-style template variables as the central config
mechanism.** Rejected because cookiecutter variables are init-time
substitutions, not runtime-readable config. gzkit needs both: init-time
substitution AND runtime introspection. AirlineOps' pattern provides
both via the dedicated config file.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
