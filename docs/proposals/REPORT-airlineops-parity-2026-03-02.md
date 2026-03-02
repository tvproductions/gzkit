# REPORT: AirlineOps Parity Scan

## Metadata

- Date: 2026-03-02
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Scope: GovZero governance tools, rules, policies, and proof surfaces
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`

---

## Executive Summary

- Overall parity status: Partial
- Open critical gaps:
  - P3 Partial: canonical `.claude/**` and `.gzkit/**` surfaces remain broader/different than gzkit's current extraction profile
- In-cycle remediations completed:
  - Imported 10 missing canonical instruction files into `.github/instructions/`
  - Imported missing canonical skill asset: `.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md`
  - Opened follow-up tracking artifacts for breadth parity:
    - `docs/design/adr/pool/ADR-pool.airlineops-surface-breadth-parity.md`
    - `docs/proposals/OBPI-STUB-airlineops-surface-breadth-parity-01.md`
- Recommended next minor(s): `0.8.x` breadth-parity tranche (curated governance-only extraction)

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
  - `test -d ../airlineops && echo "sibling present" || echo "sibling missing"`
  - `test -d /Users/jeff/Documents/Code/airlineops && echo "absolute fallback present" || echo "absolute fallback missing"`
  - `cd ../airlineops && pwd`

Observed:

- `sibling present`
- `absolute fallback present`
- `canonical_root=/Users/jeff/Documents/Code/airlineops`

---

## Canonical Coverage Matrix

| Canonical Artifact (AirlineOps) | gzkit Counterpart | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|
| `../airlineops/docs/governance/governance_runbook.md` | `docs/governance/governance_runbook.md` | Parity | P3 | `airlineops_governance_runbook=present`; `gzkit_governance_runbook=present` |
| `../airlineops/.github/instructions/*.instructions.md` | `.github/instructions/*.instructions.md` | Parity | P3 | canonical-minus-gzkit diff now empty (`comm -23 ... = empty`) |
| `../airlineops/docs/governance/GovZero/**` | `docs/governance/GovZero/**` | Parity | P3 | canonical-minus-gzkit diff empty |
| `../airlineops/.github/skills/gz-*` | `.github/skills/gz-*` | Parity | P3 | canonical-minus-gzkit diff now empty after importing `ADR_TEMPLATE_SEMVER.md` |
| `../airlineops/AGENTS.md`, `../airlineops/CLAUDE.md` | `AGENTS.md`, `CLAUDE.md` | Partial | P3 | contract parity is high; AirlineOps includes product-domain constraints intentionally not extracted |
| `../airlineops/.claude/**` | `.claude/**` | Partial | P3 | canon has broader ops-specific surfaces (`airlineops .claude` file count 179 vs gzkit 81) |
| `../airlineops/.codex/**` | `.codex/**` | Parity | P3 | `airlineops_codex=missing`; `gzkit_codex=missing` |
| `../airlineops/.gzkit/**` | `.gzkit/**` | Partial | P3 | structures differ (canon includes ontology/lessons; gzkit emphasizes manifest/ledger/skills) |

---

## Behavior / Procedure Source Matrix

| Behavior Class | Canonical Source(s) | gzkit Source(s) | Status | Severity | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | `AGENTS.md`, `.github/instructions/**`, governance runbook | `AGENTS.md`, `.github/instructions/**`, `docs/governance/governance_runbook.md` | Parity | P3 | instruction-surface parity closed this cycle |
| Tool-use control surfaces | `gz-*` skills and ritual docs | `gz-*` skills, `docs/user/commands/**`, runtime CLI | Parity | P3 | canonical skill file-set diff empty |
| Post-tool accounting | audit protocol + receipt routines | `gz audit`, `gz adr emit-receipt`, ledger outputs | Parity | P3 | command surfaces and docs exist |
| Validation | gate rules + command contracts | `gz cli audit`, `gz check-config-paths`, docs build | Parity | P3 | ritual commands PASS on 2026-03-02 |
| Verification | closeout and audit checks | `gz closeout`, `gz attest`, `gz adr audit-check` | Parity | P3 | `uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol` PASS |
| Presentation | governance runbooks and operator docs | `docs/governance/governance_runbook.md`, `docs/user/runbook.md`, command docs | Parity | P3 | docs surfaces present and build successfully |
| Human authority boundary | Gate 5 attestation doctrine | `AGENTS.md`, `docs/user/commands/attest.md` | Parity | P3 | explicit attestation boundary remains documented |

---

## Habit Parity Matrix (Required)

| Habit Class | Canonical Source Signal | gzkit Surface(s) | Status (Parity/Partial/Missing/Divergent) | Severity (P0-P3) | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | instruction files + runbook preflight | AGENTS + `.github/instructions/**` + governance runbook | Parity | P3 | canonical instruction-set now present |
| Tool-use control surfaces | canonical skill naming/assets and invocation | gz skills + CLI docs + compatibility aliases | Parity | P3 | canonical skill file-set now present |
| Post-tool accounting | audit + receipts | `gz audit`, receipt emitters | Parity | P3 | runtime commands + docs available |
| Validation | executable ritual checks | cli audit, config-path audit, mkdocs strict | Parity | P3 | all required checks PASS |
| Verification | closeout -> attestation -> audit progression | closeout/attest/audit flow | Parity | P3 | `gz adr audit-check` PASS |
| Presentation for humans | procedural runbook + command docs | governance runbook + user runbook + command docs | Parity | P3 | docs surfaces coherent and buildable |
| Human authority boundary | explicit human attestation requirement | AGENTS OBPI protocol + attest docs | Parity | P3 | no drift observed |

---

## GovZero Mining Inventory

| Mined Norm / Habit | Canonical Source Path | gzkit Extraction Path | Status | Confidence | Remediation |
|---|---|---|---|---|---|
| Maintain dedicated governance runbook | `../airlineops/docs/governance/governance_runbook.md` | `docs/governance/governance_runbook.md` | Parity | High | keep in sync during weekly parity scans |
| Deterministic canonical-root resolution with fail-closed behavior | canonical runbook parity procedures | `.gzkit/skills/airlineops-parity-scan/SKILL.md` + parity reports | Parity | High | none |
| Governance instruction files are first-class doctrine | `../airlineops/.github/instructions/*.instructions.md` | `.github/instructions/**` | Parity | High | completed this cycle |
| GovZero docs require path-level parity evidence | `../airlineops/docs/governance/GovZero/**` | `docs/governance/GovZero/**` | Parity | High | maintain recursive parity checks |
| Skill lifecycle compatibility must preserve canonical assets, not only SKILL.md | `../airlineops/.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md` | `.github/skills/gz-adr-manager/**` | Parity | High | completed this cycle |
| Human attestation is the authority boundary | `../airlineops/AGENTS.md`, `../airlineops/docs/governance/GovZero/charter.md` | `AGENTS.md`, `docs/user/commands/attest.md` | Parity | High | none |
| Layered trust ordering is explicit and executable | `../airlineops/docs/governance/GovZero/layered-trust.md` | `docs/governance/GovZero/layered-trust.md`, governance runbook | Parity | High | none |

## Parity Intake Rubric Decisions (Required)

Use `docs/governance/parity-intake-rubric.md` to classify each candidate import.

| Candidate Item | Canonical Source | gzkit Target | Classification (Import Now / Import with Compatibility / Defer (Tracked) / Exclude) | Rationale | Runtime/Proof Backing |
|---|---|---|---|---|---|
| Missing governance instruction files (closed in-cycle) | `../airlineops/.github/instructions/*.instructions.md` | `.github/instructions/*.instructions.md` | Import Now (Completed) | High pre-tool drift impact; imported this cycle | path-level diff now empty + ritual checks |
| Missing canonical `gz-adr-manager` template asset (closed in-cycle) | `../airlineops/.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md` | `.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md` | Import with Compatibility (Completed) | Alias existed; asset imported this cycle to close drift | path-level diff now empty |
| Full `.claude/**` breadth mirror from AirlineOps | `../airlineops/.claude/**` | `.claude/**` | Defer (Tracked) | Canon contains many product-domain plans/hooks; governance-only extraction should be selected deliberately | count/topology comparison evidence + tracked ADR/OBPI stub |
| `.gzkit/**` structure convergence breadth | `../airlineops/.gzkit/**` | `.gzkit/**` | Defer (Tracked) | Canon and extraction currently serve different runtime roles; needs explicit design decision | structure diff evidence + tracked ADR/OBPI stub |
| AirlineOps product-domain workflows (warehouse/dataset behavior) | `../airlineops/src/airlineops/**` | N/A | Exclude | Product capability behavior, not GovZero process doctrine | package/domain path evidence |

## NOT GovZero Exclusion Log

Use this section for exclusion-first classification. Anything excluded from GovZero scope MUST be justified as product capability.

| Candidate Item | Canonical Source Path | Exclusion Rationale (Product Capability) | Evidence | Reviewer |
|---|---|---|---|---|
| AirlineOps data/forecasting and warehouse product workflows | `../airlineops/src/airlineops/**` | Product capability, not governance process | domain-specific package namespace and command families | Agent |

---

## Findings

### F-001

- Type: Resolved (in-cycle)
- Canonical artifact: `.github/instructions/*.instructions.md`
- gzkit artifact: `.github/instructions/*.instructions.md`
- Why it matters: Missing instruction files reduce pre-tool orientation parity and can reintroduce process drift.
- Evidence: canonical-minus-gzkit instruction diff is now empty.
- Proposed remediation: complete (imported 10 missing canonical instruction files).
- Target SemVer minor: `0.8.x` maintenance closure
- ADR/OBPI linkage: `ADR-pool.airlineops-canon-reconciliation` -> `instruction-surface-parity`

### F-002

- Type: Resolved (in-cycle)
- Canonical artifact: `.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md`
- gzkit artifact: `.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md`
- Why it matters: Asset-level drift in compatibility skills can cause canonical ritual/template divergence.
- Evidence: canonical skill file-set diff is now empty.
- Proposed remediation: complete (asset imported).
- Target SemVer minor: `0.5.x` maintenance closure
- ADR/OBPI linkage: `ADR-0.5.0-skill-lifecycle-governance` follow-up (`skill-asset-parity`)

### F-003

- Type: Partial (Tracked)
- Canonical artifact: `.claude/**`, `.gzkit/**`
- gzkit artifact: `.claude/**`, `.gzkit/**`
- Why it matters: Broader canon surfaces include process habits not yet explicitly mapped into gzkit.
- Evidence: topology/count differences (`.claude` 179 vs 81 files; `.gzkit` structure divergence).
- Proposed remediation: execute curated governance-only extraction tranches under new pool ADR.
- Target SemVer minor: `0.8.x`
- ADR/OBPI linkage:
  - `ADR-pool.airlineops-surface-breadth-parity`
  - `OBPI-STUB-airlineops-surface-breadth-parity-01`

---

## Proof Surface Check

Primary proofs must remain synchronized:

- [x] User documentation
- [x] Command manpages
- [x] Operator runbook
- [x] Behavior/procedure source matrix completed

Executable ritual checks (record command + result):

- [x] `uv run gz cli audit` (PASS: `CLI audit passed.`)
- [x] `uv run gz check-config-paths` (PASS: `Config-path audit passed.`)
- [x] `uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol` (PASS)
- [x] `uv run mkdocs build --strict` (PASS)

Notes:

- MkDocs strict build succeeded; informational notices remain for nav inclusion and unresolved absolute/relative link handling.

---

## Risk Summary

- Blocks 1.0 readiness:
  - Breadth parity for canonical `.claude/**` and `.gzkit/**` remains open (tracked).
- Can wait:
  - Full breadth import, provided all decisions remain tracked through the new pool ADR/OBPI stub.
- Must be done next cycle:
  - Build curated candidate inventory and intake decisions for `.claude/**` and `.gzkit/**`.

---

## Next Actions

1. Action: Build and classify canonical candidate inventory for `.claude/**` and `.gzkit/**` breadth parity.
   Parent ADR: `ADR-pool.airlineops-surface-breadth-parity`
   OBPI: `OBPI-STUB-airlineops-surface-breadth-parity-01`
   Owner: Human + Agent
2. Action: Prepare first governance-only import tranche with explicit exclusions for product-domain assets.
   Parent ADR: `ADR-pool.airlineops-surface-breadth-parity`
   OBPI: `OBPI-STUB-airlineops-surface-breadth-parity-01`
   Owner: Human + Agent
3. Action: Continue weekly parity scans with rubric-backed import/defer decisions.
   Parent ADR: `ADR-0.3.0-airlineops-canon-reconciliation`
   OBPI: maintenance cadence
   Owner: Agent

---

## Deferrals

| Item | Rationale | Revisit by |
|---|---|---|
| Full `.claude/**` breadth import | Requires governance-only filtering from product-domain plans/hooks | 2026-03-16 |
| Full `.gzkit/**` structure convergence | Canon and extraction currently serve different runtime roles; convergence needs explicit design decision | 2026-03-16 |
