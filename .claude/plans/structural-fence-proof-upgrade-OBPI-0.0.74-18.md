# Plan: OBPI-0.0.74-18 — Structural Fence Proof Upgrade

**OBPI:** OBPI-0.0.74-18-structural-fence-proof-upgrade
**Parent ADR:** ADR-0.0.74-mx-mode-maintenance-hangar
**Lane:** Heavy
**Date:** 2026-06-25

## Context

`resolve_fence_proof` in `src/gzkit/req_kind.py` currently resolves ALL
`[structural-fence]` REQs the same way: check whether the parent ADR has a
`## Boundary Invariants` heading. This allows an enforcement-asserting fence REQ
(one whose claim text declares something is enforced/validated/fail-closed/gated)
to pass on a prose anchor alone — a facade identical to §5's original problem.

The amendment distinguishes two subtypes:
- **Enforcement-asserting**: REQ text contains enforcement vocabulary
  (`@enforces`, `enforcement`, `fail-closes`, `live nc`, `live negative control`,
  `_negative_control_debt`). These require a live `@enforces` NC in the
  enforcement registry to resolve "pass".
- **State-property**: Non-enforcement text. These continue to resolve via the
  `## Boundary Invariants` anchor (no change to existing behavior).

## Files

- `src/gzkit/req_kind.py` — amend `resolve_fence_proof` and update `_enrich`
- `tests/governance/test_fence_proof_live_nc.py` — CREATE: unit tests for both paths

## Steps

### Step 1: Add `_ENFORCEMENT_FENCE_KEYWORDS` and `_is_enforcement_asserting` to `req_kind.py`

Add after `_BOUNDARY_INVARIANTS_HEADING` (line ~78):

```python
_ENFORCEMENT_FENCE_KEYWORDS: tuple[str, ...] = (
    "@enforces",
    "enforcement",
    "fail-closes",
    "live nc",
    "live negative control",
    "_negative_control_debt",
)


def _is_enforcement_asserting(req_text: str) -> bool:
    """Return True if the REQ text asserts enforcement rather than a state-property."""
    lower = req_text.lower()
    return any(kw in lower for kw in _ENFORCEMENT_FENCE_KEYWORDS)
```

### Step 2: Amend `resolve_fence_proof` signature and body

Change signature from `(req_id: str, project_root: Path) -> str` to
`(req_id: str, project_root: Path, req_text: str = "") -> str`.

Add enforcement-asserting path before the anchor-only path:

```python
if _is_enforcement_asserting(req_text):
    from gzkit.enforcement import get_enforcement_registry  # noqa: PLC0415
    return "pass" if get_enforcement_registry() else "unproven-fence"
```

The anchor-only path follows unchanged for state-property fences. Backward
compatibility: existing 2-arg callers (e.g. `closeout_proof.py`) get `req_text=""`
which `_is_enforcement_asserting` returns False for → unchanged anchor path.

### Step 3: Update call site in `_enrich` (req_kind.py line ~454)

Change the STRUCTURAL_FENCE branch of `_enrich` from:
```python
else:  # STRUCTURAL_FENCE
    if project_root is not None:
        proof_status = resolve_fence_proof(entry.req_id, project_root)
```
to:
```python
else:  # STRUCTURAL_FENCE
    if project_root is not None:
        req_text = dreq.entity.description if dreq else ""
        proof_status = resolve_fence_proof(entry.req_id, project_root, req_text)
```

### Step 4: Create `tests/governance/test_fence_proof_live_nc.py`

TDD (RED first for enforcement path, then GREEN):

- `TestEnforcementAssertingFencePath`:
  - `test_enforcement_asserting_with_live_nc_resolves_pass` @covers REQ-0.0.74-18-01
  - `test_enforcement_asserting_without_nc_resolves_unproven_fence` @covers REQ-0.0.74-18-01
  - `test_enforcement_asserting_keywords_detected` @covers REQ-0.0.74-18-01
- `TestStatePropertyFencePath`:
  - `test_state_property_with_anchor_resolves_pass` @covers REQ-0.0.74-18-02
  - `test_state_property_without_anchor_resolves_unproven_fence` @covers REQ-0.0.74-18-02
  - `test_empty_req_text_uses_anchor_path` @covers REQ-0.0.74-18-02
  - `test_non_enforcement_keywords_do_not_trigger_nc_path` @covers REQ-0.0.74-18-02

Use `reset_enforcement_registry()` / `set_known_claims()` from enforcement.py
for test isolation. Create fake ADR structures in `tempfile.TemporaryDirectory()`.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_fence_proof_live_nc -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run mkdocs build --strict
```

## Notes

- `closeout_proof.py` is DENIED PATH — it calls `resolve_fence_proof(req_id, project_root)`
  (2-arg form). The `req_text=""` default ensures no regression there.
- The enforcement registry check (`get_enforcement_registry()`) uses a lazy import
  to avoid a module-load cycle. The import pattern mirrors `closeout_proof.py`'s
  lazy imports from `gzkit.req_kind`.
- REQ-18-03 is STRUCTURAL-FENCE — proved at ADR closeout via parent ADR
  Boundary Invariants #10. No @covers test needed.
