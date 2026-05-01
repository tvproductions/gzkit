---
id: OBPI-0.26.0-04-adr-governance
parent: ADR-0.26.0-governance-library-module-absorption
item: 4
status: Completed
lane: heavy
date: 2026-03-21
decision: Confirm
---

# OBPI-0.26.0-04: ADR Governance

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-04 — "Evaluate and absorb lib/adr_governance.py (535 lines) — ADR governance policy enforcement"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/adr_governance.py` (535 lines)
against gzkit's partial governance enforcement in `src/gzkit/ledger.py` and
determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or
Exclude (domain-specific). The opsdev module provides dedicated governance
policy enforcement for lane determination, gate validation, attestation
requirements, and compliance checks. gzkit has partial coverage in
`src/gzkit/ledger.py`, but the comparison must determine whether gzkit's
ledger-centric approach adequately covers the same policy-enforcement patterns.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/adr_governance.py` (535 lines)
- **gzkit equivalent:** Partial in `src/gzkit/ledger.py`

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any absorption outcome would
add or change a runtime module / CLI surface. Confirm and Exclude outcomes
inherit Heavy because the decision is binding on future governance-library
absorption work and because the brief frontmatter records a doctrine
choice (autolink-as-skill-not-CLI) that future agents will treat as
canonical.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Governance policy enforcement is a core governance primitive that belongs in gzkit
- gzkit's ledger.py may embed some governance enforcement but likely lacks the breadth of a dedicated 535-line governance module
- The actual gzkit comparison surface for opsdev `lib/adr_governance.py` is `commands/adr_audit.py` + `commands/adr_coverage.py` + `commands/covers.py` + `traceability.py`, not `ledger.py` — recorded in `## Comparison` body section (parent-ADR-authored Source Material header not amended)

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing ledger infrastructure if it is already sufficient for its own purposes
- Re-running the comparison work already attested under OBPI-0.25.0-20-adr-governance-pattern (2026-04-11) on identical source material — divergent rationale on identical material is itself a doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Confirm / Exclude.
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Confirm: document why gzkit's implementation is sufficient despite the dedicated module gap.
6. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` for Confirm/Exclude outcomes (no code, no tests, no CLI change)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — understand the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-02-references brief — confirm canonical section headings, [doc] REQ tag pattern, and Confirm/Exclude rationale shape
- [x] Sibling OBPI-0.26.0-03-adr-recon plan — confirm in-flight comparison-unit plan template
- [x] OBPI-0.25.0-20-adr-governance-pattern brief (Completed 2026-04-11) — canonical precedent for the same source-module evaluation, recorded **Decision: Confirm** with five-point rationale
- [x] `src/gzkit/schemas/obpi.json` — required headers contract

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/adr_governance.py` (535 lines) — opsdev source under review
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Required path exists: `tests/test_adr_governance_confirm.py` — pre-existing canonical witness for the OBPI-0.25.0-20 Confirm decision (4 tests, all green)
- [x] Parent ADR Cross-Reference Matrix row for `adr_governance.py` reviewed: anticipates "Decide whether current policy enforcement is sufficient or should be split into a dedicated library"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/adr_governance.py` read end-to-end (lines 1-535): three internalized scripts (evidence_audit, adr_autolink, verification_report), regex-based parsing, stdlib dataclass models, ops-internal imports (`airlineops.paths.subpaths`, `opsdev.lib.ledger_schema`), `<!-- VERIFICATION:BEGIN/END -->` autolink marker mechanism
- [x] gzkit comparison surface read: `src/gzkit/commands/adr_audit.py` (758 lines, full audit-check + emit-receipt + authenticity gate), `src/gzkit/commands/adr_coverage.py` (426 lines, REQ traceability + `_synthesize_doc_proof_linkage`), `src/gzkit/commands/covers.py` (187 lines, `gz covers` CLI), `src/gzkit/traceability.py` (418 lines, AST-based scanner + Pydantic coverage models)
- [x] gzkit autolink doctrine: `.gzkit/skills/gz-adr-autolink/SKILL.md` line 37 explicitly documents *"There is no dedicated `gz adr` autolink subcommand in this repository"* — manual workflow is canonical doctrine, not capability gap
- [x] Duplicate-OBPI surface check: same source module `lib/adr_governance.py` evaluated under both ADR-0.25.0/OBPI-20 (Completed Confirm) and ADR-0.26.0/OBPI-04 (this brief) — defect tracked under GHI #376

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior, the brief names
  `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.26.0-04-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb`, `Confirm`, or `Exclude`.
  **Decision: Confirm** — see `## Decision` below.
- [x] REQ-0.26.0-04-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev and
  gzkit. See `## Comparison` (per-subcommand dimension table) and `## Decision`
  (five-point rationale enumeration anchored on OBPI-0.25.0-20).
- [x] REQ-0.26.0-04-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests needed to carry the pattern safely. **N/A — Confirm
  outcome.** No code absorbed; this REQ is vacuously satisfied.
- [x] REQ-0.26.0-04-04: [doc] Given a `Confirm` or `Exclude` outcome, then the
  brief explains why no upstream absorption is warranted. See `## Decision` —
  the five-point rationale documents why gzkit's existing surface
  (`traceability.py` + `commands/covers.py` + `commands/adr_audit.py`,
  ~1010 lines) already surpasses opsdev's `lib/adr_governance.py` (535 lines)
  across parsing fidelity, coverage depth, evidence audit, convention
  compliance, and intentional doctrine choice on autolink.
- [x] REQ-0.26.0-04-05: [doc] Given any operator-visible behavior change, then
  Gate 4 behavioral proof is present; otherwise the brief records `N/A` with
  rationale. **N/A.** Confirm outcome with zero code changes under
  `src/gzkit/`, zero new CLI verbs, zero generated-surface change — nothing
  operator-visible changes, so Gate 4 behavioral proof is not required.

## Comparison

### Source-material observation

The brief Source Material header at line 31 names `src/gzkit/ledger.py` as
the gzkit equivalent — mirroring the parent ADR's Tidy First Plan table at
`ADR-0.26.0-...md:29`. ledger.py is the gzkit ledger-event authoring surface
(728 lines), not ADR governance policy enforcement. The actual gzkit
ADR-governance surface that mirrors opsdev's `lib/adr_governance.py` (535
lines) is the same one OBPI-0.25.0-20-adr-governance-pattern compared
against three weeks earlier:

| gzkit module | Lines | Role |
|--------------|-------|------|
| `src/gzkit/traceability.py` | 418 | AST-based `@covers` scanning, `covers()` decorator with runtime REQ validation, Pydantic models (`CoverageEntry`, `CoverageRollup`, `CoverageReport`), multi-level rollups |
| `src/gzkit/commands/covers.py` | 187 | `gz covers` CLI with human/JSON/plain output, filtering by ADR/OBPI |
| `src/gzkit/commands/adr_audit.py` | 758 | `adr_audit_check()` brief content inspection + `adr_covers_check()` REQ traceability + `adr_emit_receipt_cmd` attestation authenticity gating |

This observation is body-level (Comparison section); the parent-ADR-authored
Source Material header is intentionally not amended.

### Per-subcommand mapping (opsdev → gzkit)

opsdev `lib/adr_governance.py` consolidates three internalized scripts. Each
maps to a richer gzkit surface:

| opsdev capability | opsdev source | gzkit equivalent | Verdict |
|-------------------|---------------|------------------|---------|
| `evidence_audit()` (~120 lines, lines 82–199): scan ADR files for title, status, and `## Evidence` heading presence; TSV/human output. | `airlineops/src/opsdev/lib/adr_governance.py:82-199` | `gz adr audit-check` (`commands/adr_audit.py:159` `adr_audit_check`) — inspects brief content sections (`Implementation Summary`, `Key Proof`, `Human Attestation`) via the central ledger graph, partitions findings by severity (`commands/adr_audit.py:99` `_partition_coverage_findings`), and integrates with the kind/lane/sensitivity matrix at `commands/adr_audit.py:279` `_requires_human_obpi_attestation`. | gzkit-superior |
| `adr_autolink()` (~100 lines, lines 207–306): regex `@covers`/`# ADR:` parsing via `parse_test_file()`, `collect_test_map()`, and `write_into_adr()` — auto-rewrite ADR `## Verification` sections from discovered tests. | `airlineops/src/opsdev/lib/adr_governance.py:207-306` | `.gzkit/skills/gz-adr-autolink/SKILL.md` (manual workflow) + `gz covers` discovery via `traceability.py` AST scanner. gzkit's `gz-adr-autolink` skill explicitly documents *"There is no dedicated `gz adr` autolink subcommand in this repository"* (line 37) — manual workflow is the canonical doctrine choice, not a capability gap. | gzkit-by-design |
| `verification_report()` (~80 lines, lines 314–535): regex-based `discover_covers()` over `tests/`, `_write_covers_ledger()` writing local `logs/covers-map.jsonl`, ADR Verification section update. | `airlineops/src/opsdev/lib/adr_governance.py:314-535` | `gz covers` (`commands/covers.py:148` `covers_cmd`) emits `summary` + `entries` payload via `traceability.py:compute_coverage` — multi-level ADR/OBPI/REQ rollup with central-ledger-graph integration via `gzkit.ledger.Ledger`, no local sidecar file. | gzkit-superior |

### Per-dimension comparison (canon-anchored from OBPI-0.25.0-20)

The dimension table established by OBPI-0.25.0-20-adr-governance-pattern
(2026-04-11, attested) holds verbatim because the source module is identical
and the gzkit comparison surface is unchanged across the three weeks between
attestations:

| Dimension | opsdev | gzkit | Source anchor |
|-----------|--------|-------|---------------|
| Parsing | Regex (`DECOR_RX`, `COMM_RX`, `RX_COVERS`) — fragile against non-trivial formatting | AST-based (`scan_test_tree`) — handles string expressions, nested decorators, multi-line constructs correctly | OBPI-0.25.0-20 § Dimension comparison row 1 |
| Coverage model | Flat ADR-to-tests mapping (`collect_test_map`, `discover_covers`) | Multi-level rollup: ADR/OBPI/REQ via `compute_coverage()` | OBPI-0.25.0-20 row 2 |
| Data models | stdlib `@dataclass(AdrRecord)` (line 47–55) | Pydantic `BaseModel` (`CoverageEntry`, `CoverageRollup`, `CoverageReport`) with `ConfigDict` | OBPI-0.25.0-20 row 3 |
| Evidence audit | Title/status/`## Evidence` heading presence check | Brief content inspection (Implementation Summary, Key Proof, Human Attestation) via ledger graph | OBPI-0.25.0-20 row 4 |
| Ledger integration | Local covers-map JSONL file (`logs/covers-map.jsonl`) | Central ledger graph (receipt events via `Ledger`) | OBPI-0.25.0-20 row 5 |
| Auto-writing | Injects `## Verification` sections into ADR files via `<!-- VERIFICATION:BEGIN/END -->` markers | Not used (OBPI briefs + `@covers` workflow + `gz-adr-autolink` skill) — intentional doctrine choice, not capability gap | OBPI-0.25.0-20 row 6 |
| Runtime validation | None | `covers()` decorator validates REQ exists at decoration time | OBPI-0.25.0-20 row 7 |
| Output formats | TSV / human text | Human / JSON / plain via `gz covers` CLI | OBPI-0.25.0-20 row 8 |

### Cross-platform / convention-compliance observations

opsdev `lib/adr_governance.py` imports `airlineops.paths.subpaths` (line 18)
and `opsdev.lib.ledger_schema` (line 19) — both ops-internal dependencies
that fail the subtraction test. Hardcodes `Path("tests")` (line 23) and uses
`docs_path("design", "adr")` (line 22) — neither portable to a gzkit-style
config-driven path resolution. gzkit's equivalent surface uses `pathlib.Path`
throughout, consults `gzkit.config` for adr_dir, and avoids the
ops-internal-import problem by construction.

## Decision

**Confirm.** gzkit's governance surface (`traceability.py` +
`commands/covers.py` + `commands/adr_audit.py`, ~1010 lines, plus the
`.gzkit/skills/gz-adr-autolink/SKILL.md` manual-workflow doctrine) already
covers and surpasses opsdev's `lib/adr_governance.py` (535 lines) across all
three internalized capabilities. No absorption warranted.

### Rationale

1. **Canonical precedent.** OBPI-0.25.0-20-adr-governance-pattern evaluated
   the same opsdev source file (`lib/adr_governance.py`, 535 lines) against
   the same gzkit surface three weeks earlier (attested 2026-04-11) and
   recorded **Decision: Confirm** with five-point rationale anchored on
   parsing, coverage, evidence, convention, and auto-writing dimensions.
   The pre-existing proof artifact `tests/test_adr_governance_confirm.py`
   (4 tests, all green) is the canonical witness. Re-running the comparison
   with divergent rationale on identical source material would itself be a
   doctrine-drift signal — Confirm-by-reference is the structurally correct
   landing.
2. **Parsing fidelity.** gzkit AST-based `scan_test_tree` correctly handles
   string expressions, nested decorators, and multi-line constructs that
   opsdev's `DECOR_RX`/`COMM_RX`/`RX_COVERS` regex chain misses
   (`adr_governance.py:28-34`).
3. **Coverage depth.** gzkit `compute_coverage()` produces three-level
   rollups (ADR / OBPI / REQ) consumed by `gz covers`, `gz adr covers-check`,
   and the OBPI Stage 3 Phase 1b parity gate. opsdev produces only flat
   ADR-to-test-path mapping.
4. **Evidence audit and central ledger integration.** gzkit
   `adr_audit_check()` inspects brief content sections via the central
   `Ledger` graph; opsdev `evidence_audit()` only checks `## Evidence`
   heading presence and writes a local sidecar JSONL.
5. **Autolink as doctrine choice, not capability gap.** opsdev's
   `write_into_adr()` and `adr_autolink(write=True)` inject Verification
   sections directly into ADR markdown via `<!-- VERIFICATION:BEGIN/END -->`
   markers. gzkit's OBPI-based governance model uses `@covers` decorators
   tracked through `gz adr audit-check` and the `gz-adr-autolink` manual
   workflow, with the skill body explicitly documenting *"there is no
   dedicated `gz adr` autolink subcommand in this repository"* (line 37). This
   is an intentional architectural choice, not absence.
6. **Cross-platform/convention compliance.** opsdev hardcodes `Path("tests")`
   and `docs_path("design", "adr")` and imports `airlineops.paths.subpaths`
   plus `opsdev.lib.ledger_schema` — both ops-internal. Adapting any of
   these to gzkit would require absorbing two further ops-internal modules
   (`airlineops.paths` and `opsdev/lib/ledger_schema.py`), neither in scope
   for this brief.

### Tracking the duplicate-evaluation signal

This brief is the second OBPI evaluating `lib/adr_governance.py` across two
parent ADRs. The duplicate-OBPI surface is itself a governance defect tracked
under **GHI #376** — the absorption sweep should not have authored two
parallel OBPIs for the same source artifact, and the proposed mechanical
guard `gz validate --absorption-duplicates` would have caught the drift at
brief authoring time. The Confirm-by-reference verdict here closes the
in-flight duplicate; the GHI carries the long-term tracking surface.

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing governance surface is sufficient — no new commands, flags,
output formats, or behavioral changes are introduced.

## Verification

Concrete, reproducible commands that verify this OBPI's acceptance criteria.
The REQ-01/REQ-04/REQ-05 patterns are OBPI-specific (they grep this brief for
decision text and Gate 4 rationale).

```bash
test -f ../airlineops/src/opsdev/lib/adr_governance.py
# Expected: opsdev source under review exists

test -f src/gzkit/ledger.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-04-adr-governance.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-04-adr-governance
# Expected: OBPI-scoped tests remain green (vacuous pass when no @covers tests
# target this OBPI — the `[doc]` REQ pattern routes to brief-content proof
# via _synthesize_doc_proof_linkage; covered by gz covers parity gate)

uv run -m unittest tests.test_adr_governance_confirm -v
# Expected: 4 tests pass — pre-existing canonical witness for OBPI-0.25.0-20
# Confirm decision on the same opsdev source module

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-04-adr-governance.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Decision rationale completed
- [ ] **Gate 4 (BDD):** Behavioral proof present or `N/A` recorded with rationale
- [ ] **Gate 5 (Human):** Attestation recorded

### Implementation Summary


- Decision: Confirm — gzkit's governance surface (`traceability.py` + `commands/covers.py` + `commands/adr_audit.py`, ~1010 lines) already covers and surpasses opsdev's `lib/adr_governance.py` (535 lines).
- Modules compared: opsdev `adr_governance.py` (3 internalized scripts: evidence_audit, adr_autolink, verification_report) vs gzkit triad (AST-based scanning, multi-level coverage rollups, brief-content evidence inspection, central ledger graph).
- Canonical precedent: OBPI-0.25.0-20-adr-governance-pattern (Completed 2026-04-11) recorded **Confirm** with five-point rationale and proof artifact `tests/test_adr_governance_confirm.py` (4 tests, all green).
- Per-subcommand mapping recorded in `## Comparison`: evidence_audit -> `gz adr audit-check` (gzkit-superior); adr_autolink -> `.gzkit/skills/gz-adr-autolink/SKILL.md` (gzkit-by-design doctrine choice); verification_report -> `gz covers` / `gz adr covers-check` (gzkit-superior).
- Source-material observation: brief Source Material header names `src/gzkit/ledger.py`; actual comparison surface is the gzkit `adr_audit.py` + `adr_coverage.py` + `covers.py` triad. Recorded in body, parent-ADR-authored header not amended.
- Duplicate-OBPI surface tracked under **GHI #376** — same source module evaluated twice across ADR-0.25.0/OBPI-20 and ADR-0.26.0/OBPI-04. Confirm-by-reference closes the in-flight duplicate; GHI carries long-term mechanical-guard tracking.
- No code absorbed; no `src/gzkit/` or `tests/` edits required.

### Key Proof


```bash
uv run -m unittest tests/test_adr_governance_confirm.py -v
# Ran 4 tests in 0.039s -- OK (pre-existing canonical witness for the Confirm decision, OBPI-0.25.0-20)
# ARB receipts (Stage 3): arb-ruff-b21f574537af4f239c6073d70479dcb7, arb-step-typecheck-5ce5e810debf43c5bef16d0e7bf2d303, arb-step-unittest-4637896a55774cc8805fc4bff4707f5a, arb-step-mkdocs-be9cfe8604484ab2b41f52558f2177c2
# REQ->@covers parity: uv run gz covers OBPI-0.26.0-04-adr-governance --json -> uncovered_reqs: 0 ([doc] REQs route via _synthesize_doc_proof_linkage)
```

## Human Attestation

- Attestor: `Jeffry Babb`
- Date: 2026-05-01
- Attestation: attest completed — Confirm-by-reference to OBPI-0.25.0-20-adr-governance-pattern (Completed 2026-04-11) on identical opsdev source `lib/adr_governance.py` (535 lines). Per-subcommand mapping recorded: evidence_audit → `gz adr audit-check` (gzkit-superior), adr_autolink → `.gzkit/skills/gz-adr-autolink/SKILL.md` (gzkit-by-design doctrine), verification_report → `gz covers` / `gz adr covers-check` (gzkit-superior). Six-point rationale anchored on parsing, coverage, evidence, convention, autolink-doctrine, ops-internal-imports. Duplicate-OBPI defect filed as GHI #376. ARB receipts: ruff arb-ruff-b21f574537af4f239c6073d70479dcb7, typecheck arb-step-typecheck-5ce5e810debf43c5bef16d0e7bf2d303, unittest arb-step-unittest-4637896a55774cc8805fc4bff4707f5a, mkdocs arb-step-mkdocs-be9cfe8604484ab2b41f52558f2177c2. Canonical proof artifact `tests/test_adr_governance_confirm.py` runs 4/4 green. Heavy-lane Gate 5; no code under `src/gzkit/` or `tests/` modified — Gate 4 N/A documented inline.

### Closing Argument

**Confirm.** opsdev's `lib/adr_governance.py` (535 lines) is a 2024-vintage
consolidation of three regex-based scripts: evidence_audit (ADR section
presence), adr_autolink (auto-rewrite of `## Verification` sections from
`@covers` decorators), and verification_report (covers-map JSONL emit).
gzkit's governance surface (`traceability.py` + `commands/covers.py` +
`commands/adr_audit.py`, ~1010 lines) already covers and surpasses all three
capabilities: AST-based scanning instead of regex, Pydantic models with
runtime REQ validation instead of stdlib dataclass, multi-level coverage
rollups (ADR/OBPI/REQ) instead of flat mapping, and brief content inspection
via the central ledger graph instead of section-presence checks. The
auto-writing feature is specific to opsdev's older workflow and intentionally
not used in gzkit's OBPI-based governance model — the
`.gzkit/skills/gz-adr-autolink/SKILL.md` skill explicitly documents the
manual workflow as canonical doctrine.

This brief is the second evaluation of `lib/adr_governance.py` across two
parent ADRs; the canonical precedent is OBPI-0.25.0-20-adr-governance-pattern
(attested 2026-04-11). Re-running the comparison with divergent rationale
on identical source material would itself be a doctrine-drift signal —
Confirm-by-reference is the structurally correct landing, with GHI #376
filed to track the duplicate-evaluation surface so the absorption sweep does
not silently recur.
