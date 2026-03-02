# REPORT: AirlineOps GovZero Mining

## Metadata

- Date: 2026-03-02
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`
- Scope: GovZero process-habit extraction across control surfaces

---

## Mining Surfaces

- [x] `AGENTS.md`
- [x] `CLAUDE.md`
- [x] `.github/**`
- [x] `.claude/**`
- [x] `.codex/**`
- [x] `.gzkit/**`
- [x] `docs/governance/GovZero/**`
- [x] `docs/governance/governance_runbook.md`

---

## Mined Norms

| Norm ID | Mined Habit / Rule | Canonical Source Path | Product Capability? (Y/N) | Included in GovZero Scope? | gzkit Extraction Path(s) | Status (Parity/Partial/Missing/Divergent) | Notes |
|---|---|---|---|---|---|---|---|
| N-001 | Keep a dedicated governance runbook for procedural operation | `../airlineops/docs/governance/governance_runbook.md` | N | Y | `docs/governance/governance_runbook.md` | Parity | Present in both repos |
| N-002 | Canonical-root parity scans are deterministic and fail closed | canonical runbook parity procedures | N | Y | `.gzkit/skills/airlineops-parity-scan/SKILL.md` + parity reports | Parity | Root resolved via sibling-first strategy |
| N-003 | Governance instruction files are first-class orientation doctrine | `../airlineops/.github/instructions/*.instructions.md` | N | Y | `.github/instructions/**` | Parity | Missing files imported this cycle |
| N-004 | GovZero docs should maintain path-level parity | `../airlineops/docs/governance/GovZero/**` | N | Y | `docs/governance/GovZero/**` | Parity | No canonical GovZero file missing |
| N-005 | Skill parity includes assets/templates, not SKILL.md only | `../airlineops/.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md` | N | Y | `.github/skills/gz-adr-manager/**` | Parity | Missing canonical template asset imported |
| N-006 | Human attestation is required authority boundary for completion claims | `../airlineops/AGENTS.md`, `../airlineops/docs/governance/GovZero/charter.md` | N | Y | `AGENTS.md`, `docs/user/commands/attest.md` | Parity | Runtime + doctrine alignment intact |
| N-007 | Layered trust ordering (evidence -> ledger -> sync) governs reconciliation | `../airlineops/docs/governance/GovZero/layered-trust.md` | N | Y | `docs/governance/GovZero/layered-trust.md`, runbooks | Parity | Explicit in docs and command flow |
| N-008 | Validation rituals must be executable, not declarative only | canonical runbook validation bundle | N | Y | `gz cli audit`, `gz check-config-paths`, `gz adr audit-check`, `mkdocs --strict` | Parity | All required checks PASS on 2026-03-02 |
| N-009 | Canonical `.claude/**` and `.gzkit/**` breadth requires curated governance-only intake | `../airlineops/.claude/**`, `../airlineops/.gzkit/**` | N | Y | `.claude/**`, `.gzkit/**` | Partial | Tracked via new pool ADR + OBPI stub |

## NOT GovZero Exclusion Log

Exclusions are exceptional. Default is inclusion in GovZero scope unless product capability evidence is explicit.

| Candidate Item | Canonical Source Path | Why NOT GovZero | Product Capability Evidence | Reviewer |
|---|---|---|---|---|
| AirlineOps domain-specific data/forecasting routines | `../airlineops/src/airlineops/**` | Product behavior, not governance process | domain package namespace and command families are product-specific | Agent |

---

## Procedure Parity Checks

| Procedure Class | Canonical Source(s) | gzkit Runtime/Docs Surface(s) | Executable Check | Result | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | `AGENTS.md`, canonical instruction files, governance runbook | `AGENTS.md`, `.github/instructions/**`, governance runbook | path-level diff | PASS | canonical-minus-gzkit instruction diff empty |
| Tool-use control | canonical `gz-*` skill surfaces (including assets) | gz skills + CLI docs + alias skill | skill/path check | PASS | canonical-minus-gzkit skill file-set diff empty |
| Post-tool accounting | audit protocol + receipt routines | `gz audit`, receipt commands | command availability | PASS | command docs and runtime surfaces present |
| Validation | canonical ritual commands | `uv run gz cli audit` | command run | PASS | `CLI audit passed.` |
| Validation | canonical ritual commands | `uv run gz check-config-paths` | command run | PASS | `Config-path audit passed.` |
| Verification | canonical ledger evidence checks | `uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol` | command run | PASS | all linked OBPIs completed with evidence |
| Presentation | docs-as-proof discipline | `uv run mkdocs build --strict` | command run | PASS | strict build succeeded with informational notices only |
| Human attestation boundary | closeout + attestation doctrine | `gz closeout`, `gz attest`, AGENTS protocol | doc/runtime alignment | PASS | explicit attestation language present |

## Intake Decisions (Required)

Classify each high-impact mined candidate with the parity intake rubric.

| Norm ID | Candidate | Classification | Why | Follow-up Linkage |
|---|---|---|---|---|
| N-003 | Canonical instruction files | Import Now (Completed) | High impact on orientation and behavioral consistency; imported this cycle | Closed in `REPORT-airlineops-parity-2026-03-02.md` |
| N-005 | Canonical `gz-adr-manager` template asset | Import with Compatibility (Completed) | Alias existed; asset imported to close template drift | Closed in `REPORT-airlineops-parity-2026-03-02.md` |
| N-009 | `.claude/**` breadth parity inventory and intake | Defer (Tracked) | Governance-only filtering required before import | `ADR-pool.airlineops-surface-breadth-parity` + `OBPI-STUB-airlineops-surface-breadth-parity-01` |
| N-009 | `.gzkit/**` breadth parity inventory and intake | Defer (Tracked) | Structure-level differences need explicit decision | `ADR-pool.airlineops-surface-breadth-parity` + `OBPI-STUB-airlineops-surface-breadth-parity-01` |
| N-008 | Executable validation ritual bundle | Import Now (Maintain) | Runtime-backed and passing; preserve as required ceremony | `ADR-0.6.0-pool-promotion-protocol` maintenance |

---

## Required Commands

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol
uv run mkdocs build --strict
```

---

## Findings and Next Actions

1. Finding:
   - Severity: P3 (resolved)
   - Why it matters: Instruction-surface parity now matches canonical file set.
   - ADR/OBPI linkage: closure of prior `instruction-surface-parity` action
   - Next action: maintain parity via weekly scan cadence.

2. Finding:
   - Severity: P3 (resolved)
   - Why it matters: Skill asset drift in `gz-adr-manager` is closed.
   - ADR/OBPI linkage: closure of prior `skill-asset-parity` action
   - Next action: include asset-level checks in parity diff bundles.

3. Finding:
   - Severity: P3 (tracked)
   - Why it matters: Canonical `.claude/**` and `.gzkit/**` surfaces are broader than current extraction.
   - ADR/OBPI linkage: `ADR-pool.airlineops-surface-breadth-parity`, `OBPI-STUB-airlineops-surface-breadth-parity-01`
   - Next action: produce curated candidate inventory and execute first governance-only import tranche.

4. Finding:
   - Severity: P3 (healthy)
   - Why it matters: Runtime ritual checks remain executable and passing, preserving procedure parity confidence.
   - ADR/OBPI linkage: maintenance cadence
   - Next action: maintain weekly scan cadence and refresh dated reports.
