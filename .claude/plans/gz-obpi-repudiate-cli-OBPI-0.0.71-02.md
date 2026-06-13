# Implementation Plan: OBPI-0.0.71-02 — gz obpi repudiate CLI

**OBPI:** OBPI-0.0.71-02-gz-obpi-repudiate-cli
**ADR:** ADR-0.0.71-completion-repudiation
**Lane:** Heavy
**Approach committed before plan was written:** `obpi_repudiate_cmd()` in `obpi_cmd.py` following `obpi_withdraw_cmd` pattern; `repudiate` subparser alongside `withdraw` in `parser_artifacts.py`; `repudiated_receipt` auto-derived from most recent `obpi_receipt_emitted` in ledger (not a CLI flag).
**Rejected alternatives:** (1) Separate `obpi_repudiate_cmd.py` file — brief names `obpi_cmd.py`. (2) `--repudiated-receipt` CLI flag — REQs don't require it; auto-derive is deterministic and cleaner UX.

---

## Files

| Path | Action |
|------|--------|
| `tests/test_obpi_repudiate_cli.py` | **Create** — TDD RED first; 5 BEHAVIOR REQs as unit tests |
| `src/gzkit/commands/obpi_cmd.py` | **Modify** — add `obpi_repudiate_cmd(obpi, cause, reason, attestor, dry_run)` |
| `src/gzkit/cli/parser_artifacts.py` | **Modify** — add `repudiate` subparser under `gz obpi` |
| `docs/user/manpages/obpi-repudiate.md` | **Create** — manpage modeled on `obpi-withdraw.md` |
| `features/obpi_repudiate.feature` | **Create** — heavy-lane behave smoke test |
| `.gzkit/rules/governance-core.md` | **Modify** — add withdraw-vs-repudiate disambiguation section |

---

## Steps

### Step 1: Write failing tests (RED)

Create `tests/test_obpi_repudiate_cli.py` with tests for:
- REQ-0.0.71-02-01: valid cause/reason/attestor emits exactly one `obpi_completion_repudiated` event
- REQ-0.0.71-02-02: empty `--attestor` exits 1, no ledger write
- REQ-0.0.71-02-03: empty `--reason` exits 1, no ledger write
- REQ-0.0.71-02-04: `--dry-run` prints planned event, ledger unchanged
- REQ-0.0.71-02-05: out-of-enum `--cause` exits 2 (parser reject) before any ledger write

Tests use a temporary ledger with a pre-seeded `obpi_receipt_emitted` event so the command can find the completion receipt. Tests derive assertions from REQ semantics, not from running the code first.

### Step 2: Implement `obpi_repudiate_cmd` (GREEN)

In `src/gzkit/commands/obpi_cmd.py`, add:

```python
def obpi_repudiate_cmd(obpi: str, cause: str, reason: str, attestor: str, dry_run: bool) -> None:
```

Logic:
1. `config = ensure_initialized()`, build `Ledger`
2. `canonical_id = ledger.canonicalize_id(obpi)`
3. `graph = ledger.get_artifact_graph()`, `info = graph.get(canonical_id, {})`
4. Guard: type must be `"obpi"`, raise `GzCliError` if not found
5. Guard: `not info.get("ledger_completed")` → exit 1 (nothing to repudiate)
6. Guard: `info.get("withdrawn")` → exit 1 (withdrawn OBPIs cannot be repudiated)
7. Find `repudiated_receipt`: scan `ledger.query("obpi_receipt_emitted", canonical_id)` for most recent event with `receipt_event == "completed"` or `receipt_event == "attested_completed"`; use its `ts` as the receipt identifier. If none found → exit 1.
8. Validate `attestor.strip()` and `reason.strip()` non-empty (belt-and-suspenders; argparse also enforces `required=True`)
9. Build event via `obpi_completion_repudiated_event(canonical_id, parent, repudiated_receipt, cause, attestor, reason)`
10. If `dry_run`: print event JSON, return
11. `ledger.append(event)`, print confirmation

Import at top of file: `from gzkit.ledger_events import obpi_completion_repudiated_event`

### Step 3: Register parser

In `src/gzkit/cli/parser_artifacts.py`, add after `p_obpi_withdraw` block:

```python
CAUSE_CHOICES = ["model-induced-fabrication", "operator-error", "verification-invalid"]

p_obpi_repudiate = obpi_commands.add_parser(
    "repudiate",
    help="Repudiate a fraudulent or erroneous OBPI completion without retiring the OBPI",
    description=(
        "Record an obpi_completion_repudiated event. Reverses a completion "
        "without the permanent retirement semantics of withdraw — the OBPI "
        "stays live for re-completion. Operator-gated: requires non-empty "
        "--attestor and --reason."
    ),
    epilog=build_epilog([
        'gz obpi repudiate OBPI-0.0.70-02 --cause model-induced-fabrication --reason "agent fabricated attestation" --attestor "g0"',
        'gz obpi repudiate OBPI-0.0.70-02 --cause operator-error --reason "..." --attestor "g0" --dry-run',
    ]),
)
p_obpi_repudiate.add_argument("obpi", help="OBPI identifier (e.g. OBPI-0.21.0-01)")
p_obpi_repudiate.add_argument("--cause", required=True, choices=CAUSE_CHOICES, help="Cause enum")
p_obpi_repudiate.add_argument("--reason", required=True, help="Required repudiation reason (non-empty)")
p_obpi_repudiate.add_argument("--attestor", required=True, help="Human attestor name (non-empty)")
add_dry_run_flag(p_obpi_repudiate)
p_obpi_repudiate.set_defaults(
    func=lambda a: _lazy("obpi_repudiate_cmd")(obpi=a.obpi, cause=a.cause, reason=a.reason, attestor=a.attestor, dry_run=a.dry_run)
)
```

Also add `"obpi_repudiate_cmd": "gzkit.commands.obpi_cmd"` to `_LAZY_IMPORTS`.

### Step 4: Create manpage

`docs/user/manpages/obpi-repudiate.md` modeled on `obpi-withdraw.md`:
- Title: `gz obpi repudiate`
- Usage section with all required flags
- Description explaining repudiate vs withdraw distinction
- Arguments and Flags tables
- Exit codes (0=success, 1=user error, 2=parser error for invalid cause)
- Examples including dry-run

### Step 5: Create behave feature

`features/obpi_repudiate.feature`:
- Scenario: Missing OBPI exits 1
- Scenario: Help text shows `--cause`, `--reason`, `--attestor`
- Tag with `@REQ-0.0.71-02-01` on the smoke scenario

### Step 6: Add disambiguation to governance-core.md

In `.gzkit/rules/governance-core.md`, add a section distinguishing:
- `gz obpi withdraw` = permanent one-way retirement (sets `withdrawn=True`, OBPI hidden from `gz state`)
- `gz obpi repudiate` = reverse-and-keep (flips `ledger_completed → False`, sets `repudiated=True`, OBPI stays live for re-completion)

Bump rule version: `0.3.0` → `0.4.0`.

### Step 7: Run sync

`uv run gz agent sync control-surfaces` — propagates `.gzkit/rules/governance-core.md` to vendor mirrors.

### Step 8: Verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.test_obpi_repudiate_cli -v
uv run gz cli audit
uv run gz validate --documents
uv run -m behave features/obpi_repudiate.feature
```

---

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_obpi_repudiate_cli -v
uv run gz cli audit
uv run gz obpi repudiate OBPI-0.0.71-01-completion-repudiation-event --cause operator-error --reason "smoke" --attestor "g0" --dry-run
```

---

## REQ Coverage Map

| REQ | Mechanism | Test |
|-----|-----------|------|
| REQ-0.0.71-02-01 | `obpi_repudiate_cmd` emits event | `TestObpiRepudiateCmd.test_valid_repudiation_emits_event` |
| REQ-0.0.71-02-02 | argparse `required=True` + command guard on empty attestor | `TestObpiRepudiateCmd.test_empty_attestor_exits_1` |
| REQ-0.0.71-02-03 | argparse `required=True` + command guard on empty reason | `TestObpiRepudiateCmd.test_empty_reason_exits_1` |
| REQ-0.0.71-02-04 | `--dry-run` path prints event, no ledger write | `TestObpiRepudiateCmd.test_dry_run_no_ledger_write` |
| REQ-0.0.71-02-05 | argparse `choices=CAUSE_CHOICES` → exit 2 | `TestObpiRepudiateCmd.test_invalid_cause_rejected_by_parser` |
| REQ-0.0.71-02-06 | Structural-fence: ADR Boundary Invariant 1 (closeout) | n/a — verified at ADR closeout |
| REQ-0.0.71-02-07 | `gz cli audit` exit 0 + `gz validate --documents` exit 0 + ledger events | Integration verification |
