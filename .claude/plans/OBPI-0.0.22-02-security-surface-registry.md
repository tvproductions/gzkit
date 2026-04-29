# Plan: OBPI-0.0.22-02 — Security-surface registry data file

## OBPI

`OBPI-0.0.22-02-security-surface-registry`

Parent ADR: `ADR-0.0.22-security-sensitivity-doctrine` (foundation, heavy)

## Context

ADR-0.0.22 codifies `sensitivity` as a third orthogonal classification axis. OBPI-01 already
landed the schema enum and Pydantic frontmatter field (`tests/governance/test_schema_sensitivity.py`,
`tests/models/test_frontmatter_sensitivity.py`). This OBPI authors the registry that
`gz validate --sensitivity` (OBPI-03) will intersect against brief Allowed Paths.

The registry is the "what counts as security-sensitive" data layer. It must be self-bootstrapping:
the first commit (this OBPI) lands the data file, the schema fragment, and the Pydantic model. The
governance contract that future edits require a `sensitivity: security` brief is documented
inline. The bootstrap exception is the parent ADR brief itself — recorded by the rule file
authored in OBPI-06.

This OBPI does NOT author the schema/frontmatter field (OBPI-01, done), the validate scope
(OBPI-03), the audit OR (OBPI-04), the walkthrough extension (OBPI-05), the rule file (OBPI-06),
or the AGENTS.md matrix (OBPI-06). Strict scope discipline per REQ-08.

## Destination-in-mind

The approach decided before plan authoring: a JSON-Schema-validated registry shipped as a
list-of-objects in `data/security_surfaces.json`, with a Pydantic model + glob-matching helper
co-located in `src/gzkit/models/security_surfaces.py`. The governance contract lives in a sibling
README (`data/README-security-surfaces.md`) because JSON cannot carry top-of-file comments — REQ-06
permits the sibling-README form. Tests split unit-tier (model semantics) from
governance-tier (registry on-disk integrity + glob matching).

## Rejected alternatives

1. **YAML-with-comments registry.** Rejected: gzkit's existing data files (`data/flags.json`,
   `data/behave_coverage_waivers.json`) are JSON; introducing YAML for the registry creates a
   parsing-surface inconsistency for one file. Sibling README satisfies REQ-06 cleanly.
2. **Embed glob-matching helper in `src/gzkit/governance/trust_audits.py`.** Rejected: scope
   creep. OBPI-03 will consume the helper from `validate_sensitivity_binding`; placing it in the
   model module keeps OBPI-02's surface tight (the model module already knows the registry
   structure). The audit module imports it.
3. **One JSON object keyed by category vs list of entries.** Rejected: a list shape supports
   future multi-entry-per-category (e.g. two distinct credential paths with different rationales);
   the keyed-object shape forces one entry per category and cannot grow without a schema break.
4. **Hand-author 9 entries from memory.** Rejected: vibe-coded pattern matching. Each glob
   must trace to a real path under `src/`. Plan step 4 below cross-checks each entry against the
   tree.

## Files

**Created:**

- `src/gzkit/schemas/security_surfaces.json` — JSON schema fragment for the registry. Top-level
  is an array of `SecuritySurfaceEntry` objects. Each entry: `category` (enum of 9 names),
  `globs` (non-empty array of strings), `rationale` (non-empty string). `additionalProperties: false`.
- `data/security_surfaces.json` — the registry data file. Array of 9 entries, one per category,
  each with at least one glob pattern + rationale.
- `data/README-security-surfaces.md` — governance contract: edits require a brief carrying
  `sensitivity: security`; bootstrap exception cites parent ADR.
- `src/gzkit/models/security_surfaces.py` — Pydantic `SecuritySurfaceEntry` model with
  `ConfigDict(frozen=True, extra="forbid")`; module-level constants for the canonical category set;
  `load_registry(path: Path) -> tuple[SecuritySurfaceEntry, ...]` loader; `match_globs(globs:
  Sequence[str], registry: Sequence[SecuritySurfaceEntry]) -> tuple[str, ...]` helper for REQ-05.
- `tests/models/test_security_surface_entry.py` — REQ-03, REQ-04. Pydantic construction
  semantics (frozen, extra-forbid, unknown-category rejection, malformed glob rejection,
  extra-key rejection).
- `tests/governance/test_security_surfaces_registry.py` — REQ-01, REQ-02, REQ-05, REQ-06.
  On-disk registry validates against the schema; all 9 canonical categories present each with
  ≥1 glob; `match_globs` returns category labels for intersecting brief allowed-paths;
  governance README exists and references parent ADR.

**Modified:**

- `src/gzkit/models/__init__.py` — re-export `SecuritySurfaceEntry` and `load_registry` /
  `match_globs` so OBPI-03's `validate_sensitivity_binding` has a clean import path.

## Steps

1. **Red:** Author `tests/models/test_security_surface_entry.py` with table-driven tests for
   REQ-03 (unknown category, malformed glob, extra key all rejected with `ValidationError`) and
   REQ-04 (`model_config.frozen is True`, `model_config.extra == "forbid"`). Run; observe import
   failure (module doesn't exist yet) — this is the right RED.
2. **Green:** Author `src/gzkit/models/security_surfaces.py` with `CANONICAL_CATEGORIES` tuple
   (the 9 names from REQ-02), `SecuritySurfaceEntry` model (`category: Literal[...]` constrained
   to the canonical set; `globs: tuple[str, ...]` with min-length validator; `rationale: str`
   with `min_length=1`; `model_config = ConfigDict(frozen=True, extra="forbid")`). Re-run model
   tests; expect GREEN.
3. **Red:** Author the schema fragment `src/gzkit/schemas/security_surfaces.json` and a
   minimal `tests/governance/test_security_surfaces_registry.py::TestSchemaIntegrity` that
   validates a 1-entry fixture against the schema. Schema not yet authored → import/validation
   error → RED.
4. **Green:** Write `src/gzkit/schemas/security_surfaces.json`. Top-level array; per-item object
   with `category` enum (9 names), `globs` (`type: array, minItems: 1, items: {type: string,
   minLength: 1}`), `rationale` (`type: string, minLength: 1`); `required: [category, globs,
   rationale]`; `additionalProperties: false`. Re-run schema-fixture test; GREEN.
5. **Red:** Author `tests/governance/test_security_surfaces_registry.py::TestRegistryContents`
   asserting REQ-01 (registry validates against schema), REQ-02 (all 9 categories present,
   each with ≥1 glob), REQ-06 (sibling README exists and contains the parent ADR ID +
   "sensitivity: security" string + "bootstrap" mention). Registry file doesn't exist → RED.
6. **Green:** Author `data/security_surfaces.json` with 9 entries — one per canonical category.
   Each entry's globs cross-checked against current `src/` tree:
   - `credential_handling`: globs covering credential/auth helper modules (e.g. `src/gzkit/**/*credential*.py`)
   - `subprocess_user_input`: subprocess-invoking modules (e.g. `src/gzkit/utils/git_cmd.py`,
     `src/gzkit/arb/**/*.py`)
   - `crypto_primitives`: hashing/signing modules (e.g. `src/gzkit/**/*hash*.py`)
   - `auth_boundaries`: identity/auth gates (e.g. `src/gzkit/commands/adr_audit.py` —
     `_enforce_human_attestation_authenticity`)
   - `external_api_surfaces`: HTTP/network egress
   - `ledger_integrity`: ledger writers (`src/gzkit/ledger/**/*.py`)
   - `arb_receipt_chain`: ARB receipt emission/validation (`src/gzkit/arb/**/*.py`)
   - `secret_handling`: token/key handling
   - `deserialization_user_input`: yaml/json/pickle loaders on untrusted input
   Each entry carries a one-sentence rationale tying the globs to the category's failure mode.
   Author `data/README-security-surfaces.md` with the governance contract (one brief paragraph
   citing ADR-0.0.22 + the self-bootstrapping clause). Re-run `TestRegistryContents`; GREEN.
7. **Red:** Author `tests/governance/test_security_surfaces_registry.py::TestMatchGlobs` for
   REQ-05: a brief allowed-paths list containing `src/gzkit/arb/validator.py` returns
   `("arb_receipt_chain",)`; an allowed-paths list containing only `docs/**` returns `()`; an
   allowed-paths list intersecting two categories returns both labels. Helper not yet
   exposed → RED.
8. **Green:** Implement `match_globs` in `src/gzkit/models/security_surfaces.py` using
   `fnmatch.fnmatchcase` (stdlib glob matching). Update `src/gzkit/models/__init__.py` to
   re-export `SecuritySurfaceEntry`, `load_registry`, `match_globs`,
   `CANONICAL_CATEGORIES`. Re-run `TestMatchGlobs`; GREEN.
9. **Refactor + verify:**
   - `uv run gz arb ruff` (lint clean — emits arb-ruff-* receipt)
   - `uv run gz arb typecheck` (type clean — emits arb-step-typecheck-* receipt)
   - `uv run gz arb step --name unittest -- uv run -m unittest tests.models.test_security_surface_entry tests.governance.test_security_surfaces_registry -v`
     (focused green — emits arb-step-unittest-* receipt)
   - `uv run gz arb step --name unittest -- uv run -m unittest -q` (full suite green)
   - `uv run gz validate --documents` (heavy lane gate)
10. **REQ → @covers parity:** `uv run gz covers OBPI-0.0.22-02-security-surface-registry --json`
    must report `uncovered_reqs == 0`. REQ-07 (bootstrap-exception narrative) is satisfied by
    the README + this brief itself; REQ-08 (scope discipline) is a negative requirement —
    decorate the registry-contents test that asserts the registry's structure + the absence of
    cross-OBPI artifacts (no validate scope authored, no audit OR, etc.) with `@covers
    REQ-0.0.22-02-07` and `@covers REQ-0.0.22-02-08`.

## Verification

```bash
# Stage 3 baseline (ARB-wrapped)
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents

# Brief-specified verification
test -f data/security_surfaces.json
test -f data/README-security-surfaces.md
test -f src/gzkit/schemas/security_surfaces.json

# OBPI-scoped tests
uv run -m unittest tests.models.test_security_surface_entry tests.governance.test_security_surfaces_registry -v

# REQ → @covers parity gate
uv run gz covers OBPI-0.0.22-02-security-surface-registry --json
```

## Notes

- **Helper function placement (REQ-05).** `match_globs` is part of the model module so OBPI-03
  imports `from gzkit.models import match_globs, load_registry` rather than reaching into
  `gzkit.governance`. Keeps the data + the data shape together.
- **Bootstrap exception (REQ-07).** The parent ADR's brief carries `sensitivity: security` as a
  declared frontmatter value (cannot be auto-detected since the registry doesn't exist before
  this OBPI commits). OBPI-06's rule file records the waiver explicitly. This OBPI does NOT add
  the waiver entry — that's OBPI-06's scope.
- **Scope discipline (REQ-08).** No edits to `src/gzkit/governance/`, `src/gzkit/commands/`,
  `src/gzkit/arb/`, `src/gzkit/cli/`, `.gzkit/rules/`, or `AGENTS.md`. The plan touches only the
  Allowed Paths.
- **Lane: Heavy + foundation-kind + sensitivity:security (declared on parent brief).** Gate 5
  human attestation required at brief level. The current ADR-0.0.22 attestation gate
  (`_requires_security_review_attestation`) is not yet wired up (OBPI-04), so the foundation-kind
  branch of `_requires_human_obpi_attestation` is what fires this attestation gate today.
- **Glob-cross-check discipline.** Step 6 cross-checks each glob against the actual `src/` tree
  via `git ls-files src/gzkit | grep -E <pattern>` before pasting it into the registry. No
  pattern-matching from memory.
