---
id: ADR-pool.skill-surface-mechanical-defenses
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.skill-surface-mechanical-defenses: Skill-Surface Mechanical Defenses

## Status

Pool

## Intent

Convert the `SKILL.md` authoring surface from honor-system prose into
mechanically audited evidence — the skill-layer sibling of
[`ADR-pool.contract-surface-mechanical-defenses`](ADR-pool.contract-surface-mechanical-defenses.md),
which does the same for the `AGENTS.md`/`CLAUDE.md` contract surface.

The Mechanical-Enforcement Scorecard (`docs/governance/advisory-rules-audit.md`)
has never been run on the skill+tool surface. Primary-source verification
(2026-06-15 strength-of-compliance session) found that surface at the bottom of
the Mechanical / Promotable / Judgment / Ambiguous ladder — strong *routing* to
skills, near-zero *binding* once a skill is reached:

- **8 wholesale template stubs** — `gz-constitute`, `gz-prd`, `gz-state`,
  `gz-validate`, `gz-implement`, `gz-cli-audit`, `gz-check-config-paths`,
  `gz-migrate-semver` — each ~30-33 lines of identical boilerplate
  (*"Operate the gz `<verb>` command surface as a reusable governance workflow"*,
  *"Run uv run gz `<verb>` with the required options"*). All are routed-to by
  `gz-skill-router` (several also by `docs/user/runbook.md`) yet bind nothing at
  the destination — a strong deterministic route into a zero-strength stub.
- **A broken `$<skill>` placeholder** shipped as the `## Example` section of 12
  skills (the 8 stubs + `gz-gates`, `gz-agent-sync`, `gz-plan`, `gz-init`).
- **`skill-version` absent** on the 8 stubs, contradicting
  `.gzkit/rules/skill-surface-sync.md` non-negotiable rule #2 (*"Skills carry
  `skill-version:` … validated by the skill schema"*) — the schema check is not
  firing.
- **No `gz_command:` + output-contract** on 14 of 15 tool/router skills (only
  `gz-init` declares `gz_command`), leaving the route→tool binding and its return
  shape implicit. The operator-stated intention — *skills instruct the agent to
  wield our home-grown tool* — is unenforced.

This is the failure class `contract-surface-mechanical-defenses` names —
Promotable rules sitting unpromoted because nothing fails closed when authoring
drifts — applied to a second binding surface the original ADR explicitly does not
cover.

## Decision

Author parallel `gz validate` scopes over the `SKILL.md` surface, each a single
fail-closed predicate, **reusing** the snapshot → scorecard → promotion-aging
primitives defined by `contract-surface-mechanical-defenses` (this ADR is a
consumer of that mechanism, not a re-implementation).

### Queued children (promotion order)

#### 1. `gz validate --skill-authoring-floor` *(promote first)*

| Field | Value |
|---|---|
| Single predicate | Every `SKILL.md` declares `skill-version` (+ `last_reviewed`), declares `gz_command` for tool-bound skills, declares a named output-contract, and contains no unresolved `$<skill>` placeholder or *"the required options"* non-authoring. |
| Failure case | A wholesale stub or un-versioned skill ships. Fail-close exit 3. |
| Side effect | Authoring the 8 stubs is forced by landing this — a stub cannot pass the floor. |
| Heavy lane | New `gz validate` scope (CLI surface) + skill-schema field requirements (runtime contract). Gates 3/4/5 apply. |

#### 2. `gz validate --skill-surface-scorecard`

| Field | Value |
|---|---|
| Single predicate | Every binding directive in a `SKILL.md` has a row in a new `docs/governance/skill-surface-audit.md`, scored Mechanical / Promotable / Judgment / Ambiguous (sibling of `advisory-rules-audit.md` and the planned `contract-surface-audit.md`). |
| Why second | Depends on the authoring floor to bound what counts as a "binding directive". |

#### 3. Aging

Reuse `contract-surface-mechanical-defenses` child 3
(`gz validate --scorecard-promotion-aging`) — it already walks *every* audit doc;
add `skill-surface-audit.md` to its set rather than authoring a fourth aging
predicate.

## Absorbed findings

Verified 2026-06-15; each rides this ADR as a motivating instance rather than an
ad-hoc fix (the direct-fix moratorium stands for non-drainage defects).

| ID | Surface | Defect |
|---|---|---|
| F1 | `ghi-triage/SKILL.md:167` vs `scripts/triage.py:342,374-378` | SKILL claims the script validates `action <=80 / why <=120` char limits; `triage.py` rejects any key but `number`/`severity` (GHI #424). Stale doc binds the agent to input the script hard-rejects. |
| F2 | `gz-adr-create/SKILL.md:19` vs `:8` | H1 `(v6.0.0)` drifts from frontmatter `skill-version: "6.5.0"`. |
| F3 | size-rule routing | `gz-adr-create:259` / `gz-obpi-specify:141` give only *"one OBPI brief per checklist item"*. Matrix-as-code (`core/scoring.py:64,100`) + `gz validate --decomposition` (`validate_cmd.py:104`) bind COUNT to the scorecard target, but the dimension scores can default (`default_dimension_scores:75`) and the authoring skills never route the agent to the scorecard the validator enforces. Cross-links `ADR-pool.obpi-authoring-mechanical-floor`. |

## Alternatives Considered

**A. Fold into `ADR-pool.skill-behavioral-hardening`.** Rejected. That ADR's
Non-Goals are explicit — *"No new governance infrastructure — all changes are
SKILL.md markdown files"* — and its scope hardens existing skill *prose* against
rationalization for four named skills. The mechanical floor (schema, validators,
authoring the stubs) is out of its scope by construction.

**B. Fold into `ADR-pool.contract-surface-mechanical-defenses`.** Rejected. That
ADR's predicates are scoped to `AGENTS.md`/`CLAUDE.md` by construction. The skill
surface is a distinct file set with distinct frontmatter; a sibling keeps each
single-predicate validator sharp — the same reasoning that ADR used to reject
conflating `--advisory-scorecard`.

**C. File three GHIs, skip the ADR.** Rejected. Same reasoning
`contract-surface-mechanical-defenses` recorded: mechanical work without recorded
architectural intent is the slop trajectory this family exists to close.

## Cadence / Sequencing

Pool backlog item — **lands with the campaign's cadence**
([build-to-1.0 Magna Carta](../../../governance/build-to-1.0-campaign-2026-06-10.md)):
terminal disposition in **Phase G** (full-pool build-out), pulled with the
compliance-strength family (`contract-surface-mechanical-defenses` +
`obpi-authoring-mechanical-floor` + `skill-behavioral-hardening` + this sibling),
reusing the shared snapshot/scorecard/aging mechanism. **NOT pulled forward** —
green-first (#621) and the CMS marquee (B.1) keep their sequence.

Surfaced by the 2026-06-15 strength-of-compliance session — a four-skill craft
review (Matt Pocock's `grill-with-docs` / `to-prd` / `to-issues` / `triage`) that
re-scoped to "max strength of agent compliance for skills+tools".

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

Recommended promotion order: child 1 (`--skill-authoring-floor`) first as
`foundation` `0.0.x` (the skill-binding floor is an app-system invariant), then
child 2 once child 1 closes Gate 5. Promotion-time refines the exact required
frontmatter fields and the tool-bound-skill set against the live catalog
(`gz skill list`).
