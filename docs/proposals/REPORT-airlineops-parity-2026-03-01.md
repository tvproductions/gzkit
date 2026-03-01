# REPORT: AirlineOps Parity Scan

## Metadata

- Date: 2026-03-01
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Scope: GovZero governance tools, rules, policies, and proof surfaces
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`

---

## Executive Summary

- Overall parity status: Partial
- Open critical gaps:
  - P2 Partial: `.github/instructions/*.instructions.md` is now scaffolded with a governance-focused subset; full file-by-file parity remains pending
  - P3 Partial: canonical `.claude/**` and `.gzkit/**` surfaces remain broader in AirlineOps
- In-scan remediations completed:
  - Added `docs/governance/governance_runbook.md` and wired it into MkDocs nav
  - Fixed parity-scan skill lodestar references to `docs/design/lodestar/*`
  - Imported `docs/governance/GovZero/governance-registry-design.md` from canonical
  - Scaffolded `.github/instructions/` governance-critical subset
  - Added `gz-adr-manager` compatibility alias strategy mapped to `gz-adr-create`
- Recommended next minor(s): promote `ADR-pool.airlineops-canon-reconciliation` for continued parity closure (0.8.x candidate)

---

## Canonical-Root Resolution Evidence (Required)

- Resolution order used:
  1. explicit override (if provided)
  2. sibling path `../airlineops`
  3. absolute fallback `/Users/jeff/Documents/Code/airlineops`
- Selected canonical root: `/Users/jeff/Documents/Code/airlineops`
- Fallback engaged: no
- Fail-closed behavior statement: if no candidate resolves, stop and report blockers; do not emit parity conclusions.
- Evidence commands:
  - `test -d ../airlineops && test -d .`
  - `cd ../airlineops && pwd`

Observed:

- `repo_check=pass`
- `canonical_root=/Users/jeff/Documents/Code/airlineops`

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|
| `../airlineops/docs/governance/governance_runbook.md` | `docs/governance/governance_runbook.md` | Parity | P3 | `airlineops_governance_runbook=present`; `gzkit_governance_runbook=present` |
| `../airlineops/.github/instructions/*.instructions.md` | `.github/instructions/*.instructions.md` | Partial | P2 | `airlineops_instructions=present`; `gzkit_instructions=present` (governance-focused subset scaffolded) |
| `../airlineops/docs/governance/GovZero/governance-registry-design.md` | `docs/governance/GovZero/governance-registry-design.md` | Parity | P3 | `airlineops_registry_doc=present`; `gzkit_registry_doc=present` |
| `../airlineops/.github/skills/gz-adr-manager` | `.github/skills/gz-adr-manager` + `.github/skills/gz-adr-create` | Parity | P3 | compatibility alias added in gzkit canonical/mirror surfaces |
| `../airlineops/docs/governance/GovZero/**` | `docs/governance/GovZero/**` | Parity | P3 | missing canonical file imported; recursive set now path-complete |
| `../airlineops/.claude/**` | `.claude/**` | Partial | P3 | canonical has broader surface; gzkit retains governance subset |
| `../airlineops/.codex/**` | `.codex/**` | Parity | P3 | both currently absent |
| `../airlineops/.gzkit/**` | `.gzkit/**` | Partial | P3 | structures differ (canon: governance/lessons/locks; gzkit: manifest/ledger/skills) |

---

## Behavior / Procedure Source Matrix

| Behavior Class | Canonical Source(s) | gzkit Source(s) | Status | Severity | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | `AGENTS.md`, `.github/instructions/**`, governance runbook | `AGENTS.md`, `.github/instructions/**`, `docs/governance/governance_runbook.md` | Partial | P2 | governance-critical instruction subset present; full parity backlog remains |
| Tool-use control surfaces | `gz-*` skills and runbook procedures | `gz-*` skills, `docs/user/commands/**`, runbooks | Parity | P3 | `gz-adr-manager` compatibility alias now delegates to canonical `gz-adr-create` |
| Post-tool accounting | audit protocol + receipt rituals | `gz audit`, `gz obpi emit-receipt`, `gz adr emit-receipt` | Parity | P3 | runtime commands and docs align |
| Validation | gate rules + command contracts | `gz cli audit`, `gz check-config-paths`, `mkdocs build --strict` | Parity | P3 | all ritual checks PASS on 2026-03-01 |
| Verification | closeout and audit progression | `gz closeout`, `gz attest`, `gz audit`, `gz adr audit-check` | Parity | P3 | command surfaces available + documented |
| Presentation | governance runbooks and checklists | `docs/user/runbook.md`, `docs/governance/governance_runbook.md` | Parity | P3 | governance runbook added in this scan |
| Human authority boundary | Gate 5 and attestation doctrine | `AGENTS.md`, `docs/user/commands/attest.md`, runbooks | Parity | P3 | explicit attestation steps present |

---

## Habit Parity Matrix (Required)

| Habit Class | Canonical Source Signal | gzkit Surface(s) | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | instruction files + runbook preflight | AGENTS + `.github/instructions/**` + governance runbook | Partial | P2 | governance-critical subset implemented; full canonical instruction parity remains |
| Tool-use control surfaces | canonical skill naming and invocation | gz skills + CLI docs + alias skill | Parity | P3 | `gz-adr-manager` compatibility alias delegates to `gz-adr-create` |
| Post-tool accounting | audit + receipts | `gz audit`, receipt emitters | Parity | P3 | command help + docs available |
| Validation | repeatable ritual checks | cli audit, config path audit, mkdocs | Parity | P3 | command results PASS |
| Verification | closeout -> attestation -> audit | closeout/attest/audit runbook flow | Parity | P3 | workflows documented and executable |
| Presentation for humans | operator/governance runbooks | `docs/user/runbook.md` + new governance runbook | Parity | P3 | extraction completed this scan |
| Human authority boundary | explicit attestation language | AGENTS OBPI acceptance protocol + attest command | Parity | P3 | boundary remains explicit |

---

## GovZero Mining Inventory

| Mined Norm / Habit | Canonical Source Path | gzkit Extraction Path | Status | Confidence | Remediation |
|---|---|---|---|---|---|
| Maintain a dedicated governance runbook separate from daily operator loop | `../airlineops/docs/governance/governance_runbook.md` | `docs/governance/governance_runbook.md` | Parity | High | Implemented in this scan |
| Deterministic canonical-root parity scan with fail-closed behavior | `../airlineops/docs/governance/governance_runbook.md` | `.gzkit/skills/airlineops-parity-scan/SKILL.md` | Parity | High | Path references fixed in this scan |
| Governance instruction files are first-class behavioral doctrine | `../airlineops/.github/instructions/**` | `.github/instructions/**` | Partial | High | Governance-critical subset scaffolded; expand to full parity incrementally |
| Keep GovZero canonical docs path-complete | `../airlineops/docs/governance/GovZero/**` | `docs/governance/GovZero/**` | Parity | High | `governance-registry-design.md` imported |
| Attestation remains the human authority boundary | `../airlineops/AGENTS.md`, runbook ceremony sections | `AGENTS.md`, attest docs | Parity | High | none |
| Layered trust ordering (evidence -> ledger -> sync) must be explicit | `../airlineops/docs/governance/GovZero/layered-trust.md` | `docs/governance/GovZero/layered-trust.md`, governance runbook | Parity | High | none |

## NOT GovZero Exclusion Log

| Candidate Item | Canonical Source Path | Exclusion Rationale (Product Capability) | Evidence | Reviewer |
|---|---|---|---|---|
| AirlineOps data/forecasting product command workflows | `../airlineops/src/airlineops/**` | Product capability, not governance doctrine | domain-specific package paths | Agent |

---

## Findings

### F-001

- Type: Partial (in-scan remediation applied)
- Canonical artifact: `.github/instructions/*.instructions.md`
- gzkit artifact: `.github/instructions/*.instructions.md`
- Why it matters: Instruction parity reduces pre-tool drift and improves repeatability.
- Evidence: `airlineops_instructions=present`; `gzkit_instructions=present`
- Proposed remediation: Expand from governance-critical subset to fuller canonical parity as follow-up.
- Target SemVer minor: 0.8.x
- ADR/OBPI linkage: `ADR-pool.airlineops-canon-reconciliation` -> `instruction-surface-parity`

### F-002

- Type: Resolved (in-scan)
- Canonical artifact: `docs/governance/GovZero/governance-registry-design.md`
- gzkit artifact: `docs/governance/GovZero/governance-registry-design.md`
- Why it matters: Canonical GovZero surface is incomplete, weakening documentation parity claims.
- Evidence: `airlineops_registry_doc=present`; `gzkit_registry_doc=present`
- Proposed remediation: keep imported file synchronized with canonical updates.
- Target SemVer minor: 0.8.x maintenance
- ADR/OBPI linkage: `ADR-pool.airlineops-canon-reconciliation` -> `govzero-doc-surface-completion`

### F-003

- Type: Resolved via compatibility strategy (in-scan)
- Canonical artifact: `gz-adr-manager`
- gzkit artifact: `gz-adr-create` + `gz-adr-manager` alias
- Why it matters: Naming divergence complicates cross-repo ritual reuse and documentation transfer.
- Evidence: `airlineops_gz_adr_manager=present`; `gzkit_gz_adr_manager=present`; `gzkit_gz_adr_create=present`
- Proposed remediation: keep alias delegated to canonical create behavior; avoid semantic drift.
- Target SemVer minor: 0.8.x maintenance
- ADR/OBPI linkage: `ADR-0.5.0-skill-lifecycle-governance` follow-up compatibility policy

### F-004

- Type: Resolved (in-scan)
- Canonical artifact: `docs/governance/governance_runbook.md`
- gzkit artifact: `docs/governance/governance_runbook.md`
- Why it matters: Runbook-level operational maturity from canon is now directly available in gzkit.
- Evidence: file created and linked in MkDocs nav.
- Proposed remediation: keep synchronized via recurring parity scans.
- Target SemVer minor: 0.7.x stabilization
- ADR/OBPI linkage: `ADR-0.7.0-obpi-first-operations`

### F-005

- Type: Resolved (in-scan)
- Canonical artifact: parity-scan prerequisites for lodestar references
- gzkit artifact: `.gzkit/skills/airlineops-parity-scan/SKILL.md`
- Why it matters: Broken skill path references degrade repeatable parity execution.
- Evidence: replaced `docs/lodestar/*` with `docs/design/lodestar/*`
- Proposed remediation: keep mirrored via `gz agent sync control-surfaces`.
- Target SemVer minor: 0.3.x maintenance
- ADR/OBPI linkage: `ADR-0.3.0-airlineops-canon-reconciliation` / OBPI-0.3.0-05 maintenance follow-up

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [x] User documentation
- [x] Command manpages
- [x] Operator runbook
- [x] Behavior/procedure source matrix completed

Executable ritual checks (record command + result):

- [x] `uv run gz cli audit` (PASS)
- [x] `uv run gz check-config-paths` (PASS)
- [x] `uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol` (PASS)
- [x] `uv run mkdocs build --strict` (PASS)

Notes:

- MkDocs reported informational nav/link notices only; strict build passed.

---

## Next Actions

1. Action: Expand `.github/instructions/` from governance-critical subset toward fuller canonical parity.
   Parent ADR: `ADR-pool.airlineops-canon-reconciliation`
   OBPI: `instruction-surface-parity`
   Owner: Human + Agent
2. Action: Decide long-term naming convergence policy (`gz-adr-manager` alias retention vs canonical rename upstream).
   Parent ADR: `ADR-0.5.0-skill-lifecycle-governance`
   OBPI: alias/rename follow-up
   Owner: Human
3. Action: Continue weekly parity scans and record in dated reports.
   Parent ADR: `ADR-0.3.0-airlineops-canon-reconciliation`
   OBPI: maintenance cadence
   Owner: Agent

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| Full instruction-surface parity import beyond governance-critical files | Requires selection of governance-only subset from canonical instructions | 2026-03-15 |
