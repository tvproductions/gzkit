---
id: ADR-pool.vendor-alignment-codex
status: Pool
lane: heavy
parent: PRD-GZKIT-1.0.0
---

# ADR-pool.vendor-alignment-codex: OpenAI Codex Vendor Alignment

## Persona

`main-session`: a craftsperson who treats cross-vendor parity as equivalent
observable governance behavior, not matching filenames. Vendor claims require
runtime evidence from the harness-specific adapter and the shared invariant.

## Intent

Align gzkit's Codex surface (`.agents/` and `.codex/`) with OpenAI Codex's native
affordances. The repository now carries a minimal hand-maintained Codex
configuration, an obsolete hook file that Codex 0.144.1 parses as zero
handlers, five hand-maintained subagent roles, and generated skill/persona
mirrors. These surfaces do not yet form a generated enforcement contract.
Codex has matured significantly across CLI,
IDE extension, and app:
project-scoped `.codex/config.toml`, AGENTS.md instruction chains, MCP
servers, skills, subagents, sandbox policies, approval modes, hooks, and
session continuity. This ADR captures the design decisions needed to activate
the Codex surface as an equal first-class vendor target.

---

## Decision

Promote `ADR-pool.vendor-alignment-codex` into active implementation and execute the following tracked scope:

- **codex-config-generation** — Generate and validate project-scoped `.codex/config.toml` from gzkit configuration while preserving user-owned settings
- **codex-hooks-policy** — Generate current Codex hook registration and vendor-native adapters for ten direct lifecycle behaviors, with two `ExitPlanMode` behaviors enforced by runtime substitutes
- **codex-skills-personas-subagents** — Generate Codex subagent role definitions from canonical persona and role contracts, and validate skill, persona, and agent-role parity without editing vendor mirrors as source
- **harness-aware-pipeline-runtime** — Replace Claude-only `.claude/plans` authority with harness-neutral plan-audit and pipeline-transition state while retaining Claude compatibility
- **codex-surface-validation** — Extend `gz validate --surfaces` and tests so Codex config, hooks, skills, personas, and generated metadata drift fail like Claude drift
- **codex-instruction-budget-and-docs** — Prove Codex instruction-budget headroom and publish an observed-output runbook for the completed first-class surface

## Consequences

### Positive

- Codex receives the same governing decisions at the earliest lifecycle event
  its harness can safely express.
- Shared runtime predicates remain authoritative while vendor adapters stay
  thin, testable translations.
- Generated Codex config, hooks, skills, personas, and agent roles become
  reproducible distribution surfaces rather than hand-maintained files.

### Negative

- Codex does not expose Claude's `ExitPlanMode`; plan-audit and pipeline-router
  parity require first-mutation and runtime-transition substitutes.
- Codex documents incomplete interception for some shell and alternative tool
  paths, so hooks improve feedback latency but cannot become the only gate.
- Project hook changes require Codex trust review before the new definition runs.

## Boundary Invariants

1. **Runtime authority:** no fail-closed governance invariant may exist only in
   a vendor hook; the shared `gz` runtime, validator, or guarded git path remains
   the authoritative enforcement point.
2. **Semantic parity:** Claude and Codex adapters may differ in event and output
   shape, but equivalent repository state and intended action must produce the
   same allow, deny, or corrective-feedback decision.
3. **Generated-surface direction:** `.codex/**`, `.agents/skills/**`, and
   `.agents/personas/**` are delivery surfaces. Canonical inputs live under
   `src/gzkit/**` or `.gzkit/**`; sync never reads a vendor mirror as source.
4. **Ordered composites:** because Codex launches matching hooks concurrently,
   checks with ordering dependencies execute inside one composite adapter per
   lifecycle event.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The generated Codex surface satisfies the repository's surface contract. | uv run gz validate --surfaces | 0 |

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

- [ ] OBPI-0.44.0-01: **codex-config-generation** — Generate and validate project-scoped `.codex/config.toml` from gzkit configuration while preserving user-owned settings
- [ ] OBPI-0.44.0-02: **codex-hooks-policy** — Generate current Codex hook registration and vendor-native adapters for ten direct lifecycle behaviors, with two `ExitPlanMode` behaviors enforced by runtime substitutes
- [ ] OBPI-0.44.0-03: **codex-skills-personas-subagents** — Generate Codex subagent roles from canonical inputs and validate skill, persona, and role parity without treating vendor mirrors as source
- [ ] OBPI-0.44.0-04: **harness-aware-pipeline-runtime** — Replace Claude-only `.claude/plans` authority with harness-neutral plan-audit and pipeline-transition state while retaining Claude compatibility
- [ ] OBPI-0.44.0-05: **codex-surface-validation** — Extend `gz validate --surfaces` and tests so Codex config, hooks, skills, personas, and generated metadata drift fail like Claude drift
- [ ] OBPI-0.44.0-06: **codex-instruction-budget-and-docs** — Prove Codex instruction-budget headroom and publish an observed-output runbook for the completed first-class surface

## Target Scope

- **codex-config-generation** — Generate and validate project-scoped
  `.codex/config.toml` from gzkit config.
- **codex-hooks-policy** — Generate `.codex/hooks.json` and Codex adapters for
  the ten Claude enforcement behaviors with direct lifecycle homes; keep the
  two `ExitPlanMode`-dependent behaviors as explicit runtime substitutes.
- **codex-skills-personas-subagents** — Make Codex skills, personas, and
  subagent role config a coherent generated surface.
- **harness-aware-pipeline-runtime** — Remove Claude-only `.claude/plans`
  assumptions from pipeline runtime paths.
- **codex-surface-validation** — Extend surface validation and tests to cover
  Codex drift.
- **codex-instruction-budget-and-docs** — Prove Codex instruction-budget
  headroom and publish observed config, trust, hook, role, pipeline, and
  validation workflows.

Execution order is `01 -> 04 -> 02 -> 03 -> 05 -> 06`. Hook enforcement
depends on harness-neutral plan-transition state; validation and documentation
close only after all generated surfaces exist.

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md with a Codex-specific file — AGENTS.md is
  the shared contract.
- No blind parity with Claude's hook system — Codex hooks exist, but their
  event behavior and blocking semantics differ. Parity is operational, not
  textual.

---

## Dependencies

- **Blocks on**: OBPI-0.44.0-02 is blocked by OBPI-0.44.0-04;
  OBPI-0.44.0-05 is blocked by OBPI-0.44.0-01 through -04;
  OBPI-0.44.0-06 is blocked by OBPI-0.44.0-05
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
- Codex hooks are stable in the installed 0.144.1 runtime but remain a
  guardrail rather than a complete enforcement boundary. The key design
  question is not "does Codex have hooks?" but "which gzkit invariants can be
  enforced through Codex hooks without inventing false fail-closed semantics?"
- Codex subagents are explicitly spawned by the operator or primary agent. This
  aligns with gzkit's Prime Directive preference for deliberate delegation with
  a clear "Why" parameter.
- `agents/openai.yaml` is Codex-native optional skill metadata. Existing skill
  packages already preserve that metadata through byte-for-byte mirroring;
  role generation must not invent a second metadata source.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.vendor-alignment-codex` on 2026-07-10; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.44.0 | Pending | | | |
