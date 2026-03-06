# ADR Closeout Form: ADR-0.6.0-pool-promotion-protocol

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
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/` |
| Gate 2 | Tests pass | `uv run -m unittest discover tests` |
| Gate 3 | Docs build | `uv run mkdocs build --strict` |
| Gate 4 | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz attest ADR-0.6.0-pool-promotion-protocol --status completed` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.6.0-01](obpis/OBPI-0.6.0-01-pool-source-contract.md) | Pool source contract | Completed |
| [OBPI-0.6.0-02](obpis/OBPI-0.6.0-02-promotion-command-lineage.md) | Promotion command lineage | Completed |
| [OBPI-0.6.0-03](obpis/OBPI-0.6.0-03-operator-narratives-and-auditability.md) | Operator narratives and auditability | Completed |

## Human Attestation

### Verbatim Attestation

- `attest completed`

**Attested by**: Jeff
**Timestamp (UTC)**: 2026-03-06T05:37:11Z

---

## Post-Attestation (Phase 2)

Recorded commands:

- `uv run gz closeout ADR-0.6.0-pool-promotion-protocol`
- `uv run gz attest ADR-0.6.0-pool-promotion-protocol --status completed`
- `uv run gz audit ADR-0.6.0-pool-promotion-protocol`

Step 8 issue review result:

- Queried open issues by ADR/OBPI/keyword:
  - `gh issue list --repo tvproductions/gzkit --search "ADR-0.6.0" --state open --json number,title,url,labels`
  - `gh issue list --repo tvproductions/gzkit --search "OBPI-0.6.0" --state open --json number,title,url,labels`
  - `gh issue list --repo tvproductions/gzkit --search "ADR-0.6" --state open --json number,title,url,labels`
  - `gh issue list --repo tvproductions/gzkit --search "pool promotion protocol" --state open --json number,title,url,labels`
- Result: no matching open issues; no closures performed.

Step 9 release notes confirmation:

- `RELEASE_NOTES.md` contains `## v0.6.0 (2026-03-04)` with ADR and gate evidence details.

Step 10 release publication:

- Ran policy-mandated pre-release sync: `uv run gz git-sync --apply --lint --test`
- Existing release detected: `gh release view v0.6.0 --repo tvproductions/gzkit --json tagName,name,isDraft,isPrerelease,publishedAt,url`
- Updated release metadata: `gh release edit v0.6.0 --repo tvproductions/gzkit --title "v0.6.0" --notes-file /tmp/gzkit-v0.6.0-release-notes.md`
- Release URL: <https://github.com/tvproductions/gzkit/releases/tag/v0.6.0>
