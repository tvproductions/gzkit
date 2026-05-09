---
id: ADR-pool.config-evaluation-tooling
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.config-evaluation-tooling: Config Evaluation Tooling with Guidance Mode

## Status

Pool

## Date

2026-05-09

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Provide a discovery surface for opt-in configuration features so that opt-in
hooks, runtime knobs, and agent gates do not silently sit uninstalled. The
canonical motivating instance is OBPI-0.0.29-05's complexity-advisor
auto-chain hook — opt-in per ADR-0.0.29 § Negative #6 (pre-commit hook
interaction is fragile), but an opt-in hook with no discovery surface
reproduces the *"advisor exists but never fires"* failure class the parent
ADR itself names as the reason auto-chain exists.

gzkit's config surface is now sophisticated enough that operators need
guided discovery across at least three independent control surfaces:

- `.pre-commit-config.yaml` carries ~12 hooks with interaction
  dependencies (e.g. xenon → advisor chain, where the auto-chain
  *replaces* xenon-complexity rather than supplementing it).
- `.gzkit.json` carries runtime config (e.g. `advisor_timeout_seconds`).
- `.claude/settings.json` carries agent hooks with governance gates.

No existing tool surfaces gaps such as *"you have xenon-as-gate but not the
advisor auto-chain"* or recommends installation order. Operators discover
opt-in features only by reading ADRs, which inverts the discovery contract.

---

## Decision

Pool a config evaluation tool with a guidance mode. Concrete scope to be
locked at promotion time, but the design conversation centres on four
target capabilities:

1. **`gz check --config-recommendations`** (or `gz config evaluate` —
   verb shape decided at promotion). Scans the repo's config surfaces
   against a recommendation registry and surfaces gaps with install
   commands. Exits non-zero when a recommendation marked
   `severity: required` is unmet; advisory mode for soft recommendations.
2. **Recommendation registry — data-driven, not code-driven.** A
   declarative list of config recommendations, each with:
   - a precondition (e.g. *"xenon-complexity is present in
     `.pre-commit-config.yaml`"*),
   - a recommendation (e.g. *"install
     `complexity-advisor-auto-chain`"*),
   - a rationale citation (e.g. ADR-0.0.29 § Negative #6),
   - install/repair commands the operator can run as-is.
   The registry lives under governance (`.gzkit/recommendations/` or
   similar) so additions are auditable and registered, not buried in
   validator code.
3. **Agent-session orientation integration.** The session orientation
   hook (`scripts/session_orientation.py`) surfaces uninstalled-but-
   recommended hooks alongside its existing freshness/handoff
   reporting, so agents can prompt operators at session boundaries
   instead of letting opt-in features rot silently.
4. **Claude Code hook discovery.** Whether agent-tool hooks
   (`PreToolUse` / `PostToolUse` in `.claude/settings.json`) should
   detect and recommend git-level hooks is a meaningful design
   question — different trigger surface from pre-commit, different
   audit envelope, different recovery story when a hook misfires.
   Resolved at promotion.

The pool-level commitment is to the *contract*: opt-in features are
discoverable through a registered tool surface, not through ADR
spelunking. Implementation shape (verb, registry path, integration
points) is the design-conversation work that promotion unlocks.

---

## Alternatives Considered

1. **Document opt-in features in runbooks only.** Rejected: runbook
   prose decays without a fail-close enforcement surface. The existing
   `gz validate --cli-alignment` rule (`.claude/rules/governance-core.md`
   § Operator-doc verb resolution) exists precisely because doc-only
   contracts rot. The same logic applies to opt-in config.
2. **Auto-install opt-in hooks on `gz init` / `gz tidy`.** Rejected:
   ADR-0.0.29 § Negative #6 already named pre-commit hook interaction
   as fragile; auto-installing without operator consent inverts the
   opt-in contract and converts a discovery problem into a surprise
   problem.
3. **Bundle discovery into existing `gz preflight` / `gz status` /
   `gz state`.** Likely *consumed* by those surfaces post-promotion,
   but the recommendation registry itself is a new artifact class with
   its own schema, governance, and CI footprint. Folding registry
   authoring into a consumer surface obscures the registry as the
   source of truth.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- Do not replicate `gz validate`, `gz preflight`, or `gz state` logic
  inside the recommendation tool — those surfaces produce *facts*; this
  tool produces *recommendations* over those facts.
- Do not introduce new ledger event classes pre-promotion; emission
  contract is part of the promotion design conversation.
- Do not add operator-configurable suppression for required-severity
  recommendations without an explicit doctrine entry.

---

## Dependencies

- **Blocks on**: None known.
- **Blocked by**:
  - ADR-0.0.29 (complexity-advisor auto-chain) — the canonical first
    recommendation, and the surface whose discovery gap motivated this
    pool entry.
  - OBPI-0.0.29-05 — the opt-in hook surface whose discovery gap is
    the immediate trigger.

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Operator assigns a SemVer ADR ID for active implementation.
2. Verb shape (`gz check --config-recommendations` vs. `gz config
   evaluate` vs. integration into an existing surface) is decided.
3. Recommendation registry schema (precondition / recommendation /
   rationale / install commands / severity) is decided and added under
   `src/gzkit/schemas/`.
4. Claude Code hook discovery scope (in or out of v1) is decided.
5. Session-orientation integration contract (output shape, exit-code
   semantics, agent-prompt template) is decided.

---

## Trigger

Surfaced during OBPI-0.0.29-05 Stage 4 ceremony — operator noted the
opt-in advisor auto-chain hook will not be noticed without a config
guidance surface, reproducing the *"advisor exists but never fires"*
class the parent ADR was authored to close.

Routed here under GHI #408 (closed `superseded` against this pool ADR).

---

## Related

- ADR-0.0.29 § Negative #6 — pre-commit hook fragility rationale.
- OBPI-0.0.29-05 — auto-chain hook (the immediate surface that needs
  discovery).
- `.gzkit/rules/complexity-doctrine.md` — the doctrine cluster this
  hook serves.
- `.claude/rules/governance-core.md` § Operator-doc verb resolution —
  precedent for fail-close enforcement of opt-in doctrine.
- `scripts/session_orientation.py` — likely integration point for
  agent-session surfacing.

---

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
