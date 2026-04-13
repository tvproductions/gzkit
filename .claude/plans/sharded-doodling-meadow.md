# OBPI-0.25.0-28 — Layout Verification Pattern (Exclude)

## Context

OBPI-0.25.0-28 is a comparison brief inside ADR-0.25.0 (Core Infrastructure
Pattern Absorption). The task: evaluate `airlineops/src/opsdev/lib/layout_verify.py`
(143 lines) against gzkit's layout verification surface
(`src/gzkit/commands/config_paths.py` 310 lines +
`src/gzkit/validate_pkg/manifest.py` 116 lines) and record one of
**Absorb / Confirm / Exclude** with concrete rationale.

Exploration findings from reading both implementations end-to-end:

1. **Different config abstractions, not two implementations of one schema.**
   airlineops `verify_layout()` loads `config/governance/tree_layout.json` —
   a file that does not exist in gzkit. It validates six hardcoded root
   keys: `source_root`, `config_root`, `data_root`, `artifacts_root`,
   `docs_root`, `ops_tooling_root`. gzkit's equivalent surface reads
   `.gzkit/manifest.json` via `load_manifest()` and `.gzkit.json` via
   `GzkitConfig`, and validates against a declared schema
   (`load_schema("manifest")`). The two modules answer different questions
   about different config files — they are not two implementations of the
   same contract.

2. **gzkit's surface is functionally a superset of what layout_verify.py
   does.** `check_config_paths_cmd()` already covers:
   - Required dirs and files from `config.paths.*` (existence + type)
   - Manifest artifact paths (existence + legacy-OBPI migration contract)
   - Control-surface paths with explicit dir-vs-file type checking for ten
     named control surfaces (hooks, skills, canonical_rules, etc.)
   - OBPI path contract enforcement (rejects deprecated global OBPI paths)
   - **AST-based source literal scanning** — walks `src/gzkit/**/*.py`,
     parses each file, and flags string constants that look like
     filesystem paths but are not covered by any manifest entry. This is
     a unique capability airlineops lacks entirely.
   - `--json` output mode wired to the CLI
   `validate_manifest()` complements this with schema-driven required-field
   validation, returning typed `ValidationError` instances.

3. **airlineops uses the retired `_repo_root_from_here()` anti-pattern.**
   `layout_verify.py:13-19` derives repo root via
   `Path(__file__).resolve().parents[3]`. This is the exact anti-pattern
   gzkit removed in OBPI-0.0.7-04 ("Hooks module migration") as part of
   ADR-0.0.7's config-first resolution discipline. Absorbing the module
   wholesale would **regress** prior governance work. (Same anti-pattern
   concern as OBPI-0.25.0-27 flagged in `guards.py`.)

4. **Airline-specific checks.** `verify_layout()` has a hardcoded semantic
   check at line 121-126: "ops_tooling_root should contain opsdev package"
   — this assumes the presence of an "opsdev" package under the tooling
   root, which is an airlineops-only concern.

5. **`_is_within()` path escape check is a non-problem for gzkit.** The
   only isolated robustness helper in layout_verify.py is a 7-line
   `_is_within(path, parent)` function that catches paths escaping the
   repo via `Path.resolve().relative_to()`. This solves the threat of
   user-supplied runtime paths escaping root — but gzkit's config paths
   come from trusted in-repo JSON (`.gzkit.json`, `.gzkit/manifest.json`)
   loaded through `GzkitConfig` with schema validation. Paths are
   concatenated as `project_root / rel_path` where `rel_path` is a
   committed string under version control. Path escape is not a live
   threat model, unlike the `_safe_print` case in OBPI-27 where the
   Windows cp1252 crash was a concrete pre-commit risk.

**Subtraction test.** Strip airline-specific pieces (tree_layout.json
schema, required root names `ops_tooling_root`/`artifacts_root`,
`_repo_root_from_here()`, opsdev package semantic check) and nothing novel
remains. The only residue is `_is_within()`, which addresses a threat model
gzkit does not have.

**Decision: Exclude.** This OBPI absorbs no code from airlineops. gzkit's
layout verification surface (`config_paths.py` + `validate_pkg/manifest.py`)
is architecturally superior and already covers every capability
`layout_verify.py` provides. No narrow robustness feature exists that
concretely benefits gzkit (contrast with OBPI-0.25.0-27, where
`_safe_print` was directly applicable to gzkit's pre-commit Windows path).

This is a **documentation-only** decision. No `src/` or `tests/` code
changes. No new test file. Gate 4 BDD is `N/A` because no operator-visible
behavior changes.

## Implementation

### 1. Update the OBPI brief

Edit `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-28-layout-verification-pattern.md`:

- Add **§Capability Comparison** table with concrete dimensions: config
  source, API design, root resolution, validation scope, data model,
  schema validation, CLI integration, unique features, convention
  compliance, subtraction test.
- Add **§Decision: Exclude** with the 5-point rationale above.
- Populate **§Gate 1–5 checklist** marked per actual evidence.
- Add **§Gate 4 (BDD): N/A** subsection explaining no operator-visible
  behavior change (no code absorbed, so no external surface to exercise).
- Add **§Implementation Summary** describing that no code was absorbed and
  why gzkit's existing surface is sufficient.
- Add **§Key Proof** (three verification commands + expected output) —
  subtraction proof, decision-present proof, and existing-gzkit-surface
  proof.
- Add **§Closing Argument** narrative tying evidence to decision.
- Leave **§Human Attestation** section blank until Stage 4 ceremony;
  `uv run gz obpi complete` will populate it atomically in Stage 5.

### 2. No code changes, no new tests

`src/gzkit/commands/config_paths.py` and `src/gzkit/validate_pkg/manifest.py`
remain untouched. No files in `tests/` change. Existing test coverage for
these modules already proves gzkit's superior surface works — no new
evidence is required by an Exclude decision. The brief allowlist permits
edits to `src/gzkit/` and `tests/`, but point 5 of the rationale above
establishes that a hardening backport of `_is_within()` is not warranted.

## Critical files

| Path | Action | Reason |
|------|--------|--------|
| `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-28-layout-verification-pattern.md` | Edit | Record Exclude decision, rationale, gate checklist, ceremony content |

## Reuse

- Follows the comparison-brief template established by sibling Exclude
  decisions: OBPI-0.25.0-15 (manifests), OBPI-0.25.0-14 (os),
  OBPI-0.25.0-12 (admission), OBPI-0.25.0-10 (errors),
  OBPI-0.25.0-08 (ledger), OBPI-0.25.0-07 (types), OBPI-0.25.0-06
  (registry), OBPI-0.25.0-05 (dataset version), OBPI-0.25.0-04
  (world state), OBPI-0.25.0-03 (signature).
- gzkit's existing validation surface is untouched: `check_config_paths_cmd`
  in `src/gzkit/commands/config_paths.py:263` and `validate_manifest` in
  `src/gzkit/validate_pkg/manifest.py:10`.

## Verification

Stage 3 Phase 1 (baseline):

```bash
uv run gz lint
uv run gz typecheck
uv run gz test                              # full suite incl. behave
uv run gz validate --documents              # heavy lane
uv run mkdocs build --strict                # heavy lane
```

Stage 3 Phase 1b (REQ → @covers parity):

```bash
uv run gz covers OBPI-0.25.0-28-layout-verification-pattern --json
# Expected: summary.uncovered_reqs == 0 (comparison briefs report
# total_reqs == 0 — the REQs are stated as brief acceptance criteria,
# not as Requirements-section entries the canonical scanner parses,
# so parity is trivially satisfied)
```

Stage 3 Phase 2 (brief-specific):

```bash
test -f ../airlineops/src/opsdev/lib/layout_verify.py
# Expected: airlineops source under review exists

test -f src/gzkit/validate_pkg/manifest.py
# Expected: gzkit comparison target exists

rg -n 'Decision: Exclude' \
  docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-28-layout-verification-pattern.md
# Expected: one match — "## Decision: Exclude"
```

Out-of-scope: `features/core_infrastructure.feature` — Gate 4 BDD is `N/A`
because no operator-visible behavior changes (no code absorbed).
