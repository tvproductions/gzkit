# Plan — OBPI-0.0.24-01-validator-scope

**Parent ADR:** `ADR-0.0.24-attestation-receipt-binding` (kind: foundation, lane: heavy)
**Brief:** `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/obpis/OBPI-0.0.24-01-validator-scope.md`
**Execution mode:** Normal (Gate 5 attestation required — heavy + foundation)
**Plan-audit context:** Brief amended under option B (2026-05-02) to align receipt
storage model and ID regex with runtime reality (`artifacts/receipts/<run_id>.json`,
`arb-(ruff|step-<name>)-[a-f0-9]{32}`). ADR Decision-1 sentence amended in same patch.
Insight recorded in `.gzkit/insights/agent-insights.jsonl`.

## Destination-in-mind (Step 6a disclosure)

Approach already formed before authoring this plan: a new `attestation_receipts.py`
module under `src/gzkit/governance/trust_audits/` that (a) parses the attestation
text via a single anchored regex against the real `arb-(ruff|step-<name>)-[a-f0-9]{32}`
shape, (b) reads each parsed run_id from `receipts_root()/<run_id>.json` (no ledger
lookup), (c) classifies each result as `resolved | missing | status_mismatch |
claim_mismatch | malformed_id`, (d) returns a Pydantic `frozen=True, extra="forbid"`
result model. The `audit_*` wrapper for the validate-scope dispatch table is a thin
adapter; the worker is the testable surface. Lane/kind behavior is parameter-driven
(REQ #10) but does NOT mutate `obpi complete` / `adr emit-receipt` (that's OBPI-02).

## Rejected alternatives (Step 6a disclosure)

1. **Reuse `validate_receipts()` directly.** Rejected: that primitive scans the
   most-recent N receipts in a directory; this OBPI needs targeted lookup by
   exact `run_id`. Different access pattern. Will re-use the schema constants
   (`LINT_SCHEMA_ID`, `STEP_SCHEMA_ID`) and the `CANONICAL_STEP_COMMANDS` table,
   not the iteration helper.
2. **Inline the validator inside `validate_cmd.py`.** Rejected: violates the
   trust_audits package convention (every other audit lives there) and skips
   the `__init__.py` re-export the dispatch table reads. Discoverability cost
   exceeds the import-cycle saving.
3. **Use `re.findall` with one loose regex over the whole text.** Rejected: a
   loose regex bleeds into adjacent prose ("arb-ruff-deadbeef..." matches
   inside `arb-ruff-deadbeef...XYZ`). Use anchored shape with surrounding
   `\b` and explicit `[a-f0-9]{32}$` so we accept only canonical IDs.
4. **Compute claim category by parsing words "near" the receipt ID.** Rejected
   for OBPI-01: too many natural-language permutations. Use the canonical pattern
   from AGENTS.md § Attestation: `(<category>: receipt <run_id>)` and accept
   `<run_id>` standing alone with category derived from the run_id prefix.
   Both forms covered.

## Implementation Steps

### Step 1: Author RED tests — module skeleton + REQ table

**Files:** `tests/governance/test_attestation_receipt_validator.py` (new)

Write a `unittest.TestCase` subclass `AttestationReceiptValidatorTest` with one
test method per acceptance criterion (REQ-0.0.24-01-01 through REQ-0.0.24-01-06).
Each test decorated `@covers("REQ-0.0.24-01-NN")` per `.claude/rules/tests.md`.

Each test stages a temp directory via `tempfile.TemporaryDirectory()`, sets
`os.environ["GZKIT_ARB_RECEIPTS_ROOT"]` to that path under `setUp`, restores
under `tearDown`. Writes one or more receipt JSON files per the real
schemas (`gzkit.arb.lint_receipt.v1`, `gzkit.arb.step_receipt.v1`) using
representative payloads cribbed from `artifacts/receipts/`. Asserts both
the worker function's `AttestationReceiptValidationResult` shape and the
result `exit_code` field.

Tests required (one per REQ + one per branch):

| Test method | REQ | Scenario |
|---|---|---|
| `test_all_resolved_returns_exit_zero` | REQ-01 | Heavy lane, one resolved receipt, expect exit 0 |
| `test_missing_receipt_returns_exit_three` | REQ-02 | Cite a run_id with no file on disk |
| `test_status_mismatch_returns_exit_three` | REQ-03 | Stage a receipt with `exit_status: 1` |
| `test_claim_mismatch_returns_exit_three` | REQ-04 | Cite `lint:` adjacent to an `arb-step-typecheck-*` receipt |
| `test_malformed_receipt_id_reported_not_silent` | REQ-05 | Embed a near-shape garbage token; assert it surfaces (does not silently skip) |
| `test_zero_receipts_warn_only_on_lite_non_foundation` | REQ-06 | lane="lite", kind="feature", attestation has zero IDs => exit 0 with warn flag |
| `test_zero_receipts_fail_closed_on_heavy` | REQ-06 | lane="heavy", zero IDs => exit 3 |
| `test_zero_receipts_fail_closed_on_foundation` | REQ-06 | lane="lite", kind="foundation", zero IDs => exit 3 |

Run `uv run -m unittest tests.governance.test_attestation_receipt_validator -v`.
Confirm RED (every test fails on `ImportError` or `AttributeError`).

### Step 2: GREEN — author worker module

**Files:** `src/gzkit/governance/trust_audits/attestation_receipts.py` (new),
`src/gzkit/governance/trust_audits/__init__.py` (re-export)

Module contents:

- `_RECEIPT_ID_RE` anchored regex: `re.compile(r"\barb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}\b")`
- `_CITATION_CATEGORY_RE` regex to find `(<category>:\s*receipt\s+<run_id>)` pairings; tolerate
  the bare-citation case (run_id without category prefix — category derived from run_id shape)
- `_canonical_category_for(run_id: str) -> str` — `arb-ruff-...` => `lint`; `arb-step-<name>-...` => `<name>`
- `class AttestationReceiptValidationResult(BaseModel)` with `frozen=True, extra="forbid"`,
  fields: `entries: tuple[AttestationReceiptEntry, ...]`, `exit_code: int`, `warn_only: bool`
- `class AttestationReceiptEntry(BaseModel)` with `frozen=True, extra="forbid"`, fields:
  `run_id: str | None`, `cited_category: str | None`, `derived_category: str | None`,
  `status: Literal["resolved", "missing", "status_mismatch", "claim_mismatch", "malformed_id"]`,
  `message: str`
- `validate_attestation_receipts(attestation_text, lane, kind, *, project_root) -> AttestationReceiptValidationResult`
- `audit_attestation_receipts(project_root) -> list[ValidationError]` — wrapper for dispatch
  (returns empty list when invoked without an attestation argument; the umbrella `--audits`
  pass uses this no-op shape, matching the `validate_attestation_receipts` worker only when
  the `--attestation-receipts <text|@file>` flag is supplied — see Step 4)

Re-export both names from `trust_audits/__init__.py`.

Run tests; iterate until GREEN.

### Step 3: REFACTOR — extract receipt loader, normalize categories

After GREEN, factor the receipt-file loader into a private helper
`_load_receipt(receipts_root: Path, run_id: str) -> dict | None` that returns
`None` on missing-file (so the caller maps to `missing` status) and raises only
on JSON-decode errors (the caller maps those to `malformed_id` status with a
descriptive message). Consolidate the canonical-category derivation in one
helper. Keep functions <=50 lines per `.claude/rules/pythonic.md`.

Re-run tests. Confirm GREEN.

### Step 4: Wire `--attestation-receipts` flag

**Files:** `src/gzkit/cli/parser_artifacts.py` (`gz validate` subparser),
`src/gzkit/commands/validate_cmd.py` (dispatch handler)

Add `--attestation-receipts <text-or-@file>` argument to the `gz validate`
subparser. The argument accepts:
- A literal attestation string
- An `@path/to/file` reference (read file content as the attestation text)

Add a new dispatch branch in `validate_cmd.py` that:
1. Reads the lane/kind from optional `--lane` and `--kind` flags
   (default lane=`heavy`, kind=`feature` — fail-closed defaults)
2. Calls `validate_attestation_receipts(text, lane, kind, project_root=...)`
3. Renders the result (rich-table for human; JSON when `--json`)
4. Exits 0 on resolved, 3 on any mismatch, per `.claude/rules/cli.md`

Add `attestation_receipts` to `_explicit_scope_runners` is NOT needed — the
flag is a dedicated entrypoint, not part of the umbrella `--audits` sweep
(per REQ #10: "lane behavior is parameter-driven in this OBPI but NOT yet
wired into `obpi complete` / `adr emit-receipt`"). The dispatch is direct.

### Step 5: Author one bash test for the smoke command

Add an integration test in the same test module that invokes `gz validate
--attestation-receipts` via `subprocess.run(["uv", "run", "gz", "validate",
"--attestation-receipts", "lint clean (lint: receipt arb-ruff-DEADBEEF...)"])`
against a temp `GZKIT_ARB_RECEIPTS_ROOT` with a staged receipt. Assert exit
code 0. Skip on Windows if shell quoting cost is high (mark
`@unittest.skipIf(sys.platform == "win32", ...)`).

### Step 6: Lint, typecheck, full quality pass

Run:
```bash
uv run ruff check . --fix && uv run ruff format .
uv run gz typecheck
uv run -m unittest -q
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```
Receipts emitted at this step are the ones cited in Stage 4 evidence.

### Step 7: REQ → @covers parity gate

```bash
uv run gz covers OBPI-0.0.24-01-validator-scope --json
```
Confirm `summary.uncovered_reqs == 0`.

## Files

**New:**
- `src/gzkit/governance/trust_audits/attestation_receipts.py`
- `tests/governance/test_attestation_receipt_validator.py`

**Modified:**
- `src/gzkit/governance/trust_audits/__init__.py` (re-export)
- `src/gzkit/cli/parser_artifacts.py` (add `--attestation-receipts` flag)
- `src/gzkit/commands/validate_cmd.py` (dispatch handler)

**Read-only references:**
- `src/gzkit/arb/validator.py` (`CANONICAL_STEP_COMMANDS`, schema IDs)
- `src/gzkit/arb/paths.py` (`receipts_root()`, env override)

All paths within brief Allowed Paths. No edits to `obpi.py`, `adr_emit_receipt.py`,
`AGENTS.md`, `docs/governance/arb-middleware.md`, or `features/**` — those are
denied per brief.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_attestation_receipt_validator.py -v
uv run gz validate --attestation-receipts "lint clean (lint: receipt arb-ruff-c9fb17787ccc4f7b8a1a0ba670565768)"
uv run gz covers OBPI-0.0.24-01-validator-scope --json
```

## Notes

- Heavy + foundation => Gate 5 attestation REQUIRED at Stage 4.
- Brief Denied Paths exclude `obpi.py` and `adr_emit_receipt.py` — wiring is OBPI-02.
- BDD coverage is OBPI-04 — no `features/` edits in this OBPI.
- Manpage/doc updates are OBPI-03 — no `AGENTS.md` or `docs/governance/arb-middleware.md` edits.
- Coverage floor: 40% (per brief Gate 2). Add receipt-loader edge-case tests if the floor would otherwise regress.
