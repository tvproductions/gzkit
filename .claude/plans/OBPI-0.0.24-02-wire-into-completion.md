# Plan: OBPI-0.0.24-02 — Wire receipt-binding gate into completion

**OBPI:** `OBPI-0.0.24-02-wire-into-completion`
**Parent ADR:** `ADR-0.0.24-attestation-receipt-binding` (kind=foundation, lane=heavy)
**Mode:** Normal (no Exception declared on parent ADR)

## Context

OBPI-0.0.24-01 landed the validator at
`src/gzkit/governance/trust_audits/attestation_receipts.py`:

```python
validate_attestation_receipts(
    attestation_text: str,
    *, lane: str, kind: str,
    project_root: Path | None = None,
) -> AttestationReceiptValidationResult  # .exit_code (0 or 3), .warn_only, .entries
```

The validator already encodes zero-receipts policy (heavy/foundation → fail-closed
exit 3; lite-non-foundation → exit 0 + warn_only=True). For non-zero receipts
with any failure it always returns exit_code=3, warn_only=False — the **call
site** must reduce that to a warning on lite-non-foundation per REQ-03.

This OBPI wires the gate into the three completion/emission entry points,
extends `CANONICAL_STEP_COMMANDS` with the meta slot, and emits a self-attesting
ledger event when the gate fires successfully. Per REQ-07 the gate runs BEFORE
`_enforce_human_attestation_authenticity` so a mechanical-receipt failure
short-circuits TTY prompting.

## Allowed surface (from brief)

- `src/gzkit/commands/obpi_complete.py` — primary `gz obpi complete` path
- `src/gzkit/commands/obpi_cmd.py` — `obpi_emit_receipt_cmd` (alternative path)
- `src/gzkit/commands/adr_audit.py` — `adr_emit_receipt_cmd` (ADR-level)
- `src/gzkit/arb/validator.py` — `CANONICAL_STEP_COMMANDS` extension
- `tests/commands/test_obpi_complete.py` — wire tests
- `tests/commands/test_adr_emit_receipt.py` — wire tests
- (Tests for `obpi_emit_receipt_cmd` — extend existing `tests/commands/test_obpi.py` if present)

Read-only access to `src/gzkit/governance/trust_audits/attestation_receipts.py`
(OBPI-01 owns the function body).

## Plan steps

### Step 1: TDD RED — author failing tests for the receipt-binding gate

File: `tests/commands/test_obpi_complete.py` (extend) and
`tests/commands/test_adr_emit_receipt.py` (extend or create).

Each test decorated `@covers(REQ-0.0.24-02-NN)`. Use tempfile-backed:
- `tempfile.TemporaryDirectory()` as project_root, with `.gzkit/` skeleton
- ARB receipts dir override via `GZKIT_ARB_RECEIPTS_ROOT` env var
- Write fixture receipt JSON files under that dir for resolved-receipt tests
- Patch `_enforce_human_attestation_authenticity` to no-op (it's tested separately;
  here we want to assert the gate runs *before* it via call-order assertion)
- Patch `Ledger.append` to capture emitted events for meta-receipt-bind assertion

Test cases (one per REQ + one composite):

| Test | REQ | Setup | Asserts |
|------|-----|-------|---------|
| `test_obpi_complete_heavy_valid_receipt_succeeds` | 01 | heavy ADR, attestation cites a fixture receipt with `exit_status=0` | exit 0; brief flips Completed; meta-receipt-bind event in ledger |
| `test_obpi_complete_heavy_missing_receipt_exits_3` | 02 | heavy ADR, attestation cites non-existent receipt ID | SystemExit(3); brief unchanged; no completion event in ledger |
| `test_obpi_complete_lite_nonfoundation_missing_warns` | 03 | feature kind, lite lane, attestation with no receipts | exit 0; warning emitted to stderr/console; brief flips Completed |
| `test_obpi_complete_foundation_lite_missing_exits_3` | 04 | foundation kind (e.g. ADR-0.0.X), lite lane, missing receipt | SystemExit(3); foundation overrides lite |
| `test_adr_emit_receipt_heavy_missing_exits_3` | 05 | `gz adr emit-receipt --event validated` against heavy ADR, missing receipt | SystemExit(3); no event written |
| `test_obpi_complete_meta_receipt_bind_payload` | 08 | heavy + valid receipt | meta-receipt-bind event has `claim="attestation receipts resolved"`, `exit_status=0`, payload lists the resolved run_ids |
| `test_obpi_complete_gate_runs_before_tty_gate` | 07 | heavy + missing receipt | `_enforce_human_attestation_authenticity` is NOT invoked when gate fails |

Run `uv run -m unittest tests/commands/test_obpi_complete.py -v` and confirm all
tests fail with the expected pre-implementation errors.

### Step 2: Extend `CANONICAL_STEP_COMMANDS` (REQ-06)

File: `src/gzkit/arb/validator.py:52-64`

Add a `meta-receipt-bind` slot. Initial canonical command is empty list
(matching the `security` slot pattern at line 63 — reserved slot, internally
emitted; not a user-runnable invocation):

```python
CANONICAL_STEP_COMMANDS: dict[str, list[str]] = {
    "typecheck": [...],
    "unittest": [...],
    "coverage": [...],
    "mkdocs": [...],
    "security": [],
    # Reserved by ADR-0.0.24 (attestation-receipt-binding), OBPI-02.
    # Receipts in the ``arb-meta-receipt-bind-`` family are emitted by
    # ``gz obpi complete`` and ``gz adr emit-receipt`` when the receipt-binding
    # gate fires successfully. The slot is reserved (empty canonical command)
    # because the receipt is emitted internally rather than via a user-runnable
    # invocation; provenance is enforced by `step.command == []` in receipts
    # the gate writes.
    "meta-receipt-bind": [],
}
```

Add a unit test in `tests/arb/test_validator.py` (or wherever existing tests
live) that asserts the slot exists and is empty.

### Step 3: TDD GREEN — implement the gate wrapper

File: `src/gzkit/commands/obpi_complete.py`

Add a new helper `_enforce_attestation_receipt_gate(...)`:

```python
def _enforce_attestation_receipt_gate(
    *, obpi_id: str, parent_adr: str, parent_lane: str,
    parent_kind: str, attestation_text: str, ledger: Ledger,
    project_root: Path, as_json: bool, dry_run: bool,
) -> None:
    """Run validate_attestation_receipts; fail-closed on heavy/foundation.

    On success emits an ``arb-meta-receipt-bind-<timestamp>`` event to the
    ledger naming the resolved receipt IDs.
    """
    if dry_run:
        return
    from gzkit.governance.trust_audits.attestation_receipts import (
        validate_attestation_receipts,
    )
    result = validate_attestation_receipts(
        attestation_text, lane=parent_lane, kind=parent_kind,
        project_root=project_root,
    )
    fail_closed = parent_lane.lower() == "heavy" or parent_kind.lower() == "foundation"
    if result.exit_code != 0:
        if fail_closed:
            _fail(
                "Attestation receipt binding failed (heavy/foundation gate). "
                "See `gz validate --attestation-receipts` for diagnostics.",
                exit_code=3, as_json=as_json, obpi_id=obpi_id,
            )
        else:
            console.print(
                "[yellow]Warning:[/yellow] attestation cites no resolved receipts "
                "(lite-non-foundation; warn-only)."
            )
            return
    if result.warn_only:
        console.print(
            "[yellow]Warning:[/yellow] attestation contains no ARB receipts "
            "(lite-non-foundation policy)."
        )
        return
    # All resolved → emit self-attesting meta-receipt-bind event
    resolved_ids = [e.run_id for e in result.entries if e.status == "resolved" and e.run_id]
    _emit_meta_receipt_bind_event(
        ledger=ledger, obpi_id=obpi_id, parent_adr=parent_adr,
        resolved_ids=resolved_ids,
    )
```

Add `_emit_meta_receipt_bind_event(...)` that constructs a ledger event of
shape compatible with `gzkit.ledger_events` (likely a generic
`audit_receipt_emitted_event` or a new `arb_meta_receipt_bind_event` —
prefer extending `gzkit.ledger_events` rather than inventing a freeform
event) with the payload `{claim: "attestation receipts resolved", exit_status:
0, resolved_receipt_ids: [...]}`.

If extending `gzkit.ledger_events` proves out-of-scope (the brief denies edits
beyond the listed paths), fall back to writing the meta-receipt as an ARB
receipt JSON via `gzkit.arb.paths.receipts_root() / f"arb-meta-receipt-bind-{ts}.json"`
matching the `gzkit.arb.step_receipt.v1` schema, and emitting a generic
`obpi_receipt_emitted_event` linking it. **Decision deferred to implementation**
— pick the path with the smallest blast radius once the ledger_events module
is read.

Wire the helper into `obpi_complete_cmd` BETWEEN step 4a (security gate) and
step 4b (TTY authenticity gate). Resolve `parent_kind` from the parent ADR
frontmatter via `parse_frontmatter_value` on the ADR file content, defaulting
to `"feature"` when absent.

### Step 4: Mirror in `obpi_emit_receipt_cmd`

File: `src/gzkit/commands/obpi_cmd.py:125`

Inside `obpi_emit_receipt_cmd`, when `receipt_event == "completed"` and
`evidence` carries `attestation_text`, run the same gate **before**
`_gate_completed_receipt_authenticity` is called (around line 181-189).

Same import / same helper — extract `_enforce_attestation_receipt_gate` into
a shared location if both modules need it. Candidate: keep the helper in
`obpi_complete.py` and import it from `obpi_cmd.py`, OR move it to a small
shared module under `src/gzkit/commands/` (e.g. `attestation_gate.py`). The
import-from-obpi_complete path is simplest and stays inside the allowed
paths. Use that.

### Step 5: Mirror in `adr_emit_receipt_cmd`

File: `src/gzkit/commands/adr_audit.py:686`

Inside `adr_emit_receipt_cmd`, when `_is_human_attestation_receipt_event(receipt_event)`
is True (validated/attested/accepted), run the gate **before**
`_enforce_human_attestation_authenticity` (around line 733-746).

For `gz adr emit-receipt`:
- `parent_lane`: read from the ADR frontmatter via `resolve_adr_lane`
- `parent_kind`: read from the ADR frontmatter `kind` field
- `attestation_text`: extracted from `evidence.get("attestation_text") or evidence.get("scope")` (matches existing pattern at lines 736-738)

If no attestation_text is present, the gate sees an empty string and produces
zero-receipts; heavy/foundation policy fail-closes. This is correct behavior
for REQ-05.

### Step 6: TDD GREEN verify

```bash
uv run -m unittest tests/commands/test_obpi_complete.py tests/commands/test_adr_emit_receipt.py -v
```

All REQ-01..08 tests pass. Iterate fix→retest if any fail (max 2 attempts).

### Step 7: Quality gates (Stage 3 baseline)

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

Lint clean, type check clean, full suite passes. Heavy lane → also:

```bash
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
```

### Step 8: REQ→@covers parity gate

```bash
uv run gz covers OBPI-0.0.24-02-wire-into-completion --json
```

Expect `summary.uncovered_reqs == 0`. Each REQ-0.0.24-02-NN shall have a
@covers reference in test code.

## Verification (per brief)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_obpi_complete.py tests/commands/test_adr_emit_receipt.py -v
```

## Destination-in-mind disclosure (Step 6a)

**Conclusion already formed:** Insert the gate as a new helper in
`obpi_complete.py` between step 4a (security gate) and step 4b (TTY gate),
import the same helper into `obpi_cmd.py:obpi_emit_receipt_cmd` and
`adr_audit.py:adr_emit_receipt_cmd`. Extend `CANONICAL_STEP_COMMANDS` with
`meta-receipt-bind: []` mirroring the `security: []` reserved-slot pattern.
TDD with tempfile fixtures patching the receipts root and the TTY gate.

**Rejected alternatives:**

1. **Move the gate into `validate_attestation_receipts` itself, mutating the
   ledger from the validator.** Rejected: violates separation of concerns —
   the validator is a pure function under `governance/trust_audits/` and
   the brief's denied-paths explicitly forbid edits to its body. The gate
   firing is a CLI concern; the validator is the worker.
2. **Emit the meta-receipt as an actual ARB receipt JSON file in
   `artifacts/receipts/` instead of a ledger event.** Considered: would let
   future attestations cite the meta-receipt itself. Rejected: REQ-05 says
   "recorded in the ledger"; receipt JSON is a Layer-3 artifact, ledger
   event is Layer-2 source-of-truth. Defer file emission to a follow-up GHI.
3. **Hardcode the `parent_kind` derivation from ADR-ID regex
   (`^ADR-0\.0\.\d+$ → foundation`).** Considered: matches the existing
   pattern at `_requires_human_obpi_attestation`. Rejected for this OBPI:
   read kind from ADR frontmatter for accuracy. (The regex pattern is
   used in `_requires_human_obpi_attestation` because it predates the
   `kind:` schema field; we now have first-class kind frontmatter.)
4. **Add a `--skip-receipt-binding` flag for emergency use.** Rejected
   explicitly by REQ-12 and parent ADR Non-Goal #1.

## Notes

- Confidence ≥90% — no `gz-justify` walkthrough required (Stage 1→2 gate).
- Heavy lane → all gates required at closeout (Gate 5 attestation TTY+ATTEST).
- This OBPI is foundation-kind, so brief-level Gate 5 attestation is required.
- Lock claim: `OBPI-0.0.24-02-wire-into-completion` (full slug from brief id).
