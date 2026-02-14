# REPORT: AirlineOps Parity Scan

## Metadata

- Date: 2026-02-12
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Scope: GovZero governance tools, rules, policies, and proof surfaces

---

## Executive Summary

- Overall parity status: Partial (high drift risk)
- Critical gaps:
  - P1 Missing: 14 of 16 canonical `gz-*` skills are absent in gzkit.
  - P1 Divergent: the 2 shared `gz-*` skills (`gz-adr-audit`, `gz-adr-create`) are reduced stubs versus canon.
  - P1 Missing: 11 of 12 canonical `docs/governance/GovZero/*.md` files are not present as canonical files in gzkit.
- Recommended next minor(s): 0.3.x (canon reconciliation execution), with low-priority spillover into 0.4.x only if 0.3.x capacity is exhausted.

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|
| `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-*` (16 dirs) | `.github/skills/gz-*` (2 dirs) | Partial | P1 | `find .../airlineops/.github/skills -name 'gz-*'` vs `find .github/skills -name 'gz-*'` |
| `.../skills/gz-adr-audit/SKILL.md` | `.github/skills/gz-adr-audit/SKILL.md` | Divergent | P1 | `diff -u` shows canonical 272 lines vs gzkit 41 lines with missing Layer-2 trust/audit procedure |
| `.../skills/gz-adr-create/SKILL.md` | `.github/skills/gz-adr-create/SKILL.md` | Divergent | P1 | `diff -u` shows canonical 229 lines vs gzkit 41 lines with missing lifecycle/compliance rules |
| `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/*.md` (12 files) | `docs/user/*`, `docs/design/*`, `docs/lodestar/*` | Missing | P1 | Exact-name match check returns only `charter.md`; 11 canonical files absent as canonical docs |
| `.../GovZero/charter.md` | `docs/user/reference/charter.md` | Divergent | P2 | Both exist, but semantics and structure differ materially |
| `.../GovZero/adr-lifecycle.md` + `.../adr-obpi-ghi-audit-linkage.md` + `.../audit-protocol.md` | `docs/user/concepts/lifecycle.md`, `docs/user/concepts/obpis.md`, `docs/user/concepts/closeout.md` | Partial | P2 | Concepts exist, but canonical naming/constraints and closeout semantics are not 1:1 |
| Canonical parity-scan precondition (`../airlineops`) | `.github/skills/airlineops-parity-scan/SKILL.md` usage in worktree contexts | Partial | P2 | Worktree cwd breaks `../airlineops` assumption; canonical repo exists at absolute path |

---

## Findings

### F-001

- Type: Missing
- Canonical artifact: `gz-adr-autolink`, `gz-adr-check`, `gz-adr-closeout-ceremony`, `gz-adr-map`, `gz-adr-recon`, `gz-adr-status`, `gz-adr-sync`, `gz-adr-verification`, `gz-arb`, `gz-obpi-audit`, `gz-obpi-brief`, `gz-obpi-reconcile`, `gz-obpi-sync`, `gz-session-handoff`
- gzkit artifact: No corresponding skill directories under `.github/skills/`
- Why it matters: Canonical enforcement mechanics for ADR/OBPI drift detection and reconciliation are not extractable in gzkit.
- Evidence: Canonical `gz-*` count is 16; gzkit `gz-*` count is 2.
- Proposed remediation: Port missing canonical `gz-*` skills with canonical assets and command surfaces first, then reconcile naming and invocation patterns.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: Parent ADR `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`; create OBPI set for Phase 2 skills audit/port.

### F-002

- Type: Divergent
- Canonical artifact: `.../gz-adr-audit/SKILL.md`, `.../gz-adr-create/SKILL.md`
- gzkit artifact: `.github/skills/gz-adr-audit/SKILL.md`, `.github/skills/gz-adr-create/SKILL.md`
- Why it matters: Shared skill names mask major behavior loss, producing false confidence in parity.
- Evidence: Line-level `diff -u` shows canonical full governance procedure replaced by placeholder-style steps.
- Proposed remediation: Restore canonical structure (frontmatter metadata, governance constraints, step procedures, and assets references) or explicitly declare intentional divergence via ADR.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: Parent ADR `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`; create OBPI for divergent skill reconciliation.

### F-003

- Type: Missing
- Canonical artifact: `adr-lifecycle.md`, `adr-obpi-ghi-audit-linkage.md`, `adr-status.md`, `architectural-enforcement.md`, `audit-protocol.md`, `gate5-architecture.md`, `gzkit-structure.md`, `layered-trust.md`, `ledger-schema.md`, `session-handoff-schema.md`, `validation-receipts.md`
- gzkit artifact: No canonical-path counterparts under `docs/governance/GovZero/`
- Why it matters: Canonical governance reference set is not available as canonical files, weakening doctrinal fidelity and discoverability.
- Evidence: Exact-name scan across gzkit docs matches only `charter.md`.
- Proposed remediation: Introduce canonical `docs/governance/GovZero/` surface in gzkit and port these docs with explicit lineage references.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: Parent ADR `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`; create OBPI for GovZero doc-surface extraction.

### F-004

- Type: Partial
- Canonical artifact: `charter.md`, `adr-lifecycle.md`, `adr-obpi-ghi-audit-linkage.md`, `audit-protocol.md`
- gzkit artifact: `docs/user/reference/charter.md`, `docs/user/concepts/lifecycle.md`, `docs/user/concepts/obpis.md`, `docs/user/concepts/closeout.md`
- Why it matters: Core semantics are close but not canonical, including lifecycle/pool constraints and closeout protocol details.
- Evidence: Canonical docs and gzkit concept pages cover similar domains with non-1:1 constraints and wording.
- Proposed remediation: Publish canonical docs first, then demote or relink concept pages as explanatory overlays that reference canonical sources.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: Parent ADR `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`; create OBPI for semantic reconciliation.

### F-005

- Type: Partial
- Canonical artifact: Parity-scan execution assumptions in `.github/skills/airlineops-parity-scan/SKILL.md`
- gzkit artifact: Weekly automation in worktree context
- Why it matters: Relative canonical-path assumptions can produce false blocker reports despite canonical repo availability.
- Evidence: `../airlineops` is absent from worktree cwd while `/Users/jeff/Documents/Code/airlineops` exists.
- Proposed remediation: Update skill guidance to resolve canonical path via absolute fallback and/or `git worktree` root detection.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: Parent ADR `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`; create OBPI for parity-scan path hardening.

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [x] User documentation
- [x] Command manpages
- [x] Operator runbook

Notes: Proof surfaces exist in gzkit, but canonical GovZero source docs are not yet mirrored as canonical-path artifacts.

---

## Risk Summary

- Blocks 1.0 readiness: Missing canonical reconciliation machinery (`gz-obpi-sync`, `gz-adr-verification`, related GovZero docs) blocks trustworthy parity claims.
- Can wait: Lower-frequency doctrine docs (`layered-trust`, `session-handoff-schema`, `validation-receipts`) can be sequenced after core gate/lifecycle surfaces.
- Must be done next cycle: Skills parity (missing + divergent) and canonical GovZero doc-surface import.

---

## Next Actions

1. Action: Promote `ADR-0.3.0` from Pool to active implementation ADR and freeze a canonical extraction scope for this cycle.
   Parent ADR: `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`
   OBPI: Create initial 0.3.x OBPI set on promotion
   Owner: Human
2. Action: Port missing canonical `gz-*` skills and reconcile `gz-adr-audit`/`gz-adr-create` to canonical behavior.
   Parent ADR: `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`
   OBPI: Proposed `skills-parity` OBPI group (Phase 2 checklist)
   Owner: Human + Agent
3. Action: Create canonical `docs/governance/GovZero/` surface in gzkit and import missing canonical docs with provenance notes.
   Parent ADR: `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`
   OBPI: Proposed `govzero-docs-parity` OBPI
   Owner: Human + Agent
4. Action: Reconcile lifecycle/linkage/closeout semantics so concept docs become overlays, not canonical substitutes.
   Parent ADR: `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`
   OBPI: Proposed `core-governance-semantics-sync` OBPI
   Owner: Human + Agent
5. Action: Patch parity-scan skill to resolve canonical repo path robustly in worktree and non-worktree sessions.
   Parent ADR: `docs/design/adr/pool/ADR-pool.airlineops-canon-reconciliation.md`
   OBPI: Proposed `parity-scan-path-hardening` OBPI
   Owner: Agent

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| Full canon mirror of low-frequency governance docs (`layered-trust`, `session-handoff-schema`, `validation-receipts`) | Lower immediate impact than gate/lifecycle/parity enforcement surfaces | 0.4.x planning |
