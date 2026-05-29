# Implementation Plan: OBPI-0.0.63-03 — evidence-summary-and-proof-binding

## Context

ADR-0.0.63 Decision items 4 & 5 require:
- (4) Evidence Summary Template gains a REQ column binding (REQ-ID, receipt-ID, file-line range) in markdown + structured JSON
- (5) New `gz validate --closeout-proof-binding` fails closed (exit 3) when a REQ in an ADR at closeout lacks a ledger-present receipt-ID binding

The structured binding surface (`ln` field, model `ReqEvidence`) was owned by the unpromoted `ADR-pool.obpi-authoring-mechanical-floor` item 2. Per operator direction (schema-first M2 decision 2026-05-29), OBPI-03 folds the field-add in as its first consumer; OBPI-06 will consume it in the runtime. This is a producer/first-consumer pattern — no new OBPI-08.

ADR-0.0.63 Checklist item #3 and Target Scope #3 are already expanded (done pre-plan). Pool ADR Decision item 2 is already marked relocated (done pre-plan). Brief is fully authored with real REQs, Allowed Paths, and Decisions Made.

## Files to Create / Modify

### 1. `src/gzkit/governance/brief_structure.py` — add ReqEvidence + ln field

```python
class ReqEvidence(BaseModel):
    """Structured REQ↔receipt-ID proof-binding entry (ADR-0.0.63 / OBPI-03)."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    req_id: str = Field(..., description="REQ identifier e.g. REQ-0.0.63-03-02")
    receipt_ids: list[str] = Field(..., min_length=0, description="Cited receipt IDs")
    file_lines: list[str] = Field(default_factory=list, description="file:line references")
```

Add to `BriefStructure`:
```python
ln: list[ReqEvidence] = Field(
    default_factory=list,
    description="REQ↔receipt-ID proof-binding entries (ADR-0.0.63 / OBPI-03). Optional at authoring; required by gz validate --closeout-proof-binding at closeout.",
)
```

Legacy-safety: `ln` is NOT in the `required` set check (`{"allowlist", "reqs", "verification"}`), so briefs without `ln` continue to load as `BriefStructure` unchanged.

### 2. `src/gzkit/schemas/obpi_brief_structure.json` — mirror the model

Add optional `ln` property (NOT in `"required"`):
```json
"ln": {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["req_id", "receipt_ids"],
    "properties": {
      "req_id": {"type": "string"},
      "receipt_ids": {"type": "array", "items": {"type": "string"}},
      "file_lines": {"type": "array", "items": {"type": "string"}}
    },
    "additionalProperties": false
  },
  "description": "REQ↔receipt-ID proof-binding entries (ADR-0.0.63 / OBPI-03)"
}
```

### 3. `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — NEW scope function

Mirror `advisor_proof_binding.py` structure. Public API:

```python
def validate_closeout_proof_binding(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for REQs with no ledger-present receipt-ID binding.

    In-scope ADRs: those with a persisted ceremony state file at
    .gzkit/ceremonies/<ADR-ID>.ceremony.json. For each in-scope ADR:
    - load all OBPI briefs under docs/design/adr/**/{adr_id}/obpis/
    - parse each brief via parse_brief() → BriefStructure
    - for each REQ in BriefStructure.reqs, check ln has a matching entry with
      non-empty receipt_ids, and each receipt_id resolves to an existing receipt
      artifact (artifacts/receipts/<receipt_id>.json)
    - emit ValidationError(type="closeout_proof_binding", ...) per violation
    """
```

Private helpers:
- `_iter_ceremony_adrs(project_root) -> Iterator[str]` — glob `.gzkit/ceremonies/*.ceremony.json`, read JSON, yield `adr_id`
- `_find_adr_dir(project_root, adr_id) -> Path | None` — search `docs/design/adr/` for directory matching `adr_id`
- `_receipt_exists(project_root, receipt_id) -> bool` — `(project_root / "artifacts" / "receipts" / f"{receipt_id}.json").exists()`

ValidationError type: `"closeout_proof_binding"` (routes to exit 3 via `_POLICY_BREACH_ERROR_TYPES`).

### 4. `src/gzkit/governance/trust_audits/__init__.py`

Add import + `__all__` entry (mirror the `advisor_proof_binding` lines 30-31, 182):
```python
from gzkit.governance.trust_audits.closeout_proof_binding import (
    validate_closeout_proof_binding,
)
```
Add `"validate_closeout_proof_binding"` to `__all__`.

### 5. `src/gzkit/cli/parser_maintenance.py`

Mirror the `--advisor-proof-binding` block (~line 583):
```python
p_validate.add_argument(
    "--closeout-proof-binding",
    dest="check_closeout_proof_binding",
    action="store_true",
    help="Validate REQ↔receipt-ID proof-binding for ADRs with active closeout ceremony (ADR-0.0.63 / OBPI-03); exit 3 on any REQ with no ledger-present receipt-ID",
)
```

And in `set_defaults` (~line 768):
```python
check_closeout_proof_binding=a.check_closeout_proof_binding,
```

### 6. `src/gzkit/commands/validate_cmd.py` — ~7 sites (mirror advisor_proof_binding)

| Site | Change |
|------|--------|
| `_collect_errors()` signature | Add `check_closeout_proof_binding: bool = False` |
| `explicit_scopes` dict | `"closeout_proof_binding": check_closeout_proof_binding` |
| `_explicit_scope_runners()` | `"closeout_proof_binding": lambda: trust_audits.validate_closeout_proof_binding(project_root)` |
| `_POLICY_BREACH_ERROR_TYPES` frozenset | Add `"closeout_proof_binding"` |
| `validate()` signature | Add `check_closeout_proof_binding: bool = False` |
| `validate()` call to `_collect_errors()` | Add `check_closeout_proof_binding=check_closeout_proof_binding` |
| Final checks dict | `"closeout_proof_binding": check_closeout_proof_binding` |

### 7. `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` — lines 285-339, REQ column

In the Evidence Summary Template, expand Table 3b (Quality Evidence) to add a REQ column:

```
| Command | Result | Receipt ID | REQ Bindings | Notes |
|---------|--------|------------|--------------|-------|
| `uv run gz arb ruff` | Pass | `arb-ruff-...` | REQ-X.Y.Z-NN-MM | ... |
```

Also add a brief `**3c. REQ↔Receipt-ID Binding (structured)**` subsection noting that OBPI briefs carrying a `ln:` frontmatter field provide structured bindings consumed by `gz validate --closeout-proof-binding`.

Bump `skill-version:` and `last_reviewed:` (2026-05-29). Then run `uv run gz agent sync control-surfaces`.

### 8. `docs/user/manpages/validate.md` — document `--closeout-proof-binding`

Add to Usage section and add a new `### \`--closeout-proof-binding\`` section documenting: scope (ADRs with ceremony state), check (REQ→receipt-ID, ledger-present), exit code (3 on missing binding), example invocation `uv run gz validate --closeout-proof-binding`.

### 9. `tests/governance/test_closeout_proof_binding.py` — NEW, REQ-derived

| Test | REQ |
|------|-----|
| `TestReqEvidenceModel::test_legacy_brief_parses_without_ln` | REQ-0.0.63-03-01 (no `ln` key → empty list) |
| `TestReqEvidenceModel::test_brief_with_ln_roundtrips` | REQ-0.0.63-03-01 (with `ln` → correct model) |
| `TestValidateCloseoutProofBinding::test_unbound_req_fails_closed` | REQ-0.0.63-03-02 |
| `TestValidateCloseoutProofBinding::test_typo_receipt_id_fails_closed` | REQ-0.0.63-03-03 |
| `TestValidateCloseoutProofBinding::test_all_reqs_bound_passes` | REQ-0.0.63-03-04 |

Use `@covers("REQ-0.0.63-03-0N")` decorators. Tests use `tmp_path` fixtures with synthetic ceremony state and brief files — no live ADR directory required.

## Order of Operations (TDD — Red then Green)

1. Write tests (RED) — all fail because neither model field nor validator exists
2. Add `ReqEvidence` + `ln` to `brief_structure.py` and `obpi_brief_structure.json` (REQ-01 tests GREEN)
3. Create `closeout_proof_binding.py` scope function (REQ-02/03/04 tests GREEN)
4. Wire `__init__.py` export
5. Wire `parser_maintenance.py` + `validate_cmd.py` (~7 sites)
6. Edit SKILL.md REQ column + sync
7. Edit manpage
8. Run `uv run gz arb ruff`, `uv run gz arb typecheck`, `uv run gz arb step --name unittest`, `uv run gz arb step --name mkdocs`, `uv run gz cli audit`

## Key Reuse

- `gzkit.governance.brief_structure.parse_brief` — loads each OBPI brief; already handles legacy vs structured
- `gzkit.governance.trust_audits.advisor_proof_binding` — wiring template (exact mirror)
- `gzkit.core.validation_rules.ValidationError` — shared error model
- The `explicit_scopes` / `_explicit_scope_runners` dispatch in `validate_cmd.py` — opt-in scope registry

## Verification

```bash
uv run gz validate --closeout-proof-binding
uv run gz arb ruff
uv run gz arb step --name typecheck -- uvx ty check .
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz cli audit
```

Exit 0 on all = gates green. `gz cli audit` must show `--closeout-proof-binding` documented.
