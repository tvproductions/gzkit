---
id: OBPI-0.25.0-25-docs-validation-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 25
status: in_progress
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-25: Documentation Validation Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-25 — "Evaluate and absorb opsdev/lib/docs.py (218 lines) — documentation structure validation"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/docs.py` (218 lines) against gzkit's
documentation validation surface and determine: Absorb, Confirm, or Exclude.
The airlineops module covers documentation structure validation. gzkit's
equivalent surface spans the `doc_coverage/` package — `scanner.py` (496 lines),
`models.py` (93 lines), `manifest.py` (85 lines), and `runner.py` (128 lines)
— approximately 800+ lines across 4 modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/docs.py` (218 lines)
- **gzkit equivalent:** `src/gzkit/doc_coverage/` package (~800+ lines across 4 modules)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 4x larger surface suggests more mature coverage — comparison will verify

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's doc_coverage package around airlineops's approach

## Comparison

### airlineops `docs.py` (218 lines)

| Function | Lines | Assessment |
|----------|-------|-----------|
| `check_files()` | 59-63 | Existence check for `docs/index.md` only; all other "deep checks" explicitly suspended per module docstring ("ultra-minimal Docs gate during 0.0.0 -> 1.0.0 remodel") |
| `check_nav()`, `check_links()` | 66-71 | Stubs — both are no-ops during the remodel; TODO list preserves intent to restore |
| `build_site_strict()` | 74-87 | Subprocess wrapper around `python -m mkdocs build --clean --strict`; captures stdout/stderr, exits 1 on mkdocs failure |
| `_is_external()`, `_normalize()` | 106-130 | Link parsing helpers: URL scheme/netloc detection, path resolution under `docs/`, external anchor suppression |
| `collect_markdown()` | 133-135 | `rglob("*.md")` under docs root |
| `parse_links()` | 138-145 | Regex-based markdown link extraction (`r"\[[^\]]+\]\(([^)]+)\)"`) with forced UTF-8 decode |
| `build_graph()` | 148-161 | Constructs outgoing-edge graph of markdown files with resolved targets |
| `find_orphans()` | 164-180 | 2-click reachability walk from `docs/index.md`; returns pages unreachable within depth 3 |
| `validate_links()` | 183-200 | Returns `(missing_links, orphaned_pages)` tuple; re-parses sources to detect broken targets |
| `docs_link_lint()` | 203-218 | Orchestrator: prints broken links and orphans, returns exit code |
| `fail()`, `ok()` | 43-51 | Trivial stderr/stdout print helpers coupled to `sys.exit()` |
| Module state | 35, 54-56 | Hardcoded `_REPO_ROOT` from `__file__`, `MD_ROOT` via `airlineops.paths.subpaths.docs_path()` import, compiled regex at module scope |
| Data model | throughout | Plain `dict`, `set`, `list`, `tuple` primitives; no Pydantic, no typed models, no validation |

### gzkit doc_coverage surface

| Module | Lines | Capabilities |
|--------|-------|-------------|
| `doc_coverage/scanner.py` | 496 | AST-driven `discover_commands()` — static parsing of `_build_parser` and `register_*_parsers` without importing; 5-surface check per command (manpage, index_entry, operator_runbook, governance_runbook, docstring); handler docstring resolution via import map; `find_orphaned_docs()` for manpages with no matching command; manifest exemption application |
| `doc_coverage/models.py` | 93 | 7 frozen Pydantic models (`SurfaceResult`, `CommandCoverage`, `OrphanedDoc`, `CoverageReport`, `GapItem`, `OrphanedDocItem`, `DocCoverageGapReport`) with `ConfigDict(frozen=True, extra="forbid")` |
| `doc_coverage/manifest.py` | 85 | `DocCoverageManifest` with per-command `SurfaceRequirements`; `load_manifest()` reads `config/doc-coverage.json`; `find_undeclared_commands()` detects AST-discovered commands absent from the manifest |
| `doc_coverage/runner.py` | 128 | Manifest-aware gap report builder (`build_gap_report()`); `run_doc_coverage()` entry point with human-readable and JSON output modes; filters coverage results against declared obligations |

### Capability Comparison

| Dimension | airlineops `docs.py` (218 lines) | gzkit `doc_coverage/` (802 lines across 4 modules) | Winner |
|-----------|---------------------------------|---------------------------------------------------|--------|
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
| Test coverage | Unknown — no dedicated test module shipped with `docs.py` in airlineops | 87 tests across 3 files (`test_doc_coverage.py`, `test_manifest_v2.py`, `test_manifest_resolution.py`) covering AST discovery, all 5 surface checks, orphan detection, manifest loading/validation, gap reporting, integration | gzkit: 87x minimum ratio |
| Self-declared status | Module docstring: "Ultra-minimal Docs gate during 0.0.0 -> 1.0.0 remodel" with TODO to restore | Shipping production surface behind `gz chores doc-coverage` and `gz cli audit` | gzkit: stable and active |

## Decision: Confirm

gzkit's existing `doc_coverage/` package plus `mkdocs build --strict` integration already covers every functional need that airlineops `docs.py` addresses. No absorption is warranted.

**Rationale:**

1. **Different problem scopes with no unique airlineops coverage gap:** airlineops `docs.py` validates documentation *structure* — does `docs/index.md` exist, do markdown links resolve, are any pages orphaned from the index? gzkit's `doc_coverage/` validates CLI-to-documentation *coverage* — for each AST-discovered command, do all required documentation surfaces exist? The structure-validation concerns airlineops tries to cover are either (a) subsumed by `mkdocs build --strict` (broken link detection, nav integrity) or (b) explicitly suspended in airlineops itself ("ultra-minimal Docs gate during 0.0.0 -> 1.0.0 remodel"). The only live check in airlineops is `check_files()` — a single existence assertion for `docs/index.md` — which is trivially enforced by mkdocs build when the nav root is missing.
2. **Link validation is redundant with mkdocs strict builds:** airlineops's regex-based link parser and graph-reachability orphan walker (`parse_links`, `build_graph`, `find_orphans`, `validate_links`) solve a problem that `mkdocs build --strict` already solves natively: the strict build fails on missing internal links, missing nav targets, and unreachable pages. gzkit uses `mkdocs build --strict` in CI and as part of `gz validate --documents`, so absorbing airlineops's custom link linter would introduce a second, weaker, regex-based validator for the same concern.
3. **Manifest-driven obligations vs hardcoded checks:** gzkit's `config/doc-coverage.json` declaratively enumerates per-command surface obligations with boolean toggles per surface — 50+ commands are currently declared with explicit exemptions. airlineops has no manifest layer — every check is hardcoded in `check_files()` and the link validator, with no extensibility mechanism and no mechanism to declare "this surface is not required for this command/page".
4. **Type-safe models vs untyped primitives:** gzkit uses 7 frozen Pydantic `BaseModel` classes (`SurfaceResult`, `CommandCoverage`, `CoverageReport`, `DocCoverageGapReport`, etc.) with `ConfigDict(frozen=True, extra="forbid")` for all documentation coverage data. airlineops uses plain `dict`, `set`, `list`, and `tuple` primitives throughout — no validation, no immutability, no serialization contracts, no typed interfaces.
5. **Test coverage gap:** gzkit's documentation coverage surface has 87 tests across 3 dedicated test modules covering AST discovery, all 5 surface checks, manifest loading/validation, gap reporting, and integration scenarios. airlineops ships `docs.py` without a dedicated test module — the docstring-internal TODO list signals that the module is itself in a suspended/partial state awaiting remodel.
6. **Self-declared temporary status:** airlineops `docs.py` announces in its own module docstring that it is an "ultra-minimal Docs gate during 0.0.0 -> 1.0.0 remodel" with explicit TODOs to restore mkdocs parsing, internal link verification, and ADR presence checks. Absorbing a module its own author marks as temporary would be absorbing technical debt.
7. **Subtraction test:** Removing gzkit's coverage from airlineops leaves the link validator and 2-click orphan walker. Neither is airline-specific, but both solve problems that `mkdocs build --strict` already solves. The remainder is the `check_files()` + `build_site_strict()` pair — trivially covered by existing gzkit commands. Nothing in airlineops `docs.py` is both unique and non-redundant.

### Gate 4 (BDD): N/A

No operator-visible behavior change. This is a Confirm decision — no code was added, removed, or modified. The existing `doc_coverage/` subsystem, `gz validate --documents`, and `mkdocs build --strict` integration continue to function identically. Per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm decision)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-25-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [x] REQ-0.25.0-25-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [x] REQ-0.25.0-25-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [x] REQ-0.25.0-25-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [x] REQ-0.25.0-25-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/docs.py
# Expected: airlineops source under review exists

test -d src/gzkit/doc_coverage
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-25-docs-validation-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (no code changes — Confirm decision)
- [x] **Gate 3 (Docs):** Decision rationale completed with side-by-side comparison
- [x] **Gate 4 (BDD):** N/A — Confirm decision, no operator-visible behavior change
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

gzkit's documentation coverage surface spans the `doc_coverage/` package (802 lines across `scanner.py`, `models.py`, `manifest.py`, `runner.py`), providing AST-driven CLI command discovery without import or execution, 5-surface documentation coverage per command (manpage, index_entry, operator_runbook, governance_runbook, docstring), manifest-driven obligations via `config/doc-coverage.json` declaring 50+ commands with per-surface boolean toggles and exemption support, structured `DocCoverageGapReport` output with both human-readable and JSON formats, and orphaned manpage detection for files with no matching discovered command — backed by 87 tests across 3 dedicated test modules. airlineops's `opsdev/lib/docs.py` (218 lines) provides a fundamentally different and explicitly temporary surface: a single existence check for `docs/index.md` (`check_files`), a subprocess wrapper around `python -m mkdocs build --strict` (`build_site_strict`), and a regex-based markdown link validator with 2-click reachability orphan detection (`parse_links`, `build_graph`, `find_orphans`, `validate_links`, `docs_link_lint`). The module's own docstring labels it an "ultra-minimal Docs gate during 0.0.0 -> 1.0.0 remodel" with explicit TODOs to restore its deep checks. Its link validation capability — the only non-trivial piece — is already solved natively by `mkdocs build --strict`, which gzkit uses in CI and as part of `gz validate --documents`. The remainder (`check_files`, `build_site_strict`) is subsumed by existing gzkit commands. With 87 tests vs a dedicated test module that does not exist, frozen Pydantic models vs plain dict/set/list primitives, manifest-driven obligations vs hardcoded ad-hoc checks, and AST-based CLI coverage vs `sys.exit`-coupled structural stubs, gzkit's approach is architecturally superior in every comparable dimension. Nothing in airlineops `docs.py` is both unique and non-redundant. **Decision: Confirm.**

### Implementation Summary


- **Decision:** Confirm — gzkit's existing documentation coverage surface is sufficient
- **Patterns evaluated:** 11 airlineops `docs.py` functions + module state (218 lines)
- **gzkit equivalents:** `doc_coverage/` package (~802 lines across 4 modules) plus `mkdocs build --strict` integration via `gz validate --documents`
- **Discovery approach:** gzkit uses AST-based static parsing of `_build_parser`; airlineops uses regex and `rglob` over the docs tree
- **Coverage model:** gzkit enforces 5 documentation surfaces per CLI command via a manifest; airlineops validates docs tree structure and is explicitly suspended
- **Link validation:** airlineops has a regex-based markdown link validator and 2-click orphan walker; gzkit delegates to `mkdocs build --strict` which solves the same problem natively
- **Test ratio:** 87 tests (gzkit) vs no dedicated test module (airlineops `docs.py`)
- **Subtraction test:** The unique airlineops capability (link validation) is already solved by `mkdocs build --strict`; the remainder is trivially covered by existing gzkit commands
- **Self-declared status:** airlineops `docs.py` module docstring explicitly declares "ultra-minimal Docs gate during 0.0.0 -> 1.0.0 remodel" with TODOs to restore deep checks
- **Convention compliance:** airlineops uses plain dict/set/list primitives, `sys.exit` coupling, and imports `airlineops.paths.subpaths`; gzkit uses frozen Pydantic models and a package-internal `get_project_root()` helper
- **Code changes:** None — Confirm decision, no absorption warranted

### Key Proof


```bash
rg -n 'Decision: Confirm' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-25-docs-validation-pattern.md
# Expected: "## Decision: Confirm"
```

### Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-12
- Attestation: Accepted. Confirm decision for airlineops opsdev/lib/docs.py — gzkit doc_coverage/ package plus mkdocs strict builds already cover all functional needs; airlineops module is self-declared temporary technical debt.
