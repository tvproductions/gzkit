# REPORT: AirlineOps Parity Scan

## Metadata

- Date: 2026-02-11
- Scanner: Human + Agent
- Canonical Source: `../airlineops`
- Scope: GovZero governance tools, rules, policies, and proof surfaces

---

## Executive Summary

- Overall parity status: Blocked (canonical repo unavailable)
- Critical gaps: Canonical AirlineOps repo missing from workspace; parity evidence unavailable
- Recommended next minor(s): TBD after canonical scan

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|
| `../airlineops/.github/skills/gz-*` | `.github/skills/*` | Missing | P0 | `../airlineops` not present in workspace; cannot verify parity |
| `../airlineops/docs/governance/GovZero/*` | `docs/user/*` / `docs/design/*` | Missing | P0 | `../airlineops` not present in workspace; cannot verify parity |

---

## Findings

### F-001

- Type: Missing
- Canonical artifact: `../airlineops` (canonical repo)
- gzkit artifact: N/A
- Why it matters: GovZero canon is defined as AirlineOps; parity cannot be verified without the source of truth.
- Evidence: `test -d ../airlineops` failed in this workspace.
- Proposed remediation: Restore or mount `../airlineops` alongside gzkit, then re-run parity scan.
- Target SemVer minor: TBD (blocked)
- ADR/OBPI linkage: TBD (blocked)

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [ ] User documentation
- [ ] Command manpages
- [ ] Operator runbook

Notes: Proof surface check blocked; canonical repo not available.

---

## Next Actions

1. Action: Ensure `../airlineops` is available in the workspace (canonical GovZero source).
   Parent ADR: TBD
   OBPI: TBD
   Owner: Platform
2. Action: Re-run the parity scan and update this report with evidence-based findings.
   Parent ADR: TBD
   OBPI: TBD
   Owner: Platform

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| Parity findings beyond F-001 | Canonical evidence missing | Next scan after repo restored |
