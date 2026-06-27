# Plan: OBPI-0.0.74-13 — Mx Proxy Reality Detector

**OBPI:** OBPI-0.0.74-13-mx-proxy-reality-detector
**Parent ADR:** ADR-0.0.74-mx-mode-maintenance-hangar
**Lane:** Heavy

## Plan-Before-Exploration Disclosures

**Destination-in-mind:** Before writing this plan I had already concluded that
`proxy_reality.py` would define `scan()` reading the ledger for
`obpi_completion_repudiated` events with `model-induced-fabrication` cause, plus
a live NC registered via `@enforces("grader-gaming", ...)`.

**Rejected alternatives:**
- Registering `@enforces("grader-gaming", ...)` inside `invariants.py` alongside the
  gate5 claims. Rejected: `proxy_reality.py` is the brief-designated home; mixing
  it into invariants would blur the OBPI-13 / OBPI-17 boundary.
- Using a procedural `enforce()` call outside the decorator pattern. Rejected: the
  `@enforces` decorator is the established enforcement-claim surface (ADR-0.0.74-15).

## Context

- `src/gzkit/mx/invariants.py` exists with `grader-gaming` in `GATE5_INVARIANTS` ✓
- `Ledger.query(event_type="obpi_completion_repudiated")` returns `list[LedgerEvent]`;
  `event.extra["cause"]` carries the cause string; `event.extra["repudiated_receipt"]`
  names the receipt being repudiated.
- `_EventBase.extra` property — backward-compat dict of non-base fields.
- Enforcement: `from gzkit.enforcement import enforces, set_known_claims`
- Fixture/entrypoint shape mirrors `_qc_negative_controls.py` and `invariants.py` gate5 NCs.
- Test convention from `tests/mx/test_checkpoint.py`: `unittest.TestCase`, `@covers(REQ)`,
  `TemporaryDirectory`, `Path` helpers.

## Files Created

- `src/gzkit/mx/proxy_reality.py` — detector + @enforces registration
- `tests/mx/test_proxy_reality.py` — unit tests + live NC test

## Files Modified

_(none — allowed paths only)_

## Steps

### Step 1 — RED: write failing test for REQ-01 (scan detects repudiated events)

Create `tests/mx/test_proxy_reality.py` with a skeleton import and one test:
`TestScan.test_scan_counts_model_induced_fabrication` — asserts that `scan()` over a
temp ledger containing one `obpi_completion_repudiated` event with
`cause: model-induced-fabrication` returns `count == 1` and a record naming the
clearing gate.

Watch it fail: first with an import/collection error, then after adding an
importable stub (the module exists but `scan()` raises NotImplementedError or
returns count=0), watch it fail on the assertion for the right reason.

### Step 2 — GREEN: implement `scan()` in proxy_reality.py

Create `src/gzkit/mx/proxy_reality.py`:

```python
ProxyRealityRecord(BaseModel, frozen=True, extra="forbid"):
    obpi_id: str
    repudiated_receipt: str
    clearing_gate: str  # always "gate5" (Gate-5 attestation cleared the OBPI)
    cause: str

ProxyRealityScanResult(BaseModel, frozen=True, extra="forbid"):
    records: list[ProxyRealityRecord]
    count: int

def scan(root: Path | None = None) -> ProxyRealityScanResult:
    """Read the ledger for gate-green-but-reality-wrong signals."""
    # Uses Ledger(root).query(event_type="obpi_completion_repudiated")
    # Filters for cause == "model-induced-fabrication"
    # Returns records + count
```

Run test — watch it pass.

### Step 3 — REFACTOR

Clean up, confirm ruff/ty pass.

### Step 4 — RED: write failing test for REQ-02 (live negative control)

Add `TestLiveNegativeControl.test_live_nc_catches_planted_violation` to the test module:
- Calls `_build_proxy_reality_violation()` to get a temp root
- Calls `_ep_proxy_reality(temp_root)` directly
- Asserts result is truthy (violation was caught)

Watch it fail on NameError (functions not defined yet).

### Step 5 — GREEN: add `_build_proxy_reality_violation` + `_ep_proxy_reality` + @enforces

In `proxy_reality.py`:

```python
_PROXY_REALITY_CLAIM_IDS: frozenset[str] = frozenset({"grader-gaming"})

def _build_proxy_reality_violation() -> Path:
    """Plant a known proxy-reality violation: a ledger with a model-induced-fabrication
    repudiation event. The runner removes the temp dir after the entrypoint runs."""
    root = Path(tempfile.mkdtemp(prefix="gzkit-proxy-reality-nc-"))
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text(
        json.dumps({
            "schema": "gzkit.ledger.v1",
            "event": "obpi_completion_repudiated",
            "id": "OBPI-0.0.74-13-nc-test",
            "ts": "2026-01-01T00:00:00+00:00",
            "repudiated_receipt": "nc-test-receipt",
            "cause": "model-induced-fabrication",
            "attestor": "nc-test",
            "reason": "planted for live NC",
        }) + "\n",
        encoding="utf-8",
    )
    return root

def _ep_proxy_reality(root: Path) -> int:
    """Production entrypoint: run the real scan() on the fixture root.
    Returns count — truthy (> 0) when the violation is caught."""
    return scan(root).count

def _ensure_grader_gaming_registered() -> None:
    """Register the grader-gaming @enforces claim (idempotent)."""
    from gzkit.governance.trust_audits._qc_negative_controls import _KNOWN_QC_CLAIM_IDS
    set_known_claims(_KNOWN_QC_CLAIM_IDS | _PROXY_REALITY_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if "grader-gaming" not in existing:
        enforces("grader-gaming", _build_proxy_reality_violation, _ep_proxy_reality)(_marker)

def _marker() -> None:
    """Inert carrier for @enforces registration."""
```

Run test — watch it pass.

### Step 6 — REFACTOR + full quality checks

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests.mx.test_proxy_reality -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Verification

```bash
test -f src/gzkit/mx/proxy_reality.py
test -f tests/mx/test_proxy_reality.py
uv run gz covers OBPI-0.0.74-13-mx-proxy-reality-detector --json
uv run gz validate --documents
```

## Notes

- `req_atomic` is declared in frontmatter — no TASK subdivision required.
- REQ-03 is [structural-fence]; its proof channel is BI#5 + the live `@enforces`
  registration in proxy_reality.py (per OBPI-18 structural-fence proof upgrade).
- Demo: `uv run python -c "from gzkit.mx import proxy_reality; r = proxy_reality.scan(); print('proxy-reality distance count:', r.count)"`
