# REPORT: AirlineOps Parity Scan (Template)

## Metadata

- Date: YYYY-MM-DD
- Scanner: Human + Agent
- Canonical Source: `<resolved canonical root>`
- Scope: GovZero governance tools, rules, policies, and proof surfaces
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`

---

## Executive Summary

- Overall parity status:
- Critical gaps:
- Recommended next minor(s):

---

## Canonical-Root Resolution Evidence (Required)

- Resolution order used:
  1. explicit override (if provided)
  2. sibling path `../airlineops`
  3. absolute fallback `/Users/jeff/Documents/Code/airlineops`
- Selected canonical root:
- Fallback engaged (yes/no):
- Fail-closed behavior statement: if no candidate resolves, stop and report blockers; do not emit parity conclusions.
- Evidence commands:
  - `test -d ../airlineops && echo "sibling present" || echo "sibling missing"`
  - `test -d /Users/jeff/Documents/Code/airlineops && echo "absolute fallback present" || echo "absolute fallback missing"`

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|
| `../airlineops/.github/skills/gz-...` | `.github/skills/...` |  |  |  |
| `../airlineops/docs/governance/GovZero/...` | `docs/user/...` / `docs/design/...` |  |  |  |
| `../airlineops/AGENTS.md`, `../airlineops/CLAUDE.md` | `AGENTS.md`, `CLAUDE.md` |  |  |  |
| `../airlineops/.claude/**` | `.claude/**` |  |  |  |
| `../airlineops/.codex/**` | `.codex/**` (if present) |  |  |  |
| `../airlineops/.gzkit/**` | `.gzkit/**` |  |  |  |

---

## Behavior / Procedure Source Matrix

| Behavior Class | Canonical Source(s) | gzkit Source(s) | Status | Severity | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | `AGENTS.md`, skill preconditions, GovZero doctrine | OBPI briefs, runbook preflight, concept docs |  |  |  |
| Tool-use control surfaces | `gz-*` skills, instruction files | `gz-*` skills, CLI command docs, runtime command surface |  |  |  |
| Post-tool accounting | audit protocol, ledger/receipt rules | `gz audit`, `gz adr emit-receipt`, ledger event usage |  |  |  |
| Validation | gate rules and command contracts | `gz gates`, `gz check-config-paths`, lint/type/test docs |  |  |  |
| Verification | closeout/audit procedures | `gz adr audit-check`, closeout docs, proofs |  |  |  |
| Presentation | runbooks, manpages, operator narratives | `docs/user/commands/*`, `docs/user/runbook.md`, references |  |  |  |
| Human authority boundary | Gate 5 attestation doctrine | attestation steps and OBPI/ADR completion language |  |  |  |

---

## Habit Parity Matrix (Required)

| Habit Class | Canonical Source Signal | gzkit Surface(s) | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation |  |  |  |  |  |
| Tool-use control surfaces |  |  |  |  |  |
| Post-tool accounting |  |  |  |  |  |
| Validation |  |  |  |  |  |
| Verification |  |  |  |  |  |
| Presentation for humans |  |  |  |  |  |
| Human authority boundary |  |  |  |  |  |

---

## GovZero Mining Inventory

Use this section to enumerate mined process norms across all canonical control surfaces.

| Mined Norm / Habit | Canonical Source Path | gzkit Extraction Path | Status | Confidence | Remediation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## NOT GovZero Exclusion Log

Use this section for exclusion-first classification. Anything excluded from GovZero scope MUST be justified as product capability.

| Candidate Item | Canonical Source Path | Exclusion Rationale (Product Capability) | Evidence | Reviewer |
|---|---|---|---|---|
|  |  |  |  |  |

---

## Findings

### F-001

- Type: Missing / Divergent / Partial
- Canonical artifact:
- gzkit artifact:
- Why it matters:
- Evidence:
- Proposed remediation:
- Target SemVer minor:
- ADR/OBPI linkage:

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [ ] User documentation
- [ ] Command manpages
- [ ] Operator runbook
- [ ] Behavior/procedure source matrix completed

Executable ritual checks (record command + result):

- [ ] `uv run gz cli audit`
- [ ] `uv run gz check-config-paths`
- [ ] `uv run gz adr audit-check ADR-<target>`
- [ ] `uv run mkdocs build --strict`

Notes:

---

## Next Actions

1. Action:
   Parent ADR:
   OBPI:
   Owner:
2. Action:
   Parent ADR:
   OBPI:
   Owner:

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
|  |  |  |
