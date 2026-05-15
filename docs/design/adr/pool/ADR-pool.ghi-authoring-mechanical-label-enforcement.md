---
id: ADR-pool.ghi-authoring-mechanical-label-enforcement
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.ghi-authoring-mechanical-label-enforcement: GHI Authoring Mechanical Label Enforcement

## Status

Pool

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

## Alternatives Considered

**A. Tighten the `ghi-author` skill prose further.** Rejected. The
v0.26.3 regression is the empirical refutation: 10 days after the
prose-fix landed, the failure rate increased rather than decreased.
Prose-level enforcement does not hold against agent attention drift —
that is the entire trust-doctrine motivation for Layer-2 mechanical
defenses. Adding more prose to a surface already large enough to drop
out of agent context is the failure mode `ADR-pool.contract-surface-mechanical-defenses`
exists to close.

**B. `gz validate --runtime-label-coverage` alone, no authoring-time
wrapper.** Rejected as primary defense. An audit catches the failure
after the wrong-shape GHI is created and the operator has to backfill
labels — exactly the per-cycle recovery burden the v0.26.3 ceremony
demonstrated. The mechanical defense belongs at the authoring boundary,
not at a downstream consumer. Child 2 keeps this audit as
defense-in-depth, but it is not the primary close.

**C. Auto-apply the `runtime` label silently when the predicate fires.**
Rejected. Silent label mutation breaks the authoring agent's mental
model of what was filed and corrupts the `Eval-feedback-source:`
trailer family of provenance signals. The wrapper refuses and forces
the operator/agent to acknowledge the predicate hit; that is the
correct semantics for a contract surface, not silent rewriting.

**D. Move the predicate enforcement into a pre-commit hook on the
issue-body file.** Rejected. `gh issue create` does not write a
filesystem artifact before the API call; there is no pre-commit hook
boundary to attach to. The wrapper is the only natural
enforcement point in the create-time path.

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
