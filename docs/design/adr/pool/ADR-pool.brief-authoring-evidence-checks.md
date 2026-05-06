---
id: ADR-pool.brief-authoring-evidence-checks
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.brief-authoring-evidence-checks: Brief Authoring Observed-Evidence Checks

## Status

Pool

## Intent

Close the brief-authoring observed-evidence gap. `gz plan audit` (at
`src/gzkit/commands/plan_audit_cmd.py`) already runs deterministic checks on
brief and plan files after they exist, but the **authoring** path —
`gz plan create` for ADRs, `gz obpi specify` for OBPI briefs — does not
verify the draft Allowed Paths against observed evidence before writing the
artifact. The result is a class of brief defects that compound silently:
files named in Allowed Paths that already breach size caps; manpage paths
that do not exist; sibling-OBPI scope collisions that pile up in
`gz plan audit`'s advisory channel without ever blocking authoring.

GHI #380 surfaced this during OBPI-0.0.23-05 plan-audit (2026-05-02):

- `wc -l src/gzkit/commands/adr_audit.py` returns 864 lines (verified
  2026-05-02; body cited 758 at filing time). The 600-line module cap from
  `.claude/rules/pythonic.md` § Size Limits was already breached when the
  brief was authored, yet the brief named the file in its sole-implementation
  Allowed Paths section. Same failure class as DO IT RIGHT #5 (*Read the code
  before you change it*) applied at brief-authoring time rather than
  implementation time.
- `ls docs/user/manpages/` shows `arb.md`, `closeout.md`, `gz-chores.md`,
  `gz-issue.md`, `gz-justify.md`, `gz-personas.md`, `patch-release.md` — no
  `docs/user/manpages/gz-adr.md` exists despite `gz adr` carrying ~10
  subcommands. Each ADR-touching brief that names a manpage update reinvents
  the path because no convention is canonical.
- `uv run gz plan audit OBPI-0.0.23-05` reports 249 sibling-OBPI scope
  collisions on `src/gzkit/commands/adr_audit.py`, `tests/commands/test_adr_audit.py`,
  `tests/fixtures/adr_audit_covers_backfill/`, `docs/user/manpages/gz-adr.md`.
  The advisory channel was added precisely for this pattern and nothing has
  been clearing it.

This is the **authoring-time** sibling of GHI #381's execution-time
attestation gap — both surfaces vibe through observed-evidence discipline that
the rest of the gate covenant assumes is in place. AGENTS.md § MAKE LLM
STOCHASTIC VIBES INERT operative claim 4 (narrative recall instead of
receipts is the named failure class) is the doctrine root for both.

## Target Scope

Four mechanical defenses, each a candidate `gz plan` / `gz validate`-time
fail-close parallel to how `gz cli audit` and `gz validate --behave-req-tags`
close other implementation-time classes:

### 1. Pre-author file-size-cap check

`gz plan create --check-paths` (or equivalent flag on `gz obpi specify`) runs
`wc -l` against every path in the draft Allowed-Paths section and refuses to
write a plan that places new logic in an over-cap module without naming a
sibling-module proposal. The 600-line module cap and 50-line function cap
from `.claude/rules/pythonic.md` are the floor.

### 2. Pre-author scope-collision check

Extend `gz plan audit`'s 249-collision advisory into a draft-time blocker.
`gz plan create --check-scope-collisions` fails the draft when a candidate
Allowed-Paths entry contends with ≥N (suggest N=5) sibling-OBPI claims, until
the author either widens scope, splits the OBPI, or names a sibling-claim
resolution.

### 3. Pre-author manpage-anchor check

`gz plan create --check-manpage-anchor` requires every brief that names a
manpage in Allowed Paths to reference an existing path under
`docs/user/manpages/`. New manpages are allowed but require an explicit
`--new-manpage <slug>` flag, surfacing the surface-canonization decision at
author time rather than burying it in the plan.

### 4. Post-author Allowed-Paths drift validator

`gz validate --brief-allowed-paths` walks every brief and catches drift
between what the brief said it would touch and what the closing receipt's
evidence actually changed (parallel to `gz validate --commit-trailers`).
Authoring-time pre-checks defend the draft; this validator defends the
landed brief.

## Non-Goals

- No replacement of `gz plan audit` — the post-author check stays as the
  steady-state audit; this ADR adds authoring-time pre-checks plus one new
  validator scope, both upstream of `plan audit`.
- No automatic resolution of scope collisions. The `--check-scope-collisions`
  blocker raises the question; the operator (or a sibling-OBPI close) is the
  authoritative resolution, not a heuristic.
- No bundling with GHI #381's destination
  (`ADR-pool.obpi-pipeline-dispatch-attestation`). Authoring-time and
  execution-time fail-close surfaces share a root cause but have orthogonal
  mechanical defenses; either ADR may absorb both at promotion time, but the
  pool stage does not pre-bind that decision.

## Decision

Pool — design conversation home for the four defenses above. Promotion to
foundation or feature follows `gz adr promote` ceremony when the operator
sequences this work, with OBPI decomposition matrix
(`docs/governance/GovZero/obpi-decomposition-matrix.md`) applied per defense.

## Alternatives Considered

### A. Direct fix per defense, no ADR

Rejected. Each defense touches `gz` CLI surface (new flags or new validator
scope), and at least #4 changes the validator scope set — three OBPI
ceremony triggers per `AGENTS.md` § Defect-fix routing. A direct-fix path
would invert the routing doctrine.

### B. Bundle into GHI #381's destination (`ADR-pool.obpi-pipeline-dispatch-attestation`)

Rejected at the pool stage. The two GHIs share a root cause (anti-vibing
operative claim 4) but their *mechanical surfaces* are orthogonal:
authoring-time defenses live in `gz plan create` / `gz obpi specify` /
`gz validate`; execution-time defenses live in `gz obpi pipeline` and the
ledger event schema. Keeping the pool stages separate preserves promotion
flexibility — either ADR may absorb both at promotion time if the operator
chooses, but pre-binding the decision in pool would over-couple the design
conversations.

### C. Author as foundation-kind ADR-0.0.x directly

Rejected. The defense surface is feature-shaped (new CLI flags, new
validator scope) rather than invariant-shaped. Foundation kind is reserved
for app/system invariants per ADR-0.0.18; these are mechanical defenses *of*
an invariant (observed-evidence discipline at authoring time), not the
invariant itself.

### D. Strengthen `gz plan audit` to be authoring-time

Rejected as a single move. `gz plan audit` runs after the brief and plan
files exist; restructuring it to refuse-to-write would change its contract
and break consumers that rely on its current shape (post-author idempotent
check). The right move is *additive*: keep `gz plan audit` as the
post-author audit, add a pre-author check surface (defenses 1-3) that
shares logic where reasonable, plus one new validator scope (defense 4)
that closes the drift class `gz plan audit` cannot detect.

## Origin

- GHI #380 (authoring-time vibes; this ADR's primary surfacing event)
- OBPI-0.0.23-05 plan-audit (2026-05-02) — the surfacing run
- Sibling: GHI #381 (execution-time vibes;
  `ADR-pool.obpi-pipeline-dispatch-attestation` is the destination there)
- AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 4 (the
  doctrine root for both)

## Notes

**Sibling routing receipts:**

- GHI #406 (cluster-brief coupled-surface coherence at brief-authoring time)
  closes `superseded` against this ADR. Adds cluster-level dimensions to the
  per-brief defenses above: (a) cross-OBPI schema-coherence — REQ enum
  constraints in OBPI-N+1 applied to predecessor OBPI-N's deliverable shape
  (e.g. ADR-0.0.28's `radon_mi` p85/p65/p40 vs `corpus_percentile ∈
  {50,75,90,95,99}`); (b) Discovery Checklist substantive-subsection check
  at authoring time (port `gz obpi validate --authored` from precomplete to
  authoring); (c) vendor-mirror exclusion in Allowed Paths
  (`.claude/rules/`, `.claude/skills/`, `.agents/`, `.github/instructions/`,
  `.github/skills/` are sync targets, not edit surfaces); (d) sibling-OBPI
  deliverable-shape consistency. Promotion-time decision: fold these into a
  fifth defense ("Pre-author cross-OBPI cluster-coherence check"), or split
  into a sibling pool ADR — the operator chooses at `gz adr promote`.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
