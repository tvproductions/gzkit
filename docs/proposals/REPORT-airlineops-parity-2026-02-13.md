# REPORT: AirlineOps Parity Scan

## Metadata

- Date: 2026-02-13
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Canonical Commit Pin: `1ad9637da`
- Scope: GovZero governance tools, rules, policies, and proof surfaces
- Update: Post-OBPI-0.3.0-01 verification refresh (same-day in-place update)

---

## Executive Summary

- Overall parity status: Partial (improving)
- Critical gaps (current):
  - P1 Divergent: shared `gz-adr-audit` and `gz-adr-create` remain reduced stubs versus canon.
  - P1 Missing: canonical `docs/governance/GovZero/*.md` surface is still absent (15 of 16 filenames missing).
  - P2 Partial: parity scan path assumptions and lifecycle/linkage semantic overlays still need reconciliation.
- Completed this cycle:
  - OBPI-0.3.0-01 imported 14 missing canonical `gz-*` skill directories and mirrored them into `.claude/skills`.
- Recommended next work: execute OBPI-0.3.0-02 then OBPI-0.3.0-03.

---

## Canonical Coverage Matrix (Post-OBPI-0.3.0-01)

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|
| `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-*` (16 dirs) | `.github/skills/gz-*` (16 dirs) | Parity | P3 | Canonical/local count both 16; `comm` missing set empty |
| `.../skills/gz-adr-audit/SKILL.md` | `.github/skills/gz-adr-audit/SKILL.md` | Divergent | P1 | Canonical 272 lines vs gzkit 41 lines; non-equivalent |
| `.../skills/gz-adr-create/SKILL.md` | `.github/skills/gz-adr-create/SKILL.md` | Divergent | P1 | Canonical 229 lines vs gzkit 41 lines; non-equivalent |
| `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/*.md` (16 files) | `docs/user/*`, `docs/design/*`, `docs/lodestar/*` | Missing | P1 | Basename match still finds only `charter.md`; `docs/governance/GovZero/` absent |
| `.../GovZero/charter.md` | `docs/user/reference/charter.md` | Divergent | P2 | Both exist but content differs; canonical 112 lines vs gzkit 301 lines |
| `.../GovZero/adr-lifecycle.md`, `.../adr-obpi-ghi-audit-linkage.md`, `.../audit-protocol.md` | `docs/user/concepts/lifecycle.md`, `docs/user/concepts/obpis.md`, `docs/user/concepts/closeout.md` | Partial | P2 | Topic overlap exists; canonical constraints are not yet mirrored 1:1 |
| Parity scan precondition (`../airlineops`) | Worktree automation execution context | Partial | P2 | Sibling path not guaranteed in worktrees; absolute canonical path exists |

---

## Severity Rollup (Open Missing/Partial/Divergent Findings)

| Severity | Missing | Partial | Divergent | Total |
|---|---:|---:|---:|---:|
| P1 | 1 | 0 | 2 | 3 |
| P2 | 0 | 2 | 1 | 3 |
| P3 | 0 | 0 | 0 | 0 |

Resolved since baseline:
- Prior P1 Missing skill-surface gap (14 missing canonical `gz-*` directories) is now closed by OBPI-0.3.0-01.

---

## Findings

### F-001 (Resolved in OBPI-0.3.0-01)

- Type: Resolved (was Missing)
- Canonical artifact: 14 `gz-*` skills previously missing in gzkit
- gzkit artifact: `.github/skills/gz-*` now includes all canonical directories
- Evidence: Canonical/local skill directory counts both 16; imported skill dirs are diff-clean against commit `1ad9637da`.
- ADR/OBPI linkage: Parent ADR `ADR-0.3.0`; delivered by `OBPI-0.3.0-01-skills-surface-parity` (Completed).

### F-002

- Type: Divergent
- Canonical artifact: `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-audit/SKILL.md`, `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-create/SKILL.md`
- gzkit artifact: `/Users/jeff/.codex/worktrees/ba0b/gzkit/.github/skills/gz-adr-audit/SKILL.md`, `/Users/jeff/.codex/worktrees/ba0b/gzkit/.github/skills/gz-adr-create/SKILL.md`
- Why it matters: Shared names currently imply false governance parity.
- Evidence: Canonical files are 272/229 lines; gzkit files are 41/41 lines and omit canonical trust-model/compliance sections.
- Proposed remediation: Execute OBPI-0.3.0-02 to restore canonical structure and procedure depth.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: `ADR-0.3.0` -> `OBPI-0.3.0-02-divergent-skill-reconciliation`

### F-003

- Type: Missing
- Canonical artifact: `adr-lifecycle.md`, `adr-obpi-ghi-audit-linkage.md`, `adr-status.md`, `architectural-enforcement.md`, `audit-protocol.md`, `gate5-architecture.md`, `gzkit-structure.md`, `handoff-chaining.md`, `handoff-validation.md`, `layered-trust.md`, `ledger-schema.md`, `session-handoff-obligations.md`, `session-handoff-schema.md`, `staleness-classification.md`, `validation-receipts.md`
- gzkit artifact: No canonical-path counterparts under `docs/governance/GovZero/`
- Why it matters: Canonical governance reference surface is still not path-level mirrored.
- Evidence: Canonical docs count 16; basename match in gzkit still returns only `charter.md`; canonical directory missing.
- Proposed remediation: Execute OBPI-0.3.0-03 to introduce canonical GovZero docs surface.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: `ADR-0.3.0` -> `OBPI-0.3.0-03-govzero-canonical-doc-surface`

### F-004

- Type: Divergent
- Canonical artifact: `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/charter.md`
- gzkit artifact: `/Users/jeff/.codex/worktrees/ba0b/gzkit/docs/user/reference/charter.md`
- Why it matters: Charter-level divergence can alter gate and authority interpretation.
- Evidence: Files differ materially; canonical 112 lines vs gzkit 301 lines.
- Proposed remediation: Execute OBPI-0.3.0-04 after canonical docs import, then reposition gzkit charter text as overlay.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: `ADR-0.3.0` -> `OBPI-0.3.0-04-core-semantics-reconciliation`

### F-005

- Type: Partial
- Canonical artifact: `adr-lifecycle.md`, `adr-obpi-ghi-audit-linkage.md`, `audit-protocol.md`
- gzkit artifact: `docs/user/concepts/lifecycle.md`, `docs/user/concepts/obpis.md`, `docs/user/concepts/closeout.md`
- Why it matters: Semantic overlap exists without canonical structure fidelity.
- Evidence: Concept pages cover related areas but not as canonical mirrors.
- Proposed remediation: Execute OBPI-0.3.0-04 to align overlays with canonical references.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: `ADR-0.3.0` -> `OBPI-0.3.0-04-core-semantics-reconciliation`

### F-006

- Type: Partial
- Canonical artifact: `.github/skills/airlineops-parity-scan/SKILL.md` precondition (`../airlineops`)
- gzkit artifact: Worktree execution contexts where canonical repo is not a sibling
- Why it matters: Relative-path assumptions can produce false blocker reports.
- Evidence: `../airlineops` absent in this worktree while canonical repo exists at `/Users/jeff/Documents/Code/airlineops`.
- Proposed remediation: Execute OBPI-0.3.0-05 to add deterministic canonical path resolution.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: `ADR-0.3.0` -> `OBPI-0.3.0-05-parity-scan-path-hardening`

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [x] User documentation
- [x] Command manpages
- [x] Operator runbook

Notes: Proof surfaces exist and skill-surface parity improved, but canonical GovZero docs are still missing as canonical-path artifacts.

---

## Risk Summary

- What blocks 1.0 readiness now: Divergent shared `gz-adr-*` skills plus missing canonical GovZero doc surface.
- What can wait: Low-frequency doctrine overlays after canonical doc import and shared-skill reconciliation are complete.
- What must be done next cycle: OBPI-0.3.0-02 and OBPI-0.3.0-03, then OBPI-0.3.0-04/05.

---

## Next Actions (Required ADR/OBPI Follow-up)

1. Action: Execute `OBPI-0.3.0-02-divergent-skill-reconciliation` for `gz-adr-audit` and `gz-adr-create`.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-02-divergent-skill-reconciliation`
   Owner: Human + Agent
2. Action: Execute `OBPI-0.3.0-03-govzero-canonical-doc-surface` to import missing canonical GovZero docs.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-03-govzero-canonical-doc-surface`
   Owner: Human + Agent
3. Action: Execute `OBPI-0.3.0-04-core-semantics-reconciliation` to align charter/lifecycle/linkage/closeout overlays.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-04-core-semantics-reconciliation`
   Owner: Human + Agent
4. Action: Execute `OBPI-0.3.0-05-parity-scan-path-hardening` to eliminate worktree path fragility.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-05-parity-scan-path-hardening`
   Owner: Agent
5. Action: Start OBPI-0.3.0-02 implementation with `gz-adr-audit` and `gz-adr-create` canonical reconciliation as first patch set.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-02-divergent-skill-reconciliation`
   Owner: Human + Agent

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| Canonical mirror refinements beyond core skills/docs parity | Do after blocking parity surfaces are in place and validated | 0.4.x planning |
