# ADR Closeout Form: ADR-0.10.0-obpi-runtime-surface

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [x] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/` |
| Gate 2 | Tests pass | `uv run -m unittest discover tests` |
| Gate 3 | Docs build | `uv run mkdocs build --strict` |
| Gate 4 | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz attest ADR-0.10.0-obpi-runtime-surface --status completed` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.10.0-01](obpis/OBPI-0.10.0-01-obpi-runtime-contract-and-state-model.md) | OBPI runtime contract and derived state model | Completed |
| [OBPI-0.10.0-02](obpis/OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces.md) | OBPI-native query and reconcile command surfaces | Completed |
| [OBPI-0.10.0-03](obpis/OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration.md) | OBPI proof state and lifecycle integration | Completed |

## Human Attestation

### Verbatim Attestation

- `attest completed`

**Attested by**: Test User
**Timestamp (UTC)**: 2026-03-10T10:55:42Z

---

## Post-Attestation (Phase 2)

Recorded commands:

- `uv run gz closeout ADR-0.10.0-obpi-runtime-surface`
- `uv run gz attest ADR-0.10.0-obpi-runtime-surface --status completed`
- `uv run gz audit ADR-0.10.0-obpi-runtime-surface`
- `uv run gz adr emit-receipt ADR-0.10.0-obpi-runtime-surface --event validated --attestor "human:jeff" --evidence-json '{"scope":"ADR-0.10.0-obpi-runtime-surface","date":"2026-03-10"}'`

Step 8 issue review result:

- Queried open issues by ADR/OBPI/keyword:
  - `gh issue list --repo tvproductions/gzkit --search "ADR-0.10.0" --state open --json number,title,url,labels`
  - `gh issue list --repo tvproductions/gzkit --search "OBPI-0.10.0" --state open --json number,title,url,labels`
  - `gh issue list --repo tvproductions/gzkit --search "obpi runtime surface" --state open --json number,title,url,labels`
  - `gh issue view 9 --repo tvproductions/gzkit --json number,title,body,url,labels,state`
- Result: no matching ADR/OBPI issues remained open; issue `#9` was reviewed and left open because it tracks a broader maturity-plan enhancement rather than ADR-0.10.0 delivery.

Step 9 release notes confirmation:

- `RELEASE_NOTES.md` updated with `## v0.10.0 (2026-03-10)` entry for ADR-0.10.0.

Step 10 release publication:

- Policy requires `uv run gz git-sync --apply --lint --test` immediately before `gh release create` or any release update command.
- Prepared release command: `gh release create v0.10.0 --repo tvproductions/gzkit --title "v0.10.0" --notes-file /tmp/gzkit-v0.10.0-release-notes.md`
