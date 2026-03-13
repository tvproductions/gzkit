---
id: ADR-0.12.0-obpi-pipeline-enforcement-parity
status: Proposed
semver: 0.12.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-12
promoted_from: ADR-pool.obpi-pipeline-enforcement-parity
---

# ADR-0.12.0-obpi-pipeline-enforcement-parity: AirlineOps-Style OBPI Pipeline Enforcement Parity

## Intent

gzkit now has the documented OBPI pipeline mandate from
`ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`, but the repository
still relies on agent memory and written instructions to make that mandate
stick. AirlineOps already proved a stronger model: hook-enforced routing that
pushes OBPI work onto the required pipeline before scope expands into
implementation or completion accounting.

That missing enforcement layer is now the primary procedural defect in gzkit's
OBPI workflow:

- plan-mode work can exit without a mechanical handoff into
  `gz-obpi-pipeline`;
- write-time changes under `src/` or `tests/` can still begin outside the
  pipeline path;
- completion reminders exist as doctrine, not as active runtime pressure;
- hook registration and ordering are not yet aligned with the AirlineOps
  control surface that already proved reliable.

This ADR closes that defect by importing the AirlineOps enforcement chain into
gzkit as faithful parity work. The target is not a loose local approximation.
It is the same operator-shaping behavior adapted to gzkit-native paths,
commands, and governance artifacts.

## Decision

Implement AirlineOps-style OBPI pipeline enforcement parity as a seven-unit
heavy-lane package:

1. **Canonical Intake Contract**: inventory the AirlineOps hook chain,
   settings registration, and bridging state needed for parity, then map each
   source surface to a gzkit-native target contract (`OBPI-0.12.0-01`).
2. **Plan-Exit Audit Gate**: port the plan-exit audit hook so unfinished plan
   state is checked before agents leave planning mode (`OBPI-0.12.0-02`).
3. **Pipeline Router + Active Marker Bridge**: port the routing hook and the
   active-marker/receipt bridge that converts approved plan work into an active
   `gz-obpi-pipeline` session (`OBPI-0.12.0-03`).
4. **Write-Time Pipeline Gate**: port the write-time blocking hook for `src/`
   and `tests/` so implementation cannot proceed outside an active OBPI
   pipeline (`OBPI-0.12.0-04`).
5. **Completion Reminder Surface**: port the pre-commit / pre-push reminder
   behavior that keeps unfinished pipeline state visible before code leaves the
   local workstation (`OBPI-0.12.0-05`).
6. **Registration + Verification Alignment**: register the imported hooks in
   gzkit settings with the correct ordering and align tests, docs, and operator
   evidence to the enforced runtime (`OBPI-0.12.0-06`).
7. **Plan-Audit Skill + Receipt Parity**: port `gz-plan-audit` and the
   `.claude/plans/.plan-audit-receipt.json` contract required by the gate and
   router. This remains numbered `OBPI-0.12.0-07` to avoid renumbering the
   already-seeded briefs, but it is a prerequisite surface consumed by
   `OBPI-0.12.0-02` and `OBPI-0.12.0-03`.

This ADR deliberately builds on earlier work instead of replacing it:

- `ADR-0.11.0` established the faithful OBPI completion pipeline and canonical
  skill surface, but not the mechanical hook chain that forces agents onto that
  path.
- `ADR-0.9.0` already imported AirlineOps governance surfaces broadly, so this
  ADR is a focused parity tranche for the specific enforcement runtime.
- `ADR-pool.prime-context-hooks` and `ADR-pool.execution-memory-graph` remain
  related backlog work, but neither is required to import the proven hook
  chain now.

## Consequences

### Positive

- gzkit gains mechanical enforcement for a pipeline mandate that is currently
  only documented.
- Heavy-lane OBPI execution becomes harder to bypass through habit drift or
  partial local reinterpretation.
- Operator documentation, hook settings, and pipeline lifecycle evidence can
  converge on one runtime story.

### Negative

- The work spans multiple hook surfaces and settings order, so mistakes can
  create noisy or over-blocking local behavior.
- Faithful parity raises the verification burden because docs, tests, and hook
  registration all need to agree at once.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 0
- Split Total: 2
- Final Target OBPI Count: 7

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [x] OBPI-0.12.0-01: Inventory the canonical AirlineOps hook chain and define
      the gzkit parity contract.
- [x] OBPI-0.12.0-02: Port the plan-exit audit gate with gzkit-compatible
      blocking behavior.
- [ ] OBPI-0.12.0-03: Port the pipeline router and active-marker bridge that
      hand approved plan work into `gz-obpi-pipeline`.
- [ ] OBPI-0.12.0-04: Port the write-time pipeline gate for `src/` and
      `tests/`.
- [ ] OBPI-0.12.0-05: Port the completion reminder surfaces that reinforce
      unfinished pipeline state before commit and push.
- [ ] OBPI-0.12.0-06: Register the hook chain in settings and align tests,
      docs, and operator verification with the enforced runtime.
- [x] OBPI-0.12.0-07: Port `gz-plan-audit` and the receipt-generation contract
      consumed by the plan-exit gate and pipeline router.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion seeded via `gz adr promote`; interview transcript not captured.

Draft framing preserved from:

- `docs/design/adr/pool/ADR-pool.obpi-pipeline-enforcement-parity.md`
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/`
- AirlineOps parity target hooks:
  - `../airlineops/.claude/hooks/plan-audit-gate.py`
  - `../airlineops/.claude/hooks/pipeline-router.py`
  - `../airlineops/.claude/hooks/pipeline-gate.py`
  - `../airlineops/.claude/hooks/pipeline-completion-reminder.py`

Key conclusion preserved here: gzkit already has the mandate and the canonical
pipeline skill, but it still lacks the runtime enforcement chain that keeps
agents from drifting back into advisory-only behavior.

Implementation note added during `OBPI-0.12.0-01`: the canonical hook chain
also depends on a `gz-plan-audit` receipt generator. That surfaced as a real
hidden dependency once this ADR was promoted and decomposed. The package
therefore adds `OBPI-0.12.0-07` instead of silently overloading
`OBPI-0.12.0-03`.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`
- [ ] Hook surfaces: `.claude/hooks/`, generated control surfaces, and hook
      settings registration
- [ ] ADR package: `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/`

## Alternatives Considered

- Keep this work in pool until reprioritized.
- Continue relying on `AGENTS.md` pipeline doctrine without mechanical hook
  enforcement.
- Defer all hook work until `ADR-pool.execution-memory-graph` or
  `ADR-pool.prime-context-hooks` is promoted.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.12.0 | Completed | Test User | 2026-03-13 | completed |
