# Plan: OBPI-0.30.0-03-okf-conformance-validator

**OBPI:** OBPI-0.30.0-03-okf-conformance-validator
**Parent ADR:** ADR-0.30.0-okf-documentation-knowledge-structure
**Lane:** Heavy

## Context

OBPI-0.30.0-01 (model) and OBPI-0.30.0-02 (bundle generator + `.gzkit/governance/knowledge/`) are
complete. This OBPI adds `gz validate --okf-conformance`, which checks ONLY the generated OKF
bundle for well-formedness — parseable frontmatter, non-empty `type`, reserved `index.md`/`log.md`
structure — without ever gating authored source documents. It also carries the STRUCTURAL-FENCE
REQ (REQ-05) that no `gz validate` / gates / closeout surface consumes OKF data as enforcement
evidence, audited at ADR-closeout layer.

**Bundle detection rule:** the validator recognizes a bundle by its reserved files (`index.md`/`log.md`)
plus concept docs that carry `type` frontmatter — NEVER by an `okf/`-format folder name.

## Files

### New
- `src/gzkit/governance/trust_audits/okf_conformance.py` — validator module
- `tests/governance/test_okf_conformance.py` — REQ-derived unittest cases

### Modified
- `src/gzkit/governance/trust_audits/__init__.py` — re-export `audit_okf_conformance`
- `src/gzkit/commands/validate_cmd.py` — add `_ScopeEntry("okf_conformance", ...)` + `check_okf_conformance` param
- `src/gzkit/cli/parser_maintenance.py` — register `--okf-conformance` flag
- `docs/user/manpages/validate.md` — document the new scope

## Steps (TDD — Red-Green-Refactor per behavior)

### Step 1: Write failing tests (RED phase)

Write `tests/governance/test_okf_conformance.py` with unittest cases derived from the brief REQs:

- **REQ-01 test** (`test_clean_bundle_exits_0`): Given the real `.gzkit/governance/knowledge/`
  bundle (a clean generated bundle), call `audit_okf_conformance(project_root)` and assert it
  returns an empty list (exit-0 semantics).

- **REQ-02a test** (`test_malformed_frontmatter_exits_3`): Given a temp bundle with a file
  containing unparseable frontmatter (e.g. `type: [unclosed`), assert the audit returns at least
  one `ValidationError` naming the file and the `frontmatter` field.

- **REQ-02b test** (`test_empty_type_exits_3`): Given a temp bundle with a concept doc where
  `type: ""` (empty), assert a ValidationError naming the file and `type` field.

- **REQ-02c test** (`test_missing_type_exits_3`): Given a temp bundle with a concept doc with no
  `type` key in frontmatter, assert a ValidationError naming the file and `type` field.

- **REQ-03 test** (`test_authored_source_doc_not_gated`): Given an authored source doc with no
  OKF frontmatter (e.g. `docs/governance/state-doctrine.md`), calling `audit_okf_conformance`
  with a project root where no bundle exists (no `index.md`/`log.md` in the governed path)
  should return no errors for that file. Alternatively: inject a fixture temp dir where the
  bundle dir contains only concept docs (no `index.md`), confirm the validator does NOT scan
  arbitrary source dirs.

Run `uv run -m unittest tests.governance.test_okf_conformance -v` — expect failures (ModuleNotFoundError or AttributeError because the module doesn't exist yet). Get to assertion-level failures by creating an empty stub.

### Step 2: Implement `okf_conformance.py` (GREEN phase)

Create `src/gzkit/governance/trust_audits/okf_conformance.py`:

```
Bundle detection:
  - Walk the project root looking for directories that contain BOTH an `index.md`
    AND at least one concept doc with parseable YAML frontmatter containing `type`.
  - Also detect if a bundle root itself has an `index.md` at `.gzkit/governance/knowledge/`.
  - The CURRENT real bundle is at `.gzkit/governance/knowledge/` — detect by checking
    for an `index.md` in that root (canonical path), plus any other discovered bundle roots.

Per-file validation (for each non-reserved markdown file in a bundle root):
  - Parse YAML frontmatter (between `---` delimiters) using the `yaml` stdlib module.
  - If frontmatter is unparseable: emit ValidationError(type="okf_conformance",
    artifact=<path>, message="<file>: unparseable frontmatter (field: frontmatter)")
  - If frontmatter is missing `type` key or has empty `type`: emit ValidationError
    naming the file and field "type".
  - Reserved files (`index.md`, `log.md`): validate they have parseable frontmatter
    but do NOT require `type` (they are structure files, not concept docs). Index
    files require a title or description for OKF structure.

Return list[ValidationError] — empty = clean, non-empty = exits 3.
```

Public function: `def audit_okf_conformance(project_root: Path) -> list[ValidationError]`.

Run tests — watch them go GREEN one by one.

### Step 3: Wire the scope

**`trust_audits/__init__.py`:** Add `audit_okf_conformance` re-export alongside the other audits.

**`validate_cmd.py`:**
1. Add `_ScopeEntry("okf_conformance", "explicit", True, lambda r, _f: _ta().audit_okf_conformance(r))` after the `closeout_proof` entry (end of the explicit scopes section around line 408).
2. Add `check_okf_conformance: bool = False` parameter to the validate function signature (around line 1286 pattern).
3. Add `"okf_conformance": check_okf_conformance` to the scope-dispatch dict.

**`parser_maintenance.py`:**
1. Add the `--okf-conformance` flag after `--closeout-proof` (around line 593 pattern):
   ```python
   parser.add_argument(
       "--okf-conformance",
       dest="check_okf_conformance",
       action="store_true",
       default=False,
       help="OKF bundle conformance (ADR-0.30.0 / OBPI-0.30.0-03). Exit 0: clean bundle; 3: malformed file.",
   )
   ```
2. Wire `check_okf_conformance=a.check_okf_conformance` in the function call (around line 799 pattern).

Run `uv run -m unittest tests.governance.test_okf_conformance -v` — all GREEN.
Run `uv run gz validate --okf-conformance` — exit 0 on the real bundle.

### Step 4: Update `docs/user/manpages/validate.md`

1. Add `[--okf-conformance]` to the Synopsis line (adjacent to `[--closeout-proof]`).
2. Add a `### --okf-conformance` section (after `### --router-tables` or `### --closeout-proof`):
   - Description: generated-bundle-only OKF conformance check (OBPI-03, ADR-0.30.0)
   - What it checks: parseable frontmatter, non-empty `type` on concept docs, reserved `index.md`/`log.md` structure
   - What it does NOT do: does not gate authored source documents (Boundary Invariant 2)
   - Exit codes: 0 = clean, 3 = malformed file (names the file and field)
   - Example usage
3. Add row to the summary/options table at the end: `| --okf-conformance | opt-in | ... |`

Run `uv run gz cli audit` — confirm exit 0 (new flag covered in manpage).
Run `uv run gz validate --documents` — confirm exit 0.

### Step 5: Quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --okf-conformance
uv run gz cli audit
uv run mkdocs build --strict
```

Run `uv run gz covers OBPI-0.30.0-03-okf-conformance-validator --json` to confirm parity
(REQ-01, REQ-02, REQ-03 covered by `@covers` decorators in test file;
REQ-04 covered by `artifact_edited` ledger event + cli-audit/validate-documents passing;
REQ-05 is STRUCTURAL-FENCE audited at ADR closeout, not a per-OBPI test).

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_okf_conformance -v
uv run gz validate --okf-conformance
uv run gz cli audit
uv run mkdocs build --strict
```

## Notes

- The validator does NOT import `ConceptFrontmatter` from `gzkit.knowledge` to parse —
  the model validates via Pydantic, but the audit needs raw YAML parsing to distinguish
  frontmatter-unparseable from missing-type (two different error messages naming different
  fields). Use `yaml.safe_load()` directly.
- Bundle root detection uses `.gzkit/governance/knowledge/` as the canonical path for the
  real project bundle. For tests, use `tempfile.TemporaryDirectory` to create fixture bundles.
- `exit_code=3` maps to `ValidationError` entries with `type="okf_conformance"` (policy_breach).
  The `run_validate` orchestrator maps non-empty lists to exit 3 via the existing error-type
  policy.
- REQ-05 (STRUCTURAL-FENCE) is a STRUCTURAL-FENCE REQ kind — proof is via the parent ADR's
  `## Boundary Invariants` entry, audited at ADR closeout. No per-OBPI behavior test is needed;
  the brief's `@covers` for REQ-05 is the ADR-closeout layer check.
