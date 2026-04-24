---
id: ADR-0.44.0-vendor-alignment-codex
status: Proposed
kind: feature
semver: 0.44.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-23
promoted_from: ADR-pool.vendor-alignment-codex
---

# ADR-0.44.0-vendor-alignment-codex: OpenAI Codex Vendor Alignment

## Persona

Agents working on this ADR use the `main-session` persona for design and
operator-facing judgment, `implementer` for OBPI execution, and
`quality-reviewer` for surface validation. The behavioral frame is direct,
governance-aware craftsmanship: read the existing vendor generation surface
whole before changing it, preserve `.gzkit/` as canon, and treat Codex parity as
an operational contract rather than a directory-copy exercise.

## Intent

Align gzkit's Codex surface (`.agents/` and `.codex/`) with OpenAI Codex's native
affordances. The current `.agents/skills/` and `.agents/personas/` mirrors prove
that Codex is recognized by sync, but the mirror is not enough: no generated
`.codex/config.toml`, no `.codex/hooks.json`, no Codex subagent role config, no
Codex drift validation, and no pipeline runtime abstraction for non-Claude plan
and marker paths. This leaves Codex as a passive copy target while Claude is an
active harness with settings, hooks, roles, and validation. Codex has matured
across CLI, IDE extension, and app: project-scoped config, AGENTS.md instruction
chains, MCP servers, skills, subagents, sandbox policies, approval modes, hooks,
and session continuity. This ADR activates Codex as an equal first-class vendor
target without making Claude-specific assumptions portable by assertion.

---

## Decision

1. Promote `ADR-pool.vendor-alignment-codex` into active Heavy-lane feature
   implementation as `ADR-0.44.0` because the work changes generated
   configuration, hook registration, runtime path semantics, and validation
   surfaces used by agents and operators.
2. Treat `.gzkit/` as the canonical authoring surface and generate Codex-native
   artifacts from it. Codex parity is not achieved by hand-editing `.agents/` or
   `.codex/`; generated surfaces must round-trip through
   `gz agent sync control-surfaces` and fail drift validation.
3. Add `.codex/config.toml` generation as the first implementation increment so
   model, approval, sandbox, skill, MCP, and subagent defaults are explicit and
   reviewable before hooks or runtime behavior depend on them.
4. Add `.codex/hooks.json` generation only after classifying each existing
   Claude hook by portability. The rationale is fail-closed governance: a hook
   that cannot block or order execution the same way in Codex must become a
   runtime check or a documented non-portable behavior, not a false parity claim.
5. Make skills, personas, and Codex subagent roles a single generated role
   surface. `.agents/skills`, optional `agents/openai.yaml`, `.agents/personas`,
   and Codex `[agents.*]` config must agree on role names and behavioral
   identity.
6. Introduce a harness-aware pipeline path abstraction before Codex pipeline
   execution is advertised. The current `.claude/plans` assumption is a Claude
   implementation detail; Codex needs its own plan receipt and marker path
   contract without breaking existing Claude receipts.
7. Close GHI #298 only after the ADR package owns the implementation path and
   final OBPI evidence proves Codex config, hooks, skills/personas/subagents,
   pipeline runtime paths, validation, and docs behave as first-class surfaces.

## Rationale

The dominant reason to promote this ADR is asymmetry. Claude has a generated
`CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/`, `.claude/rules/`,
`.claude/skills/`, `.claude/personas/`, and pipeline plan markers. Codex has
shared `AGENTS.md`, `.agents/skills/`, and `.agents/personas/`, but no generated
configuration or validation that makes those mirrors operational. That mismatch
causes two failure classes: Codex agents silently miss governance mechanics that
Claude agents receive mechanically, and future maintainers mistake mirror
presence for harness readiness.

The decision favors a governed, generated Codex surface over a one-off local
config because gzkit's core invariant is that control surfaces are generated
from canonical doctrine. Codex-specific behavior belongs in explicit adapters:
`src/gzkit/config.py` for vendor config, `src/gzkit/sync_surfaces.py` for
generation orchestration, `src/gzkit/sync_skills.py` for skills, `src/gzkit/rules.py`
for rule rendering decisions, `src/gzkit/personas.py` for persona adapters, and
pipeline runtime modules for plan/marker path behavior. Tests under `tests/`
must assert those semantics so the generated Codex surface cannot drift
silently.

## Architectural Alignment

Source-path anchors for this ADR:

- `src/gzkit/config.py` — existing `VendorsConfig.codex` and path defaults.
- `src/gzkit/sync_surfaces.py` — manifest generation, vendor-aware sync, Claude
  settings generation, persona mirrors, and future Codex config/hook generation.
- `src/gzkit/sync_skills.py` — canonical skill mirror generation for
  `.agents/skills`.
- `src/gzkit/rules.py` — existing Claude/Copilot rule renderers and the decision
  point for whether Codex receives generated command rules or explicit
  non-support.
- `src/gzkit/personas.py` — existing Codex persona renderer.
- `src/gzkit/pipeline_runtime.py` and related pipeline modules — current plan
  and marker path assumptions that must become harness-aware.
- `tests/test_sync.py`, `tests/test_sync_surfaces.py`,
  `tests/test_persona_loading.py`, `tests/test_pipeline_runtime.py`, and
  `tests/test_validate_sync_parity.py` — precedent test surfaces for generated
  vendor artifacts and drift validation.

Precedents:

- ADR-0.16.0 established canonical `.gzkit/` content with generated vendor
  mirrors rather than hand-authored vendor files.
- ADR-0.17.0 slimmed Claude context by delegating to canonical surfaces instead
  of duplicating catalog content.
- ADR-0.18.0 and the pipeline skills established agent role specialization and
  subagent-driven execution as governed surfaces.
- ADR-0.0.20 established that binding agent rules must live where agents
  actually load them and that generated mirrors cannot be the source of truth.

Anti-patterns this ADR rejects:

- Treating `.agents/skills` as sufficient Codex support while leaving config,
  hooks, roles, and validation absent.
- Copying `.claude/hooks` semantics into `.codex/hooks.json` without proving the
  event model can enforce the same invariant.
- Hand-editing `.codex/` or `.agents/` artifacts instead of generating them from
  `.gzkit/`.
- Advertising Codex pipeline support while runtime code still assumes
  `.claude/plans`.
- Ignoring the instruction-budget risk from a root `AGENTS.md` larger than
  Codex's documented default project-doc budget.

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

- [ ] OBPI-0.44.0-01: **codex-config-generation** — Generate and validate project-scoped `.codex/config.toml` from gzkit config, including model, approval, sandbox, skill, MCP, and subagent defaults
- [ ] OBPI-0.44.0-02: **codex-hooks-policy** — Generate `.codex/hooks.json` only for gzkit behaviors whose semantics are safe under Codex hook execution, and document non-portable Claude hook behavior explicitly
- [ ] OBPI-0.44.0-03: **codex-skills-personas-subagents** — Make `.agents/skills`, `agents/openai.yaml`, `.agents/personas`, and Codex subagent role config a coherent generated surface
- [ ] OBPI-0.44.0-04: **harness-aware-pipeline-runtime** — Remove Claude-only `.claude/plans` assumptions from pipeline runtime paths by introducing a harness-aware plan and marker path abstraction
- [ ] OBPI-0.44.0-05: **codex-surface-validation** — Extend `gz validate --surfaces` and tests so Codex config, hooks, skills, personas, and generated metadata drift fail like Claude drift
- [ ] OBPI-0.44.0-06: **codex-instruction-budget-and-docs** — Resolve Codex instruction-budget risk, update docs/runbooks, and close GHI #298 with evidence that the Codex surface is now first-class

## Target Scope

- **codex-config-generation** — Generate and validate project-scoped
  `.codex/config.toml` from gzkit config.
- **codex-hooks-policy** — Generate `.codex/hooks.json` only for gzkit
  behaviors whose semantics are safe under Codex hook execution.
- **codex-skills-personas-subagents** — Make Codex skills, personas, and
  subagent role config a coherent generated surface.
- **harness-aware-pipeline-runtime** — Remove Claude-only `.claude/plans`
  assumptions from pipeline runtime paths.
- **codex-surface-validation** — Extend surface validation and tests to cover
  Codex drift.
- **codex-instruction-budget-and-docs** — Resolve Codex instruction-budget risk,
  update docs, and close GHI #298 with evidence.

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md with a Codex-specific file — AGENTS.md is
  the shared contract.
- No blind parity with Claude's hook system — Codex hooks exist, but their
  event behavior and blocking semantics differ. Parity is operational, not
  textual.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.universal-agent-onboarding (Codex benefits from
  vendor onboarding), ADR-pool.vendor-alignment-claude-code (MCP/server design
  shared), ADR-pool.per-command-persona-context (Codex subagents align with
  persona routing), ADR-pool.harness-aware-execution-modes,
  ADR-pool.harness-agnostic-plan-capture, GHI #298

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Decision made: promote as Heavy feature ADR because config, hooks,
   generated control surfaces, and pipeline runtime paths affect operator and
   agent contracts.
3. Proposed OBPI Decomposition table is present and promotion-ready.
4. Multi-agent thread limits agreed for OBPI parallel work.

---

## Notes

- Codex's `config.toml` is far more granular than Claude's `settings.json` —
  model reasoning effort, verbosity, per-agent config files, sandbox write
  roots, network proxy policies. This is both powerful and complex.
- Codex hooks are experimental and under active development. The key design
  question is not "does Codex have hooks?" but "which gzkit invariants can be
  enforced through Codex hooks without inventing false fail-closed semantics?"
- Codex subagents are explicitly spawned by the operator or primary agent. This
  aligns with gzkit's Prime Directive preference for deliberate delegation with
  a clear "Why" parameter.
- `agents/openai.yaml` is Codex-native optional skill metadata. Existing skill
  mirrors should be audited for useful metadata rather than copied as inert
  files.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.vendor-alignment-codex` on 2026-04-23; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Keep Codex alignment in the pool backlog.** Rejected because GHI #298
   surfaced an active operator request to make Codex first-class now. Leaving
   the work in the pool would preserve the mirror-only status quo and give
   future Codex sessions the false signal that `.agents/skills` is sufficient.
2. **Patch `.codex/config.toml` by hand as an adopter-local file.** Rejected
   because gzkit's control-surface doctrine requires generated vendor artifacts
   from canonical `.gzkit/` state. A hand-authored file would drift immediately
   and would not help downstream gzkit adopters.
3. **Pursue Claude feature parity textually.** Rejected because Codex hooks,
   config, skills, and subagents have different semantics. The ADR chooses
   operational parity: preserve the invariant where Codex can enforce it, move
   enforcement into gzkit runtime where hooks cannot fail closed, and document
   non-portable Claude behavior.
4. **Split each Codex surface into independent ADRs.** Rejected for this phase
   because config, hooks, skills/personas/subagents, pipeline path behavior, and
   validation form one vendor-readiness chain. Splitting them would create a
   partially first-class Codex target with no single closeout point.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.44.0 | Pending | | | |
