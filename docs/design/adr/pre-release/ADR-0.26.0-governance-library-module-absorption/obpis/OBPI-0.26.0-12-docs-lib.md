---
id: OBPI-0.26.0-12-docs-lib
parent: ADR-0.26.0-governance-library-module-absorption
item: 12
status: Completed
lane: heavy
date: 2026-03-21
decision: Confirm
paired_with: OBPI-0.25.0-25-docs-validation-pattern
---

# OBPI-0.26.0-12: Documentation Library

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-12 — "Evaluate and absorb lib/docs.py (218 lines) — documentation generation and validation"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/docs.py` (218 lines) and determine:
Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude
(domain-specific). The brief Source Material asserts the gzkit equivalent
is "None"; that wording is incomplete. gzkit's documentation-validation
surface lives in `src/gzkit/doc_coverage/` (~802 L across `scanner.py`
496 L, `models.py` 93 L, `manifest.py` 85 L, `runner.py` 128 L) plus
`mkdocs build --strict` integration via `gz validate --documents` and
the canonical `arb-step-mkdocs-*` ARB receipt slot. The same opsdev source
artifact was already evaluated and decided **Confirm** under
**OBPI-0.25.0-25-docs-validation-pattern** (attested 2026-04-12) on
subtraction-test grounds. The comparison must determine whether gzkit's
post-precedent surface state preserves that verdict.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/docs.py` (218 lines)
- **gzkit equivalent:** Body-level observation in `## Comparison`: parent-ADR
  Tidy First Plan table reads "gzkit equivalent: None," but the actual
  gzkit documentation-validation surface is `src/gzkit/doc_coverage/`
  (~802 L across 4 modules) plus `mkdocs build --strict` integration. This
  source artifact was already evaluated and decided **Confirm** under
  OBPI-0.25.0-25-docs-validation-pattern on the basis that gzkit's existing
  AST-driven CLI-to-documentation coverage validator + mkdocs strict builds
  cover every functional need that opsdev `docs.py` addresses, with the
  only non-trivial opsdev capability (regex-based link validation +
  2-click orphan walk) being mkdocs-redundant. Parent-ADR Cross-Reference
  Matrix row 12 is intentionally not amended (mirror of
  OBPI-0.26.0-04/05/06/07/08/09/10/11 pattern).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane. The brief frontmatter records
a doctrine choice (Confirm-by-reference to OBPI-0.25.0-25) that future
agents will treat as canonical, so Heavy scrutiny applies even though no
code changes under this brief.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Documentation generation and validation is a governance primitive that
  aligns with gzkit's documentation-as-first-class-deliverable principle
- ~~No existing gzkit equivalent means either Absorb or Exclude — there is
  no Confirm path~~ — **brief-scaffold defect**: the canonical
  OBPI-0.25.0-25 already evaluated this exact source artifact and decided
  **Confirm** with eleven-dimension rationale; gzkit's documentation
  surface is `src/gzkit/doc_coverage/` (~802 L) plus `mkdocs build --strict`
  integration, and the opsdev module's only non-trivial capability is
  mkdocs-redundant. Ninth structural instance of the same scaffold-defect
  class across ADR-0.26.0 briefs (also present in
  OBPI-04/05/06/07/08/09/10/11 wording); tracked structurally under
  GHI #376 (closed by `gz validate --absorption-duplicates` audit and
  `paired_with` waiver mechanism).

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a general-purpose documentation framework — focus on governance documentation
- Re-running the comparison work already attested under
  OBPI-0.25.0-25-docs-validation-pattern on identical source material —
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

- Any path outside the ADR-0.26.0 directory for a Confirm-by-reference
  outcome (the existing surface was already evaluated under OBPI-0.25.0-25;
  this brief introduces no new code or tests)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — re-confirmed the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-11-artifacts-lib brief (Completed 2026-05-02) — most-recently-attested by-reference precedent
- [x] Sibling OBPI-0.26.0-04 / -05 / -06 / -07 / -08 / -09 / -10 briefs (all Completed) — eight prior by-reference precedents establishing the doctrinal pattern
- [x] OBPI-0.25.0-25-docs-validation-pattern brief (attested 2026-04-12) — canonical precedent; recorded **Decision: Confirm** with eleven-dimension rationale anchored on the subtraction test (different problem scopes; link validation mkdocs-redundant; manifest-driven obligations vs hardcoded checks; type-safe models vs untyped primitives; 87 vs 0 tests; opsdev's self-declared "ultra-minimal Docs gate during 0.0.0 → 1.0.0 remodel" temporary status)
- [x] `src/gzkit/schemas/obpi.json` — required headers contract; ALL-CAPS heading drift corrected to title case (sibling pattern)
- [x] GHI #376 (closed) — duplicate-OBPI tracking surface; mechanical guard `gz validate --absorption-duplicates` added (commit 2a21ebdc); `paired_with` waiver populated across all 12 ADR-0.26.0 briefs (commit cdd8e396)

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/docs.py` (218 lines; unchanged from precedent) — opsdev source under review
- [x] Required path exists: `src/gzkit/doc_coverage/scanner.py` (496 L) — AST-driven `discover_commands` with 5-surface per-command coverage check
- [x] Required path exists: `src/gzkit/doc_coverage/models.py` (93 L) — 7 frozen Pydantic models with `ConfigDict(frozen=True, extra="forbid")`
- [x] Required path exists: `src/gzkit/doc_coverage/manifest.py` (85 L) — per-command `SurfaceRequirements` loaded from `config/doc-coverage.json`
- [x] Required path exists: `src/gzkit/doc_coverage/runner.py` (128 L) — gap-report builder with human-readable and JSON output modes
- [x] Required path exists: parent ADR file
- [x] Parent ADR Cross-Reference Matrix row for `docs.py` reviewed: anticipates "Decide whether governance-document generation and validation should remain ad hoc rather than becoming an explicit upstream library capability"
- [x] Frontmatter `paired_with: OBPI-0.25.0-25-docs-validation-pattern` waiver present — consumed by `gz validate --absorption-duplicates`

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/docs.py` structure confirmed: 218 lines; module docstring self-declares "ultra-minimal Docs gate during 0.0.0 → 1.0.0 remodel" with TODO list to restore deep checks; `check_files()` (existence check for `docs/index.md` only); `check_nav()` / `check_links()` (no-op stubs); `build_site_strict()` (subprocess wrapper around `python -m mkdocs build --clean --strict`); `_is_external()` / `_normalize()` (URL/path helpers); `collect_markdown()` (`rglob("*.md")` under docs root); `parse_links()` (regex `r"\[[^\]]+\]\(([^)]+)\)"` with forced UTF-8 decode); `build_graph()` (outgoing-edge graph of markdown files); `find_orphans()` (2-click reachability walk from `docs/index.md`); `validate_links()` (returns `(missing_links, orphaned_pages)`); `docs_link_lint()` (orchestrator); `fail()`/`ok()` (stderr/stdout helpers coupled to `sys.exit()`); plain `dict`/`set`/`list`/`tuple` primitives throughout; no Pydantic, no typed models, no validation
- [x] `src/gzkit/doc_coverage/scanner.py` confirmed (496 L): AST-driven `discover_commands()` — static parsing of `_build_parser` and `register_*_parsers` without importing; 5-surface check per command (manpage, index_entry, operator_runbook, governance_runbook, docstring); handler docstring resolution via import map; `find_orphaned_docs()` for manpages with no matching command; manifest exemption application
- [x] `src/gzkit/doc_coverage/models.py` confirmed (93 L): 7 frozen Pydantic models (`SurfaceResult`, `CommandCoverage`, `OrphanedDoc`, `CoverageReport`, `GapItem`, `OrphanedDocItem`, `DocCoverageGapReport`) with `ConfigDict(frozen=True, extra="forbid")`
- [x] `src/gzkit/doc_coverage/manifest.py` confirmed (85 L): `DocCoverageManifest` with per-command `SurfaceRequirements`; `load_manifest()` reads `config/doc-coverage.json`; `find_undeclared_commands()` detects AST-discovered commands absent from the manifest
- [x] `src/gzkit/doc_coverage/runner.py` confirmed (128 L): manifest-aware gap report builder (`build_gap_report()`); `run_doc_coverage()` entry point with human-readable and JSON output modes; filters coverage results against declared obligations
- [x] Duplicate-OBPI surface check: same source module `lib/docs.py` evaluated under both ADR-0.25.0/OBPI-25 (Confirm) and ADR-0.26.0/OBPI-12 (this brief) — defect tracked under **GHI #376** (closed); paired_with waiver populated; `gz validate --absorption-duplicates` audit consumes the waiver

## Quality Gates

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test --obpi OBPI-0.26.0-12-docs-lib` (vacuous parity-gate pass on `[doc]` REQ pattern)
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — **N/A**, Confirm outcome

### Gate 3: Docs

- [x] Completed brief records a final `Confirm` decision (frontmatter + body)
- [x] Comparison rationale names concrete capability differences and the chosen outcome (eleven-dimension table from OBPI-0.25.0-25 precedent + seven-point Decision rationale + duplicate-OBPI tracking)

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior, the brief names `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [x] Otherwise the brief records `N/A` rationale for no external-surface change — see `### Gate 4 (BDD): N/A` in `## Decision`

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — recorded during Stage 4 ceremony of `gz-obpi-pipeline`

## Acceptance Criteria

- [x] REQ-0.26.0-12-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb`, `Confirm`, or `Exclude`. **Decision:
  Confirm** — see frontmatter and `## Decision` below.
- [x] REQ-0.26.0-12-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (eleven-dimension capability table inherited
  from OBPI-0.25.0-25) and `## Decision` (seven-point rationale anchored on
  OBPI-0.25.0-25).
- [x] REQ-0.26.0-12-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests. **N/A — Confirm outcome.**
- [x] REQ-0.26.0-12-04: [doc] Given a `Confirm` or `Exclude` outcome, then
  the brief explains why no upstream absorption is warranted. See `## Decision`
  — gzkit's `doc_coverage/` package + `mkdocs build --strict` integration
  already covers every functional need that opsdev `docs.py` addresses; the
  only non-trivial opsdev capability (regex link validation + 2-click orphan
  walk) is mkdocs-redundant; opsdev `docs.py` self-declares temporary status.
- [x] REQ-0.26.0-12-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Confirm outcome with zero code changes
  under `src/gzkit/`, zero new CLI verbs, zero generated-surface change.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/docs.py
# Expected: opsdev source under review exists

test -d src/gzkit/doc_coverage
# Expected: gzkit existing documentation-validation surface exists (Confirm precedent under OBPI-0.25.0-25)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
# Expected: brief frontmatter and Decision body record the Confirm verdict

rg -n 'OBPI-0.25.0-25' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
# Expected: brief cites the canonical precedent in body and Closing Argument

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-12-docs-lib
# Expected: vacuous parity-gate pass on [doc] REQ pattern via _synthesize_doc_proof_linkage

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
# Expected: completed brief captures Gate 4 N/A rationale

uv run gz validate --absorption-duplicates
# Expected: clean exit; paired_with waiver consumed for OBPI-0.26.0-12 ↔ OBPI-0.25.0-25 pair
```

## Comparison

### Source-material observation

The brief Source Material at parent-ADR Cross-Reference Matrix row 12 reads
"gzkit equivalent: None." That assertion is incomplete at this brief's
authoring time:

1. gzkit's documentation-validation surface lives in
   `src/gzkit/doc_coverage/` (~802 L across `scanner.py` 496 L,
   `models.py` 93 L, `manifest.py` 85 L, `runner.py` 128 L) plus
   `mkdocs build --strict` integration via `gz validate --documents` and
   the canonical `arb-step-mkdocs-*` ARB receipt slot.
2. The same source artifact was already evaluated as **fundamentally
   different in problem scope** to opsdev's `lib/docs.py` under
   **OBPI-0.25.0-25-docs-validation-pattern** (attested 2026-04-12), with
   the only non-trivial opsdev capability (regex link validation +
   2-click orphan walk) found to be mkdocs-redundant.
3. Since the OBPI-0.25.0-25 attestation, opsdev `docs.py` remains
   unchanged at 218 L (self-declared temporary status persists);
   `src/gzkit/doc_coverage/` continues to host the AST-driven
   CLI-to-documentation coverage validator without acquiring opsdev-style
   regex-based link parsing.

| Surface | Lines | Role |
|---------|-------|------|
| `../airlineops/src/opsdev/lib/docs.py` | 218 | opsdev module: existence check for `docs/index.md` only (`check_files`); no-op stubs for nav/links during remodel; `mkdocs --strict` subprocess wrapper (`build_site_strict`); regex-based markdown link parser (`parse_links`, `_normalize`) with 2-click reachability orphan detection (`find_orphans`); `sys.exit`-coupled `fail`/`ok` helpers; plain `dict`/`set`/`list`/`tuple` primitives; library-only |
| `src/gzkit/doc_coverage/scanner.py` | 496 | AST-driven `discover_commands()` — static parsing of `_build_parser` and `register_*_parsers` without importing; 5-surface check per command (manpage, index_entry, operator_runbook, governance_runbook, docstring); handler docstring resolution; `find_orphaned_docs()` for manpages with no matching command |
| `src/gzkit/doc_coverage/models.py` | 93 | 7 frozen Pydantic models (`SurfaceResult`, `CommandCoverage`, `OrphanedDoc`, `CoverageReport`, `GapItem`, `OrphanedDocItem`, `DocCoverageGapReport`) with `ConfigDict(frozen=True, extra="forbid")` |
| `src/gzkit/doc_coverage/manifest.py` | 85 | `DocCoverageManifest` with per-command `SurfaceRequirements`; `load_manifest()` reads `config/doc-coverage.json`; `find_undeclared_commands()` detects AST-discovered commands absent from the manifest |
| `src/gzkit/doc_coverage/runner.py` | 128 | manifest-aware gap report builder (`build_gap_report()`); `run_doc_coverage()` entry point with human-readable and JSON output modes |

This observation is body-level (Comparison section); the parent-ADR-authored
Cross-Reference Matrix row 12 is intentionally not amended.

### Per-dimension comparison (re-anchored from OBPI-0.25.0-25 precedent)

The dimension comparison established by OBPI-0.25.0-25-docs-validation-pattern
holds because the source artifact is identical (`lib/docs.py`, 218 lines)
and the gzkit surface preserves its AST-driven coverage architecture plus
mkdocs strict integration.

| Dimension | opsdev `lib/docs.py` (218 L) | gzkit `doc_coverage/` (~802 L) + mkdocs strict | Winner |
|-----------|------------------------------|--------------------------------------------|--------|
| Problem scope | Docs structure validation (file existence, links, orphans) | CLI-to-documentation coverage validation | Different problems |
| Documentation validation | Single hardcoded `docs/index.md` existence check (remaining checks explicitly suspended) | AST-driven 5-surface coverage (manpage, index_entry, operator_runbook, governance_runbook, docstring) per discovered command | gzkit: fundamentally broader |
| Link validation | Regex-based markdown link parser, graph builder, 2-click reachability orphan detection | N/A — handled externally by `mkdocs build --strict` during docs build | Different approach (redundancy, not gap) |
| MkDocs integration | Subprocess wrapper around `python -m mkdocs build --clean --strict` | External invocation via `gz validate --documents` and CI `mkdocs build --strict` | Both equivalent |
| Manifest/config | None — all checks hardcoded | `config/doc-coverage.json` declares per-command surface obligations (50+ commands) with boolean toggles and exemption support | gzkit only |
| Gap reporting | Plain print statements for broken links and orphans | Structured `DocCoverageGapReport` with JSON output, undeclared command detection, ordered gap listing | gzkit: structured and machine-readable |
| Orphan detection | Page-level: markdown pages unreachable from index within 2 clicks | Command-level: manpage files with no matching discovered CLI command | Different targets |
| Error handling | `sys.exit(1)` with stderr message; `fail()` helper couples error reporting to process exit | Pydantic validation errors; structured model failures; non-exit-coupled handlers | gzkit: composable, testable |
| Cross-platform | Forced `encoding="utf-8"` on reads; hardcoded `_REPO_ROOT` via `Path(__file__).resolve().parents[3]` | pathlib throughout; `get_project_root()` helper; UTF-8 consistently applied | gzkit: more robust |
| Convention compliance | Private airlineops path dependency (`airlineops.paths.subpaths`); untyped primitives; top-of-module singletons | Pydantic `BaseModel` + `ConfigDict` throughout; pathlib; frozen immutable models; no cross-repo coupling | gzkit follows gzkit conventions |
| Test coverage | Unknown — no dedicated test module shipped with `docs.py` in opsdev | 87 tests across 3 files (`test_doc_coverage.py`, `test_manifest_v2.py`, `test_manifest_resolution.py`) covering AST discovery, all 5 surface checks, orphan detection, manifest loading/validation, gap reporting, integration | gzkit: 87× minimum ratio |
| Self-declared status | Module docstring: "Ultra-minimal Docs gate during 0.0.0 → 1.0.0 remodel" with TODO to restore | Shipping production surface behind `gz chores run doc-coverage` and `gz cli audit` | gzkit: stable and active |

### Subtraction test

Removing gzkit from airlineops leaves: a single existence check for
`docs/index.md`, a `mkdocs --strict` subprocess wrapper, and the
regex-based link validator with 2-click orphan walker. None is
airline-specific, but every capability is either (a) trivially covered
by existing gzkit commands (`mkdocs build --strict` invoked by
`gz validate --documents` and CI; `arb-step-mkdocs-*` canonical ARB
receipt slot) or (b) mkdocs-redundant (the strict build natively
detects missing internal links and unreachable nav targets). The
remainder is the `check_files()` + `build_site_strict()` pair —
trivially subsumed by existing gzkit invocations. **Nothing in opsdev
`docs.py` is both unique and non-redundant.**

### Cross-platform / convention-compliance observations

opsdev `lib/docs.py` carries three structural conflicts with gzkit
doctrine that absorb-by-copy could not eliminate:

1. **Untyped primitives violate Pydantic policy.** gzkit's models are
   `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` per
   `.claude/rules/models.md`; opsdev uses plain `dict`, `set`, `list`,
   `tuple` throughout — no validation, no immutability, no typed
   interfaces. Absorbing would require rewriting all data flow.
2. **`sys.exit`-coupled error handling violates testability doctrine.**
   `fail()` couples error reporting to process exit; `sys.exit(1)` is
   called inside utility functions; orchestrators print and exit. gzkit
   uses Pydantic validation errors and structured handlers that allow
   composition and test isolation.
3. **No problem to solve.** gzkit has no link-graph-validation use case
   that `mkdocs build --strict` does not already cover, and gzkit has a
   fundamentally different documentation-coverage problem (per-command
   surface obligations) that opsdev `docs.py` does not address. Even
   with conventions adapted, the absorbed code would have no caller in
   gzkit.

Per OBPI-0.25.0-25's analysis, these are not adapt-and-clean fixes —
they are decisive evidence that the module is mkdocs-redundant and
self-declared temporary technical debt.

## Decision

**Confirm** (by reference to OBPI-0.25.0-25-docs-validation-pattern,
attested 2026-04-12). gzkit's existing `src/gzkit/doc_coverage/` package
(~802 L across 4 modules) plus `mkdocs build --strict` integration via
`gz validate --documents` and the canonical `arb-step-mkdocs-*` ARB
receipt slot already covers every functional need that opsdev `docs.py`
(218 L; self-declared "ultra-minimal Docs gate during 0.0.0 → 1.0.0
remodel") addresses. The only non-trivial opsdev capability (regex
link validation + 2-click orphan walk) is mkdocs-redundant; the
remainder (`check_files`, `build_site_strict`) is trivially covered by
existing gzkit invocations. Zero functional gap; subtraction test
fails completely; convention violations (untyped primitives, `sys.exit`-
coupled handlers) preclude clean absorption even if scope overlap
existed. No absorption is warranted.

### Brief-scaffold defect (surfaced)

The brief Source Material at parent-ADR Cross-Reference Matrix row 12 reads
"gzkit equivalent: None," and the brief Assumptions block originally
asserted "No existing gzkit equivalent means either Absorb or Exclude —
there is no Confirm path." Both wordings are **incomplete and misleading**:

- gzkit's documentation-validation surface lives in
  `src/gzkit/doc_coverage/` (~802 L across 4 modules) plus
  `mkdocs build --strict` integration, NOT nowhere.
- OBPI-0.25.0-25 already evaluated this exact source artifact and decided
  **Confirm** with full eleven-dimension rationale.
- OBPI-0.26.0-04 / -05 / -06 / -07 / -08 / -09 / -10 / -11 (eight sibling
  briefs) carried analogous Source Material drift yet successfully
  landed `decision: Confirm` or `decision: Exclude` by-reference outcomes.

The Source Material wording is the ninth instance of this defect class
across ADR-0.26.0 briefs (also present in OBPI-04/05/06/07/08/09/10/11
wording). Tracked structurally under GHI #376 (closed); mechanical guard
`gz validate --absorption-duplicates` consumes the `paired_with` frontmatter
waiver populated under commit cdd8e396. Doctrine here is that authoritative
precedent (OBPI-0.25.0-25) overrides incomplete brief Source Material.

### Rationale

1. **Zero functional gap (canonical precedent).** OBPI-0.25.0-25
   evaluated the same opsdev source file (`lib/docs.py`, 218 lines) and
   recorded **Decision: Confirm** with an eleven-dimension rationale.
   The opsdev module's two non-trivial capabilities are (a) regex-based
   parsing of markdown links with graph-reachability orphan detection,
   and (b) a subprocess wrapper around `mkdocs build --strict`. Both
   are mkdocs-redundant; gzkit invokes `mkdocs build --strict` in CI
   and via `gz validate --documents` and emits the canonical
   `arb-step-mkdocs-*` ARB receipt for the strict build. The remainder
   (`check_files`) is a single existence assertion subsumed by mkdocs
   strict failure on missing nav root.

2. **Different problem scopes — fundamentally different concerns.**
   opsdev validates documentation *structure* (file existence, links,
   orphans). gzkit `doc_coverage/` validates CLI-to-documentation
   *coverage* (per AST-discovered command, do all required documentation
   surfaces exist). The two surfaces share neither inputs (markdown link
   graphs vs AST-discovered commands), outputs (plain print of broken
   links vs structured `DocCoverageGapReport`), control flow (regex link
   parsing vs AST traversal of `_build_parser`), nor failure modes
   (`sys.exit(1)` vs Pydantic validation errors).

3. **Manifest-driven obligations vs hardcoded checks.** gzkit's
   `config/doc-coverage.json` declaratively enumerates per-command
   surface obligations with boolean toggles per surface — 50+ commands
   are currently declared with explicit exemptions. opsdev `docs.py`
   has no manifest layer; every check is hardcoded with no extensibility.

4. **Convention violations preclude clean absorption.** Plain
   `dict`/`set`/`list`/`tuple` primitives violate gzkit's Pydantic
   `BaseModel` + `ConfigDict(frozen=True, extra="forbid")` policy
   (`.claude/rules/models.md`). `sys.exit`-coupled `fail()` helper and
   process-exit-from-utilities violate gzkit's structured-error
   testability doctrine. Adapting both would require rewriting from
   scratch — defeating the absorb-rather-than-reinvent guideline.

5. **gzkit doc_coverage/ post-precedent state preserves the Confirm
   verdict *a fortiori*.** Since the OBPI-0.25.0-25 attestation
   (2026-04-12), `src/gzkit/doc_coverage/` continues to host the
   AST-driven CLI-to-documentation coverage validator across 4 modules
   (~802 L) on the same Pydantic foundation — without acquiring any
   opsdev-style regex link parsing or 2-click orphan walking. The
   surface deepens governance-coverage validation on the same
   architectural foundation; the Confirm verdict is structurally
   stronger today than at the precedent attestation.

6. **Self-declared temporary status of opsdev source.** opsdev `docs.py`
   announces in its own module docstring that it is an "ultra-minimal
   Docs gate during 0.0.0 → 1.0.0 remodel" with explicit TODOs to
   restore mkdocs parsing, internal link verification, and ADR presence
   checks. Absorbing a module its own author marks as temporary
   technical debt would be the anti-pattern the parent ADR's
   critical-constraint section explicitly names.

7. **Subtraction test re-stated.** `opsdev.lib.docs - gzkit = mkdocs-
   redundant link validator + trivially-subsumed structural stubs`. The
   test is decisive: every capability in opsdev `docs.py` is either
   covered by `mkdocs build --strict` (which gzkit already invokes) or
   trivially covered by existing gzkit commands. gzkit's
   `doc_coverage/` package solves a fundamentally different and broader
   problem (per-command documentation coverage) that opsdev does not
   address. **Confirm.**

### Tracking the duplicate-evaluation signal

This brief is the ninth OBPI evaluating an opsdev `lib/` module across
two parent ADRs that the canonical OBPI-0.25.0-* sweep had already
covered:

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
| OBPI-0.26.0-11 | ADR-0.26.0 | (same) | Exclude-by-reference | attested 2026-05-02 |
| OBPI-0.25.0-25 | ADR-0.25.0 | `lib/docs.py` | Confirm | attested 2026-04-12 |
| **OBPI-0.26.0-12** | **ADR-0.26.0** | **(same)** | **Confirm-by-reference** (this brief) | **in-flight** |

Same root cause as the prior eight instances: ADR-0.26.0 authoring did not
check whether ADR-0.25.0's earlier absorption sweep had already covered
each module in scope. Mechanical resolution already landed under GHI #376:
`gz validate --absorption-duplicates` (commit 2a21ebdc) consumes the
`paired_with` frontmatter waiver populated across all 12 briefs (commit
cdd8e396).

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing documentation-validation surface continues to function
identically; no new commands, flags, output formats, or behavioral
changes are introduced. `features/heavy_lane_gate4.feature` is not
touched.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #12 captured verbatim.
- [x] **Gate 2 (TDD):** `uv run gz test --obpi OBPI-0.26.0-12-docs-lib` remains green; vacuous pass on `[doc]` REQ pattern.
- [x] **Gate 3 (Docs):** Decision rationale completed with concrete capability deltas across eleven dimensions.
- [x] **Gate 4 (BDD):** N/A — Confirm-by-reference outcome introduces no operator-visible behavior change.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony.

### Implementation Summary


- Decision: Confirm — by reference to OBPI-0.25.0-25-docs-validation-pattern. opsdev's `lib/docs.py` (218 L; self-declared "ultra-minimal Docs gate during 0.0.0 → 1.0.0 remodel" with TODO list to restore deep checks) has zero functional gap against gzkit's documentation-validation surface (`doc_coverage/` ~802 L across `scanner.py` 496 L, `models.py` 93 L, `manifest.py` 85 L, `runner.py` 128 L) plus `mkdocs build --strict` integration via `gz validate --documents` and the canonical `arb-step-mkdocs-*` ARB receipt slot.
- Modules compared: opsdev `docs.py` (218 L; `check_files` existence assertion for `docs/index.md`, `check_nav`/`check_links` no-op stubs during remodel, `build_site_strict` mkdocs subprocess wrapper, `parse_links` regex markdown link parser, `build_graph` outgoing-edge graph, `find_orphans` 2-click reachability walk, `validate_links` orchestrator, `docs_link_lint` exit-code wrapper, `fail`/`ok` `sys.exit`-coupled helpers, plain `dict`/`set`/`list`/`tuple` primitives) vs gzkit `doc_coverage/` (AST-driven `discover_commands` static parser, 5-surface per-command coverage check, 7 frozen Pydantic models with `ConfigDict(frozen=True, extra="forbid")`, manifest-driven obligations from `config/doc-coverage.json`, structured `DocCoverageGapReport` with JSON output).
- Eleven-dimension capability separation: problem scope (structure validation vs CLI-to-documentation coverage), documentation validation (single hardcoded check vs AST-driven 5-surface coverage), link validation (regex parser vs delegated to mkdocs strict), MkDocs integration (subprocess wrapper vs gz validate --documents + CI), manifest/config (none vs config/doc-coverage.json with 50+ commands), gap reporting (plain print vs structured DocCoverageGapReport), orphan detection (page-level vs command-level), error handling (sys.exit-coupled vs Pydantic validation errors), cross-platform (forced UTF-8 + hardcoded _REPO_ROOT vs pathlib + helper), convention compliance (untyped primitives + cross-repo coupling vs Pydantic + frozen models), test coverage (0 dedicated tests vs 87 tests across 3 files), self-declared status (temporary remodel placeholder vs shipping production surface).
- New observations since OBPI-0.25.0-25: opsdev source unchanged at 218 L (self-declared temporary status persists); `src/gzkit/doc_coverage/` continues to host AST-driven CLI coverage validator on same Pydantic foundation. Confirm verdict structurally stronger today than at precedent attestation.
- Subtraction test decisive: removing gzkit from airlineops leaves an mkdocs-redundant link validator + trivially-subsumed structural stubs — every capability is either covered by `mkdocs build --strict` (which gzkit invokes) or trivially covered by existing gzkit commands.
- Convention violations preclude clean absorption even if scope overlap existed: plain `dict`/`set`/`list`/`tuple` primitives violate `.claude/rules/models.md` (Pydantic `BaseModel` policy); `sys.exit`-coupled `fail()` and process-exit-from-utilities violate gzkit's structured-error testability doctrine.
- Brief-scaffold-defect surfaced: brief Source Material asserts "gzkit equivalent: None" but the actual gzkit documentation-validation surface is `doc_coverage/` ~802 L across 4 modules plus mkdocs strict integration; the precedent OBPI-0.25.0-25 attests Confirm; OBPI-0.26.0-04 through -11 already established by-reference outcomes are validator-accepted despite stale Source Material wording. Ninth structural instance of the same scaffold-defect class across ADR-0.26.0 briefs.
- Duplicate-OBPI surface tracked under **GHI #376** (closed) — ninth structural instance after OBPI-0.26.0-04 through -11. Mechanical resolution already landed: `gz validate --absorption-duplicates` (commit 2a21ebdc) consumes the `paired_with: OBPI-0.25.0-25-docs-validation-pattern` frontmatter waiver populated under commit cdd8e396.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings → title case; added missing `## Lane`, `## Denied Paths`, `## Discovery Checklist`, `## Comparison`, `## Decision` sections; `Verification Commands (Concrete)` → `Verification` with OBPI-specific verification commands; added `### Implementation Summary`, `### Key Proof`, `### Closing Argument` H3 evidence sections per `.claude/rules/brief-heading-conventions.md`.
- No code absorbed under this brief; no `src/gzkit/` or `tests/` edits — Confirm decided existing surface solves the same problem (and a broader one); modifying it would invalidate the OBPI-0.25.0-25 attestation.

### Key Proof


```bash
rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
# Confirms brief frontmatter and ## Decision body record the Confirm verdict.

rg -c 'OBPI-0.25.0-25' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
# Expected: ≥10 — brief cites the canonical precedent across body, Decision rationale, Implementation Summary, Closing Argument.

test -d src/gzkit/doc_coverage && test -f ../airlineops/src/opsdev/lib/docs.py
# Expected: both surfaces present (Confirm precedent under OBPI-0.25.0-25 attests gzkit's surface solves the same problem and a broader one).

wc -l ../airlineops/src/opsdev/lib/docs.py src/gzkit/doc_coverage/scanner.py src/gzkit/doc_coverage/models.py src/gzkit/doc_coverage/manifest.py src/gzkit/doc_coverage/runner.py
# Expected: 218 + 496 + 93 + 85 + 128 = 1020 L. opsdev unchanged (218 L), gzkit doc_coverage/ ~802 L on same Pydantic foundation since OBPI-0.25.0-25 — Confirm a fortiori.

uv run gz covers OBPI-0.26.0-12-docs-lib --json
# Expected: {"summary": {"total_reqs": 0, "uncovered_reqs": 0, ...}} — parity-gate pass for [doc] REQs via _synthesize_doc_proof_linkage.

uv run gz validate --absorption-duplicates
# Expected: clean exit; paired_with: OBPI-0.25.0-25-docs-validation-pattern waiver consumed.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-12-docs-lib.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): cited inline at Stage 4 ceremony after Stage 3 quality checks complete. REQ→@covers parity: `gz covers OBPI-0.26.0-12-docs-lib --json` → `uncovered_reqs: 0` (vacuous parity-gate pass on `[doc]` REQs via `_synthesize_doc_proof_linkage`).

## Human Attestation

- Attestor: `Jeffry Babb`
- Date: 2026-05-02
- Attestation: attest completed — OBPI-0.26.0-12 Confirm-by-reference verdict on opsdev lib/docs.py (218 L). Anchored on OBPI-0.25.0-25-docs-validation-pattern (Decision: Confirm attested 2026-04-12) with eleven-dimension subtraction-test rationale: gzkit's doc_coverage/ surface (~802 L across scanner.py 496 L, models.py 93 L, manifest.py 85 L, runner.py 128 L) plus mkdocs build --strict integration via gz validate --documents and the canonical arb-step-mkdocs-* ARB receipt slot already covers every functional need that opsdev docs.py addresses. opsdev's only non-trivial capability (regex link validation + 2-click orphan walk) is mkdocs-redundant; the remainder (check_files + build_site_strict) is trivially subsumed by existing gzkit invocations. opsdev module self-declares "ultra-minimal Docs gate during 0.0.0 → 1.0.0 remodel" temporary status. Convention violations preclude clean absorption: plain dict/set/list/tuple primitives violate .claude/rules/models.md Pydantic policy; sys.exit-coupled fail() helper violates structured-error testability doctrine. Post-precedent surface state preserves verdict a fortiori: gzkit doc_coverage/ continues hosting AST-driven CLI coverage validator on same Pydantic foundation; opsdev unchanged at 218 L. Ninth structural instance of ADR-0.26.0 ↔ ADR-0.25.0 duplicate-OBPI pattern (after -04/-05/-06/-07/-08/-09/-10/-11), mechanically suppressed by closed GHI #376 guard chain (gz validate --absorption-duplicates + paired_with frontmatter waiver populated under cdd8e396). Heavy-lane Stage 3 ARB receipts: lint arb-ruff-40f723da80794805b1f30fbd22e53dfa, typecheck arb-step-typecheck-8085e6cebfde4e6eb39174efabf5ec17, full unittest arb-step-unittest-758684d150cf4772af21e99511aa7a94, OBPI-scoped unittest (80/80) arb-step-unittest-0721b7ab55794ed7882191c1333c3cf4, mkdocs strict (2.25s) arb-step-mkdocs-ffd00e3fa3974ec6bc593e367f476e37. REQ→@covers parity: 5×[doc] REQs, uncovered_reqs:0 via _synthesize_doc_proof_linkage. gz validate --absorption-duplicates / --brief-headings clean; gz obpi precomplete READY (5/5). No src/ or tests/ edits (Confirm preserves OBPI-0.25.0-25 attestation). Gate 4 N/A (zero operator-visible behavior change). Brief-scaffold drift corrected in flight: ALL-CAPS headings → Title Case, status Pending → pending, added Lane / Denied Paths / Discovery Checklist / Comparison / Decision / Human Attestation sections, plus H3 evidence sections per .claude/rules/brief-heading-conventions.md.

### Closing Argument

**Confirm-by-reference.** opsdev's `lib/docs.py` (218 L) provides three
capabilities: (1) a single existence check for `docs/index.md`
(`check_files`); (2) a subprocess wrapper around
`python -m mkdocs build --clean --strict` (`build_site_strict`); and
(3) regex-based markdown link validation (`parse_links`, `_normalize`,
`build_graph`) with 2-click reachability orphan detection
(`find_orphans`, `validate_links`, `docs_link_lint`). The module's own
docstring labels it an "ultra-minimal Docs gate during 0.0.0 → 1.0.0
remodel" with explicit TODOs to restore mkdocs parsing, internal link
verification, and ADR presence checks — self-declared temporary
technical debt awaiting a remodel that has not landed. gzkit's
existing documentation-validation surface — ~802 L distributed across
`src/gzkit/doc_coverage/scanner.py` (496 L; AST-driven
`discover_commands` static parser without imports, 5-surface per-command
coverage check, handler-docstring resolution, `find_orphaned_docs` for
manpages with no matching command), `models.py` (93 L; 7 frozen Pydantic
models with `ConfigDict(frozen=True, extra="forbid")`), `manifest.py`
(85 L; per-command `SurfaceRequirements` from `config/doc-coverage.json`,
`find_undeclared_commands` detector), and `runner.py` (128 L;
manifest-aware gap report builder, `run_doc_coverage` entry point with
human-readable and JSON output) — solves the fundamentally different
and broader problem of CLI-to-documentation coverage validation. The
two surfaces share neither inputs (markdown link graphs vs
AST-discovered CLI commands), outputs (plain print of broken links vs
structured `DocCoverageGapReport`), control flow (regex link parsing
vs AST traversal of `_build_parser`), nor failure modes (`sys.exit(1)`
vs Pydantic validation errors). The opsdev module's only non-trivial
capability (regex link validation + 2-click orphan walk) is
mkdocs-redundant: `mkdocs build --strict` natively detects missing
internal links and unreachable nav targets, and gzkit invokes
`mkdocs build --strict` in CI and via `gz validate --documents`,
emitting the canonical `arb-step-mkdocs-*` ARB receipt for the strict
build. Zero functional gap.

The opsdev module's plain `dict`/`set`/`list`/`tuple` primitives
violate gzkit's Pydantic policy (`.claude/rules/models.md` requires
`BaseModel` with `ConfigDict(frozen=True, extra="forbid")`); the
`sys.exit`-coupled `fail()` helper and process-exit-from-utilities
violate gzkit's structured-error testability doctrine. Even if the
absorption subtraction test were not decisive, these convention
conflicts would force a full rewrite that defeats the
absorb-rather-than-reinvent guideline. The post-OBPI-0.25.0-25
evolution of `src/gzkit/doc_coverage/` continues to host the AST-driven
CLI coverage validator across 4 modules (~802 L) on the same Pydantic
foundation without acquiring any opsdev-style regex link parsing or
2-click orphan walking — the Confirm verdict is structurally stronger
today than at the precedent attestation. Not absorbed.

This brief is the ninth evaluation of an opsdev `lib/` module across
two parent ADRs that the canonical OBPI-0.25.0-* sweep had already
covered. The brief Source Material's "gzkit equivalent: None" wording
(and the matching Assumption that "No existing gzkit equivalent means
either Absorb or Exclude — there is no Confirm path") is itself a
brief-scaffold defect — gzkit's primary documentation-validation surface
is `doc_coverage/`'s AST-driven CLI coverage validator (~802 L across
4 modules) plus `mkdocs build --strict` integration, not nowhere — and
the precedent (OBPI-0.25.0-25 with Decision: Confirm) attests the
Confirm verdict on identical source. OBPI-0.26.0-04 through -11 (eight
prior siblings) already established the precedent that
`decision: Confirm` and `decision: Exclude` by-reference outcomes are
validator-accepted despite incomplete brief Source Material; this brief
follows that precedent. GHI #376 is closed; the mechanical guard
`gz validate --absorption-duplicates` consumes the `paired_with`
frontmatter waiver populated across all 12 ADR-0.26.0 briefs (commits
cdd8e396 + 2a21ebdc), so the absorption sweep does not silently recur.
No code under `src/gzkit/` or `tests/` is modified by this brief;
modifying the existing surface would invalidate the OBPI-0.25.0-25
attestation. Gate 4 N/A: zero operator-visible behavior change.
