# REPORT: AirlineOps Parity Scan

## Metadata

- Date: 2026-02-15
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Scope: GovZero governance tools, rules, policies, and proof surfaces
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`

---

## Executive Summary

- Overall parity status: Partial
- Critical gaps:
  - P1 Missing: `.github/instructions/**` governance instruction surface absent in gzkit
  - P1 Divergent: `gz-adr-manager` in AirlineOps vs `gz-adr-create` in gzkit (skill + mirror surfaces)
  - P2 Missing: `.codex/skills` mirror absent in gzkit
  - P2 Partial: `.gzkit/` governance surfaces differ (canon has governance/insights/lessons; gzkit only ledger + manifest)
  - P2 Validation failures: `gz check-config-paths` and `mkdocs build --strict`
- Recommended next minor(s): 0.3.x (governance parity + doc-surface closure)

---

## Canonical-Root Resolution Evidence (Required)

- Resolution order used:
  1. explicit override (if provided)
  2. sibling path `../airlineops`
  3. absolute fallback `/Users/jeff/Documents/Code/airlineops`
- Selected canonical root: `/Users/jeff/Documents/Code/airlineops`
- Fallback engaged: yes (sibling missing; absolute fallback present)
- Fail-closed behavior statement: if no candidate resolves, stop and report blockers; do not emit parity conclusions.
- Evidence commands:
  - `test -d ../airlineops && echo "sibling present" || echo "sibling missing"`
  - `test -d /Users/jeff/Documents/Code/airlineops && echo "absolute fallback present" || echo "absolute fallback missing"`

Observed:

- `sibling missing`
- `absolute fallback present`

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|
| `../airlineops/.github/skills/gz-*` | `.github/skills/gz-*` | Divergent | P1 | AirlineOps includes `gz-adr-manager`; gzkit has `gz-adr-create` instead |
| `../airlineops/.github/instructions/*.instructions.md` | `.github/instructions/*.instructions.md` | Missing | P1 | gzkit has no `.github/instructions/` directory |
| `../airlineops/docs/governance/GovZero/**` | `docs/governance/GovZero/**` | Parity | P3 | File set matches (including `audits/` + `releases/`) |
| `../airlineops/AGENTS.md`, `../airlineops/CLAUDE.md` | `AGENTS.md`, `CLAUDE.md` | Partial | P3 | gzkit contract is narrower; missing cross-platform + gate5 references |
| `../airlineops/.claude/**` | `.claude/**` | Partial | P2 | gzkit lacks many canonical skills (chores + governance adjacents) |
| `../airlineops/.codex/**` | `.codex/**` (if present) | Missing | P2 | canonical `.codex/skills` present; gzkit missing `.codex` mirror |
| `../airlineops/.gzkit/**` | `.gzkit/**` | Partial | P2 | canon has governance/insights/lessons; gzkit only ledger + manifest |

---

## Behavior / Procedure Source Matrix

| Behavior Class | Canonical Source(s) | gzkit Source(s) | Status | Severity | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | `AGENTS.md`, GovZero doctrine | `AGENTS.md` | Partial | P3 | gzkit lacks canonical instruction surfaces |
| Tool-use control surfaces | `.github/skills/gz-*`, `.github/instructions/**` | `.github/skills/gz-*`, docs | Partial | P1 | missing `.github/instructions/**`; skill naming divergence |
| Post-tool accounting | audit protocol + ledger rules | `gz cli audit`, ledger + reports | Parity | P3 | `uv run gz cli audit` PASS |
| Validation | gate rules + command contracts | `gz check-config-paths`, `mkdocs build --strict` | Partial | P2 | `gz check-config-paths` FAIL; mkdocs theme error |
| Verification | audit/closeout procedures | `gz adr audit-check` | Parity | P3 | `uv run gz adr audit-check ADR-0.3.0` PASS |
| Presentation | runbooks + operator narrative | `docs/user/*`, report artifacts | Partial | P2 | mkdocs build failure blocks published proof surface |
| Human authority boundary | Gate 5 doctrine | attestation steps in docs | Partial | P3 | canonical doctrine not mirrored in instructions surface |

---

## Habit Parity Matrix (Required)

| Habit Class | Canonical Source Signal | gzkit Surface(s) | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | canonical instruction + doctrine surfaces | `AGENTS.md` only | Partial | P3 | `.github/instructions/**` missing |
| Tool-use control surfaces | skill naming, instruction docs | `.github/skills`, `.claude/skills` | Divergent | P1 | `gz-adr-manager` vs `gz-adr-create` |
| Post-tool accounting | audit protocol + receipts | `gz cli audit` | Parity | P3 | CLI audit PASS |
| Validation | gate commands | `gz check-config-paths`, mkdocs | Partial | P2 | config-path audit fail; mkdocs theme missing |
| Verification | audit-check + closeout | `gz adr audit-check` | Parity | P3 | ADR-0.3.0 audit-check PASS |
| Presentation for humans | docs + runbook | mkdocs build | Partial | P2 | mkdocs theme error |
| Human authority boundary | Gate 5 attestation | `gz attest`, docs | Partial | P3 | canonical instruction surfaces missing |

---

## GovZero Mining Inventory

| Mined Norm / Habit | Canonical Source Path | gzkit Extraction Path | Status | Confidence | Remediation |
|---|---|---|---|---|---|
| Instruction surfaces must be read before work | `../airlineops/.github/instructions/*.instructions.md` | n/a | Missing | High | Add `.github/instructions/**` mirror in gzkit |
| Skills must be mirrored across control surfaces | `../airlineops/.codex/skills` | n/a | Missing | High | Add `.codex/skills` mirror in gzkit |
| Skill naming for ADR tools | `../airlineops/.github/skills/gz-adr-manager` | `.github/skills/gz-adr-create` | Divergent | High | Backport rename to AirlineOps or align gzkit |
| Ledger + audit protocol as proof surface | `../airlineops/docs/governance/GovZero/audit-protocol.md` | `docs/governance/GovZero/audit-protocol.md` | Parity | High | None |

## NOT GovZero Exclusion Log

| Candidate Item | Canonical Source Path | Exclusion Rationale (Product Capability) | Evidence | Reviewer |
|---|---|---|---|---|
| non-gz operational skills (forecasting, dataset, fleet, etc.) | `../airlineops/.github/skills/*` | Product capability | Skills names + domain scope | Agent |

---

## Findings

### F-001

- Type: Missing
- Canonical artifact: `.github/instructions/*.instructions.md`
- gzkit artifact: none
- Why it matters: Instruction surfaces encode canonical governance rules; absence risks procedural drift.
- Evidence: gzkit has no `.github/instructions/` directory.
- Proposed remediation: mirror canonical instruction files into gzkit.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: ADR-0.3.0 / new OBPI (instruction-surface parity)

### F-002

- Type: Divergent
- Canonical artifact: `gz-adr-manager`
- gzkit artifact: `gz-adr-create`
- Why it matters: skill naming divergence breaks parity and cross-repo rituals.
- Evidence: AirlineOps contains `gz-adr-manager` in `.github/skills` + `.claude/skills`; gzkit does not.
- Proposed remediation: backport rename to AirlineOps or re-align gzkit naming.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: ADR-0.3.0 / OBPI-0.3.0-02 (backport execution)

### F-003

- Type: Missing
- Canonical artifact: `.codex/skills` mirror
- gzkit artifact: none
- Why it matters: Codex control-surface parity required for agent discipline.
- Evidence: AirlineOps `.codex/skills` present; gzkit lacks `.codex/`.
- Proposed remediation: add `.codex/skills` mirror and sync ritual.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: ADR-0.3.0 / new OBPI (control-surface mirror parity)

### F-004

- Type: Partial
- Canonical artifact: `.gzkit/` governance surfaces
- gzkit artifact: `.gzkit/ledger.jsonl`, `.gzkit/manifest.json`
- Why it matters: governance insights/lessons surfaces are canonical; gzkit lacks them.
- Evidence: AirlineOps has `.gzkit/governance`, `.gzkit/insights`, `.gzkit/lessons`.
- Proposed remediation: backport governance/insights/lessons surfaces or justify exclusion.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: ADR-0.3.0 / new OBPI (gzkit governance surfaces)

### F-005

- Type: Partial
- Canonical artifact: Validation proof surface
- gzkit artifact: `gz check-config-paths`, `mkdocs build --strict`
- Why it matters: Proof surfaces must build cleanly to satisfy Gate 3/5 alignment.
- Evidence: `gz check-config-paths` FAIL (missing `docs/design/obpis` path); mkdocs theme `material` missing.
- Proposed remediation: restore config paths or update settings; add mkdocs-material dependency or adjust theme.
- Target SemVer minor: 0.3.x
- ADR/OBPI linkage: ADR-0.3.0 / new OBPI (proof-surface validation fixes)

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [ ] User documentation
- [ ] Command manpages
- [ ] Operator runbook
- [x] Behavior/procedure source matrix completed

Executable ritual checks (record command + result):

- [x] `uv run gz cli audit` (PASS)
- [ ] `uv run gz check-config-paths` (FAIL: docs/design/obpis missing)
- [x] `uv run gz adr audit-check ADR-0.3.0` (PASS)
- [ ] `uv run mkdocs build --strict` (FAIL: theme 'material' not installed)

Notes:

- `uv run gz check-config-paths` failed with missing `paths.obpis` and `manifest.artifacts.obpi.path`.
- `uv run mkdocs build --strict` failed due to unrecognized theme `material`.

---

## Next Actions

1. Action: Mirror canonical `.github/instructions/**` into gzkit.
   Parent ADR: ADR-0.3.0
   OBPI: New OBPI (instruction-surface parity)
   Owner: Human
2. Action: Resolve `gz-adr-manager` vs `gz-adr-create` divergence (backport to AirlineOps).
   Parent ADR: ADR-0.3.0
   OBPI: OBPI-0.3.0-02 (backport execution)
   Owner: Human
3. Action: Add `.codex/skills` mirror for Codex control surface.
   Parent ADR: ADR-0.3.0
   OBPI: New OBPI (control-surface mirror parity)
   Owner: Human
4. Action: Restore `.gzkit` governance/insights/lessons surfaces or document exclusion.
   Parent ADR: ADR-0.3.0
   OBPI: New OBPI (governance surface parity)
   Owner: Human
5. Action: Fix validation proof surfaces (`gz check-config-paths`, mkdocs theme).
   Parent ADR: ADR-0.3.0
   OBPI: New OBPI (proof-surface validation fixes)
   Owner: Human

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| Non-GovZero product skills parity | Product capability exclusion | Next quarterly parity audit |
