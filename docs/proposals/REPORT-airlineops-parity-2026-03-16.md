# REPORT: AirlineOps Parity Scan — Pipeline Skill Bilateral

## Metadata

- Date: 2026-03-16
- Scanner: Human + Agent (claude-code)
- Canonical Source: `../airlineops` (sibling path)
- Scope: gz-obpi-pipeline skill, obpi-completion-validator hook, and pipeline closeout surfaces
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`

---

## Executive Summary

- Overall parity status: **Divergent** — pipeline skill and completion hook use incompatible ledger contracts in gzkit; airlineops canonical design is self-consistent but missing process guardrails discovered during gzkit execution
- Critical gaps: 2 (ledger contract mismatch in gzkit, missing anti-rationalization in both repos)
- Recommended next minor(s): ADR-0.14.0 (current), pool ADR for hook ledger alignment

---

## Canonical-Root Resolution Evidence (Required)

- Resolution order used: sibling path `../airlineops`
- Selected canonical root: `/Users/jeff/Documents/Code/airlineops`
- Fallback engaged: no
- Fail-closed behavior statement: if no candidate resolves, stop and report blockers; do not emit parity conclusions.

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status | Severity | Evidence |
|---|---|---|---|---|
| `.github/skills/gz-obpi-pipeline/SKILL.md` | `.claude/skills/gz-obpi-pipeline/SKILL.md` | Divergent | P0 | See F-001, F-002, F-003 |
| `.claude/hooks/obpi-completion-validator.py` | `.claude/hooks/obpi-completion-validator.py` | Divergent | P1 | See F-004 |
| `.claude/hooks/pipeline-gate.py` | `.claude/hooks/pipeline-gate.py` | Partial | P2 | gzkit uses runtime helpers; airlineops is inline |
| `.github/skills/gz-obpi-audit/SKILL.md` | `.claude/skills/gz-obpi-audit/SKILL.md` | Parity | P3 | Same v1.2.0 content |
| `.github/skills/gz-obpi-sync/SKILL.md` | `.claude/skills/gz-obpi-sync/SKILL.md` | Parity | P3 | Same v1.0.0 content |
| `.github/skills/gz-obpi-lock/SKILL.md` | `.claude/skills/gz-obpi-lock/SKILL.md` | Parity | P3 | Same content |

---

## Findings

### F-001: Ledger contract mismatch (gzkit-only)

- Type: Divergent
- Canonical artifact: `.claude/hooks/obpi-completion-validator.py` (airlineops)
- gzkit artifact: `.claude/hooks/obpi-completion-validator.py` (gzkit)
- Why it matters: airlineops hook checks `{adr-dir}/logs/obpi-audit.jsonl` for `type: "obpi-audit"`. The skill writes attestation to the same file. **Self-consistent.** gzkit hook checks `.gzkit/ledger.jsonl` for `event: "obpi_receipt_emitted"`. The skill was writing to the ADR-level ledger. **Inconsistent.** This caused the hook to block every brief completion, requiring manual `emit-receipt` workaround.
- Evidence: Hook at line 84 checks `event == "obpi_receipt_emitted"` in project-wide ledger. Skill Stage 6 Step 1 writes to ADR-level `logs/obpi-audit.jsonl`.
- Proposed remediation: Either (a) change gzkit hook to check ADR-local ledger like airlineops (preferred — restores canonical parity) or (b) keep current workaround with `emit-receipt` step documented in skill. Current state: (b) shipped as interim fix.
- Target SemVer minor: pool ADR (hook-ledger-alignment)
- ADR/OBPI linkage: New pool ADR recommended

### F-002: Missing anti-rationalization (both repos)

- Type: Missing
- Canonical artifact: `.github/skills/gz-obpi-pipeline/SKILL.md` (airlineops)
- gzkit artifact: `.claude/skills/gz-obpi-pipeline/SKILL.md` (gzkit)
- Why it matters: On 2026-03-16 the agent completed implementation (Stage 3), printed a summary, and stopped — skipping Stages 4-6 entirely. The skill had no defense against this failure mode. gzkit now has the Iron Law section, rationalization prevention table, mandatory stage transitions, and named anti-patterns. airlineops does not.
- Evidence: gzkit SKILL.md lines 20-55 (Iron Law), stage boundary markers. airlineops SKILL.md has none.
- Proposed remediation: Export Iron Law + anti-rationalization to airlineops pipeline skill. **Import Now.**
- Target SemVer minor: N/A (airlineops skill update)
- ADR/OBPI linkage: Bilateral export action

### F-003: Missing Stage 5 evidence template (airlineops)

- Type: Missing
- Canonical artifact: `.github/skills/gz-obpi-pipeline/SKILL.md` Stage 4 (airlineops)
- gzkit artifact: `.claude/skills/gz-obpi-pipeline/SKILL.md` Stage 5
- Why it matters: Without a codified template, Stage 4/5 ceremony output is freeform. The human cannot reliably provide attestation without seeing value narrative, key proof, evidence table, files, and REQ verification in a consistent format.
- Evidence: airlineops Stage 4 says "Value narrative, Key proof, Evidence, Wait for attestation" — no template. gzkit Stage 5 has a verbatim required output template.
- Proposed remediation: Export evidence template to airlineops. **Import Now.**
- Target SemVer minor: N/A (airlineops skill update)
- ADR/OBPI linkage: Bilateral export action

### F-004: Missing pipeline marker cleanup + final sync (airlineops)

- Type: Missing
- Canonical artifact: `.github/skills/gz-obpi-pipeline/SKILL.md` Stage 5 (airlineops)
- gzkit artifact: `.claude/skills/gz-obpi-pipeline/SKILL.md` Stage 6 Steps 7-10
- Why it matters: airlineops creates `.pipeline-active-{OBPI-ID}.json` in Stage 1 but never removes it. Stale markers accumulate. Also missing final `git-sync` after brief update, so completed brief/ADR changes may not be pushed.
- Evidence: airlineops Stage 5 has 6 steps ending at "Create handoff". No marker cleanup, no final sync.
- Proposed remediation: Export cleanup steps + final sync to airlineops. **Import Now.**
- Target SemVer minor: N/A (airlineops skill update)
- ADR/OBPI linkage: Bilateral export action

---

## Parity Intake Rubric Decisions

| Candidate Item | Canonical Source | gzkit Target | Classification | Rationale |
|---|---|---|---|---|
| ADR-local ledger for completion hook | airlineops hook | gzkit hook | Defer (Tracked) | Requires hook code change — separate OBPI |
| Iron Law + anti-rationalization | gzkit skill (new) | airlineops skill | Import Now | Process guardrail, not product-specific |
| Stage 5 evidence template | gzkit skill (new) | airlineops skill | Import Now | Human attestation surface requirement |
| Pipeline marker cleanup | gzkit skill (new) | airlineops skill | Import Now | Prevents stale state accumulation |
| Final git-sync step | gzkit skill (new) | airlineops skill | Import Now | Ensures changes are pushed |
| Completion contract section | gzkit skill (new) | airlineops skill | Import Now | Defines what "done" means |

---

## Next Actions

1. Action: Export pipeline skill improvements to airlineops (F-002, F-003, F-004)
   Owner: claude-code (this session)

2. Action: Track hook-ledger alignment for gzkit (F-001)
   Parent ADR: pool ADR (hook-ledger-alignment)
   Owner: future session

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| gzkit hook → ADR-local ledger alignment (F-001) | Requires hook code change + test updates; interim `emit-receipt` workaround is functional | ADR-0.15.0 or next governance cycle |
