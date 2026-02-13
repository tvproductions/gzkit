# REPORT: AirlineOps Parity Scan (2026-02-07)

## Metadata

- Date: 2026-02-07
- Scanner: Human + Agent
- Canonical Source: `../airlineops`
- Scope: GovZero governance tools, rules, policies, and proof surfaces

---

## Executive Summary

- Overall parity status: **Partial**
- Critical gaps: canonical `gz-*` governance skill surface is substantially under-extracted in gzkit.
- Recommended next minors: execute `0.3.0` canon extraction before advancing later minors.

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status | Severity | Evidence |
|---|---|---|---|---|
| `../airlineops/.github/skills/gz-obpi-brief` | _(missing)_ | Missing | P1 | `find ../airlineops/.github/skills -name 'gz-*'` vs `find .github/skills` |
| `../airlineops/.github/skills/gz-obpi-sync` | _(missing)_ | Missing | P1 | same |
| `../airlineops/.github/skills/gz-adr-sync` | _(missing)_ | Missing | P1 | same |
| `../airlineops/.github/skills/gz-adr-verification` | _(missing)_ | Missing | P1 | same |
| `../airlineops/docs/governance/GovZero/charter.md` | `docs/user/reference/charter.md` | Partial | P2 | both files exist; structure diverges |
| `../airlineops/docs/governance/GovZero/adr-lifecycle.md` | `docs/user/concepts/lifecycle.md` | Partial | P2 | both files exist; detail depth differs |
| `../airlineops/docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md` | `docs/user/concepts/obpis.md` + `docs/user/concepts/lifecycle.md` | Partial | P2 | canonical single-source doc not extracted 1:1 |
| `../airlineops/docs/governance/GovZero/audit-protocol.md` | `docs/user/concepts/closeout.md` + pool audit ADR | Partial | P2 | protocol exists in fragments, not full canon |
| Proof surfaces doctrine | `docs/user/runbook.md`, `docs/user/commands/*.md`, `docs/user/*` | Parity (policy) | P3 | INV-024 + runbook/manpage updates |

---

## Findings

### F-001

- Type: Missing
- Canonical artifact: AirlineOps `gz-*` governance skills (OBPI sync/reconcile + ADR sync/verification suite)
- gzkit artifact: only `gz-adr-manager`, `gz-adr-audit`, and generic lint/test/format
- Why it matters: gzkit cannot yet enforce canon parity mechanics that exist in AirlineOps.
- Evidence: skill directory listing diff (`15` canonical `gz-*` skills vs `2` governance `gz-*` skills in gzkit).
- Proposed remediation: implement `ADR-0.3.0` Phase 2 gap audit and explicitly queue missing skills into OBPIs.
- Target SemVer minor: `0.3.x`
- ADR/OBPI linkage: `ADR-pool.airlineops-canon-reconciliation`

### F-002

- Type: Partial
- Canonical artifact: GovZero governance docs (`charter`, `adr-lifecycle`, `adr-obpi-ghi-audit-linkage`, `audit-protocol`)
- gzkit artifact: equivalent concepts exist, but not as canonical one-to-one translations.
- Why it matters: partial translation increases interpretation drift.
- Evidence: canonical files exist in AirlineOps; gzkit coverage is distributed across multiple concept pages.
- Proposed remediation: produce canonical mapping and delta table per document.
- Target SemVer minor: `0.3.x`
- ADR/OBPI linkage: `ADR-pool.airlineops-canon-reconciliation`

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [x] User documentation
- [x] Command manpages
- [x] Operator runbook

Notes: Doctrine is now explicit in PRD invariants and runbook gate checklist.

---

## Next Actions

1. Action: Create and run `0.3.0` OBPIs for canon extraction phases (template port, full gap audit, sync mechanism decision).
   Parent ADR: `ADR-pool.airlineops-canon-reconciliation`
   OBPI: `OBPI-0.3.0-01..03` (to create)
   Owner: Human + Agent
2. Action: Run this parity scan weekly and before any pool promotion.
   Parent ADR: `ADR-pool.airlineops-canon-reconciliation`
   OBPI: parity-scan cadence item (to create under 0.3.0 or 0.6.0 governance chores)
   Owner: Human + Agent

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| Full AirlineOps skill-suite extraction | Needs staged delivery; avoid uncontrolled scope expansion | 0.4.0 planning window |
