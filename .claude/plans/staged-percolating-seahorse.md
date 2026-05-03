# Plan: OBPI-0.0.25-02-override-and-mirror

## Context

OBPI-01 landed the REQ-coverage gate that fails `gz obpi complete` when any brief REQ lacks a
passing `@covers`-decorated test. OBPI-02 adds the escape-hatch path: the operator can
explicitly waive one or more uncovered REQs via `--accept-uncovered=<REQ-ID>` (repeatable),
requiring a mandatory rationale and — for heavy/foundation parents — a TTY+`ACCEPT`
confirmation that mirrors the GHI #290 authenticity gate. Each waiver is recorded as a
`obpi_completion_uncovered_accept` ledger event so audit trails are explicit. The same
coverage check is mirrored in `gz adr emit-receipt --event closed`: ADR closeout is refused
when any OBPI has unwaived REQ gaps.

Pre-condition: OBPI-01 (`attested_completed`) is the gate logic; OBPI-02 extends it without
touching OBPI-01's core functions in `req_coverage.py`.

---

## Critical Files

| File | Role |
|------|------|
| `src/gzkit/commands/obpi_complete.py` | Add `--accept-uncovered` flag handling, TTY gate, ledger recording |
| `src/gzkit/commands/adr_audit.py` | Mirror coverage gate in `adr_emit_receipt_cmd`; add TTY helper |
| `src/gzkit/governance/req_coverage.py` | Add `UncoveredAcceptanceRecord` model (no behavior change to OBPI-01 functions) |
| `src/gzkit/events.py` | Add `obpi_completion_uncovered_accept` event factory |
| `src/gzkit/cli/parser_artifacts.py` | Register `--accept-uncovered`, `--accept-uncovered-reason` flags; add `"closed"` event choice |
| `tests/commands/test_obpi_complete_coverage_gate.py` | Extend with override scenarios (REQs 01-05) |
| `tests/commands/test_adr_emit_receipt_coverage_gate.py` | New: ADR closeout coverage mirror tests |

---

## Implementation Steps (TDD — Red-Green-Refactor per behavior increment)

### Step 1 — Event factory (no behavior, no tests needed beyond import check)

**File:** `src/gzkit/events.py`

Add factory function `obpi_completion_uncovered_accept_event(...)` following the
`audit_receipt_emitted_event` pattern (creates a `LedgerEvent` with `extra` payload):

```python
def obpi_completion_uncovered_accept_event(
    *,
    obpi_id: str,
    req_id: str,
    operator: str,
    rationale: str,
    acceptance_type: str,
) -> LedgerEvent:
    extra: dict[str, Any] = {
        "obpi_id": obpi_id,
        "req_id": req_id,
        "operator": operator,
        "rationale": rationale,
        "acceptance_type": acceptance_type,
    }
    return LedgerEvent(
        event="obpi_completion_uncovered_accept",
        id=obpi_id,
        parent=obpi_id,
        extra=extra,
    )
```

Export it from `events.py` alongside the other factory functions. No typed class needed
(the `LedgerEvent` generic container matches the existing factory pattern).

---

### Step 2 — `UncoveredAcceptanceRecord` model in `req_coverage.py`

**File:** `src/gzkit/governance/req_coverage.py`

Add one Pydantic model (frozen, extra=forbid) documenting the waiver record:

```python
class UncoveredAcceptanceRecord(BaseModel):
    """One accepted-uncovered REQ waiver, before writing to the ledger."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    obpi_id: str
    req_id: str
    operator: str
    rationale: str
    acceptance_type: str
```

No new functions; this is a data-transport type used by `obpi_complete.py` to build the
ledger payload. OBPI-01 functions (`parse_brief_reqs`, `discover_covers`) are untouched.

---

### Step 3 — TTY confirmation helper in `adr_audit.py`

**File:** `src/gzkit/commands/adr_audit.py`

Add constant and helper after `_enforce_human_attestation_authenticity`:

```python
_UNCOVERED_ACCEPTANCE_CONFIRMATION = "ACCEPT"

def _enforce_uncovered_acceptance_confirmation(
    *,
    obpi_id: str,
    parent_adr: str,
    req_ids: list[str],
    attestor: str,
    attestor_present: bool = False,
    project_root: Path | None = None,
) -> str:
    """Gate the --accept-uncovered override for heavy/foundation parents.

    Three-branch mirror of _enforce_human_attestation_authenticity:
    1. TTY path — stdin+stdout are a real TTY; operator types ACCEPT.
    2. Agent-relayed path — no TTY but --attestor-present + active pipeline marker.
    3. Fail-closed — headless + no marker → raises GzCliError.

    Returns acceptance_type string for the ledger event.
    """
```

Mirror the three-branch logic of `_enforce_human_attestation_authenticity` exactly,
substituting `_UNCOVERED_ACCEPTANCE_CONFIRMATION = "ACCEPT"` for `"ATTEST"` and
displaying the REQ IDs being waived in the prompt instead of attestation text.

Also export `_enforce_uncovered_acceptance_confirmation` alongside the existing exports
(imported by `obpi_complete.py`).

---

### Step 4 — Extend `_enforce_req_coverage_gate` in `obpi_complete.py`

**File:** `src/gzkit/commands/obpi_complete.py`

**4a. Red:** Write tests first in `test_obpi_complete_coverage_gate.py` (Step 7 below) for:
- Single-REQ override succeeds (heavy, TTY confirmed) → no SystemExit
- Headless heavy-lane override refused → exit 3
- Empty rationale → exit 1 (caught pre-gate in `obpi_complete_cmd`)
- Partial waiver: one of two uncovered REQs waived → exit 3 (unwaived still fails)
- Lite-lane override: no TTY required, ledger event recorded

**4b. Green:** Extend `_enforce_req_coverage_gate` signature:

```python
def _enforce_req_coverage_gate(
    *,
    obpi_id: str | None,
    parent_adr: str,
    parent_lane: str,
    parent_kind: str,
    brief_path: Path,
    project_root: Path,
    as_json: bool,
    dry_run: bool,
    # OBPI-0.0.25-02 override params:
    accept_uncovered: list[str] | None = None,
    accept_uncovered_reason: list[str] | None = None,
    attestor: str = "",
    attestor_present: bool = False,
    ledger: Any = None,
) -> None:
```

After computing `gaps` and `failing`:
1. If `accept_uncovered` provided and `fail_closed`:
   - Call `_enforce_uncovered_acceptance_confirmation(...)` (imported from `adr_audit.py`)
   - Returns `acceptance_type`; raises `GzCliError` on headless+no-marker
2. For each accepted REQ in `accept_uncovered` that is in `gaps`:
   - Emit `obpi_completion_uncovered_accept_event(...)` to ledger
   - Remove from `gaps`
3. Remaining `gaps` (unwaived) + `failing` still trigger fail-closed or warn-only

**4c. Extend `obpi_complete_cmd` signature** with `accept_uncovered: list[str] | None` and
`accept_uncovered_reason: list[str] | None`:

Pre-gate validation (before calling `_enforce_req_coverage_gate`):
- If `accept_uncovered` but no `accept_uncovered_reason` → `_fail("...rationale required...", exit_code=1, ...)`
- If `len(accept_uncovered) != len(accept_uncovered_reason)` → `_fail("...counts must match...", exit_code=1, ...)`

Pass new params through to `_enforce_req_coverage_gate`.

---

### Step 5 — Register flags in `parser_artifacts.py`

**File:** `src/gzkit/cli/parser_artifacts.py`

In the `gz obpi complete` subparser block, add after `--attestor-present`:

```python
p_complete.add_argument(
    "--accept-uncovered",
    action="append",
    dest="accept_uncovered",
    metavar="REQ_ID",
    default=None,
    help="Explicitly waive an uncovered REQ (repeatable). Requires --accept-uncovered-reason.",
)
p_complete.add_argument(
    "--accept-uncovered-reason",
    action="append",
    dest="accept_uncovered_reason",
    metavar="REASON",
    default=None,
    help="Rationale for the corresponding --accept-uncovered entry (repeatable, 1:1 pairing).",
)
```

Also update the dispatch in the argument handler to pass these to `obpi_complete_cmd`.

---

### Step 6 — `--event closed` in `adr_emit_receipt_cmd` (`adr_audit.py`)

**File:** `src/gzkit/commands/adr_audit.py`
**File:** `src/gzkit/cli/parser_artifacts.py`

**6a. Parser:** Change `choices=["completed", "validated"]` → `choices=["completed", "validated", "closed"]`.

**6b. Coverage check helper** (add to `adr_audit.py`):

```python
def _check_adr_obpi_coverage_gaps(
    adr_id: str,
    project_root: Path,
    ledger: Ledger,
) -> list[tuple[str, list[str]]]:
    """Return list of (obpi_id, unwaived_gap_req_ids) for the closing ADR.

    Walks the ADR brief directory, parses each OBPI brief's REQs, runs
    coverage discovery, then subtracts any REQs with a matching
    obpi_completion_uncovered_accept ledger event. Returns empty list
    when all OBPIs have full or waived coverage.
    """
```

Implementation:
1. Find all `OBPI-{adr_version}-*.md` files under the ADR directory using the same
   walk pattern as existing `_compute_adr_coverage` in `adr_audit.py`.
2. For each brief, call `parse_brief_reqs(brief_path)` (imported from `req_coverage.py`).
3. For each REQ, call `discover_covers(req, project_root / "tests")`.
4. Collect `gaps` (no covering tests) — do NOT re-run tests here (closeout check is structural,
   not a re-run gate).
5. Query ledger for acceptance events: read JSONL via `ledger.path` (if no `iter_events()` API
   exists on `Ledger`; check first and prefer the API method). Filter for
   `event == "obpi_completion_uncovered_accept"` + matching `obpi_id` + `req_id`.
6. Subtract waived REQs from gaps.
7. Return `[(obpi_id, unwaived_gaps)]` for any OBPI with remaining gaps.

**6c. In `adr_emit_receipt_cmd`**, add branch for `receipt_event == "closed"`:
- Call `_check_adr_obpi_coverage_gaps(...)`
- If non-empty: `_fail(structured message naming each OBPI and unwaived REQ, exit_code=3, ...)`
- If empty: proceed normally (emit an `adr_closeout_coverage_checked` receipt or reuse
  `audit_receipt_emitted` with `receipt_event="closed"`)

---

### Step 7 — Tests

**File:** `tests/commands/test_obpi_complete_coverage_gate.py` (extend)

Add new test classes, each decorated `@covers` for the relevant REQ:

| Class | REQ covered | Scenario |
|-------|-------------|----------|
| `TestObpiCompleteHeavyOverrideSingleReqAccepted` | REQ-0.0.25-02-01 | Heavy-lane, TTY present, single waiver → no SystemExit; ledger event recorded |
| `TestObpiCompleteHeadlessHeavyOverrideRefused` | REQ-0.0.25-02-02 | Heavy-lane, no TTY, no pipeline marker → exit 3 |
| `TestObpiCompletePartialOverrideOneUnwaived` | REQ-0.0.25-02-03 | Two uncovered REQs, one waived → exit 3 |
| `TestObpiCompleteOverrideEmptyRationaleExit1` | REQ-0.0.25-02-05 | `--accept-uncovered` given, `--accept-uncovered-reason` absent → exit 1 |
| `TestObpiCompleteLiteOverrideNoTtyRequired` | REQ-5 | Lite-lane override: no TTY needed; ledger event recorded |
| `TestObpiCompleteMultiReqOverrideAllWaived` | REQ-8 | Two uncovered REQs, both waived, both reasoned → no SystemExit; two ledger events |

Mock pattern: follow existing `_CoverageGateWireFixture` rig. Patch `_enforce_uncovered_acceptance_confirmation` with a TTY-presence mock (returns `"human"` when TTY present, raises `GzCliError` when headless).

**File:** `tests/commands/test_adr_emit_receipt_coverage_gate.py` (new)

| Class | REQ covered | Scenario |
|-------|-------------|----------|
| `TestAdrCloseoutSucceedsAllCovered` | ADR closeout background | All OBPIs have full coverage → no error |
| `TestAdrCloseoutFailsUnwaivedGap` | REQ-0.0.25-02-04 | One OBPI has unwaived REQ gap → exit 3 |
| `TestAdrCloseoutSucceedsAllGapsWaived` | REQ-0.0.25-02-04 (pass path) | Gaps exist but all have acceptance ledger events → no error |

Use tempfile-backed ADR directory with minimal OBPI brief stubs. Mock ledger's JSONL file
(write acceptance event records directly) rather than importing the full ledger stack.

---

## Verification

```bash
# Baseline quality (run after each step)
uv run gz arb ruff
uv run gz arb typecheck

# OBPI-scoped tests (run after Step 4+7)
uv run gz arb step --name unittest -- uv run -m unittest \
  tests.commands.test_obpi_complete_coverage_gate \
  tests.commands.test_adr_emit_receipt_coverage_gate -v

# Full suite (run at end)
uv run gz arb step --name unittest -- uv run -m unittest -q

# Smoke: --accept-uncovered on a TTY context
# uv run gz obpi complete OBPI-0.0.25-02 \
#   --attestor "Jeffry Babb" \
#   --attestation-text "..." \
#   --accept-uncovered REQ-0.0.25-02-01 \
#   --accept-uncovered-reason "waiving per operator review" \
#   --dry-run
```

---

## Key Reuse

- `_enforce_human_attestation_authenticity` in `adr_audit.py:444` — **model** this, do not call
  it for the override path (different prompt, different confirmation word `ACCEPT` vs `ATTEST`)
- `_is_human_attestation_tty_available()` in `adr_audit.py:420` — **import and reuse** directly
- `_active_pipeline_marker_exists()` in `adr_audit.py:432` — **import and reuse** directly
- `_UNCOVERED_ACCEPTANCE_CONFIRMATION = "ACCEPT"` — add alongside `_GHI_290_AUTHENTICITY_CONFIRMATION`
- Existing `_CoverageGateWireFixture` in `test_obpi_complete_coverage_gate.py` — extend, do not duplicate

---

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

Approach already formed before writing this plan: extend `_enforce_req_coverage_gate` with a
filter-then-confirm pattern, add TTY helper in `adr_audit.py`, mirror in `adr_emit_receipt_cmd`.

Rejected alternatives:
1. Embed the override rationale in the REQ-ID value (`--accept-uncovered=REQ-X:reason`) — rejected
   because the brief explicitly names `--accept-uncovered-reason` as a separate flag.
2. Put `_enforce_uncovered_acceptance_confirmation` in `obpi_complete.py` — rejected because the
   TTY infrastructure (`_is_human_attestation_tty_available`, `_active_pipeline_marker_exists`) lives
   in `adr_audit.py`; co-locating the new helper there avoids duplicate infrastructure.
3. Use `--accept-uncovered` as a boolean "waive all gaps" flag — rejected; per REQ-6, only
   explicitly named REQ-IDs are waived; the rest still fail.
