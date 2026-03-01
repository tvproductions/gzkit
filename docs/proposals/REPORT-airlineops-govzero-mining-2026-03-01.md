# REPORT: AirlineOps GovZero Mining

## Metadata

- Date: 2026-03-01
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`
- Scope: GovZero process-habit extraction across control surfaces

---

## Mining Surfaces

- [x] `AGENTS.md`
- [x] `CLAUDE.md`
- [x] `.github/**`
- [x] `.claude/**`
- [x] `.codex/**`
- [x] `.gzkit/**`
- [x] `docs/governance/GovZero/**`
- [x] `docs/governance/governance_runbook.md`

---

## Mined Norms

| Norm ID | Mined Habit / Rule | Canonical Source Path | Product Capability? (Y/N) | Included in GovZero Scope? | gzkit Extraction Path(s) | Status (Parity/Partial/Missing/Divergent) | Notes |
|---|---|---|---|---|---|---|---|
| N-001 | Keep a dedicated governance runbook for procedural operation | `../airlineops/docs/governance/governance_runbook.md` | N | Y | `docs/governance/governance_runbook.md` | Parity | Added in this scan |
| N-002 | Canonical-root parity scans are deterministic and fail closed | `../airlineops/docs/governance/governance_runbook.md` | N | Y | `.gzkit/skills/airlineops-parity-scan/SKILL.md` | Parity | Lodestar path defect fixed in this scan |
| N-003 | Governance instruction files are first-class orientation doctrine | `../airlineops/.github/instructions/*.instructions.md` | N | Y | `.github/instructions/**` | Partial | Governance-critical subset scaffolded; full parity pending |
| N-004 | GovZero doc surfaces should maintain path-level parity | `../airlineops/docs/governance/GovZero/**` | N | Y | `docs/governance/GovZero/**` | Parity | `governance-registry-design.md` imported |
| N-005 | Tool lifecycle should preserve naming consistency across mirrors | `../airlineops/.github/skills/gz-adr-manager/**` | N | Y | `.github/skills/gz-adr-manager/**` + `.github/skills/gz-adr-create/**` | Parity | Compatibility alias strategy implemented |
| N-006 | Human attestation is required authority boundary for completion claims | `../airlineops/AGENTS.md`, runbook ceremony sections | N | Y | `AGENTS.md`, `docs/user/commands/attest.md` | Parity | Runtime and doctrine align |
| N-007 | Layered trust ordering (evidence -> ledger -> sync) governs reconciliation | `../airlineops/docs/governance/GovZero/layered-trust.md` | N | Y | `docs/governance/GovZero/layered-trust.md`, governance runbook | Parity | Explicit in new runbook |
| N-008 | Validation rituals must be executable, not declarative only | Canonical runbook validation bundles | N | Y | `gz cli audit`, `gz check-config-paths`, `mkdocs --strict` | Parity | All checks PASS 2026-03-01 |

## NOT GovZero Exclusion Log

Exclusions are exceptional. Default is inclusion in GovZero scope unless product capability evidence is explicit.

| Candidate Item | Canonical Source Path | Why NOT GovZero | Product Capability Evidence | Reviewer |
|---|---|---|---|---|
| AirlineOps domain-specific data/forecasting routines | `../airlineops/src/airlineops/**` | Product behavior, not governance process | package namespace and command families are domain-specific | Agent |

---

## Procedure Parity Checks

| Procedure Class | Canonical Source(s) | gzkit Runtime/Docs Surface(s) | Executable Check | Result | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | runbook + instruction files + AGENTS | AGENTS + `.github/instructions/**` + governance runbook | path checks | Partial | governance-critical subset present; full parity backlog remains |
| Tool-use control | canonical `gz-*` skill surfaces | gz skills + CLI docs + alias skill | skill/path checks | PASS | compatibility alias removes invocation drift |
| Post-tool accounting | audit protocol + receipt routines | `gz audit`, receipt commands | command availability | PASS | command docs + CLI help |
| Validation | canonical ritual commands | `uv run gz cli audit` | command run | PASS | `CLI audit passed.` |
| Validation | canonical ritual commands | `uv run gz check-config-paths` | command run | PASS | `Config-path audit passed.` |
| Verification | canonical ledger evidence checks | `uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol` | command run | PASS | all OBPIs completed with evidence |
| Presentation | docs-as-proof discipline | `uv run mkdocs build --strict` | command run | PASS | strict build succeeded |
| Human attestation boundary | closeout + attestation doctrine | `gz closeout`, `gz attest`, AGENTS protocol | doc/runtime alignment | PASS | explicit attestation language present |

---

## Required Commands

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol
uv run mkdocs build --strict
```

---

## Findings and Next Actions

1. Finding:
   - Severity: P2
   - Why it matters: Instruction surface is now present but not yet a full mirror of all canonical instruction files.
   - ADR/OBPI linkage: `ADR-pool.airlineops-canon-reconciliation` -> `instruction-surface-parity`
   - Next action: expand instruction parity from governance-critical subset to broader canonical coverage.

2. Finding:
   - Severity: P3 (resolved)
   - Why it matters: GovZero canonical doc surface is now path-complete for the previously missing file.
   - ADR/OBPI linkage: `ADR-pool.airlineops-canon-reconciliation` -> `govzero-doc-surface-completion`
   - Next action: maintain canonical sync on future updates.

3. Finding:
   - Severity: P3 (resolved via compatibility)
   - Why it matters: Cross-repo invocation drift is reduced by alias continuity.
   - ADR/OBPI linkage: `ADR-0.5.0-skill-lifecycle-governance` follow-up compatibility policy
   - Next action: decide long-term upstream naming convergence.

4. Finding:
   - Severity: P3 (resolved)
   - Why it matters: Governance runbook extraction increases procedural maturity in gzkit.
   - ADR/OBPI linkage: `ADR-0.7.0-obpi-first-operations`
   - Next action: keep synchronized via weekly parity scans.
