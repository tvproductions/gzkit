---
id: OBPI-0.26.0-10-cli-audit-lib
parent: ADR-0.26.0-governance-library-module-absorption
item: 10
status: Completed
lane: heavy
date: 2026-03-21
decision: Confirm
paired_with: OBPI-0.25.0-24-cli-audit-pattern
---

# OBPI-0.26.0-10: CLI Audit Library

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-10 — "Evaluate and absorb lib/cli_audit.py (238 lines) — CLI audit infrastructure and contract verification"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/cli_audit.py` (238 lines) and determine:
Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude
(domain-specific). The brief Source Material asserts the gzkit equivalent is
"Partial in `src/gzkit/cli.py`"; that wording is stale. gzkit's CLI audit
surface lives in `src/gzkit/commands/cli_audit.py` (235 L) plus the
`src/gzkit/doc_coverage/` package (1,065 L across six files), totaling
~1,300 L — already evaluated and decided **Confirm** under
**OBPI-0.25.0-24-cli-audit-pattern** (attested at ADR-0.25.0 closeout). The
comparison must determine whether gzkit's distributed CLI audit surface
produces audit evidence with the same — or greater — structural rigor than
opsdev's single-module library.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/cli_audit.py` (238 lines)
- **gzkit equivalent:** Body-level observation in `## Comparison`: parent-ADR
  Tidy First Plan table reads "Partial in `src/gzkit/cli.py`," but the actual
  gzkit CLI audit surface is `src/gzkit/commands/cli_audit.py` (235 L) plus
  the `src/gzkit/doc_coverage/` package (`__init__.py` 39 L,
  `flag_scanner.py` 182 L, `manifest.py` 85 L, `models.py` 93 L, `runner.py`
  128 L, `scanner.py` 538 L = 1,065 L) totaling ~1,300 L. This source artifact
  was already evaluated and decided **Confirm** under
  OBPI-0.25.0-24-cli-audit-pattern. Parent-ADR Cross-Reference Matrix row 10
  is intentionally not amended (mirror of OBPI-0.26.0-04/05/06/07/08/09
  pattern).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane. The brief frontmatter records a
doctrine choice (Confirm-by-reference to OBPI-0.25.0-24) that future agents
will treat as canonical, so Heavy scrutiny applies even though no code
changes under this brief.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- CLI audit infrastructure is domain-agnostic — any CLI framework benefits
  from contract verification
- ~~gzkit's cli.py likely mixes CLI audit logic with command handling rather
  than providing a reusable audit library~~ — **brief-scaffold defect**:
  gzkit's CLI audit lives in `commands/cli_audit.py` + `doc_coverage/`
  package (~1,300 L), NOT `cli.py`; the canonical OBPI-0.25.0-24 evaluated
  this exact source artifact and decided **Confirm** with a six-point
  rationale anchored on AST-based discovery, 5-surface coverage,
  manifest-driven obligations, Pydantic models, 76 vs 1 tests, and the
  subtraction test. Seventh structural instance of the same scaffold-defect
  class across ADR-0.26.0 briefs (also present in
  OBPI-04/05/06/07/08/09 wording); tracked under GHI #376.

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Modifying the existing `gz cli audit` command contract without Heavy lane
  approval
- Re-running the comparison work already attested under
  OBPI-0.25.0-24-cli-audit-pattern on identical source material — divergent
  rationale on identical material is itself a doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Confirm / Exclude.
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Confirm: document why gzkit's existing surface is superior.
6. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside the ADR-0.26.0 directory for a Confirm-by-reference
  outcome (the existing surface was already evaluated as superior under
  OBPI-0.25.0-24; this brief introduces no new code or tests)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — re-confirmed the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-09-adr-audit-ledger brief (Completed 2026-05-01) — most-recently-attested Confirm-by-reference precedent
- [x] OBPI-0.25.0-24-cli-audit-pattern brief (attested at ADR-0.25.0 closeout) — canonical precedent; recorded **Decision: Confirm** with six-point rationale (AST vs private API, 5-surface coverage, manifest obligations, Pydantic models, 76 vs 1 tests, subtraction test)
- [x] `src/gzkit/schemas/obpi.json` — required headers contract; ALL-CAPS heading drift corrected to title case
- [x] GHI #376 (open) — duplicate-OBPI tracking surface; this brief is the seventh structural instance of the same defect

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/cli_audit.py` (238 lines) — opsdev source under review
- [x] Required path exists: `src/gzkit/commands/cli_audit.py` (235 L; was 226 L at OBPI-0.25.0-24 authoring; +9 L, +4%)
- [x] Required path exists: `src/gzkit/doc_coverage/` package (1,065 L total across `__init__.py` 39 L + `flag_scanner.py` 182 L + `manifest.py` 85 L + `models.py` 93 L + `runner.py` 128 L + `scanner.py` 538 L; was ~802 L at OBPI-0.25.0-24 authoring; +263 L, +33%)
- [x] Required path exists: parent ADR file
- [x] Parent ADR Cross-Reference Matrix row for `cli_audit.py` reviewed: anticipates "Decide whether reusable CLI-audit logic should stay inline or move into a dedicated library"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/cli_audit.py` structure confirmed: 238 lines; `extract_all_arguments()` walks `parser._actions` (private argparse API) to extract argument metadata; `audit_parser()` recursively traverses subparsers via `argparse._SubParsersAction` (private API); `analyze_consistency()` checks naming conventions and cross-command option conflicts; data via `dict[str, Any]`; library-only module
- [x] `src/gzkit/commands/cli_audit.py` confirmed (235 L): `discover_commands()` AST-based static parsing; uses 7 frozen Pydantic `BaseModel` classes with `extra="forbid"`; first-class CLI verb (`gz cli audit`)
- [x] `src/gzkit/doc_coverage/` confirmed (1,065 L total): scanner package with 5-surface coverage model (manpage, index_entry, operator_runbook, governance_runbook, docstring); `flag_scanner.py` (182 L; post-OBPI-0.25.0-24 extension); manifest-driven obligations via `config/doc-coverage.json`; ~76 tests across 3 files
- [x] Duplicate-OBPI surface check: same source module `lib/cli_audit.py` evaluated under both ADR-0.25.0/OBPI-24 (Confirm) and ADR-0.26.0/OBPI-10 (this brief) — defect tracked under **GHI #376** (will be extended via seventh-instance comment in Stage 5 if operator authorizes)

## Quality Gates

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test --obpi OBPI-0.26.0-10-cli-audit-lib` (vacuous parity-gate pass on `[doc]` REQ pattern)
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — **N/A**, Confirm outcome

### Gate 3: Docs

- [x] Completed brief records a final `Confirm` decision (frontmatter + body)
- [x] Comparison rationale names concrete capability differences and the chosen outcome (six-dimension table from OBPI-0.25.0-24 precedent + seven-point Decision rationale + duplicate-OBPI tracking)

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior, the brief names `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [x] Otherwise the brief records `N/A` rationale for no external-surface change — see `### Gate 4 (BDD): N/A` in `## Decision`

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — recorded during Stage 4 ceremony of `gz-obpi-pipeline`

## Acceptance Criteria

- [x] REQ-0.26.0-10-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb`, `Confirm`, or `Exclude`. **Decision:
  Confirm** — see frontmatter and `## Decision` below.
- [x] REQ-0.26.0-10-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (six-dimension capability table) and
  `## Decision` (seven-point rationale anchored on OBPI-0.25.0-24 plus the
  doc_coverage 33% growth update).
- [x] REQ-0.26.0-10-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests. **N/A — Confirm outcome.**
- [x] REQ-0.26.0-10-04: [doc] Given a `Confirm` or `Exclude` outcome, then
  the brief explains why no upstream absorption is warranted. See `## Decision`
  — gzkit's distributed AST + 5-surface coverage surface is materially
  superior to opsdev's parser-tree introspection on six dimensions, and
  opsdev's private-API approach is structurally fragile.
- [x] REQ-0.26.0-10-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Confirm outcome with zero code changes
  under `src/gzkit/`, zero new CLI verbs, zero generated-surface change.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/cli_audit.py
# Expected: opsdev source under review exists

test -f src/gzkit/commands/cli_audit.py && test -d src/gzkit/doc_coverage
# Expected: gzkit existing CLI audit surface exists (Confirm precedent under OBPI-0.25.0-24)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
# Expected: brief frontmatter and Decision body record the Confirm verdict

rg -n 'OBPI-0.25.0-24' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
# Expected: brief cites the canonical precedent in body and Closing Argument

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-10-cli-audit-lib
# Expected: vacuous parity-gate pass on [doc] REQ pattern via _synthesize_doc_proof_linkage

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
# Expected: completed brief captures Gate 4 N/A rationale
```

## Comparison

### Source-material observation

The brief Source Material at parent-ADR Cross-Reference Matrix row 10 reads
"gzkit equivalent: Partial in `src/gzkit/cli.py`." That assertion is stale at
this brief's authoring time:

1. gzkit's CLI audit surface does NOT live primarily in `src/gzkit/cli.py`;
   it lives in `src/gzkit/commands/cli_audit.py` (235 L) plus the
   `src/gzkit/doc_coverage/` package (1,065 L across six files).
2. The same source artifact was already evaluated as **architecturally
   superior** to opsdev's `lib/cli_audit.py` under
   **OBPI-0.25.0-24-cli-audit-pattern** (attested at ADR-0.25.0 closeout).
3. Since the OBPI-0.25.0-24 attestation, the `doc_coverage/` package has
   grown 33% (~802 L → 1,065 L) with `flag_scanner.py` (182 L) added and
   `scanner.py` expanded.

| Surface | Lines | Role |
|---------|-------|------|
| `../airlineops/src/opsdev/lib/cli_audit.py` | 238 | opsdev module: parser tree introspection via `parser._actions` private API; `dict[str, Any]` data model; library-only |
| `src/gzkit/commands/cli_audit.py` | 235 | AST-based discovery (`discover_commands()`); 7 frozen Pydantic models; first-class CLI verb |
| `src/gzkit/doc_coverage/scanner.py` | 538 | 5-surface coverage scanning (manpage, index_entry, operator_runbook, governance_runbook, docstring) |
| `src/gzkit/doc_coverage/flag_scanner.py` | 182 | flag-level scanning (post-OBPI-0.25.0-24 extension) |
| `src/gzkit/doc_coverage/runner.py` | 128 | scan orchestration |
| `src/gzkit/doc_coverage/models.py` | 93 | Pydantic coverage models |
| `src/gzkit/doc_coverage/manifest.py` | 85 | manifest loading and validation |
| `src/gzkit/doc_coverage/__init__.py` | 39 | package surface |

This observation is body-level (Comparison section); the parent-ADR-authored
Cross-Reference Matrix row 10 is intentionally not amended.

### Per-dimension comparison (re-anchored from OBPI-0.25.0-24 precedent)

The dimension comparison established by OBPI-0.25.0-24-cli-audit-pattern
holds because the source artifact is identical (`lib/cli_audit.py`,
238 lines) and the gzkit surface preserves its AST-based discovery
architecture. Line anchors are refreshed; the surface-size dimension is
updated to reflect post-precedent growth.

| Dimension | opsdev `lib/cli_audit.py` (238 L) | gzkit equivalent (~1,300 L distributed) | Winner |
|-----------|------------------------------------|-----------------------------------------|--------|
| Discovery approach | `parser._actions` + `argparse._SubParsersAction` private API introspection | AST-based static parsing via `discover_commands()` — no import or execution required | gzkit (private-API fragility avoided) |
| Coverage model | Parser-tree structural checks (naming conventions, option conflicts) | 5-surface documentation coverage (manpage, index_entry, operator_runbook, governance_runbook, docstring) | gzkit (broader problem subsumes narrower one) |
| Extensibility | Hardcoded `ISSUE_CATEGORIES`; no manifest mechanism | `config/doc-coverage.json` declares per-command obligations with boolean toggles per surface | gzkit (declarative obligations) |
| Type discipline | `dict[str, Any]` throughout | 7 frozen Pydantic `BaseModel` classes with `extra="forbid"` | gzkit (validation, immutability, serialization contracts) |
| Test coverage | 1 test verifying JSON artifact files are written | 76 tests across 3 files covering AST discovery, all 5 surface checks, orphan detection, manifest loading/validation, gap reporting, integration | gzkit (76:1 ratio) |
| CLI integration | Library-only — no operator surface | First-class `gz cli audit` verb; integrates with `gz validate --documents` and the broader doc-coverage chore | gzkit |
| Cross-platform | Platform-portable (argparse stdlib) but private-API drift risk across Python versions | pathlib + AST stdlib + Pydantic; no private-API exposure | gzkit (maintainability) |

### Cross-platform / convention-compliance observations

opsdev `lib/cli_audit.py` carries three structural conflicts with gzkit
doctrine that absorb-by-copy could not eliminate:

1. **Private API drift.** `parser._actions` and `argparse._SubParsersAction`
   are undocumented and can change across Python versions without notice.
   gzkit's AST-based approach reads source files directly — Python-version-
   resistant.
2. **`dict[str, Any]` violates Pydantic policy.** gzkit's models are
   `frozen=True, extra="forbid"`; absorbing would require a full rewrite,
   defeating pattern absorption.
3. **No manifest extensibility.** gzkit's `config/doc-coverage.json`
   declares per-command obligations declaratively; absorbing opsdev's
   hardcoded `ISSUE_CATEGORIES` would replace the extension surface with a
   constant.

Per OBPI-0.25.0-24's analysis, these are not adapt-and-clean fixes — they
are structural mismatches that make the absorbed module strictly worse than
the existing distributed surface.

## Decision

**Confirm** (by reference to OBPI-0.25.0-24-cli-audit-pattern, attested at
ADR-0.25.0 closeout). gzkit's existing CLI audit surface (~1,300 L
distributed across `commands/cli_audit.py` + `doc_coverage/` package) is
architecturally a strict superset of opsdev's `lib/cli_audit.py` (238 L) on
seven named dimensions; absorbing the opsdev module would degrade
maintainability (private-API drift), violate Pydantic policy (untyped
dicts), and remove the manifest-driven extension mechanism. No absorption
is warranted.

### Brief-scaffold defect (surfaced)

The brief Source Material at parent-ADR Cross-Reference Matrix row 10 reads
"Partial in `src/gzkit/cli.py`," and the brief Assumptions block asserts
"gzkit's cli.py likely mixes CLI audit logic with command handling rather
than providing a reusable audit library." Both wordings are **stale and
misleading**:

- gzkit's CLI audit surface lives in `commands/cli_audit.py` (235 L) plus
  the `doc_coverage/` package (1,065 L), NOT in `cli.py`.
- OBPI-0.25.0-24 already evaluated this exact source artifact and decided
  **Confirm** with full six-point rationale.
- OBPI-0.26.0-04 / -07 / -08 / -09 (sibling briefs) carried analogous
  Source Material drift yet successfully landed `decision: Confirm`.

The Source Material wording is the seventh instance of this defect class
across ADR-0.26.0 briefs (also present in OBPI-04/05/06/07/08/09 wording).
Tracked structurally under GHI #376; doctrine here is that authoritative
precedent (OBPI-0.25.0-24) overrides stale brief Source Material.

### Rationale

1. **Strict superset of capability (canonical precedent).** OBPI-0.25.0-24
   evaluated the same opsdev source file (`lib/cli_audit.py`, 238 lines)
   and recorded **Decision: Confirm** with a six-point rationale. The gzkit
   surface covers every behavior the opsdev module provides — command
   discovery, argument extraction, structural checks — with strictly
   greater capability and structure (AST vs private API, 5-surface
   coverage vs parser-tree only, manifest obligations vs hardcoded
   categories, Pydantic vs dict, 76 vs 1 tests, ~1,300 L vs 238 L).

2. **AST-based vs private API introspection.** gzkit's `discover_commands()`
   uses static AST parsing to discover CLI commands without importing or
   executing the parser module. opsdev walks `parser._actions` and
   `argparse._SubParsersAction` — undocumented private APIs that can break
   across Python versions. gzkit's approach is safer and more maintainable.

3. **5-surface documentation coverage vs parser structural checks.** gzkit
   enforces 5 documentation surfaces per command (manpage, index_entry,
   operator_runbook, governance_runbook, docstring) via a manifest declaring
   50+ commands. opsdev checks parser tree structure only (naming
   conventions, option conflicts) — a narrower problem already subsumed by
   gzkit's broader coverage model.

4. **Manifest-driven obligations vs ad-hoc checks.** gzkit's
   `config/doc-coverage.json` declares per-command surface requirements
   with boolean toggles. opsdev has no equivalent — checks are hardcoded in
   `ISSUE_CATEGORIES` with no extensibility mechanism.

5. **Type-safe models vs untyped dicts.** gzkit uses 7 frozen Pydantic
   `BaseModel` classes with `extra="forbid"` for all coverage data. opsdev
   uses `dict[str, Any]` throughout — no validation, no immutability, no
   serialization contracts.

6. **76 tests vs 1 test.** gzkit's test suite covers AST discovery, all 5
   surface checks, orphan detection, manifest loading/validation, gap
   reporting, and integration scenarios. opsdev has a single test
   verifying that JSON artifact files are written.

7. **`doc_coverage/` 33% growth — Confirm holds *a fortiori*.** Since the
   OBPI-0.25.0-24 attestation, the `doc_coverage/` package has grown from
   ~802 L to 1,065 L (+263 L, +33%), adding `flag_scanner.py` (182 L) and
   expanding `scanner.py` to 538 L. The `commands/cli_audit.py` module
   grew modestly (226 L → 235 L, +4%). Total surface is now ~1,300 L vs
   ~1,028 L at the precedent attestation. The growth deepens coverage
   rigor (flag-level scanning, expanded scanner heuristics) without
   altering the architectural foundation. The Confirm verdict is therefore
   structurally stronger today than at the precedent attestation.

### Tracking the duplicate-evaluation signal

This brief is the seventh OBPI evaluating an opsdev `lib/` module across
two parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered:

| OBPI | Parent ADR | Source | Decision | Status |
|------|------------|--------|----------|--------|
| OBPI-0.25.0-20 | ADR-0.25.0 | `lib/adr_governance.py` | Confirm | attested 2026-04-11 |
| OBPI-0.26.0-04 | ADR-0.26.0 | (same) | Confirm-by-reference | attested |
| OBPI-0.25.0-29 | ADR-0.25.0 | `lib/ledger_schema.py` | Exclude | attested 2026-04-13 |
| OBPI-0.26.0-05 | ADR-0.26.0 | (same) | Exclude-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-26 | ADR-0.25.0 | `lib/drift_detection.py` | Absorb | attested 2026-04-09 |
| OBPI-0.26.0-06 | ADR-0.26.0 | (same) | Absorb-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-22 | ADR-0.25.0 | `lib/adr_traceability.py` | Confirm | attested 2026-04-09 |
| OBPI-0.26.0-07 | ADR-0.26.0 | (same) | Confirm-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-31 | ADR-0.25.0 | `lib/validation_receipt.py` | Confirm | attested 2026-04-13 |
| OBPI-0.26.0-08 | ADR-0.26.0 | (same) | Confirm-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-19 | ADR-0.25.0 | `lib/adr_audit_ledger.py` | Confirm | attested 2026-04-11 |
| OBPI-0.26.0-09 | ADR-0.26.0 | (same) | Confirm-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-24 | ADR-0.25.0 | `lib/cli_audit.py` | Confirm | attested at ADR-0.25.0 closeout |
| **OBPI-0.26.0-10** | **ADR-0.26.0** | **(same)** | **Confirm-by-reference** (this brief) | **in-flight** |

Same root cause as the prior six instances: ADR-0.26.0 authoring did not
check whether ADR-0.25.0's earlier absorption sweep had already covered
each module in scope. Same proposed mitigation: `gz validate
--absorption-duplicates` would catch this seventh instance alongside the
prior six.

Resolution: extend GHI #376 with this `lib/cli_audit.py` seventh instance
via `gh issue comment` rather than file a parallel GHI — pending operator
authorization.

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing CLI audit surface continues to function identically; no
new commands, flags, output formats, or behavioral changes are introduced.
`features/heavy_lane_gate4.feature` is not touched.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #10 captured verbatim.
- [x] **Gate 2 (TDD):** `uv run gz test --obpi OBPI-0.26.0-10-cli-audit-lib` remains green; vacuous pass on `[doc]` REQ pattern.
- [x] **Gate 3 (Docs):** Decision rationale completed with concrete capability deltas across seven dimensions.
- [x] **Gate 4 (BDD):** N/A — Confirm-by-reference outcome introduces no operator-visible behavior change.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony.

### Implementation Summary



- Decision: Confirm — by reference to OBPI-0.25.0-24-cli-audit-pattern. gzkit's distributed CLI audit surface (`commands/cli_audit.py` 235 L + `doc_coverage/` 1,065 L; ~1,300 L total) already constitutes an architecturally superior CLI audit surface to opsdev's `lib/cli_audit.py` (238 L) on all named dimensions.
- Modules compared: opsdev `cli_audit.py` (238 L; `parser._actions` + `argparse._SubParsersAction` private API introspection, `dict[str, Any]`, library-only, 1 test) vs gzkit distributed surface (`discover_commands()` AST-based static parsing, 7 frozen Pydantic `BaseModel` classes with `extra="forbid"`, 5-surface documentation coverage manifest, first-class CLI verb `gz cli audit`, 76 tests).
- Architectural superiority across seven dimensions: discovery approach (AST vs private API), coverage model (5-surface vs parser-tree), extensibility (manifest vs hardcoded), type discipline (Pydantic vs dict), test coverage (76:1), CLI integration (first-class vs library-only), cross-platform (portable AST vs private-API drift risk).
- New observation since OBPI-0.25.0-24: `doc_coverage/` package has grown 33% (~802 L → 1,065 L) with `flag_scanner.py` (182 L) added; `commands/cli_audit.py` grew 4% (226 L → 235 L). Confirm verdict structurally stronger today than at precedent attestation.
- Brief-scaffold-defect surfaced: brief Source Material asserts "Partial in `src/gzkit/cli.py`" but actual gzkit CLI audit surface is `commands/cli_audit.py` + `doc_coverage/` package (~1,300 L); the precedent OBPI-0.25.0-24 attests Confirm; OBPI-0.26.0-04/07/08/09 already established `decision: Confirm` is validator-accepted despite the assumption. Seventh instance of the same scaffold-defect class across ADR-0.26.0 briefs.
- Duplicate-OBPI surface tracked under **GHI #376** — seventh structural instance after OBPI-0.26.0-04/05/06/07/08/09. Resolution: extend GHI #376 with seventh-instance comment if operator authorizes; do not file parallel GHI.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings → title case; added missing `Lane`, `Denied Paths`, `Discovery Checklist` sections; status normalized `Pending` → `pending`; `Verification Commands (Concrete)` → `Verification` with two OBPI-specific verification commands.
- No code absorbed under this brief; no `src/gzkit/` or `tests/` edits — Confirm decided existing surface is superior; modifying it would invalidate the OBPI-0.25.0-24 attestation.

### Key Proof



```bash
rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
# Confirms brief frontmatter and ## Decision body record the Confirm verdict.

rg -c 'OBPI-0.25.0-24' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
# Expected: ≥10 — brief cites the canonical precedent across body, Decision rationale, Implementation Summary, Closing Argument.

test -f src/gzkit/commands/cli_audit.py && test -d src/gzkit/doc_coverage
# Expected: gzkit modules exist (Confirm precedent under OBPI-0.25.0-24 attests they are superior).

wc -l src/gzkit/commands/cli_audit.py src/gzkit/doc_coverage/*.py
# Expected: 235 + 1065 = 1,300 (vs ~1,028 at OBPI-0.25.0-24 authoring; +26% growth confirms Confirm a fortiori).

uv run gz covers OBPI-0.26.0-10-cli-audit-lib --json
# Expected: {"summary": {"total_reqs": 0, "uncovered_reqs": 0, ...}} — parity-gate pass for [doc] REQs.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): cited inline at Stage 4 ceremony after Stage 3 quality checks complete. REQ→@covers parity: `gz covers OBPI-0.26.0-10-cli-audit-lib --json` → `uncovered_reqs: 0` (vacuous parity-gate pass on `[doc]` REQs via `_synthesize_doc_proof_linkage`).

## Human Attestation

- Attestor: `Jeffry Babb`
- Date: 2026-05-02
- Attestation: attest completed — OBPI-0.26.0-10 Confirm-by-reference verdict on opsdev lib/cli_audit.py (238 L). Anchored on OBPI-0.25.0-24-cli-audit-pattern (Decision: Confirm with six-point rationale: AST vs private API, 5-surface coverage vs parser-tree, manifest obligations vs hardcoded, Pydantic vs dict, 76 vs 1 tests, subtraction test) and OBPI-0.26.0-04/07/08/09 sibling precedents for `decision: Confirm` despite stale brief Source Material asserting "Partial in src/gzkit/cli.py". Seven-dimension capability comparison authored in brief ## Comparison; seven-point rationale in ## Decision (rationale 7 records doc_coverage/ +33% growth: ~802 L → 1,065 L, with flag_scanner.py 182 L added and scanner.py expanded; commands/cli_audit.py +4% 226 L → 235 L; total surface ~1,300 L vs ~1,028 L at precedent — Confirm a fortiori). Brief-scaffold-defect surfaced (seventh instance across ADR-0.26.0); Gate 4 N/A (zero operator-visible change). Heavy-lane Stage 3 ARB receipts cited in Key Proof: lint arb-ruff-0d343eca2698454aba9eee34ada58981, typecheck arb-step-typecheck-0c11d93360b14dabb9314a604a0355d0, OBPI-scoped unittest arb-step-unittest-d18d9bc89b274da7aa349beec1110fa5, mkdocs arb-step-mkdocs-0c884bdf87134a2f83e7c17f82c11d9f. REQ→@covers parity: 5×[doc] REQs, uncovered_reqs:0 via _synthesize_doc_proof_linkage. No `src/` or `tests/` edits (Confirm preserves OBPI-0.25.0-24 attestation). GHI #376 seventh-instance comment deferred to explicit operator authorization.

### Closing Argument

**Confirm-by-reference.** opsdev's `lib/cli_audit.py` (238 lines) provides
parser-internal structural consistency checking via `parser._actions` and
`argparse._SubParsersAction` private APIs, with `dict[str, Any]` data
throughout, a single test, and library-only access. gzkit's existing CLI
audit surface — ~1,300 L distributed across `src/gzkit/commands/cli_audit.py`
(235 L; AST-based `discover_commands()`, 7 frozen Pydantic models, first-
class `gz cli audit` verb) and `src/gzkit/doc_coverage/` (1,065 L; 5-surface
coverage scanner, manifest-driven obligations via `config/doc-coverage.json`,
flag-level scanning, ~76 tests) — is architecturally a strict superset on
seven dimensions: discovery approach (AST vs private API), coverage model
(5-surface vs parser-tree), extensibility (manifest vs hardcoded), type
discipline (Pydantic vs dict), test coverage (76:1 ratio), CLI integration
(first-class vs library-only), and cross-platform maintainability (portable
AST vs private-API drift risk).

The opsdev module's `parser._actions` and `argparse._SubParsersAction`
introspection paths can break across Python versions without notice;
gzkit's AST-based approach reads source files directly and is Python-
version-resistant. The `dict[str, Any]` data model violates gzkit's
Pydantic policy (`frozen=True, extra="forbid"`); absorbing would require a
full rewrite that defeats the purpose of pattern absorption. The hardcoded
`ISSUE_CATEGORIES` mechanism has no extensibility surface; gzkit's
`config/doc-coverage.json` declares per-command obligations declaratively.
The post-OBPI-0.25.0-24 evolution of the `doc_coverage/` package (+33%
growth, +263 L) added `flag_scanner.py` and expanded `scanner.py` —
deepening coverage rigor on the same architectural foundation, making the
Confirm verdict structurally stronger today than at the precedent
attestation. Not absorbed.

This brief is the seventh evaluation of an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered.
The brief Source Material's "Partial in `src/gzkit/cli.py`" wording (and
the matching Assumption that "gzkit's cli.py likely mixes CLI audit logic
with command handling") is itself a brief-scaffold defect — gzkit's CLI
audit lives in `commands/cli_audit.py` + `doc_coverage/`, not `cli.py` —
and the precedent (OBPI-0.25.0-24 with Decision: Confirm) attests the
Confirm verdict on identical source. OBPI-0.26.0-04/07/08/09 already
established the precedent that `decision: Confirm` is validator-accepted
despite the brief assumption; this brief follows that precedent. GHI #376
to be extended (under operator authorization) with a seventh-occurrence
comment so the absorption sweep does not silently recur. No code under
`src/gzkit/` or `tests/` is modified by this brief; modifying the existing
surface would invalidate the OBPI-0.25.0-24 attestation. Gate 4 N/A: zero
operator-visible behavior change.
