---
id: ADR-pool.agent-scratch-space-defaults
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: EveryInc/compound-engineering-plugin
---

# ADR-pool.agent-scratch-space-defaults: Agent Scratch Space Defaults

## Status

Pool

## Intent

Codify where agents place transient, intermediate, and durable outputs. Every Inc's Compound Engineering plugin's `AGENTS.md` § Scratch Space has a detailed three-tier rule:

- **OS temp by default** (`mktemp -d -t <prefix>-XXXXXX`) for per-run throwaway.
- **`/tmp/<plugin>/<skill>/<run-id>/`** for cross-invocation reusable (using `/tmp` directly, not `$TMPDIR`, so paths stay user-accessible on macOS where `$TMPDIR` resolves to `/var/folders/.../T/`).
- **`.context/<plugin>/<workflow-or-skill>/`** only when the artifact is repo-bound AND meets at least one of three named conditions: user-curated (operator-inspectable outside the skill), repo+branch-inseparable (artifact's meaning is tied to this specific checkout), or path-is-core-UX (surfacing the artifact path is part of the skill's output).
- **Durable outputs** (plans, specs, learnings, docs, final deliverables) belong in `docs/` or other repo-tracked locations, not scratch.

gzkit has *implicit* conventions only: `.gzkit/insights/agent-insights.jsonl` for append-only insight stream (T2 ledger-adjacent), `.gzkit/handoffs/<date>-<topic>.md` for session handoff docs, `.gzkit/chores/<slug>/proofs/` for chore evidence (canonical/runtime_state classifier per `.claude/rules/skill-surface-sync.md`). There is **no explicit rule** about where transient scratch goes — observed agent behavior includes occasional `/tmp/` use, occasional ad-hoc files in repo root, and occasional `.gzkit/` writes that aren't clearly canonical.

The doctrinal axis: should gzkit articulate a similarly-detailed rule (CE-aligned or gzkit-specific), or is the current implicit-conventions posture sufficient until friction is observed?

## Decision

_(Pool — design conversation in progress. The minimum viable rule articulation depends on observed friction; the current implicit-conventions state has not yet produced a named defect class.)_

Open surface decisions:

- **Tier hierarchy.** Three-tier (CE-aligned) vs gzkit-specific simpler hierarchy.
- **Canonical paths.** Where exactly does cross-invocation reusable scratch go? `/tmp/gzkit/<skill>/<run-id>/` (CE-style), `~/.cache/gzkit/<skill>/` (XDG-aligned), or `.gzkit/scratch/<skill>/<run-id>/` (in-repo with gitignore)?
- **Enforcement.** Advisory rule, mechanical guard (pre-commit hook flagging untracked files in unexpected paths), or validator scope (`gz validate --scratch-paths`)?
- **Repo-bound exception conditions.** If a `.gzkit/` write is permitted for transient state, what conditions trigger the exception? CE's three conditions (user-curated, repo+branch-inseparable, path-is-core-UX) are a candidate template.
- **Cross-platform posture.** CE assumes Unix-like shells; does gzkit match that posture, or formalize a Windows-fallback path?

## Alternatives Considered

### Path A — Adopt CE three-tier rule directly

**Shape.** Author `.gzkit/rules/scratch-space.md` mirroring CE's three-tier rule with gzkit-specific naming: OS temp default, `/tmp/gzkit/<skill>/<run-id>/` for cross-invocation, `.gzkit/<sub>/` exception with the three named conditions (user-curated, repo+branch-inseparable, path-is-core-UX), durable outputs to `docs/`. Existing `.gzkit/insights/`, `.gzkit/handoffs/`, `.gzkit/chores/*/proofs/` are pre-blessed as user-curated exceptions.

**Strengths.**

- Concrete prior art shipped at scale (CE 16.7k★).
- The three exception conditions are well-articulated and operationally testable.
- Composable with gzkit's existing repo conventions.

**Weaknesses.**

- Imports CE-specific framing without re-grounding against gzkit's specific patterns.
- Cross-platform note in CE assumes Unix-like shells; gzkit's posture on Windows is unstated.
- Pre-mechanizes a problem whose actual friction in gzkit is unmeasured.

### Path B — gzkit-specific rule (canonical-or-temp)

**Shape.** Simpler two-tier rule: every agent-written file is either *canonical* (`.gzkit/<sub>/`, `docs/`, `src/`, `tests/` — durable, tracked) or *temp* (OS temp via `mktemp -d`). No intermediate "cross-invocation reusable scratch in repo" category. Cross-skill coordination uses ledger events or shared `.gzkit/` canonical files, not in-repo scratch.

**Strengths.**

- Smallest rule surface; easiest to communicate.
- Forces every in-repo write to be deliberately canonical, which aligns with gzkit's state-doctrine T1-or-T2-only stance for in-repo state.
- Eliminates the "is this scratch or canon?" ambiguity that CE's three-tier rule introduces.

**Weaknesses.**

- Loses the cross-invocation reusable tier; cross-skill coordination must rely on ledger or canonical files only, which may be heavier than CE's `/tmp/<plugin>/` pattern for genuinely transient cross-skill state.
- Doesn't address the existing implicit patterns where some `.gzkit/` writes (chores proofs, insights records) function as cross-invocation evidence — under this rule they're canonical, which is honest but more rigid.

### Path C — Defer until friction observed

**Shape.** No rule articulation. Current implicit conventions continue. Revisit when (a) an agent writes scratch into an unexpected repo path that causes drift, (b) cross-skill coordination breaks due to missing shared-scratch convention, or (c) operator observes a defect class attributable to scratch-path ambiguity.

**Strengths.**

- Zero rule cost. No premature mechanization.
- The current implicit conventions cover most observed needs without explicit rule.

**Weaknesses.**

- Doctrine drift risk: agents reading both `AGENTS.md` and CE's `AGENTS.md` will absorb CE's rule and apply it to gzkit by default, since gzkit has no contradicting rule. The cross-pollination is the most-likely silent failure mode here.
- The implicit-conventions state is brittle to agent rotation; new agents have no signal where to write scratch.

### Path D — Adopt CE rule + pre-bless gzkit canonical exceptions

**Shape.** Variant of Path A where the gzkit-specific exception conditions are explicitly enumerated up front: `.gzkit/insights/` and `.gzkit/handoffs/` are pre-attested as user-curated exceptions; `.gzkit/chores/<slug>/proofs/` is pre-attested as path-is-core-UX exception. Other `.gzkit/` paths must meet the three-condition test ad-hoc. Mechanical enforcement via `gz validate --scratch-paths` flagging non-blessed in-repo agent writes.

**Strengths.**

- Composes CE's rule rigor with gzkit's observed canonical exception paths.
- Eliminates the most-frequent ambiguity (the existing `.gzkit/` writes are pre-blessed; agents don't have to re-litigate them each time).
- Mechanically enforceable via a validator scope.

**Weaknesses.**

- Surface growth: the rule has both general conditions AND a pre-blessed exception list, doubling the maintenance load.
- Pre-blessing risks ossifying the current paths even when better alternatives emerge.
- The validator scope must distinguish "agent wrote this" from "operator wrote this" — a non-trivial signal.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Related artifacts

- **CE plugin's `AGENTS.md` § Scratch Space** — the three-tier rule (OS temp / `/tmp/<plugin>/<skill>/<run-id>/` / `.context/` exception) with cross-platform notes
- **`.gzkit/insights/agent-insights.jsonl`** — existing canonical insight stream (append-only T2; schema-validated per advisory-rules-audit row #17a)
- **`.gzkit/handoffs/`** — existing canonical session handoff surface
- **`.gzkit/chores/<slug>/proofs/`** — existing canonical chore-evidence surface (per `.claude/rules/skill-surface-sync.md` canonical/runtime_state classifier)
- **`docs/governance/state-doctrine.md`** — T1/T2/T3 storage tiers; derived-view doctrine bears on whether scratch is allowed in repo at all
- **`docs/governance/harness-engineering-appraisal.md` § Third confirming thesis** — surfaces CE's scratch-space rule as an operator-decision item

### Promotion guidance

The promotion author must commit to one of Path A, B, C, or D. If A, B, or D is chosen, the resulting feature ADR must include:

- Rule text in `.gzkit/rules/scratch-space.md` (or amendment to an existing rule).
- Mechanical enforcement plan: validator scope, pre-commit hook, or advisory-only with scorecard entry.
- Migration plan for any existing in-repo writes that don't conform under the new rule.
- Cross-platform posture (Unix-only, or Windows-fallback path defined).

If C is chosen, this pool ADR remains in the backlog until one of the named triggers fires. Cross-pollination risk from CE's rule (agents importing CE doctrine into gzkit's silent-rule space) should be re-evaluated quarterly.

### Inspired by

[EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — `AGENTS.md` § Scratch Space is the most detailed scratch-space rule in published agent-contract prior art, with explicit three-tier hierarchy, exception conditions, cross-platform notes, and rationale for `/tmp` over `$TMPDIR`. The CE rule's specificity — naming the exact `mktemp` command, the macOS `$TMPDIR` hostility, the three exception conditions — is the model whether gzkit adopts it directly (Path A), adapts it (Path D), simplifies it (Path B), or defers (Path C).
