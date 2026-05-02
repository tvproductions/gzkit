---
id: OBPI-0.26.0-11-artifacts-lib
parent: ADR-0.26.0-governance-library-module-absorption
item: 11
status: Completed
lane: heavy
date: 2026-03-21
decision: Exclude
paired_with: OBPI-0.25.0-23-artifact-management-pattern
---

# OBPI-0.26.0-11: Artifacts Library

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-11 — "Evaluate and absorb lib/artifacts.py (232 lines) — artifact management and sync primitives"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/artifacts.py` (232 lines) and determine:
Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude
(domain-specific). The brief Source Material asserts the gzkit equivalent is
"Partial in `src/gzkit/sync.py`"; that wording is incomplete. gzkit's
artifact-management surface lives in `src/gzkit/registry.py` (232 L; Pydantic
`ContentType` + `ContentTypeRegistry`) plus governance-artifact discovery
primitives in `src/gzkit/sync.py` (369 L; `scan_existing_artifacts`,
`parse_artifact_metadata`, `find_stale_mirror_paths`). The same opsdev source
artifact was already evaluated and decided **Exclude** under
**OBPI-0.25.0-23-artifact-management-pattern** (attested 2026-04-11) on
subtraction-test grounds. The comparison must determine whether gzkit's
post-precedent surface state preserves that verdict.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/artifacts.py` (232 lines)
- **gzkit equivalent:** Body-level observation in `## Comparison`: parent-ADR
  Tidy First Plan table reads "Partial in `src/gzkit/sync.py`," but the actual
  gzkit artifact-management surface is `src/gzkit/registry.py` (232 L) plus
  governance-artifact discovery utilities in `src/gzkit/sync.py` (369 L). This
  source artifact was already evaluated and decided **Exclude** under
  OBPI-0.25.0-23-artifact-management-pattern on the basis that the opsdev
  module is purely physical-file-management of an `artifacts/` directory
  convention with hardcoded preserved files — zero functional overlap with
  gzkit's governance content-type-metadata surface. Parent-ADR Cross-Reference
  Matrix row 11 is intentionally not amended (mirror of
  OBPI-0.26.0-04/05/06/07/08/09/10 pattern).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane. The brief frontmatter records a
doctrine choice (Exclude-by-reference to OBPI-0.25.0-23) that future agents
will treat as canonical, so Heavy scrutiny applies even though no code
changes under this brief.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Artifact management (discovery, cataloging, integrity) is a governance primitive that belongs in gzkit
- ~~gzkit's sync.py may handle artifact sync but may lack discovery and integrity verification depth~~ — **brief-scaffold defect**:
  the canonical OBPI-0.25.0-23 already evaluated this exact source artifact and
  decided **Exclude** with eight-dimension rationale; the opsdev module
  manages a physical `artifacts/` directory with hardcoded preserved files
  (`live_ingest_report.json`, `attestations/`) and uses regex-based
  source-code scanning — zero functional overlap with gzkit's governance
  content-type-metadata surface (`registry.py` + `sync.py` discovery). Eighth
  structural instance of the same scaffold-defect class across ADR-0.26.0
  briefs (also present in OBPI-04/05/06/07/08/09/10 wording); tracked
  structurally under GHI #376 (closed by `gz validate
  --absorption-duplicates` audit and `paired_with` waiver mechanism).

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing sync infrastructure — the goal is enriching artifact management capabilities
- Re-running the comparison work already attested under
  OBPI-0.25.0-23-artifact-management-pattern on identical source material —
  divergent rationale on identical material is itself a doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Confirm / Exclude.
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Confirm: document why gzkit's implementation is sufficient.
6. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside the ADR-0.26.0 directory for an Exclude-by-reference
  outcome (the existing surface was already evaluated under OBPI-0.25.0-23;
  this brief introduces no new code or tests)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — re-confirmed the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-10-cli-audit-lib brief (Completed 2026-05-02) — most-recently-attested by-reference precedent
- [x] Sibling OBPI-0.26.0-05-ledger-schema brief (Completed 2026-05-01) — most-recent Exclude-by-reference precedent (verdict-shape match)
- [x] OBPI-0.25.0-23-artifact-management-pattern brief (attested 2026-04-11) — canonical precedent; recorded **Decision: Exclude** with eight-dimension rationale anchored on the subtraction test (physical-file-management vs governance-content-type-metadata) plus convention violations (`@dataclass` vs Pydantic, `shutil.rmtree(ignore_errors=True)` vs cross-platform-safe cleanup)
- [x] `src/gzkit/schemas/obpi.json` — required headers contract; ALL-CAPS heading drift corrected to title case (sibling pattern)
- [x] GHI #376 (closed) — duplicate-OBPI tracking surface; mechanical guard `gz validate --absorption-duplicates` added (commit 2a21ebdc); `paired_with` waiver populated across all 12 ADR-0.26.0 briefs (commit cdd8e396)

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/artifacts.py` (232 lines; unchanged from precedent) — opsdev source under review
- [x] Required path exists: `src/gzkit/registry.py` (232 L; was 220 L at OBPI-0.25.0-23 authoring; +12 L, +5%)
- [x] Required path exists: `src/gzkit/sync.py` (369 L; governance artifact discovery surface — `scan_existing_artifacts` at line 217, `parse_artifact_metadata` at line 344, `find_stale_mirror_paths` re-export at line 85)
- [x] Required path exists: parent ADR file
- [x] Parent ADR Cross-Reference Matrix row for `artifacts.py` reviewed: anticipates "Decide whether artifact discovery/integrity belongs in a library rather than sync-only code"
- [x] Frontmatter `paired_with: OBPI-0.25.0-23-artifact-management-pattern` waiver present — consumed by `gz validate --absorption-duplicates`

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/artifacts.py` structure confirmed: 232 lines; `ART_RX = re.compile(r"artifacts[\\/]…")` and `QUOTED_SQLITE_RX` for source-code scanning; `class Hit` (`@dataclass`, file/line/kind/literal/call); `scan_artifacts_usage()` walks `.py` source files; `_classify_usage()` partitions hits as read/write/mkdir/other based on `open()`/`Path()`/`os.makedirs()`/`shutil.*` patterns; `generate_inventory_reports()` writes JSON + Markdown; `load_registry_allowed_buckets()` reads `config/artifacts_registry.json`; `clean_artifacts()` removes unrecognized directories from `artifacts/` with hardcoded preserved files (`.gitkeep`, `README.md`, `live_ingest_report.json`, `attestations/`); library-only module
- [x] `src/gzkit/registry.py` confirmed (232 L): `class ContentType(BaseModel)` (frontmatter validation, lifecycle, canonical path patterns); `class ContentTypeRegistry` (governance content-type metadata); `_translate_errors()` Pydantic-error mapping; `_bootstrap_registry()` for default content types; no source-code scanning, no physical directory cleanup, no JSON registry of artifact buckets
- [x] `src/gzkit/sync.py` confirmed (369 L): governance artifact discovery via `scan_existing_artifacts()` (rglob for `.md` files under design root) and `parse_artifact_metadata()` (frontmatter extraction); `find_stale_mirror_paths()` re-export from `sync_skill_validation`; no `artifacts/` directory management, no source-code regex scanning, no preserved-files allowlist
- [x] Duplicate-OBPI surface check: same source module `lib/artifacts.py` evaluated under both ADR-0.25.0/OBPI-23 (Exclude) and ADR-0.26.0/OBPI-11 (this brief) — defect tracked under **GHI #376** (closed); paired_with waiver populated; `gz validate --absorption-duplicates` audit consumes the waiver

## Quality Gates

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test --obpi OBPI-0.26.0-11-artifacts-lib` (vacuous parity-gate pass on `[doc]` REQ pattern)
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — **N/A**, Exclude outcome

### Gate 3: Docs

- [x] Completed brief records a final `Exclude` decision (frontmatter + body)
- [x] Comparison rationale names concrete capability differences and the chosen outcome (eight-dimension table from OBPI-0.25.0-23 precedent + six-point Decision rationale + duplicate-OBPI tracking)

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior, the brief names `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [x] Otherwise the brief records `N/A` rationale for no external-surface change — see `### Gate 4 (BDD): N/A` in `## Decision`

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — recorded during Stage 4 ceremony of `gz-obpi-pipeline`

## Acceptance Criteria

- [x] REQ-0.26.0-11-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb`, `Confirm`, or `Exclude`. **Decision:
  Exclude** — see frontmatter and `## Decision` below.
- [x] REQ-0.26.0-11-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (eight-dimension capability table) and
  `## Decision` (six-point rationale anchored on OBPI-0.25.0-23 plus the
  registry.py +5% / sync.py governance-discovery update).
- [x] REQ-0.26.0-11-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests. **N/A — Exclude outcome.**
- [x] REQ-0.26.0-11-04: [doc] Given a `Confirm` or `Exclude` outcome, then
  the brief explains why no upstream absorption is warranted. See `## Decision`
  — opsdev's `lib/artifacts.py` is pure physical-file-management of an
  airlineops-specific `artifacts/` directory convention with hardcoded
  preserved files; subtraction test fails completely; convention violations
  (`@dataclass`, `shutil.rmtree(ignore_errors=True)`) preclude clean
  absorption even if scope overlap existed.
- [x] REQ-0.26.0-11-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Exclude outcome with zero code changes
  under `src/gzkit/`, zero new CLI verbs, zero generated-surface change.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/artifacts.py
# Expected: opsdev source under review exists

test -f src/gzkit/registry.py && test -f src/gzkit/sync.py
# Expected: gzkit existing artifact-management surface exists (Exclude precedent under OBPI-0.25.0-23)

rg -n '^decision: Exclude|^\*\*Exclude\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
# Expected: brief frontmatter and Decision body record the Exclude verdict

rg -n 'OBPI-0.25.0-23' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
# Expected: brief cites the canonical precedent in body and Closing Argument

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-11-artifacts-lib
# Expected: vacuous parity-gate pass on [doc] REQ pattern via _synthesize_doc_proof_linkage

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Exclude: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
# Expected: completed brief captures Gate 4 N/A rationale

uv run gz validate --absorption-duplicates
# Expected: clean exit; paired_with waiver consumed for OBPI-0.26.0-11 ↔ OBPI-0.25.0-23 pair
```

## Comparison

### Source-material observation

The brief Source Material at parent-ADR Cross-Reference Matrix row 11 reads
"gzkit equivalent: Partial in `src/gzkit/sync.py`." That assertion is
incomplete at this brief's authoring time:

1. gzkit's artifact-management surface does NOT live primarily in
   `src/gzkit/sync.py`; the primary surface is `src/gzkit/registry.py`
   (232 L; Pydantic `ContentType` + `ContentTypeRegistry`) plus
   governance-artifact discovery primitives in `src/gzkit/sync.py`
   (369 L; `scan_existing_artifacts`, `parse_artifact_metadata`,
   `find_stale_mirror_paths`).
2. The same source artifact was already evaluated as **fundamentally
   different in problem domain** to opsdev's `lib/artifacts.py` under
   **OBPI-0.25.0-23-artifact-management-pattern** (attested 2026-04-11).
3. Since the OBPI-0.25.0-23 attestation, `src/gzkit/registry.py` has grown
   from ~220 L to 232 L (+12 L, +5%) on the same Pydantic foundation;
   `src/gzkit/sync.py` continues to host governance-artifact discovery
   without acquiring opsdev-style physical-directory management.

| Surface | Lines | Role |
|---------|-------|------|
| `../airlineops/src/opsdev/lib/artifacts.py` | 232 | opsdev module: regex source-scanning (`ART_RX`, `QUOTED_SQLITE_RX`), `@dataclass Hit` data model, usage classification (read/write/mkdir/other), JSON+Markdown inventory reports, JSON registry allowlist (`config/artifacts_registry.json`), physical `artifacts/` directory cleanup with hardcoded preserved files (`live_ingest_report.json`, `attestations/`); library-only |
| `src/gzkit/registry.py` | 232 | governance content-type metadata: `ContentType` Pydantic model (frontmatter, lifecycle, path patterns), `ContentTypeRegistry`, error translation, default-registry bootstrap |
| `src/gzkit/sync.py` | 369 | governance artifact discovery: `scan_existing_artifacts()` (rglob `.md` under design root), `parse_artifact_metadata()` (frontmatter extraction), `find_stale_mirror_paths()` (mirror-drift detection); no physical-directory cleanup, no source-code scanning |

This observation is body-level (Comparison section); the parent-ADR-authored
Cross-Reference Matrix row 11 is intentionally not amended.

### Per-dimension comparison (re-anchored from OBPI-0.25.0-23 precedent)

The dimension comparison established by OBPI-0.25.0-23-artifact-management-pattern
holds because the source artifact is identical (`lib/artifacts.py`,
232 lines) and the gzkit surface preserves its Pydantic `ContentType` +
governance-discovery architecture. Line anchors are refreshed; the
gzkit-surface dimension is updated to reflect post-precedent growth.

| Dimension | opsdev `lib/artifacts.py` (232 L) | gzkit equivalent (`registry.py` 232 L + `sync.py` 369 L = 601 L) | Assessment |
|-----------|------------------------------------|-----------------------------------------------------------------|------------|
| Purpose | Physical file management — scan code for `artifacts/` path refs, clean physical directories | Governance content-type metadata — Pydantic models, frontmatter validation, lifecycle states, governance-artifact discovery | Fundamentally different concerns |
| Scanning approach | Regex-based (`ART_RX = r"artifacts[\\/]…"`, `QUOTED_SQLITE_RX`) scanning of `.py` source files | `rglob("*.md")` scanning of governance markdown files via `scan_existing_artifacts()` | Different targets, different methods |
| Data model | `Hit` `@dataclass` with file/line/kind/literal/call | `ContentType` Pydantic `BaseModel` with name/schema/lifecycle/path pattern | No overlap; opsdev violates gzkit Pydantic policy |
| Classification | read/write/mkdir/other based on `open()` / `Path()` / `os.makedirs()` / `shutil.*` source patterns | N/A — gzkit doesn't classify file operations on source code | Airline-specific housekeeping primitive |
| Inventory reports | JSON + Markdown reports of artifact path usages (`generate_inventory_reports`) | N/A — gzkit has no source-code usage scanning use case | Domain-specific reporting |
| Registry/allowlist | JSON registry of allowed artifact buckets (`config/artifacts_registry.json`) consumed by `load_registry_allowed_buckets` | Content-type registry with Pydantic validation and vendor rendering rules | Different registry concepts entirely |
| Cleanup | `clean_artifacts()` removes unrecognized dirs from `artifacts/`; hardcoded preserves `.gitkeep`, `README.md`, `live_ingest_report.json`, `attestations/` | No physical directory cleanup; gzkit has stale-mirror detection via `find_stale_mirror_paths()` (re-exported in `sync.py`) | Hardcoded airline-specific preserved files |
| Convention compliance | `@dataclass`, `shutil.rmtree(ignore_errors=True)`, bare `print()` | Pydantic `BaseModel` (frozen models), context managers, structured errors via `_translate_errors` | opsdev violates `.claude/rules/models.md` and `.claude/rules/cross-platform.md` |

### Subtraction test

Removing gzkit from airlineops leaves: regex-based scanning of Python source
for `artifacts/` directory path references, usage classification by file
operation type, inventory report generation, JSON registry loading for
artifact bucket allowlists, and directory cleanup with hardcoded
airline-specific preserved files (`live_ingest_report.json`, `attestations/`).
Every capability is tied to airlineops's physical `artifacts/` directory
convention and its `config/artifacts_registry.json` structure. gzkit has no
`artifacts/` directory, no source-code scanning use case, and no
registry-based directory cleanup need. The subtraction result is pure
airlineops domain code.

### Cross-platform / convention-compliance observations

opsdev `lib/artifacts.py` carries three structural conflicts with gzkit
doctrine that absorb-by-copy could not eliminate:

1. **`@dataclass` violates Pydantic policy.** gzkit's models are
   `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` per
   `.claude/rules/models.md`; absorbing would require a full rewrite of
   `class Hit` and the data flow through it, defeating pattern absorption.
2. **`shutil.rmtree(ignore_errors=True)` violates cross-platform policy.**
   Per `.claude/rules/cross-platform.md` Quick Reference: avoid
   `ignore_errors=True` in cleanup; use context managers. The `clean_artifacts()`
   path swallows Windows-side errors silently.
3. **No problem to solve.** gzkit has no `artifacts/` directory, no
   source-code-scanning use case, and no JSON-registry-driven directory
   cleanup obligation. Even with conventions adapted, the absorbed code
   would have no caller in gzkit.

Per OBPI-0.25.0-23's analysis, these are not adapt-and-clean fixes — they
are decisive evidence that the module's problem domain is airlineops-only.

## Decision

**Exclude** (by reference to OBPI-0.25.0-23-artifact-management-pattern,
attested 2026-04-11). opsdev's `lib/artifacts.py` (232 L) is pure
physical-file-management of an airlineops-specific `artifacts/` directory
convention with hardcoded preserved files; gzkit's artifact-management
surface (`registry.py` 232 L + `sync.py` 369 L) solves the fundamentally
different problem of governance content-type metadata and governance-artifact
discovery. Zero functional overlap; subtraction test fails completely;
convention violations (`@dataclass`, `shutil.rmtree(ignore_errors=True)`)
preclude clean absorption even if scope overlap existed. No absorption is
warranted.

### Brief-scaffold defect (surfaced)

The brief Source Material at parent-ADR Cross-Reference Matrix row 11 reads
"Partial in `src/gzkit/sync.py`," and the brief Assumptions block asserts
"gzkit's sync.py may handle artifact sync but may lack discovery and
integrity verification depth." Both wordings are **incomplete and
misleading**:

- gzkit's artifact-management surface lives in `registry.py` (232 L; the
  primary Pydantic `ContentType` surface) plus `sync.py` (369 L; governance
  artifact discovery), NOT in `sync.py` alone.
- OBPI-0.25.0-23 already evaluated this exact source artifact and decided
  **Exclude** with full eight-dimension rationale.
- OBPI-0.26.0-04 / -05 / -06 / -07 / -08 / -09 / -10 (sibling briefs)
  carried analogous Source Material drift yet successfully landed
  `decision: Confirm` or `decision: Exclude` by-reference outcomes.

The Source Material wording is the eighth instance of this defect class
across ADR-0.26.0 briefs (also present in OBPI-04/05/06/07/08/09/10
wording). Tracked structurally under GHI #376 (closed); mechanical guard
`gz validate --absorption-duplicates` consumes the `paired_with` frontmatter
waiver populated under commit cdd8e396. Doctrine here is that authoritative
precedent (OBPI-0.25.0-23) overrides incomplete brief Source Material.

### Rationale

1. **Zero functional overlap (canonical precedent).** OBPI-0.25.0-23
   evaluated the same opsdev source file (`lib/artifacts.py`, 232 lines)
   and recorded **Decision: Exclude** with an eight-dimension rationale.
   The opsdev module's two capabilities are (a) regex-based scanning of
   Python source files for `artifacts/` path references with usage
   classification, and (b) directory cleanup driven by a JSON registry of
   allowed buckets. Neither has any caller, use case, or analog in gzkit.

2. **Physical-file-management vs governance-content-type-metadata —
   fundamentally different problems.** opsdev manages a physical
   `artifacts/` directory tree with hardcoded preserved files; gzkit
   manages governance document types in a `docs/design/` + `.gzkit/`
   hierarchy via Pydantic `ContentType` models. The two surfaces share
   neither inputs, outputs, control flow, nor failure modes.

3. **Airline-specific `artifacts/` directory convention with hardcoded
   preserved files.** `clean_artifacts()` hardcodes `live_ingest_report.json`
   and `attestations/` as preserved paths — domain-specific airlineops
   semantics. Absorbing the function would require either inheriting the
   airlineops constants (rejected by the subtraction test) or
   parameterizing them away (which leaves a thin shell over `pathlib` +
   `shutil` that gzkit does not need).

4. **Convention violations preclude clean absorption.** `class Hit` is a
   `@dataclass` (gzkit policy: Pydantic `BaseModel` with
   `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`).
   `clean_artifacts()` calls `shutil.rmtree(path, ignore_errors=True)`
   (gzkit cross-platform policy explicitly avoids `ignore_errors=True`
   per `.claude/rules/cross-platform.md`). Adapting both would require
   rewriting from scratch — defeating the absorb-rather-than-reinvent
   guideline.

5. **gzkit registry.py + sync.py post-precedent state preserves the
   Exclude verdict *a fortiori*.** Since the OBPI-0.25.0-23 attestation,
   `src/gzkit/registry.py` has grown from ~220 L to 232 L (+12 L, +5%)
   on the same Pydantic `ContentType` + `ContentTypeRegistry` foundation
   — deepening governance content-type metadata without acquiring any
   opsdev-style physical-directory or source-code-scanning semantics.
   `src/gzkit/sync.py` (369 L) continues to host governance-artifact
   discovery (`scan_existing_artifacts`, `parse_artifact_metadata`,
   `find_stale_mirror_paths`) for `.md` files under the design root —
   not physical artifact management. The growth deepens the governance
   surface on the same architectural foundation; the Exclude verdict is
   structurally stronger today than at the precedent attestation.

6. **Subtraction test re-stated.** `opsdev.lib.artifacts - gzkit = pure
   ops domain` (regex source-scanning + airline-specific directory
   cleanup with hardcoded preserved files). The test is decisive: every
   capability in the opsdev module is tied to airlineops's `artifacts/`
   directory convention and its `config/artifacts_registry.json` structure.
   gzkit has none of these surfaces. Exclude.

### Tracking the duplicate-evaluation signal

This brief is the eighth OBPI evaluating an opsdev `lib/` module across
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
| OBPI-0.26.0-10 | ADR-0.26.0 | (same) | Confirm-by-reference | attested 2026-05-02 |
| OBPI-0.25.0-23 | ADR-0.25.0 | `lib/artifacts.py` | Exclude | attested 2026-04-11 |
| **OBPI-0.26.0-11** | **ADR-0.26.0** | **(same)** | **Exclude-by-reference** (this brief) | **in-flight** |

Same root cause as the prior seven instances: ADR-0.26.0 authoring did not
check whether ADR-0.25.0's earlier absorption sweep had already covered
each module in scope. Mechanical resolution already landed under GHI #376:
`gz validate --absorption-duplicates` (commit 2a21ebdc) consumes the
`paired_with` frontmatter waiver populated across all 12 briefs (commit
cdd8e396).

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Exclude decision validates that
gzkit's existing artifact-management surface continues to function
identically; no new commands, flags, output formats, or behavioral changes
are introduced. `features/heavy_lane_gate4.feature` is not touched.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #11 captured verbatim.
- [x] **Gate 2 (TDD):** `uv run gz test --obpi OBPI-0.26.0-11-artifacts-lib` remains green; vacuous pass on `[doc]` REQ pattern.
- [x] **Gate 3 (Docs):** Decision rationale completed with concrete capability deltas across eight dimensions.
- [x] **Gate 4 (BDD):** N/A — Exclude-by-reference outcome introduces no operator-visible behavior change.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony.

### Implementation Summary


- Decision: Exclude — by reference to OBPI-0.25.0-23-artifact-management-pattern. opsdev's `lib/artifacts.py` (232 L; regex source-scanning + airline-specific physical-directory cleanup with hardcoded preserved files `live_ingest_report.json` / `attestations/`) has zero functional overlap with gzkit's artifact-management surface (`registry.py` 232 L Pydantic `ContentType` + `ContentTypeRegistry`; `sync.py` 369 L governance-artifact discovery via `scan_existing_artifacts` / `parse_artifact_metadata`).
- Modules compared: opsdev `artifacts.py` (232 L; `ART_RX` + `QUOTED_SQLITE_RX` regex source-scanning, `@dataclass Hit`, usage classification by `open()`/`Path()`/`os.makedirs()`/`shutil.*` patterns, JSON+Markdown inventory reports, `config/artifacts_registry.json` allowlist, `clean_artifacts()` with hardcoded preserves, library-only) vs gzkit distributed surface (`registry.py` Pydantic `ContentType` model + `ContentTypeRegistry`; `sync.py` governance-markdown rglob discovery, frontmatter extraction, mirror-drift detection).
- Eight-dimension capability separation: purpose (physical-file-management vs governance-content-type-metadata), scanning approach (regex source files vs rglob `.md`), data model (`@dataclass` vs Pydantic), classification (file-op-typed source hits vs N/A), inventory reports (JSON+MD vs N/A), registry/allowlist (artifact-bucket JSON vs content-type Pydantic), cleanup (hardcoded preserves vs `find_stale_mirror_paths`), convention compliance (`@dataclass` + `shutil.rmtree(ignore_errors=True)` vs Pydantic + structured errors).
- New observations since OBPI-0.25.0-23: `src/gzkit/registry.py` grew 220 L → 232 L (+12 L, +5%) on the same Pydantic foundation; opsdev source unchanged at 232 L; `src/gzkit/sync.py` continues to host governance-artifact discovery without acquiring opsdev-style physical-directory management. Exclude verdict structurally stronger today than at precedent attestation.
- Subtraction test decisive: removing gzkit from airlineops leaves regex source-scanning + airline-specific directory cleanup tied to the `artifacts/` convention and `config/artifacts_registry.json` — zero residue of governance primitive.
- Convention violations preclude clean absorption even if scope overlap existed: `@dataclass` violates `.claude/rules/models.md` (Pydantic `BaseModel` policy); `shutil.rmtree(path, ignore_errors=True)` violates `.claude/rules/cross-platform.md` (cleanup must use context managers and propagate Windows errors).
- Brief-scaffold-defect surfaced: brief Source Material asserts "Partial in `src/gzkit/sync.py`" but the actual gzkit artifact-management surface is `registry.py` + `sync.py` discovery primitives (601 L combined); the precedent OBPI-0.25.0-23 attests Exclude; OBPI-0.26.0-04 through -10 already established by-reference outcomes are validator-accepted despite stale Source Material wording. Eighth structural instance of the same scaffold-defect class across ADR-0.26.0 briefs.
- Duplicate-OBPI surface tracked under **GHI #376** (closed) — eighth structural instance after OBPI-0.26.0-04 through -10. Mechanical resolution already landed: `gz validate --absorption-duplicates` (commit 2a21ebdc) consumes the `paired_with: OBPI-0.25.0-23-artifact-management-pattern` frontmatter waiver populated under commit cdd8e396.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings → title case; added missing `## Lane`, `## Denied Paths`, `## Discovery Checklist`, `## Comparison`, `## Decision` sections; `Verification Commands (Concrete)` → `Verification` with two OBPI-specific verification commands; added `### Implementation Summary`, `### Key Proof`, `### Closing Argument` H3 evidence sections per `.claude/rules/brief-heading-conventions.md`.
- No code absorbed under this brief; no `src/gzkit/` or `tests/` edits — Exclude decided existing surface solves a different problem; modifying it would invalidate the OBPI-0.25.0-23 attestation.

### Key Proof


```bash
rg -n '^decision: Exclude|^\*\*Exclude\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
# Confirms brief frontmatter and ## Decision body record the Exclude verdict.

rg -c 'OBPI-0.25.0-23' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
# Expected: ≥10 — brief cites the canonical precedent across body, Decision rationale, Implementation Summary, Closing Argument.

test -f src/gzkit/registry.py && test -f src/gzkit/sync.py && test -f ../airlineops/src/opsdev/lib/artifacts.py
# Expected: all three surfaces present (Exclude precedent under OBPI-0.25.0-23 attests they solve fundamentally different problems).

wc -l ../airlineops/src/opsdev/lib/artifacts.py src/gzkit/registry.py src/gzkit/sync.py
# Expected: 232 + 232 + 369 = 833 L. opsdev unchanged (232 L), gzkit registry.py grew 220 L → 232 L (+5%) since OBPI-0.25.0-23 — Exclude a fortiori.

uv run gz covers OBPI-0.26.0-11-artifacts-lib --json
# Expected: {"summary": {"total_reqs": 0, "uncovered_reqs": 0, ...}} — parity-gate pass for [doc] REQs via _synthesize_doc_proof_linkage.

uv run gz validate --absorption-duplicates
# Expected: clean exit; paired_with: OBPI-0.25.0-23-artifact-management-pattern waiver consumed.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): cited inline at Stage 4 ceremony after Stage 3 quality checks complete. REQ→@covers parity: `gz covers OBPI-0.26.0-11-artifacts-lib --json` → `uncovered_reqs: 0` (vacuous parity-gate pass on `[doc]` REQs via `_synthesize_doc_proof_linkage`).

## Human Attestation

- Attestor: `g0`
- Date: 2026-05-02
- Attestation: attest completed — OBPI-0.26.0-11 Exclude-by-reference verdict on opsdev lib/artifacts.py (232 L). Anchored on OBPI-0.25.0-23-artifact-management-pattern (Decision: Exclude attested 2026-04-11) with eight-dimension subtraction-test rationale: physical-file-management vs governance-content-type-metadata, fundamentally different problems with zero functional overlap. opsdev module is purely airlineops-specific artifacts/ directory convention with hardcoded preserved files (live_ingest_report.json, attestations/) plus regex-based source-code scanning (ART_RX, QUOTED_SQLITE_RX) — gzkit has none of these surfaces. Convention violations preclude clean absorption: @dataclass Hit violates .claude/rules/models.md Pydantic policy; shutil.rmtree(ignore_errors=True) violates .claude/rules/cross-platform.md. Post-precedent surface state preserves verdict a fortiori: gzkit registry.py grew 220 L → 232 L (+5%) on same Pydantic ContentType foundation; opsdev unchanged at 232 L. Eighth structural instance of ADR-0.26.0 ↔ ADR-0.25.0 duplicate-OBPI pattern (after -04/-05/-06/-07/-08/-09/-10), mechanically suppressed by closed GHI #376 guard chain (gz validate --absorption-duplicates + paired_with frontmatter waiver populated under cdd8e396). Heavy-lane Stage 3 ARB receipts cited in Key Proof: lint arb-ruff-d3d211e5b52c40bb9adb28469fddb46e, typecheck arb-step-typecheck-f11444be558a4558979d1df46280076f, full unittest arb-step-unittest-d09a2e732fc8427e84917cf2ed0e69e6, OBPI-scoped unittest arb-step-unittest-ae0825d9d70544b696cc8e06bf91b13c, mkdocs arb-step-mkdocs-20128a74e0fd4f4ebeffbd758c6814ef. REQ→@covers parity: 5×[doc] REQs, uncovered_reqs:0 via _synthesize_doc_proof_linkage. gz validate --absorption-duplicates / --brief-headings clean. No src/ or tests/ edits (Exclude preserves OBPI-0.25.0-23 attestation). Gate 4 N/A (zero operator-visible change).

### Closing Argument

**Exclude-by-reference.** opsdev's `lib/artifacts.py` (232 L) provides two
capabilities tightly bound to airlineops's physical `artifacts/` directory
convention: (1) regex-based scanning of `.py` source files for `artifacts/`
path references and `.sqlite` literals via `ART_RX` and `QUOTED_SQLITE_RX`,
with usage classification as read/write/mkdir/other based on context-aware
matching of `open()`, `Path()`, `os.makedirs()`, and `shutil.*` patterns;
and (2) physical-directory cleanup via `clean_artifacts()` driven by a JSON
allowlist (`config/artifacts_registry.json`) with hardcoded preserved files
(`.gitkeep`, `README.md`, `live_ingest_report.json`, `attestations/`).
gzkit's existing artifact-management surface — 601 L distributed across
`src/gzkit/registry.py` (232 L; Pydantic `ContentType` + `ContentTypeRegistry`
for governance content-type metadata, frontmatter validation, lifecycle
states, canonical path patterns) and `src/gzkit/sync.py` (369 L; governance-
artifact discovery via `scan_existing_artifacts()` rglob over `.md` files,
`parse_artifact_metadata()` frontmatter extraction, `find_stale_mirror_paths()`
mirror-drift detection) — solves the fundamentally different problem of
governance content-type metadata and governance-document discovery. The two
surfaces share neither inputs (Python source files vs governance markdown),
outputs (JSON+MD inventory reports vs Pydantic-validated content-type
records), control flow (regex source-scanning vs rglob+frontmatter parsing),
nor failure modes (silent `shutil.rmtree` vs structured error translation).
Zero functional overlap.

The opsdev module's `@dataclass Hit` data model violates gzkit's Pydantic
policy (`.claude/rules/models.md` requires `BaseModel` with
`ConfigDict(frozen=True, extra="forbid")`); the `shutil.rmtree(path,
ignore_errors=True)` cleanup path violates gzkit's cross-platform policy
(`.claude/rules/cross-platform.md` Quick Reference: avoid `ignore_errors=True`
in cleanup; use context managers). Even if the absorption subtraction test
were not decisive, these two convention conflicts would force a full rewrite
that defeats the absorb-rather-than-reinvent guideline. The post-OBPI-0.25.0-23
evolution of `src/gzkit/registry.py` (+12 L, +5%) deepens governance
content-type metadata on the same Pydantic foundation without acquiring any
opsdev-style physical-directory or source-code-scanning semantics — the
Exclude verdict is structurally stronger today than at the precedent
attestation. Not absorbed.

This brief is the eighth evaluation of an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered.
The brief Source Material's "Partial in `src/gzkit/sync.py`" wording (and
the matching Assumption that "gzkit's sync.py may handle artifact sync but
may lack discovery and integrity verification depth") is itself a
brief-scaffold defect — gzkit's primary artifact-management surface is
`registry.py`'s Pydantic content-type registry plus `sync.py`'s governance-
artifact discovery, not `sync.py` alone — and the precedent (OBPI-0.25.0-23
with Decision: Exclude) attests the Exclude verdict on identical source.
OBPI-0.26.0-04 through -10 (seven prior siblings) already established the
precedent that `decision: Exclude` and `decision: Confirm` by-reference
outcomes are validator-accepted despite incomplete brief Source Material;
this brief follows that precedent. GHI #376 is closed; the mechanical
guard `gz validate --absorption-duplicates` consumes the `paired_with`
frontmatter waiver populated across all 12 ADR-0.26.0 briefs (commits
cdd8e396 + 2a21ebdc), so the absorption sweep does not silently recur.
No code under `src/gzkit/` or `tests/` is modified by this brief; modifying
the existing surface would invalidate the OBPI-0.25.0-23 attestation.
Gate 4 N/A: zero operator-visible behavior change.
