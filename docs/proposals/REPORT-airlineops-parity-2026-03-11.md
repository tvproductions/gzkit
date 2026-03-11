# REPORT: AirlineOps Parity Scan

## Metadata

- Date: 2026-03-11
- Scanner: Codex
- Canonical Source: `../airlineops`
- Scope: GovZero governance tools, rules, policies, and proof surfaces
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`

---

## Executive Summary

- Overall parity status: Partial
- Critical gaps:
  - `gz-obpi-pipeline` skill was missing from gzkit canon and all mirrors before
    this scan cycle.
  - Pipeline mandate was absent from gzkit's generated agent contracts and
    operator workflow docs.
  - Lock and plan-audit hook parity remain missing compatibility seams.
- Recommended next minor(s):
  - continue `ADR-0.11.0` for runtime enforcement and closeout alignment

---

## Canonical-Root Resolution Evidence (Required)

- Resolution order used:
  1. explicit override (not used)
  2. sibling path `../airlineops`
  3. absolute fallback `/Users/jeff/Documents/Code/airlineops`
- Selected canonical root: `../airlineops`
- Fallback engaged (yes/no): no
- Fail-closed behavior statement: if no candidate resolved, this report would
  stop with blockers instead of claiming parity.
- Evidence commands:
  - `test -d ../airlineops && echo "sibling present" || echo "sibling missing"` -> `sibling present`
  - `test -d /Users/jeff/Documents/Code/airlineops && echo "absolute fallback present" || echo "absolute fallback missing"` -> `absolute fallback present`

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status | Severity | Evidence |
|---|---|---|---|---|
| `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | `.gzkit/skills/gz-obpi-pipeline/SKILL.md` plus mirrors | Parity | P1 | Canonical skill ported in this cycle; mirrors regenerated with `uv run gz agent sync control-surfaces` |
| `../airlineops/AGENTS.md` pipeline mandate | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Partial | P1 | Mandate imported via templates and sync; lock and plan-audit hook parity still compatibility-noted |
| `../airlineops/docs/governance/governance_runbook.md` execution workflow | `docs/governance/governance_runbook.md`, `docs/user/concepts/workflow.md`, `docs/user/runbook.md` | Partial | P1 | Pipeline workflow imported; closeout and lock details still lighter than canon |
| `../airlineops/.claude/**` pipeline-adjacent hook receipts/locks | `.claude/**` | Missing | P1 | No `gz-obpi-lock` surface or plan-audit hook infrastructure present in gzkit |

---

## Behavior / Procedure Source Matrix

| Behavior Class | Canonical Source(s) | gzkit Source(s) | Status | Severity | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | AirlineOps runbook Phase 2/3, pipeline Stage 1 | `gz-obpi-pipeline` skill, GovZero transaction contract | Partial | P2 | Brief/plan receipt loading imported; receipt creation itself still absent |
| Tool-use control surfaces | `gz-obpi-pipeline`, `gz-obpi-lock` | `gz-obpi-pipeline`, `gz-obpi-audit`, `gz-obpi-sync`, `gz-session-handoff` | Partial | P1 | Pipeline sequencing imported; lock surface absent |
| Post-tool accounting | AirlineOps Stage 5 sync and audit ledger | `gz-obpi-audit`, `gz-obpi-sync`, brief evidence workflow | Parity | P2 | Sync stage now explicit in skill and runbooks |
| Validation | AirlineOps verify stage | `uv run gz validate --documents`, `uv run gz lint`, `uv run gz typecheck`, `uv run gz test` | Parity | P2 | All commands pass in this cycle |
| Verification | AirlineOps runbook and closeout checks | `uv run gz adr audit-check ADR-0.11.0-airlineops-obpi-completion-pipeline-parity` | Partial | P2 | Audit-check works and fails closed on incomplete ADR state |
| Presentation | AirlineOps ceremony stage | workflow docs + pipeline skill + generated agent contracts | Parity | P2 | verify -> ceremony -> sync now documented as mandatory |
| Human authority boundary | AirlineOps AGENTS pipeline mandate + ceremony | `AGENTS.md` generated from templates | Parity | P1 | Heavy/Foundation completion still requires attestation before `Completed` |

---

## Habit Parity Matrix (Required)

| Habit Class | Canonical Source Signal | gzkit Surface(s) | Status | Severity | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | Plan receipt + brief parse before edits | `gz-obpi-pipeline` Stage 1 | Partial | P2 | receipt consumption imported, receipt generation deferred |
| Tool-use control surfaces | Explicit pipeline command | `.gzkit/skills/gz-obpi-pipeline/SKILL.md` and mirrors | Parity | P1 | Skill exists canonically and in all mirrors |
| Post-tool accounting | Stage 5 sync after ceremony | `gz-obpi-audit` + `gz-obpi-sync` references | Parity | P2 | Pipeline and runbook both require sync stage |
| Validation | Mandatory verify stage | quality command set in skill | Parity | P2 | validate/lint/typecheck/test/build/BDD all pass |
| Verification | Fail-closed audit surfaces | `gz adr audit-check` | Partial | P2 | audit-check returns expected failure because package is incomplete |
| Presentation for humans | Acceptance ceremony before completion | workflow docs + generated contracts | Parity | P1 | ceremony is now first-class in docs and templates |
| Human authority boundary | Gate 5 cannot be bypassed | AGENTS/CLAUDE/Copilot surfaces | Parity | P1 | attestation mandate preserved during import |

---

## GovZero Mining Inventory

| Mined Norm / Habit | Canonical Source Path | gzkit Extraction Path | Status | Confidence | Remediation |
|---|---|---|---|---|---|
| OBPI execution must go through a staged pipeline after planning | `../airlineops/AGENTS.md`, `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, generated contracts, runbooks | Parity | High | imported in this cycle |
| Stage order is verify -> ceremony -> sync | `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | same plus docs workflow surfaces | Parity | High | imported in this cycle |
| Missing lock/receipt infrastructure must fail closed, not be hand-waved | `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | compatibility notes inside gzkit pipeline skill | Partial | Medium | carry into later runtime parity tranche |

## Parity Intake Rubric Decisions (Required)

| Candidate Item | Canonical Source | gzkit Target | Classification | Rationale | Runtime/Proof Backing |
|---|---|---|---|---|---|
| `gz-obpi-pipeline` skill surface | `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | `.gzkit/skills/gz-obpi-pipeline/SKILL.md` + mirrors | Import Now | high-impact missing governance surface; operator ritual was absent | `uv run gz agent sync control-surfaces`, `uv run gz cli audit` |
| Pipeline mandate in generated agent contracts | `../airlineops/AGENTS.md` | `src/gzkit/templates/*.md` -> synced contracts | Import Now | without this, agents still implement freeform | synced `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` |
| `gz-obpi-lock` and plan-audit hook parity | AirlineOps runbook + skill | future gzkit runtime/control surfaces | Defer (Tracked) | no current native surface; imported skill now fails closed and documents the gap | compatibility note in skill, `gz adr audit-check` still fail-closes |

## NOT GovZero Exclusion Log

| Candidate Item | Canonical Source Path | Exclusion Rationale (Product Capability) | Evidence | Reviewer |
|---|---|---|---|---|
| none | n/a | no product-only exclusions identified in this tranche | n/a | Codex |

---

## Findings

### F-001

- Type: Missing
- Canonical artifact: `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md`
- gzkit artifact: missing before this cycle
- Why it matters: plan-approved OBPI work in gzkit had no canonical execution
  surface, so verify, ceremony, and sync could be skipped ad hoc.
- Evidence: pre-scan skill catalogs lacked `gz-obpi-pipeline`; post-scan canon and
  mirrors contain it.
- Proposed remediation: completed in this cycle by porting the skill and syncing
  mirrors.
- Target SemVer minor: `0.11.0`
- ADR/OBPI linkage: `ADR-0.11.0` / `OBPI-0.11.0-05`

### F-002

- Type: Partial
- Canonical artifact: AirlineOps lock and plan-audit receipt orchestration
- gzkit artifact: compatibility notes only
- Why it matters: multi-agent concurrency and formal plan-receipt enforcement are
  still weaker than canon.
- Evidence: no `gz-obpi-lock` skill or plan-audit hook found in gzkit; pipeline
  skill records this as fail-closed compatibility behavior.
- Proposed remediation: continue runtime parity import in later `ADR-0.11.0`
  tranches or successor ADR.
- Target SemVer minor: `0.11.0+`
- ADR/OBPI linkage: `ADR-0.11.0` follow-on after `OBPI-0.11.0-05`

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [x] User documentation
- [x] Command manpages
- [x] Operator runbook
- [x] Behavior/procedure source matrix completed

Executable ritual checks:

- [x] `uv run gz cli audit` -> PASS
- [x] `uv run gz check-config-paths` -> PASS
- [x] `uv run gz adr audit-check ADR-0.11.0-airlineops-obpi-completion-pipeline-parity` -> FAIL-CLOSED because package OBPIs remain incomplete
- [x] `uv run mkdocs build --strict` -> PASS

Notes:

- This scan cycle is complete because it includes both a concrete import
  (`gz-obpi-pipeline`) and path-level evidence.

---

## Next Actions

1. Action: finish heavy-lane attestation and brief closeout for the imported
   pipeline tranche
   Parent ADR: `ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
   OBPI: `OBPI-0.11.0-05`
   Owner: Human + agent
2. Action: import lock and plan-audit parity so Stage 1 concurrency and receipt
   enforcement match AirlineOps more closely
   Parent ADR: `ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
   OBPI: successor tranche required
   Owner: agent

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| `gz-obpi-lock` parity | no native surface yet; current skill fails closed instead of claiming support | next `ADR-0.11.0` execution tranche |
| plan-audit hook parity | no hook implementation yet in gzkit | next planning-lifecycle parity tranche |
