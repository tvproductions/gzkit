# ADR Closeout Form: ADR-0.12.0-obpi-pipeline-enforcement-parity

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz attest ADR-0.12.0-obpi-pipeline-enforcement-parity --status completed` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.12.0-01](obpis/OBPI-0.12.0-01-canonical-hook-inventory-and-parity-contract.md) | Canonical hook inventory and parity contract | Completed |
| [OBPI-0.12.0-02](obpis/OBPI-0.12.0-02-plan-exit-audit-gate-parity.md) | Plan-exit audit gate parity | Completed |
| [OBPI-0.12.0-03](obpis/OBPI-0.12.0-03-pipeline-router-and-active-marker-bridge.md) | Pipeline router and active-marker bridge | Completed |
| [OBPI-0.12.0-04](obpis/OBPI-0.12.0-04-write-time-pipeline-gate.md) | Write-time pipeline gate | Completed |
| [OBPI-0.12.0-05](obpis/OBPI-0.12.0-05-completion-reminder-surface.md) | Completion reminder surface | Completed |
| [OBPI-0.12.0-06](obpis/OBPI-0.12.0-06-settings-registration-and-operator-verification-alignment.md) | Settings registration and operator verification alignment | Completed |
| [OBPI-0.12.0-07](obpis/OBPI-0.12.0-07-plan-audit-skill-and-receipt-parity.md) | Plan-audit skill and receipt parity | Completed |

## Human Attestation

### Verbatim Attestation

- `completed`

**Attested by**: Test User
**Timestamp (UTC)**: 2026-03-13T08:54:33Z

---

## Post-Attestation (Phase 2)

Recorded commands:

- `uv run gz closeout ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz attest ADR-0.12.0-obpi-pipeline-enforcement-parity --status completed`
- `uv run gz audit ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz adr emit-receipt ADR-0.12.0-obpi-pipeline-enforcement-parity --event validated --attestor "human:jeff" --evidence-json ...`

Step 8 issue review result:

- Queried open issues by ADR/OBPI/keyword:
  - `gh issue list --repo tvproductions/gzkit --search "ADR-0.12.0" --state open --json number,title,url,labels`
  - `gh issue list --repo tvproductions/gzkit --search "OBPI-0.12.0" --state open --json number,title,url,labels`
  - `gh issue list --repo tvproductions/gzkit --search "pipeline enforcement parity" --state open --json number,title,url,labels`
- Result: no matching open issues; no closures performed.

Step 9 release notes confirmation:

- `RELEASE_NOTES.md` updated with `## v0.12.0 (2026-03-13)` entry for ADR-0.12.0.
