---
id: ADR-0.0.44-ghi-authoring-mechanical-label-enforcement
status: Proposed
kind: foundation
semver: 0.0.44
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-15
promoted_from: ADR-pool.ghi-authoring-mechanical-label-enforcement
---

# ADR-0.0.44-ghi-authoring-mechanical-label-enforcement: GHI Authoring Mechanical Label Enforcement

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active driver:** `main-session` — see `.gzkit/personas/main-session.md`.

Agents working on this ADR treat the `gz issue file` wrapper as a Layer-2 mechanical defense, not a convenience helper — the wrapper IS the contract. The work converts honor-system prose into fail-closed code, and the craftsperson trait demands that the predicate logic, the wrapper exit code, the `runtime` label, and the downstream `gz patch release` qualifier (`runtime` ∩ src diff) all stay coherent in a single edit. Incremental patching — adding the wrapper while leaving honor-system fallbacks elsewhere — is the named failure mode this ADR exists to close. Agents extending this work enumerate every place the predicate is evaluated and route them through the single mechanical surface, not around it.

## Why foundation tier?

Without this ADR, GHI labels drift unverifiably — authors apply labels by convention, automation reads them by convention, and the loop between authoring-time labels and consumer-time enforcement has no mechanical check.

This ADR authors a port: the GHI authoring mechanical-label enforcement contract every issue-authoring and issue-consuming surface honors.

## Intent

Convert the `ghi-author` skill's Step 1 secondary-label predicate from
Layer-1 honor-system prose into a Layer-2 mechanical fail-close at
`gh issue create` time. Today the predicate (body cites `src/gzkit/`,
symptom is `gz <verb>` runtime, or remedy shape is `fix(...)`) is
evaluated by the authoring agent's judgment, with no mechanical defense
between agent-judgment and the GitHub API call. When the agent skips the
predicate check — even an agent reading the skill prose immediately
before authoring — the GHI lands without the `runtime` label and
silently drops out of `gz patch release`'s qualifier (`runtime` ∩ src
diff).

The failure mode is canonical: GHI #402 origin (2026-05-05) recorded 16
runtime-touching GHIs in the `diff_only` bucket across `v0.26.0..HEAD`,
qualifying 0 for the patch release. The prose-only mitigation landed via
ec02b089 (skill Step 1 secondary-labels table) and held for one
release. The v0.26.3 dry-run (2026-05-15) then surfaced 17 of 18
`diff_only` GHIs missing the label — the regression was wider than the
original. #402 was reopened with the regression evidence and the
finding routed to this pool ADR.

This ADR's scope is the **authoring-boundary** mechanical defense. It
is the sibling of `ADR-pool.contract-surface-mechanical-defenses` (same
trust-doctrine family — Layer-1 prose insufficient, Layer-2 fail-close
required) but operates on a different surface (`gh issue create`
invocation flow) and a different predicate (per-issue body signature,
not contract-surface accretion). The two pool ADRs do not overlap; each
closes its own slice of the prose-only-enforcement failure class.

## Decision

Extend the existing `gz issue file` wrapper such that **all** GHI
creations against `tvproductions/gzkit` flow through one mechanical
surface that parses the proposed body for the runtime predicate
signature and refuses the create when the predicate fires without
`--label runtime`.

### Queued children

Listed in promotion order. The first promotes to foundation `0.0.x`
under `gz adr promote`; subsequent children stay in pool until the
first lands and proves the wrapper integration surface.

#### 1. `gz issue file` local-repo routing + predicate enforcement *(promote first)*

| Field | Value |
|---|---|
| Single predicate | Every `gh issue create` against `tvproductions/gzkit` flows through `gz issue file`, which parses the body and refuses the create when the runtime predicate fires without `--label runtime`. |
| Failure case | A GHI body cites `src/gzkit/` paths, names a `gz <verb>` runtime symptom, or proposes a `fix(...)` remedy, yet `gh issue create` is invoked without `--label runtime`. The wrapper exits non-zero before the API call; nothing is created. |
| Predicate signature | Body parser matches: (a) regex hit for `src/gzkit/[A-Za-z0-9_/.-]+` outside fenced quote blocks; (b) regex hit for `uv run gz [a-z]+( [a-z-]+)*` as a symptom line; (c) regex hit for `fix\\(([a-z-]+)\\):` as a remedy shape. Any hit fires the predicate. |
| Integration surface | `gz issue file` already exists for cross-repo filing from consuming projects. Extension: when invoked from inside `tvproductions/gzkit` itself, route to the same wrapper instead of letting `gh issue create` run unguarded. The `ghi-author` skill's Step 5 invocation updates to call `gz issue file` directly. |
| Override path | `--accept-no-runtime-label` flag with mandatory `--accept-reason <text>` (parallel to `--accept-uncovered` REQ-coverage waiver). Reason is recorded in the issue body as an `_audit-exempt: no-runtime-label_` line and surfaces in the labeling-recovery audit. |
| Why first | Closes the canonical regression (#402 origin + v0.26.3 re-fire) at the authoring boundary. Subsequent audits and validators ride on the wrapper being the one mechanical surface; without it they are post-hoc cleanup. |
| Heavy lane | Changes CLI behavior (`gz issue file` accepts new local-repo path), changes the authoring contract (`gh issue create` is no longer the canonical invocation), and changes the `ghi-author` skill prose. Heavy gates 3 docs, 4 BDD, 5 attestation apply. |

#### 2. `gz validate --runtime-label-coverage`

| Field | Value |
|---|---|
| Single predicate | Every open GHI whose commits touch `src/gzkit/` carries the `runtime` label. |
| Failure case | A GHI was created out-of-band (e.g. via the GitHub web UI, or a bypass of `gz issue file`) without the `runtime` label despite firing the predicate on its body. The wrapper alone cannot prevent this; the audit catches it before patch-release ceremony. |
| Audit surface | `gz check` pipeline scope; runs `gh issue list --state open` cross-validated against `git log --since=$(latest_tag)` for src diff, exits 3 on any miss. |
| Why second | Defense-in-depth behind child 1. The wrapper is the primary defense at create time; this audit is the periodic backstop for everything that didn't flow through it. |
| Heavy lane | New `gz validate` scope. Heavy. |

#### 3. `gz issue file` extended-predicate scopes (security, eval-feedback)

| Field | Value |
|---|---|
| Single predicate | The same wrapper enforces the predicate heuristics for `security` and `eval-feedback` labels per the ghi-author Step 1 secondary-labels table. |
| Failure case | A GHI body cites a registered security surface (`data/security_surfaces.json`) without `--label security`, OR cites an evaluation-feedback ledger event without `--label eval-feedback`. |
| Why third | Same authoring-boundary defense extended to the other two secondary labels whose absence breaks downstream gates (Gate-5 walkthrough for `security`; commit-trailer requirement under ADR-0.0.26 for `eval-feedback`). Depends on child 1's wrapper extension landing first. |
| Heavy lane | Wrapper behavior change. Heavy. |

### Integration

Child 1 lands as foundation `0.0.x` under `gz adr promote`. The
`ghi-author` skill's Step 5 example updates from raw `gh issue create`
to `gz issue file` (skill-version bump). `AGENTS.md` § Behavior Rules —
Always #13 updates from "Author GHIs through `/ghi-author` — never call
`gh issue create` directly" to also name `gz issue file` as the
mechanical surface. The `.claude/rules/gh-cli.md` allowed-commands list
removes the unguarded `gh issue create --label defect ...` example and
points at `gz issue file` instead.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: the named gz validate --runtime-label-coverage validator and the runtime-label predicate enforcement are unlanded (ADR is Proposed); the gz issue file wrapper this ADR extends is exercised green by its test module. | uv run -m unittest tests.commands.test_issue_cmd | 0 |

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.44-01: **local-repo-routing** — Extend `gz issue file` to accept local-repo (`tvproductions/gzkit`) invocations alongside cross-repo filing.
- [ ] OBPI-0.0.44-02: **predicate-parser** — Add runtime-predicate body parser matching `src/gzkit/` path refs, `uv run gz <verb>` symptom lines, and `fix(...)` remedy shape.
- [ ] OBPI-0.0.44-03: **fail-closed-refusal** — Refuse the create when the predicate fires without `--label runtime`; exit non-zero before the `gh` API call with an error naming which predicate signature hit.
- [ ] OBPI-0.0.44-04: **accept-override** — Add `--accept-no-runtime-label` + mandatory `--accept-reason <text>` override; reason stamped into the issue body as `_audit-exempt: no-runtime-label_`.
- [ ] OBPI-0.0.44-05: **skill-invocation-update** — Update `ghi-author` skill Step 5 invocation from raw `gh issue create` to `gz issue file`; bump skill-version; sync mirrors via `gz agent sync control-surfaces`.
- [ ] OBPI-0.0.44-06: **doctrine-surface-update** — Update `AGENTS.md` § Behavior Rules — Always #13 and `.claude/rules/gh-cli.md` allowed-commands list to name `gz issue file` as the mechanical surface.

## Target Scope

Child 1 (`gz issue file` local-repo routing + predicate enforcement) is
promoted first. Children 2 and 3 stay in pool until child 1 closes Gate 5.

- **local-repo-routing** — Extend `gz issue file` to accept local-repo (`tvproductions/gzkit`) invocations alongside cross-repo filing.
- **predicate-parser** — Add runtime-predicate body parser matching `src/gzkit/` path refs, `uv run gz <verb>` symptom lines, and `fix(...)` remedy shape.
- **fail-closed-refusal** — Refuse the create when the predicate fires without `--label runtime`; exit non-zero before the `gh` API call with an error naming which predicate signature hit.
- **accept-override** — Add `--accept-no-runtime-label` + mandatory `--accept-reason <text>` override; reason stamped into the issue body as `_audit-exempt: no-runtime-label_`.
- **skill-invocation-update** — Update `ghi-author` skill Step 5 invocation from raw `gh issue create` to `gz issue file`; bump skill-version; sync mirrors via `gz agent sync control-surfaces`.
- **doctrine-surface-update** — Update `AGENTS.md` § Behavior Rules — Always #13 and `.claude/rules/gh-cli.md` allowed-commands list to name `gz issue file` as the mechanical surface.

### 1. `gz issue file` accepts local-repo invocations

Extend the existing wrapper (currently scoped to cross-repo filing from
consuming projects) so that invocations from inside `tvproductions/gzkit`
route through the same predicate-enforcement path instead of falling
through to unguarded `gh issue create`.

### 2. Runtime-predicate body parser

Add a body parser that scans the proposed issue body for the three
runtime-predicate signatures: `src/gzkit/[A-Za-z0-9_/.-]+` path
references outside fenced quote blocks; `uv run gz [a-z]+( [a-z-]+)*`
symptom lines; `fix\\(([a-z-]+)\\):` remedy-shape proposals. Any hit
fires the predicate.

### 3. Fail-closed refusal when predicate fires without `--label runtime`

When the predicate fires and `--label runtime` is absent, `gz issue file`
exits non-zero before the `gh` API call. Error names the predicate hit
(which signature, which line) and points at the override flag.

### 4. `--accept-no-runtime-label` override path

Mandatory paired flags: `--accept-no-runtime-label` plus
`--accept-reason <text>`. Reason is recorded in the issue body as an
`_audit-exempt: no-runtime-label_` line; the labeling-recovery audit
(child 2 scope) surfaces these for periodic review.

### 5. `ghi-author` skill Step 5 invocation update

Skill prose updates from raw `gh issue create` to `gz issue file`.
Skill-version bump per `.gzkit/skills/ghi-author/SKILL.md` frontmatter
convention. Sync mirrors via `gz agent sync control-surfaces`.

### 6. `AGENTS.md` § Behavior Rules — Always #13 and `.claude/rules/gh-cli.md` updates

`AGENTS.md` Rule 13 names `gz issue file` as the mechanical surface
alongside `/ghi-author`. The `gh-cli.md` allowed-commands list removes
the unguarded `gh issue create --label defect ...` example; the
canonical invocation becomes `gz issue file`.

## Non-Goals

- Children 2 and 3 of this pool ADR are out of scope for child 1's
  promotion. They stay in pool and queue separately.
- No changes to `gh issue create` direct invocations outside the
  `ghi-author` flow (third-party callers, CI scripts, operator
  ad-hoc filing) — child 1 closes the agent-authoring surface only.
- No retroactive labeling sweep on existing open GHIs — that is child
  2's scope when it promotes.
- No changes to the `runtime` label semantics in `gz patch release`'s
  qualifier — the strict `runtime` ∩ src diff predicate stays as-is;
  this ADR ensures the label is mechanically present, not redefines
  what it means.

## Notes

Surfaced from the v0.26.3 patch-release ceremony (2026-05-15) where
the labeling-recovery step backfilled `runtime` on 17 of 18
`diff_only` GHIs to unblock the qualifier. Re-opened #402 with the
regression evidence routes to this pool ADR.

### Provenance

- GHI #402 (reopened 2026-05-15) — canonical origin + regression evidence
- v0.26.3 patch-release ceremony — `uv run gz patch release --dry-run`
  output capturing the 17/18 miss rate
- `ADR-pool.contract-surface-mechanical-defenses` — sibling pool ADR
  (same trust-doctrine family, different surface)

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
Recommended promotion: child 1 as `foundation` `0.0.x` (authoring
contract is an app-system invariant); children 2 and 3 stay in pool until
child 1 closes Gate 5.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.ghi-authoring-mechanical-label-enforcement` on 2026-05-15; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.44 | Pending | | | |
