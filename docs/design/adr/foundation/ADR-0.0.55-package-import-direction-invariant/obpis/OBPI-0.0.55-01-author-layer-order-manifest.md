---
id: OBPI-0.0.55-01-author-layer-order-manifest
parent: ADR-0.0.55-package-import-direction-invariant
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.55-01-author-layer-order-manifest: Author the Tri-Role Layer-Order Manifest + Helper Port

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/ADR-0.0.55-package-import-direction-invariant.md`
- **Checklist Item:** #1 — "OBPI-0.0.55-01: Author tri-role manifest (vertical layers + Providers + Utility) + helper + rule + scorecard + baseline allowlist (post-reclassification bootstrap snapshot)"

**Status:** Draft

## Objective

Author the package-import-direction port: `data/package_layer_order.json` declaring the canonical structure (8 vertical layers, 3 Providers with floors, the Utility tier, the `provider_edges` allowlist), the `src/gzkit/governance/import_direction.py` helper (`compute_import_edges`, `classify`, `layer_of`, `violates_predicate`), the `PackageImportManifest` Pydantic model validating the manifest shape, the `.gzkit/rules/package-import-direction.md` rule file (version `0.1.0`), the scorecard entry, and `data/package_import_direction_baseline.json` capturing — under the tri-role classifier — only the genuine vertical-to-vertical violations as `phase: bootstrap` exempt.

## Lane

**Heavy** — Adds a new canonical data manifest, a new `PackageImportManifest` Pydantic model, a new governance helper module, and a new canonical rule surface. Per `.gzkit/rules/skill-surface-sync.md` a new canonical rule file is a heavy-lane surface change; the manifest is the single source of truth every downstream OBPI's validator consumes. Foundation-kind parent ADR-0.0.55 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `data/` — OBPI creates `data/package_layer_order.json` (the tri-role manifest) and `data/package_import_direction_baseline.json` (the bootstrap allowlist)
- `src/gzkit/governance/` — OBPI creates `import_direction.py` (the helper: `compute_import_edges`, `classify`, `layer_of`, `violates_predicate`); the `PackageImportManifest` Pydantic model lands here or in `src/gzkit/core/models.py`
- `src/gzkit/governance/import_direction.py` — the helper module this OBPI creates, named explicitly so OBPI-02/03 resolve it as pending-upstream rather than a dead citation
- `src/gzkit/core/models.py` — permitted home for the `PackageImportManifest` Pydantic model if the helper module is kept logic-only
- `.gzkit/rules/` — OBPI creates `.gzkit/rules/package-import-direction.md` (new rule file, version `0.1.0`)
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying the new rule
- `tests/governance/` — OBPI creates `tests/governance/test_layer_order_manifest.py` (the manifest Pydantic-shape tests)
- `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/governance/trust_audits/import_direction.py` — the `gz validate --import-direction` validator scope is OBPI-02
- Any source-file relocation or back-edge migration — OBPI-03 scope
- The validator's fail-closed promotion and rule-version bump to `1.0.0` — OBPI-04 scope
- `docs/user/manpages/validate.md` — the manpage update lands with the validator in OBPI-02
- Any `src/gzkit/**` import-graph edit — this OBPI only *measures* the graph; it relocates nothing
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `data/package_layer_order.json` exists with four top-level keys — `vertical_layers` (the 8-layer L0–L7 cascade with `members` per layer, exactly as the ADR § Decision table declares), `providers` (`ports`/`arb`/`hooks` each with `floor`, `role`, `empirical_justification`), `utility` (the depend-on-nothing module list), and `provider_edges` (the explicit Provider-to-Provider allowlist, EMPTY at this OBPI's landing).
2. REQUIREMENT: `src/gzkit/governance/import_direction.py` provides `compute_import_edges(root: Path) -> dict[tuple[str, str], list[ImportSite]]` (edges with source-line provenance), `classify(subpackage: str) -> Literal["vertical", "provider", "utility", "unknown"]`, `layer_of(subpackage: str) -> int | None`, and `violates_predicate(src: str, dst: str) -> bool` implementing all six predicate rules (vertical↔vertical, vertical↔Provider, Provider↔vertical, Provider↔Provider, anything→Utility, Utility→anything).
3. REQUIREMENT: A `PackageImportManifest` Pydantic `BaseModel` (`ConfigDict(extra="forbid")`) validates the manifest shape — vertical-layer indices contiguous; no subpackage in multiple roles; every `src/gzkit/` subdirectory and top-level utility-tier module accounted for or explicitly `excluded`; Provider floors reference valid vertical layers; `provider_edges` only references declared Providers.
4. REQUIREMENT: `.gzkit/rules/package-import-direction.md` exists with rule body version `0.1.0`, `paths:` frontmatter scoping `src/gzkit/**/*.py`, and a body declaring the invariant verbatim from the parent ADR § Decision canonical statement and citing ADR-0.0.55 plus the OpenAI Harness Engineering Figure 4 as visual exemplar.
5. REQUIREMENT: `docs/governance/advisory-rules-audit.md` gains a scorecard entry for the new rule classifying it **Mechanical**.
6. REQUIREMENT: `data/package_import_direction_baseline.json` exists, capturing — after the import-graph audit is RE-RUN under the tri-role classifier — only the genuine predicate violations as exempt. Each entry is tagged `phase: bootstrap` with a target-OBPI cleanup hint. Edges that reclassify as legitimate vertical-to-Provider imports under the tri-role classifier (notably `governance → arb`, `governance → hooks`, top-level-modules → `hooks`) do NOT appear in the baseline.
7. REQUIREMENT: This OBPI relocates ZERO source files and modifies ZERO `src/gzkit/**` import statements — it authors the manifest, helper, model, rule, scorecard, and baseline only. The graph is measured, not changed.
8. REQUIREMENT: Tests in `tests/governance/test_layer_order_manifest.py` assert REQ-derived semantics — the manifest validates against `PackageImportManifest`; a non-contiguous layer index is rejected; a subpackage in two roles is rejected; an undeclared `provider_edges` reference is rejected; `violates_predicate` returns the correct verdict for each of the six predicate rules. Tests assert semantics, not output strings.
9. REQUIREMENT: NEVER use a third-party import-graph tool (`import-linter` etc.) — per ADR § Alternatives Considered Alt 4 and the stdlib-first doctrine, the helper uses `ast` for parsing and dict lookup for layer comparison.
10. REQUIREMENT: NEVER include the operator's personal email in the manifest, the helper, the model, the rule file, the baseline, or any test.

> STOP-on-BLOCKERS: if `src/gzkit/governance/` or `.gzkit/rules/` is absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 1 — quote verbatim** into the brief's Implementation Summary. Decision item 1 is the contract.
- [ ] Parent ADR § Decision — the vertical-cascade table, the Providers table, the Utility table, and the six predicate rules.
- [ ] Parent ADR § Intent — the two-tier "1+2" composition (hexagonal at package level; DDD cascade per-domain).
- [ ] Parent ADR § Q&A Transcript — the late-stage Figure 4-driven refinement (why the tri-role classifier, not pure-vertical).

**Governance (read once, cache):**

- [ ] `.claude/rules/models.md` — Pydantic `ConfigDict(extra="forbid")` contract for `PackageImportManifest`
- [ ] `.gzkit/rules/tests.md` § Tests assert semantics, not strings
- [ ] ADR-0.0.3-hexagonal-architecture-tune-up and ADR-0.0.43-ddd-domain-cascade — the two ADRs this manifest composes

**Context — the empirical surface:**

- [ ] `src/gzkit/` — the flat 40+-subpackage layout the manifest orders
- [ ] The ADR § Q&A Transcript pre-authoring audit edge counts — the input to the tri-role re-classification
- [ ] `gzkit.core.models.RemediationPayload` (ADR-0.0.53) — the failure shape OBPI-02's validator will emit

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/governance/` present
- [ ] `.gzkit/rules/` and `docs/governance/advisory-rules-audit.md` present
- [ ] `data/` directory present

**Existing Code (understand current state):**

- [ ] Existing Pydantic manifest models (e.g. `.gzkit/manifest.json` consumers) for the model convention
- [ ] Existing `ast`-based analysis in `src/gzkit/` for the import-graph parsing convention

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 1 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED tests for the manifest shape and each predicate rule, written before implementation
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] `.gzkit/rules/package-import-direction.md` and the scorecard entry render cleanly
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — this OBPI ships a manifest + helper + model + rule, not an operator-facing CLI behavior. The behavior-bearing surface (the validator) lands in OBPI-02. Waiver noted.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
uv run python -c "import json; m = json.load(open('data/package_layer_order.json')); print('keys:', sorted(m)); assert len(m['vertical_layers']) == 8"
uv run python -c "from gzkit.governance.import_direction import classify, layer_of, violates_predicate; print(classify('cli'), layer_of('cli'), violates_predicate('governance', 'cli'))"
test -f data/package_import_direction_baseline.json
test -f .gzkit/rules/package-import-direction.md
grep -q "package-import-direction" docs/governance/advisory-rules-audit.md
uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_layer_order_manifest
uv run gz validate --documents --advisory-scorecard
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The layer manifest is the single-page tour of the package:
uv run python -c "import json; m = json.load(open('data/package_layer_order.json')); \
[print(f\"L{i}: {l['members']}\") for i, l in enumerate(m['vertical_layers'])]; \
print('Providers:', list(m['providers'])); print('Utility:', m['utility'])"
# The baseline carries only genuine vertical-to-vertical violations:
uv run python -c "import json; print(json.load(open('data/package_import_direction_baseline.json')))"
```

## Acceptance Criteria

- [ ] REQ-0.0.55-01-01: Given parent ADR § Decision item 1, when `data/package_layer_order.json` is read, then it carries `vertical_layers` (8-layer cascade), `providers` (3 with floors), `utility`, and an empty `provider_edges` — matching the ADR § Decision tables.
- [ ] REQ-0.0.55-01-02: Given `src/gzkit/governance/import_direction.py`, when imported, then `compute_import_edges`, `classify`, `layer_of`, and `violates_predicate` are callable and `violates_predicate` implements all six predicate rules.
- [ ] REQ-0.0.55-01-03: Given the `PackageImportManifest` Pydantic model, when a non-contiguous layer index, a dual-role subpackage, or an undeclared `provider_edges` reference is supplied, then validation is rejected.
- [ ] REQ-0.0.55-01-04: Given the rule-surface requirement, when the repo is inspected, then `.gzkit/rules/package-import-direction.md` exists at body version `0.1.0` with `paths: src/gzkit/**/*.py`, and `docs/governance/advisory-rules-audit.md` carries a Mechanical-classified scorecard entry.
- [ ] REQ-0.0.55-01-05: Given `data/package_import_direction_baseline.json`, when it is read, then it carries only genuine predicate violations as `phase: bootstrap` entries, and the tri-role-reclassified edges (`governance → arb`, `governance → hooks`, top-level → `hooks`) are absent.
- [ ] REQ-0.0.55-01-06: Given the scope boundary, when this OBPI's diff is reviewed, then zero `src/gzkit/**` import statements are modified and zero source files are relocated.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 1 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; manifest-shape tests pass; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (implicit, accumulating import order) vs capability-now (declared tri-role manifest + measured baseline)
- [ ] **Key Proof:** The layer-manifest tour; the baseline carrying only genuine vertical-to-vertical violations
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste unittest output + arb-step-unittest receipt ID here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
