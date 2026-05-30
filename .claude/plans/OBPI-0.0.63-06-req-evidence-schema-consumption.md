# Plan: OBPI-0.0.63-06-req-evidence-schema-consumption

## OBPI

OBPI-0.0.63-06-req-evidence-schema-consumption

## Objective

Wire the closeout ceremony runtime to mechanically consume the `ln: list[ReqEvidence]`
field from OBPI brief frontmatter (added by OBPI-0.0.63-03). Three changes:

1. `ceremony_data.py::extract_brief_metadata()` gains `ln_entries` extraction
2. `ceremony_steps.py::render_step_6_attestation()` renders the REQ↔receipt binding
   table from `ln_entries` (mechanical section 3c, not prose instruction)
3. `closeout_ceremony.py` gains a proof-binding gate at the EXECUTE→ATTESTATION edge

## Files

**Modified:**
- `src/gzkit/commands/ceremony_data.py` — add `ln_entries` to `extract_brief_metadata()` return dict
- `src/gzkit/commands/ceremony_steps.py` — add binding table to `render_step_6_attestation()`
- `src/gzkit/commands/closeout_ceremony.py` — add `_gate_proof_binding()` called in `_commit_advance()`

**Created:**
- `tests/governance/test_ceremony_ln_consumption.py` — REQ-derived tests (new file)

## Steps

### Step 1 — Write failing tests (RED)

**CREATE** tests/governance/test_ceremony_ln_consumption.py

Write tests derived from the four REQs. Each test asserts semantic behavior, not strings.

```python
# REQ-0.0.63-06-01: extract_brief_metadata returns ln_entries
class TestExtractBriefMetadataLnEntries(unittest.TestCase):
    def test_ln_entries_extracted_when_present(self):
        # brief with ln: frontmatter -> meta["ln_entries"] contains the data
    def test_ln_entries_empty_when_absent(self):
        # brief without ln: -> meta["ln_entries"] == []

# REQ-0.0.63-06-02: render_step_6_attestation renders binding table
class TestRenderStep6AttestationBindingTable(unittest.TestCase):
    def test_binding_table_present_when_ln_entries_provided(self):
        # render with non-empty ln_entries -> output contains req_id in table form
    def test_binding_table_absent_when_no_ln_entries(self):
        # render with empty ln_entries -> original prose remains, no table

# REQ-0.0.63-06-03: EXECUTE->ATTESTATION gate fails on missing binding
class TestProofBindingGateFailClose(unittest.TestCase):
    def test_gate_raises_policy_breach_on_unbound_reqs(self):
        # _gate_proof_binding with unbound REQs -> PolicyBreachError

# REQ-0.0.63-06-04: gate passes on valid binding
class TestProofBindingGatePass(unittest.TestCase):
    def test_gate_passes_when_all_reqs_bound(self):
        # _gate_proof_binding with all REQs bound -> no exception
```

Run: `uv run -m unittest tests/governance/test_ceremony_ln_consumption.py -v` — all tests FAIL (RED).

### Step 2 — Implement `extract_brief_metadata` ln_entries extraction (GREEN for REQ-01)

In `src/gzkit/commands/ceremony_data.py`, update `extract_brief_metadata()`:

After the existing frontmatter parsing loop (which extracts `id`, `status`, `lane`),
add a YAML parse of the frontmatter block to extract `ln` entries:

```python
# In the frontmatter parsing section (after the existing line-scan loop)
# Parse full frontmatter via yaml.safe_load to extract ln entries
meta["ln_entries"] = []
if lines and lines[0].strip() == "---":
    fm_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)
    fm_text = "\n".join(fm_lines)
    import yaml
    fm = yaml.safe_load(fm_text) or {}
    raw_ln = fm.get("ln") or []
    for entry in raw_ln:
        if isinstance(entry, dict):
            meta["ln_entries"].append({
                "req_id": entry.get("req_id", ""),
                "receipt_ids": entry.get("receipt_ids") or [],
                "file_lines": entry.get("file_lines") or [],
            })
```

`yaml` is already imported indirectly (via `gzkit.governance.brief_structure`). Check the existing imports in `ceremony_data.py` and add `import yaml` at the top if not present.

Run: `uv run -m unittest tests/governance/test_ceremony_ln_consumption.py::TestExtractBriefMetadataLnEntries -v` — GREEN.

### Step 3 — Implement `render_step_6_attestation` binding table (GREEN for REQ-02)

In `src/gzkit/commands/ceremony_steps.py`, update `render_step_6_attestation()` signature:

```python
def render_step_6_attestation(adr_id: str, ln_entries: list[dict] | None = None) -> str:
```

When `ln_entries` is non-empty, append the structured REQ↔receipt binding table
before the attestation instructions:

```python
if ln_entries:
    table_lines = [
        "",
        "REQ↔Receipt Binding (from brief `ln:` field):",
        "",
        "| REQ | Receipt IDs | File Lines |",
        "|-----|-------------|------------|",
    ]
    for entry in ln_entries:
        req_id = entry.get("req_id", "")
        receipts = ", ".join(entry.get("receipt_ids") or []) or "(none)"
        files = ", ".join(entry.get("file_lines") or []) or ""
        table_lines.append(f"| {req_id} | {receipts} | {files} |")
    # Insert the table after "The walkthrough is complete..." paragraph
```

The caller in `_present_step` must pass `ln_entries` from the obpi_files metadata.
Find where `render_step_6_attestation` is called in `closeout_ceremony.py::_present_step`
and update that call to extract `ln_entries` from the brief files.

Run: `uv run -m unittest tests/governance/test_ceremony_ln_consumption.py::TestRenderStep6AttestationBindingTable -v` — GREEN.

### Step 4 — Add `_gate_proof_binding` in `closeout_ceremony.py` (GREEN for REQ-03, REQ-04)

In `src/gzkit/commands/closeout_ceremony.py`, add a new gate function:

```python
def _gate_proof_binding(project_root: Path, state: CeremonyState) -> None:
    """Fail-close EXECUTE -> ATTESTATION when proof binding is incomplete.

    Called in _commit_advance at the EXECUTE->ATTESTATION edge. Calls
    validate_closeout_proof_binding — if any REQ is unbound, PolicyBreachError
    is raised naming the unbound REQs. Gate is no-op for all other transitions.
    """
    if state.current_step != CeremonyStep.EXECUTE:
        return
    from gzkit.governance.trust_audits.closeout_proof_binding import (
        validate_closeout_proof_binding,
    )
    errors = validate_closeout_proof_binding(project_root)
    if not errors:
        return
    from gzkit.core.exceptions import PolicyBreachError

    unbound = [e.message for e in errors[:5]]  # cap to 5 for readability
    raise PolicyBreachError(
        "EXECUTE -> ATTESTATION transition blocked: proof binding incomplete.\n"
        + "\n".join(f"  {m}" for m in unbound)
        + (f"\n  ... and {len(errors) - 5} more" if len(errors) > 5 else "")
        + "\nFix the brief's `ln:` field to bind each REQ to a ledger-present receipt-ID,"
        " then retry."
    )
```

In `_commit_advance`, add the call:

```python
def _commit_advance(...) -> None:
    _gate_proof_binding(project_root, state)   # <- add before _gate_attestation_boundary
    _gate_attestation_boundary(project_root, state)
    ...
```

Run: `uv run -m unittest tests/governance/test_ceremony_ln_consumption.py -v` — all 6 tests GREEN.

### Step 5 — Quality checks

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
uv run gz arb typecheck
```

Confirm module sizes stay under 600 lines:
```bash
wc -l src/gzkit/commands/ceremony_data.py src/gzkit/commands/ceremony_steps.py src/gzkit/commands/closeout_ceremony.py
```

### Step 6 — Verify covers parity

```bash
uv run gz covers OBPI-0.0.63-06-req-evidence-schema-consumption --json
```

All 4 REQs must show `covered: true`.

## Verification

```bash
uv run gz validate --documents
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_ceremony_ln_consumption.py -v
uv run gz covers OBPI-0.0.63-06-req-evidence-schema-consumption --json
```

## Notes

- `_gate_proof_binding` is a no-op for all ceremony steps except EXECUTE — so
  the gate only fires at the EXECUTE→ATTESTATION edge (Step 5→6).
- The validator scope is "ADRs with persisted ceremony state" — the gate is only
  active during an in-progress ceremony.
- `render_step_6_attestation` keeps the existing prose when `ln_entries` is empty,
  so the gate is additive: no regression on briefs that haven't adopted `ln:` yet.
- Sibling-ADR scope collisions (advisory) are from completed OBPIs — no active
  lock conflicts.

## Destination-in-mind (Step 6a disclosure)

Before writing this plan, I had already concluded:
- Implementation reading = C (Gate + Renderer), operator-confirmed
- Target functions = `extract_brief_metadata`, `render_step_6_attestation`, `_commit_advance`
- New gate function = `_gate_proof_binding` mirroring `_gate_attestation_boundary` pattern

## Rejected alternatives

1. Gate at Step 6→7 (ATTESTATION→CLOSEOUT) instead of Step 5→6: Rejected — blocks after
   the operator has already attested; worse UX and BI-3's "cannot be self-advanced" language
   points at preventing advancement TO attestation when evidence is incomplete.
2. Renderer-only (Reading B): Rejected — operator confirmed C; no gate means the ceremony
   can advance past EXECUTE without mechanical proof-binding enforcement.
3. Use `parse_brief()` + `BriefStructure.ln` instead of raw YAML in `extract_brief_metadata`:
   Rejected — `extract_brief_metadata` is a legacy dict-returning function that doesn't use
   `parse_brief`; adding typed parsing would require a larger refactor and introduces the
   permissive-mode DeprecationWarning path into ceremony rendering. Raw YAML extraction
   mirrors how `closeout_proof_binding.py` reads `ln` and keeps the change surgical.
