# Plan: OBPI-0.0.59-03-parity-gate-three-channel-extension

**OBPI:** OBPI-0.0.59-03-parity-gate-three-channel-extension
**Parent ADR:** ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine
**Lane:** Heavy
**Date:** 2026-05-26

## Context

OBPI-0.0.59-01 (doctrine) and OBPI-0.0.59-02 (validator) are both Completed.
This OBPI extends the parity gate to consume three proof channels.

Key dependencies from OBPI-02 already in place:
- `src/gzkit/req_kind.py`: `ReqKind`, `ProofChannel`, `ReqClassification` models
- `src/gzkit/triangle.py`: `_AC_LINE_PATTERN` captures `taxonomy_kind` group but does not store it in `ReqEntity`
- `src/gzkit/traceability.py`: `CoverageEntry`, `CoverageRollup`, `CoverageReport`, `compute_coverage`
- `src/gzkit/commands/covers.py`: `covers_cmd` with OBPI-scoped filter

**Additive approach:** New `compute_three_channel_coverage` function in `req_kind.py` enriches an existing `CoverageReport`. `compute_coverage` in `traceability.py` is unchanged. `gz covers OBPI-X.Y.Z-NN --json` dispatches to the enriched path when OBPI scope is detected.

**SUPPORT advisory-only:** SUPPORT proof channel is advisory in this OBPI — `gz covers` scan cannot query live ledger events. SUPPORT REQs receive `proof_status="advisory-support"` and are never fail-closed.

## Files

### Modified
- `src/gzkit/triangle.py` — add `taxonomy_kind: str | None` to `ReqEntity`; populate from `_AC_LINE_PATTERN` `taxonomy_kind` group in `extract_reqs_from_brief`
- `src/gzkit/traceability.py` — extend `CoverageEntry` with optional kind fields; extend `CoverageRollup` with `behavior_uncovered_reqs` and `grandfathered_reqs`
- `src/gzkit/req_kind.py` — add `ReqCoverageRecord`, `ReqCoverageSummary` models; add `infer_req_kind`; add `compute_three_channel_coverage`
- `src/gzkit/commands/covers.py` — add `bypass_req_kind_discipline_once` and `bypass_reason` parameters; emit `bypass_used` ledger event; dispatch to `compute_three_channel_coverage` for OBPI scope
- `src/gzkit/cli/parser_maintenance.py` — wire `--bypass-req-kind-discipline-once` and `--bypass-reason` flags

### Creates these files
- **CREATE** `data/req_kind_grandfathering.json` — initial empty operator-amendable cache `{}`
- **CREATE** `tests/governance/test_req_coverage_record.py` — tests for all new behavior

### Updated (Heavy lane docs)
- `docs/governance/req-scope-discipline.md` — three-channel parity gate section
- `docs/user/runbook.md` — `--bypass-req-kind-discipline-once` entry

## Steps

### Task 1: Add `taxonomy_kind` to `ReqEntity` in `triangle.py`

Write a failing test first: `test_req_entity_stores_taxonomy_kind` — verify that `extract_reqs_from_brief` populates `taxonomy_kind` from a `[BEHAVIOR]` tag.

Then extend `ReqEntity` with `taxonomy_kind: str | None = Field(None, ...)` and update `extract_reqs_from_brief` to pass `m.group("taxonomy_kind").upper() if m.group("taxonomy_kind") else None`.

REQ covered: none directly (infrastructure for REQ-01 and REQ-02).

### Task 2: Extend `CoverageEntry` and `CoverageRollup` in `traceability.py`

Write failing tests: `test_coverage_entry_has_kind_fields`, `test_coverage_rollup_has_behavior_uncovered`.

Extend `CoverageEntry` (keeping `extra="forbid"` compatible) with:
- `taxonomy_kind: str | None = Field(None, ...)`
- `proof_channel: str | None = Field(None, ...)`
- `proof_status: str = Field("unknown", ...)`
- `ledger_event_ids: list[str] = Field(default_factory=list, ...)`
- `parent_adr_anchor: str | None = Field(None, ...)`

Extend `CoverageRollup` with:
- `behavior_uncovered_reqs: int = Field(0, ...)`
- `grandfathered_reqs: int = Field(0, ...)`

Note: `compute_coverage` is NOT changed — new fields default to `None`/`"unknown"`/`0`. Existing tests must still pass.

REQs covered: REQ-0.0.59-03-01, REQ-0.0.59-03-05.

### Task 3: Add models and three-channel logic to `req_kind.py`

Write failing tests: `test_req_coverage_record_model_contract`, `test_req_coverage_summary_model_contract`, `test_infer_req_kind_behavior`, `test_infer_req_kind_structural_fence`, `test_infer_req_kind_support`, `test_compute_three_channel_coverage_behavior_req`, `test_compute_three_channel_coverage_legacy_req`, `test_compute_three_channel_coverage_grandfathering_cache`.

Add to `req_kind.py`:

```python
class ReqCoverageRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    req_id: str
    kind: ReqKind | None
    proof_channel: ProofChannel | None
    proof_status: str  # pass/fail/grandfathered/advisory-support/inferred-*
    covering_tests: list[str]
    ledger_event_ids: list[str]
    parent_adr_anchor: str | None
    grandfathered: bool

class ReqCoverageSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    obpi_id: str
    total_reqs: int
    covered_reqs: int
    behavior_uncovered_reqs: int
    grandfathered_reqs: int
    entries: list[ReqCoverageRecord]
```

`infer_req_kind(text: str) -> tuple[ReqKind, str]`:
- STRUCTURAL_FENCE triggers (high-specificity): "Allowed Paths", "Denied Paths", "remains inside scope", "boundary invariants", "denied path", "out of scope"
- SUPPORT triggers: "exists", "artifact_edited", "ledger event", "gz validate --"
- Default: BEHAVIOR

`compute_three_channel_coverage(report, known_reqs, grandfathering_cache=None) -> CoverageReport`:
- For each entry: look up `taxonomy_kind` from the matching `DiscoveredReq.entity.taxonomy_kind`
- If tagged: use declared kind; if untagged: run inference + set `grandfathered=True`
- Check grandfathering_cache override
- BEHAVIOR + covered → `proof_status="pass"`, BEHAVIOR + uncovered → `proof_status="fail"`
- SUPPORT → `proof_status="advisory-support"` (never fail-closed)
- STRUCTURAL-FENCE → `proof_status="grandfathered"`
- Recompute `behavior_uncovered_reqs` and `grandfathered_reqs` in rollups

REQs covered: REQ-0.0.59-03-02, REQ-0.0.59-03-03, REQ-0.0.59-03-05 (partially).

### Task 4: Author `data/req_kind_grandfathering.json`

Create with `{}` as initial content (empty operator-amendable cache).

Schema (informal, for operator reference — not mechanically enforced yet):
`{"REQ-X.Y.Z-NN-MM": "BEHAVIOR" | "SUPPORT" | "STRUCTURAL-FENCE"}`

REQ covered: REQ-0.0.59-03-06.

### Task 5: Add bypass flag and OBPI dispatch to `covers.py`

Write failing test: `test_covers_bypass_emits_ledger_event`.

Add parameters to `covers_cmd`:
- `bypass_req_kind_discipline_once: bool = False`
- `bypass_reason: str | None = None`

When `bypass_req_kind_discipline_once=True`:
- Validate `bypass_reason` is non-empty (error if missing)
- Append `bypass_used` ledger event with `reason` field
- Skip fail-close check

When target is OBPI-scoped (detected by `target.upper().startswith("OBPI-")`):
- Load `data/req_kind_grandfathering.json` (empty dict if absent)
- Call `compute_three_channel_coverage(report, discovered, cache)`
- Emit enriched report

REQ covered: REQ-0.0.59-03-04.

### Task 6: Wire CLI flags in `parser_maintenance.py`

Add to `p_covers`:
```python
p_covers.add_argument(
    "--bypass-req-kind-discipline-once",
    action="store_true",
    default=False,
    help="Skip three-channel parity gate for this run (emits bypass_used ledger event; requires --bypass-reason).",
)
p_covers.add_argument(
    "--bypass-reason",
    default=None,
    help="Reason for bypassing req-kind discipline (required with --bypass-req-kind-discipline-once).",
)
```

Update the lambda to pass new params to `covers_cmd`.

### Task 7: Update Heavy lane docs

Update `docs/governance/req-scope-discipline.md` — add section on three-channel parity gate behavior, `behavior_uncovered_reqs` field, and SUPPORT-advisory annotation.

Update `docs/user/runbook.md` — add entry for `--bypass-req-kind-discipline-once` flag with usage and mandatory `--bypass-reason`.

### Task 8: Run full verification suite

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_req_coverage_record -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.59-03 --json
```

## Verification

Per brief Verification section:

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_req_coverage_record -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
test -f data/req_kind_grandfathering.json
uv run gz covers OBPI-0.0.59-03 --json
```

## Notes

- SUPPORT advisory-only: this is an explicit scope boundary, not a defect.
- `compute_coverage` signature unchanged: additive enrichment only.
- Scope collisions are all completed OBPIs (advisory only, not blockers).
- BDD deferred to ADR closeout per brief § Gate 4 annotation.
