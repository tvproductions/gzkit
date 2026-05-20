# Implementation Plan: OBPI-0.0.37-05 Brief Reconciliation Engine

**OBPI:** OBPI-0.0.37-05-brief-reconcile-engine
**ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy
**Approach committed before plan was written:** Pure-function engine using `BriefStructure` (OBPI-04) for parsing; reuse `_known_cli_verbs()` from `trust_audits/cli.py` for verb resolution.
**Rejected alternatives:** (1) Monolithic single-file implementation — rejected for the same reason trust_audits is a package; per-dimension modules stay composable. (2) Adding ledger emission to the engine — explicitly denied by REQ-08 (pure); ledger belongs to OBPI-06. (3) Heavy validator-first (default scope) — `--brief-reconcile` is explicit-scope only since reconciling every brief on every `gz check` run pays reconcile cost repeatedly.

---

## Files

| Path | Action |
|------|--------|
| `src/gzkit/governance/brief_reconcile.py` | **Create** — engine entry point with `ReconcileResult` + dimension delta dataclasses + `reconcile_brief()` |
| `src/gzkit/governance/trust_audits/brief_reconcile.py` | **Create** — `validate_brief_reconcile(root)` validator-scope wrapper |
| `src/gzkit/governance/trust_audits/__init__.py` | **Modify** — import + re-export `validate_brief_reconcile` |
| `tests/governance/test_brief_reconcile.py` | **Create** — REQ-derived unit tests using fixture briefs |
| `tests/fixtures/brief_reconcile/` | **Create** — fixture directory with 6 fixture brief files |
| `features/brief_reconcile.feature` | **Create** — BDD scenarios tagged `@REQ-0.0.37-05-*` |
| `docs/governance/advisory-rules-audit.md` | **Modify** — scorecard entry #59 under new section |
| `src/gzkit/cli/parser_maintenance.py` | **Modify** — add `--brief-reconcile` flag to `gz validate` |
| `src/gzkit/commands/validate_cmd.py` | **Modify** — wire `check_brief_reconcile` parameter + scope runner |
| `docs/design/adr/.../OBPI-0.0.37-05-brief-reconcile-engine.md` | **Modify** — update evidence sections |

---

## Creates These Files

- `src/gzkit/governance/brief_reconcile.py`
- `src/gzkit/governance/trust_audits/brief_reconcile.py`
- `tests/governance/test_brief_reconcile.py`
- `tests/fixtures/brief_reconcile/`
- `features/brief_reconcile.feature`

---

## Steps

### Step 1: Create engine data structures and `reconcile_brief()` entry point

**File:** `src/gzkit/governance/brief_reconcile.py`

Create the pure reconciliation engine:
- Five frozen delta dataclasses: `AllowlistDelta`, `DiscoveryDelta`, `VerificationDelta`, `ReqCountDelta`, `CitationDelta`
- Frozen `ReconcileResult` dataclass with all five dimension fields + `brief_id: str` + `has_drift: bool`
- `reconcile_brief(brief_path: Path, project_root: Path) -> ReconcileResult` — main entry point
  - Parse the brief via `brief_structure.parse_brief()` (OBPI-04 surface)
  - For `LegacyBriefShape`: fall back to regex-based extraction from raw_body
  - Allowlist dimension: check each path in `BriefStructure.allowlist` for on-disk existence; check src/ files imported in REQ test files but absent from allowlist
  - Discovery Checklist dimension: parse `## Discovery Checklist` bullet paths from brief body; check on-disk existence
  - Verification verbs dimension: parse `gz <verb>` references from `## Verification` section; resolve each against `_known_cli_verbs()` from `trust_audits/cli.py` (import lazily to avoid circular)
  - REQ count dimension: compare `len(BriefStructure.reqs)` against checkbox count in `## Acceptance Criteria`
  - Citation tuples dimension: check each `(artifact_path, anchor)` in `BriefStructure.citations` for file existence and anchor presence

**Key implementation notes:**
- Engine is pure: no I/O side effects beyond file reads; no ledger writes
- Use `from __future__ import annotations` and `dataclasses.dataclass(frozen=True)`
- Lazy import of `_known_cli_verbs` inside the verb-resolution helper to avoid circular import
- For `LegacyBriefShape`, check `## Verification` block with `re.compile(r'`gz\s+([a-z][a-z0-9-]*)')`
- For Discovery Checklist: match `- \[ \].*\b(src/|docs/|tests/|features/|\.gzkit/)(\S+)` pattern
- REQ count: count `^- \[ \]` checkbox items in the `## Acceptance Criteria` section

### Step 2: Create fixture directory and fixture brief files

**Directory:** `tests/fixtures/brief_reconcile/`

Create 6 fixture brief files (minimal YAML frontmatter + key sections):
1. `passing.md` — all paths exist, verbs valid, REQ count matches, citations valid → `has_drift=False`
2. `allowlist_drift.md` — allowlisted path doesn't exist on disk → `missing_on_disk` non-empty
3. `discovery_drift.md` — Discovery Checklist references a non-existent path → `unresolved_paths` non-empty
4. `verb_drift.md` — Verification section references unregistered `gz` verb → `unresolved_verbs` non-empty
5. `req_count_drift.md` — 3 REQs declared but only 2 acceptance criteria checkboxes → `delta != 0`
6. `citation_drift.md` — citation references a non-existent file → `stale_citations` non-empty

Fixtures use LegacyBriefShape format (no structured frontmatter) for the drifted cases so they can be self-contained. The `passing.md` fixture references real project paths.

### Step 3: Write REQ-derived unit tests

**File:** `tests/governance/test_brief_reconcile.py`

Test classes (TDD: write tests first, then verify engine passes):
- `TestReconcileBriefResult`: REQ-01 — engine returns `ReconcileResult` with correct `brief_id`, all five delta fields, `has_drift`
- `TestAllowlistDimension`: REQ-02 — `missing_on_disk` for non-existent allowlisted path; `missing_in_brief` for imported-but-not-allowlisted src/ file
- `TestDiscoveryDimension`: (via REQ-01 coverage) — `unresolved_paths` for non-existent Discovery Checklist path
- `TestVerificationVerbDimension`: REQ-03 — `unresolved_verbs` for unregistered verb
- `TestReqCountDimension`: REQ-04 — `delta != 0` when REQ count ≠ acceptance criteria count
- `TestCitationDimension`: REQ-05 — `stale_citations` for non-existent artifact path
- `TestValidateBriefReconcile`: REQ-06 — `validate_brief_reconcile()` returns empty list when no drift; returns ERROR-severity errors when drift found
- `TestEnginePurity`: REQ-07/08 — engine writes no files, emits no ledger events

Decorate each test class/method with `@covers("REQ-0.0.37-05-NN")`.

### Step 4: Create the validator-scope wrapper

**File:** `src/gzkit/governance/trust_audits/brief_reconcile.py`

```python
def validate_brief_reconcile(root: Path) -> list[ValidationError]:
    """Walk all OBPI briefs; return ERROR-severity ValidationErrors for any with drift."""
```

- Walk `docs/design/adr/**/{obpis,briefs}/OBPI-*.md`
- Call `reconcile_brief(brief_path, root)` for each
- If `result.has_drift`: emit one `ValidationError(type="brief_reconcile", artifact=..., message=...)` per dimension with drift
- Exit code 3 is driven by `gz validate`'s error-type-to-exit-code mapping (existing pattern)

### Step 5: Register in trust_audits `__init__.py`

**File:** `src/gzkit/governance/trust_audits/__init__.py`

Add import and `__all__` entry:
```python
from gzkit.governance.trust_audits.brief_reconcile import validate_brief_reconcile
```
Add `"validate_brief_reconcile"` to `__all__`.

### Step 6: Wire `--brief-reconcile` flag into `gz validate`

**File:** `src/gzkit/cli/parser_maintenance.py`

After the `--invariant-coherence` block (line ~568):
```python
p_validate.add_argument(
    "--brief-reconcile",
    dest="check_brief_reconcile",
    action="store_true",
    help="Validate OBPI brief corpus against project shape across five drift dimensions (OBPI-0.0.37-05).",
)
```

Add `check_brief_reconcile=a.check_brief_reconcile` to the `validate(...)` call in the handler.

**File:** `src/gzkit/commands/validate_cmd.py`

Add `check_brief_reconcile: bool = False` parameter to `validate()`. Add to `explicit_scopes` dict:
```python
"brief_reconcile": check_brief_reconcile,
```
Add runner in `_explicit_scope_runners()`:
```python
"brief_reconcile": lambda: trust_audits.validate_brief_reconcile(project_root),
```

### Step 7: Create BDD feature file

**File:** `features/brief_reconcile.feature`

Scenarios covering each dimension, tagged `@REQ-0.0.37-05-01` through `@REQ-0.0.37-05-07`:
- `@REQ-0.0.37-05-01 Scenario: reconcile_brief returns ReconcileResult`
- `@REQ-0.0.37-05-02 Scenario: allowlist dimension detects missing path`
- `@REQ-0.0.37-05-03 Scenario: verification verb dimension detects unregistered verb`
- `@REQ-0.0.37-05-04 Scenario: req count dimension detects mismatch`
- `@REQ-0.0.37-05-05 Scenario: citation dimension detects stale citation`
- `@REQ-0.0.37-05-06 Scenario: gz validate --brief-reconcile exits 0 on clean tree`
- `@REQ-0.0.37-05-07 Scenario: engine writes no files and emits no ledger events`

### Step 8: Add advisory-rules-audit.md scorecard entry

**File:** `docs/governance/advisory-rules-audit.md`

Add new section after `### Constitutional Invariant Composition` section:

```markdown
### Brief Reconciliation Invariant (CIC-2) (`ADR-0.0.37` / OBPI-0.0.37-05)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 59 | OBPI brief reconciles against current project shape before Stage 2 and before completion | **Mechanical** | Enforced by `gz validate --brief-reconcile` (OBPI-0.0.37-05, `src/gzkit/governance/trust_audits/brief_reconcile.py`) — walks all OBPI briefs, computes per-dimension delta across five drift classes (allowlist, Discovery Checklist, Verification verbs, REQ counts, citation tuples); reports ERROR severity per dimension with drift; exits 3 on any drift. Scorecard citation: ADR-0.0.37 (parent), OBPI-0.0.37-05 (engine), OBPI-0.0.37-06 (CLI verb). |
```

Update Summary counts: Mechanical +1 (40 → 41).

---

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_brief_reconcile -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers OBPI-0.0.37-05-brief-reconcile-engine --json
uv run gz validate --brief-reconcile
uv run -m behave features/brief_reconcile.feature --tags=REQ-0.0.37-05
```

---

## Notes

- **Circular import guard:** `_known_cli_verbs` is imported lazily inside the verb-resolution helper (same pattern as `trust_audits/cli.py` imports its argparse surface lazily)
- **REQ-02 allowlist dimension (missing_in_brief):** scan test files that would cover the brief's REQs for `from gzkit.<module>` imports where `src/<module path>` is not in the allowlist — this is advisory (non-fatal) since OBPI-06 handles amendments
- **Exit code:** The `validate_brief_reconcile` function returns `ValidationError` objects with type `"brief_reconcile"`. The existing `gz validate` exit-code dispatch maps `ValidationError` items to exit code 3 when error type matches the scope name and severity is ERROR — this is the existing pattern already working for other validators
- **Scope-collision advisory warnings** from `gz plan audit` are advisory only; `trust_audits/__init__.py` and `advisory-rules-audit.md` are legitimately touched by many OBPIs and the collision is expected
