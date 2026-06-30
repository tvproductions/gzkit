# AUDIT PLAN (Gate-5) — ADR-0.30.0

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.30.0-okf-documentation-knowledge-structure |
| ADR Title | OKF Documentation Knowledge Structure |
| SemVer | 0.30.0 |
| ADR Dir | docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure |
| Audit Date | 2026-06-29 |
| Auditor(s) | g0 (operator) + Claude (pipeline-orchestrator), spec-reviewer + quality-reviewer subagents |

## Purpose

Confirm ADR-0.30.0 implementation is complete and integrated by validating its
claims with reproducible CLI evidence and the bound fidelity gate. Move the ADR
from COMPLETED → VALIDATED.

**Audit Trigger:** Gate-5 validation following completion of all 6 OBPIs
(`/gz-adr-audit ADR-0.30.0`).

## Scope & Inputs

**Primary contract surfaces introduced by this ADR:**

- `uv run gz knowledge generate` / `uv run gz knowledge refresh` — OKF bundle generator CLI (OBPI-02/04)
- `uv run gz validate --okf-conformance` — generated-bundle-only conformance validator (OBPI-03)
- OKF concept-frontmatter JSON schema: `src/gzkit/schemas/okf_concept_frontmatter.json` (OBPI-01)
- Generated bundle home: `.gzkit/governance/knowledge/` (index.md + 5 concept docs) (OBPI-02/05/06)
- Content-boundary doctrine doc: `.gzkit/governance/knowledge/content-boundary.md` (OBPI-06)

**Load-bearing fence (STRUCTURAL-FENCE):** OKF frontmatter/links are NEVER
consumed as enforcement evidence by any `gz validate` / gates / closeout surface
(ADR Boundary Invariant #1).

## Planned Checks

| Check | Command / Method | Expected Signal | Status |
|-------|------------------|-----------------|--------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.30.0 --json` | passed=true, all 6 OBPIs complete | Done ✓ |
| Bound fidelity gate | `uv run gz adr fidelity ADR-0.30.0` | All assertions PASS | Done ✓ |
| OKF conformance | `uv run gz validate --okf-conformance` | exit 0 | Done ✓ |
| Bundle idempotency | `uv run gz knowledge refresh --quiet` | exit 0, byte-stable | Done ✓ |
| Heavy gates | `uv run gz gates --adr ADR-0.30.0` | Gates 1–4 PASS | Done ✓ |
| Governance/CLI audit | `uv run gz cli audit` | passed, 114/114 covered | Done ✓ |
| Docs build (ADR edited) | `uv run mkdocs build --strict` | Build clean | Done ✓ |
| Independent REQ trace | spec-reviewer subagent | Coverage holds; kinds legitimate | Done ✓ |
| Independent integration | quality-reviewer subagent | OBPIs cohere; fence holds | Done ✓ |

## Risk Focus

- **Stale fidelity block** — authored at planning time as a WEAK "not-yet-landed"
  proxy; must be re-derived to exercise the landed surfaces. (Resolved — see AUDIT.md.)
- **STRUCTURAL-FENCE integrity** — the OKF-as-orientation-not-authority fence is
  the feature's load-bearing invariant; verified to have zero enforcement consumers.
- **Generated-bundle-only scope** — `--okf-conformance` must never gate authored
  source docs.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- Bound fidelity gate green against the running system.
- No unresolved ✗ failures.
- Validation receipt emitted; lifecycle confirmed Validated.
