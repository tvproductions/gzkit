# REPORT: AirlineOps GovZero Mining

## Metadata

- Date: 2026-03-11
- Scanner: Codex
- Canonical Source: `../airlineops`
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`
- Scope: GovZero process-habit extraction across control surfaces

---

## Mining Surfaces

- [x] `AGENTS.md`
- [x] `CLAUDE.md`
- [x] `.github/**`
- [x] `.claude/**`
- [ ] `.codex/**`
- [x] `.gzkit/**`
- [x] `docs/governance/GovZero/**`

---

## Mined Norms

| Norm ID | Mined Habit / Rule | Canonical Source Path | Product Capability? (Y/N) | Included in GovZero Scope? | gzkit Extraction Path(s) | Status | Notes |
|---|---|---|---|---|---|---|---|
| N-001 | After plan approval, OBPI work must run through a dedicated execution pipeline | `../airlineops/AGENTS.md`, `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | N | Y | `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Parity | imported in this cycle |
| N-002 | Stage order is load context -> implement -> verify -> present evidence -> sync | `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | N | Y | pipeline skill + workflow/runbook docs | Parity | now first-class in gzkit docs |
| N-003 | Missing orchestration primitives must fail closed | `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` | N | Y | compatibility note in gzkit pipeline skill | Partial | lock and plan-audit parity still missing |

## NOT GovZero Exclusion Log

Exclusions are exceptional. Default is inclusion in GovZero scope unless product capability evidence is explicit.

| Candidate Item | Canonical Source Path | Why NOT GovZero | Product Capability Evidence | Reviewer |
|---|---|---|---|---|
| none | n/a | no exclusions recorded in this tranche | n/a | Codex |

---

## Procedure Parity Checks

| Procedure Class | Canonical Source(s) | gzkit Runtime/Docs Surface(s) | Executable Check | Result | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | AirlineOps runbook execution phase | pipeline Stage 1 + transaction contract | manual inspection | PASS with compatibility note | brief/plan receipt loading imported |
| Tool-use control | `gz-obpi-pipeline` skill | canonical gzkit skill + mirrors | `uv run gz agent sync control-surfaces` | PASS | skill mirrored into `.agents`, `.claude`, `.github` |
| Post-tool accounting | Stage 5 sync | `gz-obpi-audit`, `gz-obpi-sync` references | manual inspection | PASS | sync stage explicit in skill and docs |
| Validation | verify stage | gz quality commands | `uv run gz validate --documents`, `uv run gz lint`, `uv run gz typecheck`, `uv run gz test` | PASS | all commands passed |
| Verification | fail-closed audit | `uv run gz adr audit-check ADR-0.11.0-airlineops-obpi-completion-pipeline-parity` | command | PASS (fail-closed) | command blocked on incomplete OBPIs as expected |
| Human attestation boundary | AirlineOps AGENTS ceremony rules | synced `AGENTS.md` and workflow docs | manual inspection | PASS | `Completed` still gated by human attestation |

## Intake Decisions (Required)

| Norm ID | Candidate | Classification | Why | Follow-up Linkage |
|---|---|---|---|---|
| N-001 | canonical pipeline skill | Import Now | missing operator surface, high governance impact | `ADR-0.11.0` / `OBPI-0.11.0-05` |
| N-002 | verify -> ceremony -> sync workflow narration | Import Now | pipeline without operator docs is incomplete | `ADR-0.11.0` / `OBPI-0.11.0-05` |
| N-003 | lock and plan-audit parity | Defer (Tracked) | no native gzkit surface yet; imported fail-closed compatibility wording first | successor `ADR-0.11.0` tranche |

---

## Required Commands

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
uv run mkdocs build --strict
```

---

## Findings and Next Actions

1. Finding:
   - Severity: P1
   - Why it matters: without `gz-obpi-pipeline`, gzkit agents can implement OBPI
     work without a canonical verify/ceremony/sync ritual.
   - ADR/OBPI linkage: `ADR-0.11.0` / `OBPI-0.11.0-05`
   - Next action: complete heavy-lane attestation for the imported pipeline skill

2. Finding:
   - Severity: P1
   - Why it matters: lock and plan-audit parity are still weaker than AirlineOps,
     so concurrency and plan-governance enforcement are not yet equivalent.
   - ADR/OBPI linkage: `ADR-0.11.0` successor tranche required
   - Next action: import those primitives as the next execution-parity tranche
