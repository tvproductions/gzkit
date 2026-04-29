# Plan: OBPI-0.0.22-01 — Schema + frontmatter field for sensitivity axis

**Brief:** `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/obpis/OBPI-0.0.22-01-schema-frontmatter-field.md`
**Parent ADR:** ADR-0.0.22-security-sensitivity-doctrine (foundation, heavy)
**Lane:** Heavy. **Kind:** foundation. **Attestation:** brief-level human attestation required.

## Context

ADR-0.0.22 codifies a third orthogonal classification axis (`sensitivity`) alongside the existing `kind` and `lane` axes. This OBPI is the parallel-root #1 of six: it lands the schema + Pydantic surface for the new field with no behavioral coupling to the registry (OBPI-02), the validate scope (OBPI-03), the audit OR (OBPI-04), the walkthrough extension (OBPI-05), or the rule file (OBPI-06).

Scope is purely additive: the field is optional, defaults to absent, and existing artifacts validate cleanly without modification (REQ-05 — the backwards-compatibility floor).

### Destination-in-mind (Step 6a disclosure)

Before writing this plan I had already concluded:
- Add `"sensitivity": {"type": "string", "enum": ["security"]}` (no `null`/no required) to both schemas under `properties.frontmatter.properties`.
- Add `sensitivity: Literal["security"] | None = None` to both `AdrFrontmatter` and `ObpiFrontmatter` in `src/gzkit/core/models.py`.
- Test surface: new directory `tests/models/` with a table-driven `test_frontmatter_sensitivity.py` covering REQ-01 through REQ-04; new file `tests/governance/test_schema_sensitivity.py` covering schema-level acceptance/rejection plus the REQ-05 backwards-compatibility audit.

### Rejected alternatives considered

1. **Required field with default** (`sensitivity: Literal["security", "absent"] = "absent"`) — rejected because the brief and ADR explicitly require the field stay optional/absent for backwards compatibility (REQ-02, REQ-05). A defaulted-required field would survive Pydantic-level reads but would force a frontmatter migration on ~150 existing briefs, contradicting the parallel-root design.
2. **Open string (`sensitivity: str | None`) with separate validator** — rejected because `Literal["security"] | None` gives the same compile-time and Pydantic-validation guarantee with less surface, and the ADR explicitly calls for an enum at the schema level. Open string would force REQ-03 to live inside a custom validator, drifting from the schema.
3. **Modify existing `tests/test_core_models.py` and `tests/test_schemas.py`** — rejected because those files are outside the brief Allowed Paths. Creating new test files under `tests/models/` and `tests/governance/` keeps every edit within the allowlist; the existing tests are not touched.

## Files

### Files to modify

- `src/gzkit/schemas/adr.json` — add `sensitivity` enum to `properties.frontmatter.properties`. **Not** added to `required`.
- `src/gzkit/schemas/obpi.json` — same shape as adr.json change.
- `src/gzkit/core/models.py` — add `sensitivity: Literal["security"] | None = None` to `AdrFrontmatter` (after `date`) and `ObpiFrontmatter` (after `status`).

### Files to create

- `tests/models/__init__.py` — empty package marker (this directory does not yet exist).
- `tests/models/test_frontmatter_sensitivity.py` — table-driven Pydantic tests for REQ-01..REQ-04.
- `tests/governance/test_schema_sensitivity.py` — JSON schema validation tests covering REQ-01..REQ-03 plus the REQ-05 backwards-compatibility audit over every existing ADR/OBPI under `docs/design/adr/**`.

### Files NOT touched (out of scope per the brief)

- `data/security_surfaces.json` — OBPI-02 scope.
- `src/gzkit/governance/trust_audits.py` — OBPI-03 scope (`gz validate --sensitivity`).
- `src/gzkit/commands/adr_audit.py` — OBPI-04 scope (audit OR).
- `src/gzkit/commands/obpi.py` — OBPI-05 scope (walkthrough extension).
- `src/gzkit/arb/validator.py` — OBPI-05 scope (canonical command slot).
- `.gzkit/rules/security-sensitivity.md`, `AGENTS.md` matrix — OBPI-06 scope.

## Steps

Each step maps to one or more REQs. Red-Green-Refactor per increment.

### Step 1 — RED: Schema-level acceptance/rejection tests (REQ-01, REQ-02, REQ-03)

Create `tests/governance/test_schema_sensitivity.py`:

- `test_adr_schema_accepts_sensitivity_security` (REQ-01): build minimal valid ADR frontmatter dict, add `sensitivity: "security"`, jsonschema validates without error.
- `test_obpi_schema_accepts_sensitivity_security` (REQ-01): same shape against `obpi.json`.
- `test_adr_schema_accepts_absent_sensitivity` (REQ-02): minimal valid ADR frontmatter dict without `sensitivity` key, jsonschema validates.
- `test_obpi_schema_accepts_absent_sensitivity` (REQ-02): same shape against `obpi.json`.
- `test_adr_schema_rejects_unknown_sensitivity_value` (REQ-03): `sensitivity: "confidential"` → `jsonschema.ValidationError` whose `path` references `sensitivity`.
- `test_obpi_schema_rejects_unknown_sensitivity_value` (REQ-03): same shape against `obpi.json`.

Run `uv run -m unittest tests.governance.test_schema_sensitivity -v` — expect failures (sensitivity field not yet in schemas). RED observed.

### Step 2 — GREEN: Add `sensitivity` to both JSON schemas (REQ-01, REQ-02, REQ-03)

Edit `src/gzkit/schemas/adr.json`: under `properties.frontmatter.properties`, add

```json
"sensitivity": {
  "type": "string",
  "enum": ["security"],
  "description": "Security sensitivity classification (ADR-0.0.22). Optional; absent ⇒ no security gate. Auto-detected from Allowed Paths in OBPI-03; this OBPI lands only the field surface."
}
```

Same shape into `src/gzkit/schemas/obpi.json`. Field is **not** added to `required`.

Re-run schema tests. GREEN.

### Step 3 — RED: Pydantic model tests (REQ-04)

Create `tests/models/__init__.py` (empty).

Create `tests/models/test_frontmatter_sensitivity.py` with a table-driven `unittest.TestCase`:

- `test_adr_frontmatter_accepts_sensitivity_security` — construct `AdrFrontmatter(... sensitivity="security")`, assert `.sensitivity == "security"`.
- `test_adr_frontmatter_defaults_sensitivity_to_none` — construct without `sensitivity`, assert `.sensitivity is None`.
- `test_adr_frontmatter_rejects_unknown_sensitivity_value` — construct with `sensitivity="confidential"`, expect `pydantic.ValidationError`.
- Three matching cases for `ObpiFrontmatter`.
- One immutability check per model — `frozen=True` is preserved (assigning `.sensitivity` raises).

Run `uv run -m unittest tests.models.test_frontmatter_sensitivity -v` — RED expected (field not on models yet).

### Step 4 — GREEN: Add `sensitivity` to Pydantic models (REQ-04)

Edit `src/gzkit/core/models.py`:

- In `AdrFrontmatter`, after `date`, add:
  `sensitivity: Literal["security"] | None = None`
- In `ObpiFrontmatter`, after `status`, add the same line.

Re-run Pydantic tests. GREEN.

> **Note:** `extra="allow"` is preserved on both models (matches current behavior; extra frontmatter fields like `depends_on`, `dependencies`, `date` continue to be accepted). Brief REQ-04 mentions `extra="forbid"` — that text is at odds with the live model config (`extra="allow"`), and switching to `forbid` would break existing briefs that carry `depends_on`/`dependencies`. Implementing the field as a typed optional `Literal` enforces the enum invariant the REQ actually requires; the `extra="forbid"` clause is treated as brief drift and noted as a tracked defect (see *Tracked defects*). This is consistent with `additionalProperties: true` in both JSON schemas.

### Step 5 — RED: REQ-05 backwards-compatibility audit

In `tests/governance/test_schema_sensitivity.py`, add:

- `test_existing_artifacts_validate_without_sensitivity` (REQ-05): walk every `*.md` under `docs/design/adr/**`, parse the YAML frontmatter via the project's existing frontmatter loader, and assert that for ADRs (`AdrFrontmatter`) and OBPIs (`ObpiFrontmatter`) construction succeeds. Use the existing `gzkit.core.models.validate_frontmatter_model` helper if it covers this; otherwise instantiate the model directly. Skip files that are not ADRs/OBPIs (e.g. `ADR-CLOSEOUT-FORM.md`).

Run the test — at this point it should pass already (the field is optional). If it fails, that's a pre-existing frontmatter drift defect, not OBPI-01 scope. Record observed pass/fail, then GREEN.

### Step 6 — Refactor

Tighten table parametrization, deduplicate the minimal-valid-frontmatter fixture between schema and Pydantic test files. Do not add new behavior.

### Step 7 — Quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.models.test_frontmatter_sensitivity tests.governance.test_schema_sensitivity -v
uv run gz arb step --name unittest -- uv run -m unittest -q  # full sweep
uv run gz validate --documents
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict  # heavy lane
```

Heavy-lane BDD (`gz arb step --name behave`): no new feature scenario for this OBPI — schema field surfaces with no operator-visible CLI behavior change in this increment. The brief's BDD scenarios will land alongside OBPI-03 (where `gz validate --sensitivity` becomes operator-visible). Add an entry to `data/behave_coverage_waivers.json` keyed by `OBPI-0.0.22-01` with rationale "schema-only OBPI; BDD deferred to OBPI-03 where the validate scope becomes CLI-visible" — the waiver is the canonical mechanism per `.gzkit/rules/tests.md` § Scope discipline.

### Step 8 — Coverage of `@covers` REQ parity

Decorate or document each new test with `@covers REQ-0.0.22-01-NN`. Verify:

```bash
uv run gz covers OBPI-0.0.22-01-schema-frontmatter-field --json
```

`uncovered_reqs == 0`. Stage 4 evidence table requires the file:line for each REQ.

## Verification

The brief's verification block, ARB-wrapped:

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
test -f docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md
uv run gz covers OBPI-0.0.22-01-schema-frontmatter-field --json
```

## Notes

### Tracked defects (to surface in evidence, not to fix in this OBPI)

- Brief REQ-04 references `extra="forbid"` while the canonical model config is `extra="allow"`. The OBPI implements the typed `Literal["security"] | None` constraint that REQ-04's *intent* requires; the `extra="forbid"` clause is brief drift. If the operator wants the model config tightened, that is a separate scope (would break existing briefs with `dependencies`/`depends_on` keys).

### Scope-collision warnings (advisory)

`gz plan audit` flagged 203 sibling-ADR overlaps. All but one are with **pending** ADRs (0.31, 0.32, 0.34, 0.35, 0.39, 0.0.33) whose work has not landed; the only validated overlap is ADR-0.0.17 on `src/gzkit/schemas/adr.json`, which is closed and additive-compatible. No blocker.

### Stage-4 attestation note

Heavy + foundation ⇒ brief-level human attestation required at Gate 5. The TTY+`ATTEST` gate at `_enforce_human_attestation_authenticity` will fire. The pipeline will pause at Stage 4 and present the evidence template; the operator types `attest completed` (or equivalent), then Stage 5 invokes `gz obpi complete --attestor-present` per pipeline GHI #292.
