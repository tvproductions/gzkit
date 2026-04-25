# ADR Closeout Form: ADR-0.0.30-complexity-authoring-guidance

**Status**: Phase 0 — Proposed (closeout pending OBPI completion)

---

## Pre-Attestation Checklist

Closeout evidence to be verified after OBPI completion:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes (`mkdocs build --strict`)
- [ ] Gate 4 (BDD): Behave suite passes (scenarios tagged `@REQ-0.0.30-NN-MM`)
- [ ] Code reviewed
- [ ] Foundation-kind closeout walkthrough per ADR-0.0.18 (heavy lane + foundation kind)
- [ ] `gz complexity-guide` CLI verb + manpage + behave smoke + release-notes (Heavy-lane subcommand)
- [ ] `complexity-guide` skill vendor-mirrored; Output Contract aligned with destination verb; cross-reference to `complexity-advisor` present
- [ ] Frozen `AuthoringHint` projection from `AdvisorDiagnosis` (one-direction; no reverse projection)
- [ ] LSP-style JSON-over-stdio protocol implemented; specification document at `docs/governance/complexity/authoring-guide-protocol.md` editor-author-facing
- [ ] `gz-justify` skill amendment additive only (existing structure preserved); justify renders authoring-time hints for `.py` allowed-paths
- [ ] All four foundation ADRs in the cluster (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) cite each other consistently per OBPI-0.0.27-07 link-integrity validator
- [ ] Manpage updates for `gz complexity-guide`; runbook entries under "Complexity doctrine surfaces"; cluster end-to-end runnable

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ADR-0.0.30-complexity-authoring-guidance.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build passes | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | Behave suite passes | `uv run behave features/complexity_guide.feature features/authoring_guide_protocol.feature features/justify_complexity_hints.feature` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Validator (cluster links) | Link integrity holds | `uv run gz validate --complexity-doctrine-links` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.30-complexity-authoring-guidance` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.30-01-complexity-guide-cli](obpis/OBPI-0.0.30-01-complexity-guide-cli.md) | `gz complexity-guide` CLI verb (Heavy-lane new subcommand; in-line hint prose; --json mode) | Pending |
| [OBPI-0.0.30-02-complexity-guide-skill](obpis/OBPI-0.0.30-02-complexity-guide-skill.md) | `complexity-guide` skill (vendor-mirrored; Output Contract; cross-reference to `complexity-advisor`) | Pending |
| [OBPI-0.0.30-03-authoring-hint-engine](obpis/OBPI-0.0.30-03-authoring-hint-engine.md) | `AuthoringHint` projection from `AdvisorDiagnosis` + authoring-time engine | Pending |
| [OBPI-0.0.30-04-editor-protocol-contract](obpis/OBPI-0.0.30-04-editor-protocol-contract.md) | LSP-style JSON-over-stdio protocol + specification document for editor authors | Pending |
| [OBPI-0.0.30-05-justify-integration](obpis/OBPI-0.0.30-05-justify-integration.md) | `gz justify` integration: authoring-time hints surface in justification scaffold | Pending |

## Parallelism

`OBPI-03 → OBPI-01 → OBPI-02 → OBPI-04 → OBPI-05`

The hint engine + projection (OBPI-03) is the data surface; the CLI (OBPI-01) wires it to ad-hoc invocation; the skill (OBPI-02) routes operators at the surface layer; the protocol contract (OBPI-04) extends the engine to a stdio interface for editors; the `gz justify` integration (OBPI-05) lands last because it amends an existing skill.

## Cluster Citations

ADR-0.0.30 cites:
- ADR-0.0.27 OBPI-04 (distilled-characteristics) — engine reads transitively via the advisor engine
- ADR-0.0.28-02 (`ThresholdTable`) — `advise` band consumed
- ADR-0.0.29-01 (`AdvisorDiagnosis`) — projected to `AuthoringHint`
- ADR-0.0.29-02 (advisor diagnosis engine) — wrapped by the authoring engine
- ADR-0.0.19 (pre-execution reasoning walkthrough doctrine) — `gz justify` integration closes the forward reference
- ADR-0.0.18 (taxonomy doctrine) — foundation-kind brief-level Gate 5 attestation rigor

ADR-0.0.30 is cited by:
- Pool stub `ADR-pool.complexity-authoring-editor-reference` — future ADR scope if a reference editor implementation becomes warranted (forward-reference at OBPI-04)

## Cluster Loop Closed

ADR-0.0.30 is the cluster's closing foundation. The cluster's flow:
- ADR-0.0.27: corpus methodology + distillation + citation contract (the empirical basis)
- ADR-0.0.28: threshold table + trigger-semantic vocabulary (the per-metric doctrine)
- ADR-0.0.29: trigger-time advisor (warn / block band response)
- ADR-0.0.30: authoring-time guidance (advise band consumer + `gz justify` loop closure)

All four foundation ADRs cite each other through OBPI-0.0.27-05's citation tuple form; OBPI-0.0.27-07's link-integrity validator is the structural defense against citation drift across the cluster.

## Defense Brief

*To be authored at closeout — populated by `gz closeout` ceremony from OBPI Closing Arguments.*

## Human Attestation

*Pending OBPI completion. Foundation-kind + heavy-lane stacks attestation rigor — TTY + ATTEST gate required at brief level for every OBPI per AGENTS.md § Lane & Kind Attestation Matrix.*
