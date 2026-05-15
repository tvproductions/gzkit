---
id: ADR-pool.skill-retire-on-delete-doctrine
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.skill-retire-on-delete-doctrine: Skill Retire-on-Delete Doctrine

## Status

Pool

## Intent

ADR-0.0.32 (canonical-surface-packaging) established the dual-surface model
(`.gzkit/skills/` ↔ `src/gzkit/skills/`) for authored canonical skills, and
OBPI-0.0.32-15 added `_classify_skill_file` with a `package_only` carve-out
for non-md package-machinery files (`_scaffolder.py`, JSON configs). During
ADR-0.0.32 closeout (demo 19, 2026-05-15), `gz upgrade --surface skills
--dry-run` reported `70 identical, 0 refreshed` against a baseline of 52
core skills — surfacing 18 SKILL.md files under `src/gzkit/skills/` that
carry `lifecycle_state: retired` + `archived_into: <successor>`
frontmatter and currently ride the `package_only` classifier path:

```
format/SKILL.md, lint/SKILL.md, test/SKILL.md, gz-attest/SKILL.md,
gz-audit/SKILL.md, gz-closeout/SKILL.md, gz-specify/SKILL.md,
gz-interview/SKILL.md, gz-typecheck/SKILL.md, gz-register-adrs/SKILL.md,
gz-adr-autolink/SKILL.md, gz-adr-check/SKILL.md, gz-adr-manager/SKILL.md,
gz-adr-recon/SKILL.md, gz-adr-verification/SKILL.md, gz-obpi-audit/SKILL.md,
gz-obpi-brief/SKILL.md, gz-obpi-sync/SKILL.md
```

The classifier doctrine carves out *non-md package-machinery* — applying
it to 18 retired SKILL.md stubs is scope creep that muddies the
canonical/package_only distinction and inflates the shipped wheel with
~20–30 lines of tombstone frontmatter per stub. Vendor mirrors
(`.claude/skills/`, `.github/skills/`, `.agents/skills/`) already carry
these as empty directories, confirming the mirror-sync has implicitly
treated them as non-content. The operator judgment at closeout was
explicit: *"tombstones not worth keeping if they are stubs."*

This pool ADR is the design-conversation home for the retire-on-delete
doctrine question — when a skill is superseded/consolidated, what is the
canonical disposition of its directory across `.gzkit/skills/`,
`src/gzkit/skills/`, and the three vendor mirrors?

## Decision

*(Pool placeholder — design conversation pending promotion.)*

Two candidate dispositions surfaced during GHI #464 routing:

**Option A — Delete-on-retire (operator-preferred per closeout judgment).**
When a skill is superseded/consolidated, its directory is deleted from
all five surface roots (`.gzkit/skills/`, `src/gzkit/skills/`,
`.claude/skills/`, `.github/skills/`, `.agents/skills/`). The
`_classify_skill_file` retired-frontmatter path may become unreachable
and can be simplified. Redirect UX cost: a retired-name invocation
(e.g. `/gz-obpi-audit`) returns "skill not found" rather than "use
/gz-obpi-reconcile."

**Option B — Keep-as-`package_only`-tombstone (current de-facto state).**
Retired SKILL.md stubs persist under `src/gzkit/skills/` with
`lifecycle_state: retired` + `archived_into: <successor>` frontmatter,
classified `package_only` so `gz validate --distribution` exits 0.
Tombstones ship in the wheel. Redirect UX gain: the retired skill name
remains discoverable with a pointer to its successor; the cost is
indefinite wheel inflation and a classifier path whose scope drifts
each time a skill retires.

The promoted destination is expected to choose Option A based on the
operator's recorded judgment, sequence the deletion of the 18 existing
tombstones, and codify the policy in `.gzkit/rules/skill-surface-sync.md`.
Option B remains in the pool record so the rejection is auditable.

## Alternatives Considered

- **Hybrid — tombstones in canonical surface, deleted from package
  surface.** Rejected at routing time as it inverts the dual-surface
  model: canonical content shipping under `.gzkit/` while
  `src/gzkit/skills/` (the package surface) drops them is the opposite
  of the ADR-0.0.32 invariant. Would require a third classifier
  category and split the lifecycle question into two doctrine seams.
- **Stub redirects via a successor-routing table** (no on-disk
  directories). Rejected at routing time as a heavier mechanism than
  the problem warrants — the redirect UX gain in Option B is small
  enough that a plain "skill not found" response (Option A) is
  acceptable. Revisit if user-research evidence shows retired-name
  invocations are common.

## ADR relationship matrix

| Related artifact | Relationship |
|------------------|--------------|
| ADR-0.0.32 (canonical-surface-packaging) | Parent — established the dual-surface model and the `package_only` classifier whose scope this ADR sharpens |
| OBPI-0.0.32-15 (t0-maintenance-surfaces) | Authored `_classify_skill_file`; promotion of this ADR may simplify the retired-frontmatter branch |
| GHI #464 | Routing receipt — surfaced the 18 tombstones during ADR-0.0.32 closeout; superseded by this ADR |
| GHI #465 (closed by `c1394d80`) | Adjacent classifier carve-out — `gz upgrade` named-exception and package-only filtering; no conflict, but the upgrade-surface filter list will need to drop retired skills if Option A is selected |
| `.gzkit/rules/skill-surface-sync.md` | Doctrine home — the retire policy lands here on promotion |
| `data/distribution_baseline_manifest.json` | Unchanged — retired skills are not in the baseline; deletion is consistent with baseline truth |

## Surfaces touched (on promotion)

- `src/gzkit/skills/{18 retired dirs}` — delete
- `.gzkit/skills/{18 retired dirs}` — delete (if present)
- `.claude/skills/`, `.github/skills/`, `.agents/skills/` — drop the
  18 empty directories
- `src/gzkit/skills/_classify_skill_file` — possible simplification of
  the retired-frontmatter branch
- `.gzkit/rules/skill-surface-sync.md` — codify retire-on-delete
- `data/distribution_baseline_manifest.json` — no change expected

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
