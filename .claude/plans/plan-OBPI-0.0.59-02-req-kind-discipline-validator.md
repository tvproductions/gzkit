# OBPI-0.0.59-02: REQ Kind Discipline Validator

## Context

ADR-0.0.59 Decision item 2: ship the mechanical brief-time enforcement surface
for the REQ scope discipline taxonomy. OBPI-0.0.59-01 (doctrine) already landed;
this OBPI ships the validator, Pydantic models, scaffold update, and docs.

Key constraint: existing `src/gzkit/triangle.py` has `ReqKind(CODE, DOC)` — new
three-kind taxonomy goes in a separate module `src/gzkit/req_kind.py`.

Validator scope: opt-in (`--req-kind-discipline`) + wired into `gz check` via
`quality.py`. Strict for mixed-state briefs; lenient for all-untagged legacy briefs.

## Files

| File | Action |
|------|--------|
| `src/gzkit/req_kind.py` | CREATE — ReqKind, ProofChannel, ReqClassification Pydantic models |
| `tests/governance/test_req_kind_discipline.py` | CREATE — unit tests for all REQs |
| `src/gzkit/commands/validate_cmd.py` | EDIT — add `_validate_req_kind_discipline()`, `check_req_kind_discipline` param, scope registration |
| `src/gzkit/cli/parser_maintenance.py` | EDIT — add `--req-kind-discipline` argparse flag |
| `src/gzkit/quality.py` | EDIT — add `run_req_kind_discipline_audit` function |
| `src/gzkit/commands/quality.py` | EDIT — add step to `_build_check_steps()` |
| `.gzkit/skills/gz-obpi-specify/SKILL.md` | EDIT — add § REQ Kind Authoring section |
| `docs/governance/req-scope-discipline.md` | EDIT — add § Brief-time validation section |

## Steps

### Step 1 — Author `src/gzkit/req_kind.py` (Pydantic models)

Write the three-kind taxonomy module:
- `ReqKind(StrEnum)`: BEHAVIOR, SUPPORT, STRUCTURAL_FENCE
- `ProofChannel(StrEnum)`: TEST_COVERS, LEDGER_PLUS_VALIDATOR, PARENT_ADR_INVARIANT
- `ReqClassification(BaseModel)`: req_id str, kind ReqKind, proof_channel ProofChannel, proof_status str
  - `ConfigDict(frozen=True, extra="forbid")`
  - `kind_to_channel()` class method returning the canonical channel for a kind

### Step 2 — Write RED tests in `tests/governance/test_req_kind_discipline.py`

TDD: write failing tests for all 6 REQs BEFORE implementing the validator:
- `TestReqKindModels` — verify models, enums, ConfigDict
- `TestReqKindDisciplineValidator` — mock brief content to test each validator check:
  - Mixed-state brief (tagged + untagged) → exits 3
  - All-untagged brief → passes (legacy mode)
  - BEHAVIOR REQ without tests/** in Allowed Paths → exits 3
  - SUPPORT REQ without gz validate scope + ledger keyword → exits 3
  - STRUCTURAL-FENCE REQ without parent-ADR § Boundary Invariants → exits 3
  - Clean brief (all tagged, all citations present) → exits 0
- `TestReqKindDisciplineInGzCheck` — verify step appears in `_build_check_steps()`

### Step 3 — Implement `_validate_req_kind_discipline()` in `validate_cmd.py`

Core validator logic:
1. Find all OBPI briefs under `docs/design/adr/`
2. For each brief, parse `## Acceptance Criteria` for REQs
3. Check for mixed-state (tagged + untagged) → ValidationError(type="req_kind_discipline", ...)
4. For each tagged REQ, check per-kind proof-citation gaps
5. Return `list[ValidationError]`

Per-kind checks:
- `[BEHAVIOR]`: scan `## Allowed Paths` for `tests/**` pattern
- `[SUPPORT]`: scan REQ text for `gz validate --` and ledger event keyword (artifact_edited/obpi_created/etc.)
- `[STRUCTURAL-FENCE]`: read parent ADR file, check for `## Boundary Invariants` heading

### Step 4 — Wire into `validate_cmd.py` function signature

Add:
- `check_req_kind_discipline: bool = False` parameter
- Include in `_other_scopes_active`
- Add to `opt_in_scopes` list
- Register in scope_checks dict and audit dispatch

### Step 5 — Add `--req-kind-discipline` flag in `parser_maintenance.py`

Following the `--brief-headings` pattern (action="store_true", dest="check_req_kind_discipline").
Pass through to `validate()` call.

### Step 6 — Add `run_req_kind_discipline_audit` to `quality.py`

Following the `run_kind_invariance_audit` pattern:
- Call `gz validate --req-kind-discipline` subprocess
- Return `CheckStepResult` (success=True/False)

### Step 7 — Add step to `_build_check_steps()` in `commands/quality.py`

Add `("REQ kind discipline", run_req_kind_discipline_audit)` to the step list.

### Step 8 — Update `.gzkit/skills/gz-obpi-specify/SKILL.md`

Add § REQ Kind Authoring section after the Acceptance Criteria guidance:
- BEHAVIOR: code behavior, functions, CLI outputs → `@covers` test in `tests/**`
- SUPPORT: governance artifacts, docs → `gz validate --X` + ledger event citation
- STRUCTURAL-FENCE: ADR-boundary invariants → parent-ADR `## Boundary Invariants`
- Syntax: `REQ-X.Y.Z-NN-NN [KIND]: claim text`
Bump skill-version. Run `uv run gz agent sync control-surfaces`.

### Step 9 — Extend `docs/governance/req-scope-discipline.md`

Add § Brief-time validation:
- `gz validate --req-kind-discipline` behavior
- Per-kind proof-citation syntax with examples
- Exit codes (0=clean, 3=policy breach)

### Step 10 — Run GREEN (make tests pass)

Run `uv run -m unittest tests.governance.test_req_kind_discipline -v` until green.

### Step 11 — Run full quality suite

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
uv run gz validate --documents
```

## Verification

```bash
uv run gz validate --req-kind-discipline
uv run gz check | grep -i "kind discipline"
uv run -m unittest tests.governance.test_req_kind_discipline -v
python -c "from gzkit.req_kind import ReqKind, ProofChannel, ReqClassification; print('ok')"
```
