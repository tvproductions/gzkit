---
id: OBPI-0.25.0-28-layout-verification-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 28
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-28: Layout Verification Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-28 — "Evaluate and absorb opsdev/lib/layout_verify.py (143 lines) — tree layout validation against config"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/layout_verify.py` (143 lines) against
gzkit's layout verification surface and determine: Absorb, Confirm, or Exclude.
The airlineops module covers tree layout validation against config. gzkit's
equivalent surface spans `commands/config_paths.py` and
`validate_pkg/manifest.py` (116 lines).

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/layout_verify.py` (143 lines)
- **gzkit equivalent:** `src/gzkit/commands/config_paths.py` (310 lines) and `src/gzkit/validate_pkg/manifest.py` (116 lines)

## DECISION

**Decision: Exclude** — airlineops `layout_verify.py` validates a
domain-specific config file (`config/governance/tree_layout.json`) that does
not exist in gzkit, while gzkit's layout verification surface
(`commands/config_paths.py` + `validate_pkg/manifest.py`) is already a
functional superset with capabilities airlineops lacks. No upstream
absorption warranted.

**Rationale:** airlineops's `verify_layout()` loads
`config/governance/tree_layout.json` and validates six hardcoded root keys
(`source_root`, `config_root`, `data_root`, `artifacts_root`, `docs_root`,
`ops_tooling_root`) with a trailing semantic check for an "opsdev package"
under the tooling root. gzkit's equivalent surface reads `.gzkit/manifest.json`
via `load_manifest()` and `.gzkit.json` via the typed `GzkitConfig` model,
validates against a declared schema (`load_schema("manifest")`), and
additionally performs: required-dir/file existence checks, manifest artifact
path checks with legacy-OBPI migration contract enforcement, control-surface
path checks with explicit dir-vs-file type discrimination for ten named
control surfaces, OBPI path contract enforcement (rejects deprecated global
OBPI paths), and **AST-based source-literal scanning** — a walk over
`src/gzkit/**/*.py` that parses each file and flags string constants looking
like filesystem paths but not covered by any manifest entry. airlineops's
module has none of these capabilities. Additionally, airlineops still derives
repo root via `Path(__file__).resolve().parents[3]` at
`layout_verify.py:13-19` — exactly the anti-pattern gzkit removed in
OBPI-0.0.7-04 ("Hooks module migration") as part of ADR-0.0.7's config-first
resolution discipline. Absorbing the module wholesale would regress prior
governance work. The only isolated robustness helper worth considering,
`_is_within()` (7 lines, path-escape check via
`Path.resolve().relative_to()`), addresses a threat model gzkit does not
have: config paths in gzkit come from trusted in-repo JSON under version
control, loaded through `GzkitConfig` with schema validation, not from
user-supplied runtime input. Contrast this with OBPI-0.25.0-27, where
airlineops's `_safe_print` was a concrete Windows pre-commit risk that
narrowly justified Absorb. No equivalent narrow hardening candidate exists
here. The subtraction test is decisive: stripping airline-specific pieces
(tree_layout.json schema, required root names, `_repo_root_from_here()`,
opsdev package semantic check) leaves nothing novel.

## COMPARISON ANALYSIS

| Dimension | airlineops (143 lines) | gzkit (310 + 116 lines) | Assessment |
|-----------|------------------------|-------------------------|------------|
| Config source | `config/governance/tree_layout.json` (airline-specific file) | `.gzkit/manifest.json` + `.gzkit.json` (typed `GzkitConfig`) | Different abstractions, not two implementations of one schema |
| Validation surface | 6 hardcoded root keys + opsdev semantic check | Required dirs/files + manifest artifacts + control surfaces (dir/file typed) + OBPI path contract + AST literal scan | gzkit is a functional superset |
| Root resolution | `Path(__file__).resolve().parents[3]` (retired anti-pattern) | `get_project_root()` via config-first resolution | airlineops would regress OBPI-0.0.7-04 |
| Schema validation | Inline required-key check (`_required_roots`) | `load_schema("manifest")` with typed `ValidationError` | gzkit is schema-driven, airlineops is ad-hoc |
| Data model | `list[str]` error messages | `list[ValidationError]` (Pydantic) and `list[dict[str,str]]` issues | gzkit is typed; airlineops is stringly |
| CLI integration | Standalone `verify_layout()` + `print_report()` | `gz check-config-paths` with `--json` output mode | gzkit is operator-facing; airlineops is library-only |
| Path-escape defense | `_is_within(path, parent)` helper (7 lines) | Implicit via trusted in-repo JSON + pathlib concatenation | airlineops solves non-problem for gzkit (no user-supplied runtime paths) |
| Unique capabilities | `_is_within()` path escape check | AST source-literal scanning, control-surface type checks, legacy OBPI contract, JSON output mode | gzkit carries novel capabilities airlineops lacks |
| Test coverage | Unknown (not tracked from outside repo) | `tests/test_validate_manifest.py`, `tests/test_config_paths.py`, and siblings exercise the full surface | gzkit has concrete test coverage |
| Convention compliance | `Path(__file__).parents[3]`, bare `print()`, inline required-key check | Pydantic models, typed config, structured errors, schema loader | gzkit matches `.claude/rules/models.md` and cross-platform policy |

### Subtraction Test

Strip airline-specific pieces from `layout_verify.py`: the
`tree_layout.json` schema (gzkit does not have this file), the required root
names (`source_root`/`config_root`/`data_root`/`artifacts_root`/`docs_root`/
`ops_tooling_root` — none match `GzkitConfig.paths` shape), the
`_repo_root_from_here()` anti-pattern (already removed from gzkit), and the
"opsdev package" semantic check at lines 121-126 (airline-only concern).
Residue: `_is_within()` path escape check (7 lines). This helper solves a
threat model gzkit does not have — config paths in gzkit come from trusted
in-repo JSON, not user-supplied runtime input, and the existing validators
operate on `project_root / rel_path` concatenation against paths committed
to the repo. Nothing absorbable remains.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible
behavior changes. No behavioral proof is required. The existing gzkit test
suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane
definition: "a brief may record BDD as N/A only when the final decision is
Confirm or Exclude with no external-surface change."

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's config path validation around airlineops's layout model

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
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Exclude decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Exclude decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-28-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-28-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Ten-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-28-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-28-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Subtraction test and five-point rationale in Decision section.
- [x] REQ-0.25.0-28-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/layout_verify.py
# Expected: airlineops source under review exists

test -f src/gzkit/validate_pkg/manifest.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-28-layout-verification-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Exclude)
- [x] **Gate 3 (Docs):** Decision rationale completed with comparison table
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Exclude, no behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for an Exclude decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Exclude decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented evaluation of whether airlineops's
`opsdev/lib/layout_verify.py` contained reusable patterns for gzkit. After
reading the full 143-line module, every capability is tied to an
airlineops-specific config file (`config/governance/tree_layout.json`) and
six hardcoded root keys that do not match gzkit's `GzkitConfig.paths`
shape. gzkit's layout verification surface
(`commands/config_paths.py` + `validate_pkg/manifest.py`, 310 + 116 lines)
is architecturally superior: schema-driven manifest validation via
`load_schema("manifest")`, control-surface type checks with dir-vs-file
discrimination for ten named control surfaces, legacy OBPI path contract
enforcement, and **AST-based source-literal scanning** that walks
`src/gzkit/**/*.py` to flag unmapped filesystem path strings — a unique
capability airlineops lacks entirely. airlineops additionally uses
`Path(__file__).resolve().parents[3]` (the `_repo_root_from_here()`
anti-pattern gzkit removed in OBPI-0.0.7-04), which absorbing would
regress. The only isolated robustness helper — `_is_within()` path escape
check — addresses a threat model gzkit does not have, since config paths
come from trusted in-repo JSON under version control. The subtraction test
is decisive.

### Key Proof


- Decision: Exclude
- Comparison: ten-dimension analysis in Comparison Analysis section
- airlineops layout_verify.py: 143 lines, `tree_layout.json`-schema validator with hardcoded root keys
- gzkit surface: 310 + 116 lines, schema-driven `.gzkit/manifest.json` + `.gzkit.json` validator with AST source-literal scanning, control-surface type checks, and OBPI path contract
- Subtraction test: stripping airline-specific pieces leaves only `_is_within()` (7 lines), which addresses a non-problem for gzkit
- Convention regression risk: airlineops uses retired `_repo_root_from_here()` anti-pattern gzkit removed in OBPI-0.0.7-04

### Implementation Summary


- Decision: Exclude
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Date: 2026-04-13

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — Exclude decision: airlineops layout_verify.py (143 lines) validates domain-specific config/governance/tree_layout.json with six hardcoded root keys and opsdev-package semantic check; that file and shape do not exist in gzkit. gzkit surface (commands/config_paths.py 310 lines + validate_pkg/manifest.py 116 lines) is a functional superset: schema-driven .gzkit/manifest.json validation via load_schema, dir/file control-surface type checks for ten named surfaces, legacy OBPI path contract enforcement, and unique AST-based source-literal scanning that walks src/gzkit/**/*.py. airlineops still uses Path(__file__).resolve().parents[3] (retired anti-pattern gzkit removed in OBPI-0.0.7-04). Only isolated robustness helper (_is_within() 7-line path escape check) addresses a threat model gzkit lacks since config paths come from trusted in-repo JSON under version control. Subtraction test decisive. Gate 3 green: lint, typecheck, 17 features / 110 scenarios / 584 steps pass, validate --documents, mkdocs --strict. No code or test edits. Contrast OBPI-0.25.0-27 where _safe_print was concretely relevant to Windows pre-commit path; no equivalent narrow hardening candidate exists here.
- Date: 2026-04-13

## Closing Argument

airlineops's `opsdev/lib/layout_verify.py` (143 lines) provides a single
capability: validating that a repo's tree layout matches an airline-specific
`config/governance/tree_layout.json` file with six hardcoded root keys
(`source_root`, `config_root`, `data_root`, `artifacts_root`, `docs_root`,
`ops_tooling_root`) and a trailing semantic check for an "opsdev package"
under the tooling root. That file does not exist in gzkit, and the root
names do not match gzkit's `GzkitConfig.paths` shape. gzkit's layout
verification surface — `src/gzkit/commands/config_paths.py` (310 lines) +
`src/gzkit/validate_pkg/manifest.py` (116 lines) — is architecturally
superior: it performs schema-driven manifest validation via
`load_schema("manifest")` with typed `ValidationError` results, checks
required directories and files from the typed `GzkitConfig` model,
enforces control-surface path types with explicit dir-vs-file
discrimination for ten named control surfaces, enforces the OBPI path
contract (rejecting deprecated global OBPI paths), and walks
`src/gzkit/**/*.py` with AST parsing to flag string constants looking
like filesystem paths but not covered by any manifest entry — a unique
capability airlineops lacks entirely. airlineops's module still uses
`Path(__file__).resolve().parents[3]` to derive repo root, exactly the
anti-pattern gzkit removed in OBPI-0.0.7-04 as part of ADR-0.0.7's
config-first resolution discipline; absorbing it wholesale would regress
prior governance work. The one isolated robustness helper —
`_is_within()` path escape check (7 lines) — addresses a threat model
that does not apply to gzkit, since config paths come from trusted
in-repo JSON loaded through `GzkitConfig` with schema validation, not
from user-supplied runtime input. Contrast this with OBPI-0.25.0-27,
where airlineops's `_safe_print` was a concrete Windows pre-commit crash
risk that narrowly justified Absorb; no equivalent narrow hardening
candidate exists here. The subtraction test is unambiguous: stripping
airline-specific pieces (tree_layout.json schema, hardcoded root names,
`_repo_root_from_here()`, opsdev package semantic check) leaves only
`_is_within()`, which solves a non-problem for gzkit. **Decision: Exclude.**
