# Plan: OBPI-0.0.25-01 — Implement REQ-coverage gate inside `gz obpi complete`

**OBPI:** `OBPI-0.0.25-01-implement-coverage-gate`
**Parent ADR:** `ADR-0.0.25-obpi-completion-req-coverage-gate` (kind=foundation, lane=heavy)
**Mode:** Normal (no Exception declared on parent ADR)

## Context

Today `gz obpi complete` flips a brief to Completed once attestation is well-formed,
the security gate passes, and (post-ADR-0.0.24) ARB receipts cited in the
attestation resolve. It does **not** assert the brief's own REQs are individually
covered by passing tests. That gap is currently caught post-attestation by
`gz adr audit-check` at ADR closeout — too late and at the wrong granularity.

ADR-0.0.25 redefines what `Completed` means at brief level: a brief is
completable iff every REQ in `## Acceptance Criteria` has at least one passing
`@covers`-decorated test. OBPI-01 (this brief) lands the gate inside
`gz obpi complete` only; the `gz adr emit-receipt --event closed` mirror and
the `--accept-uncovered` override land in OBPI-02; doc + BDD updates land in
OBPI-03.

### Existing primitives we will compose

The codebase already carries the discovery machinery this OBPI needs:

| Primitive | Location | Role for OBPI-01 |
|---|---|---|
| `_COVERS_REF_PATTERN` | `src/gzkit/traceability.py:45` | canonical regex for `@covers` references — REQ-05 AST safety preserved |
| `_extract_covers_arg` (AST node) | `src/gzkit/traceability.py:435` | pulls REQ-ID out of decorator AST nodes |
| `scan_test_tree(test_dir) -> list[LinkageRecord]` | `src/gzkit/traceability.py:209` | walks `tests/**` once, emits one record per `@covers` |
| `_iter_test_functions` | `src/gzkit/traceability.py:200` | yields top-level + class-method test funcs |
| `_ast_qualified_name` | `src/gzkit/traceability.py` | renders `module.TestClass.test_method` qualified name |
| `scan_briefs(dir) -> list[DiscoveredReq]` | `src/gzkit/triangle.py:260` | walks brief tree; we extract single-brief logic |
| `parse_frontmatter_value(content, key)` | `src/gzkit/ledger.py` | parses YAML frontmatter — used for kind/lane |
| `_read_adr_kind(adr_file)` | `src/gzkit/commands/obpi_complete.py:229` | reads parent ADR `kind:` field |
| `_enforce_attestation_receipt_gate` (precedent) | `src/gzkit/commands/obpi_complete.py:275-354` | mirror pattern for the new gate's helper, _fail call shape, fail-closed semantics |

The new module reuses these primitives instead of reimplementing them — the
brief mandates a *new module* and *new function names* (REQ-01) but does not
mandate new discovery internals. AST-based discovery (REQ-05) is satisfied by
reusing the same AST walk `scan_test_tree` already performs (no test modules
imported, no `importlib`, no `inspect`).

## Allowed surface (from brief)

- `src/gzkit/commands/obpi.py` — gate logic in `complete` subcommand.
  **Note:** the actual completion handler lives at `src/gzkit/commands/obpi_complete.py`
  (the brief was authored before OBPI-04 split the file). The wiring lands there;
  `obpi.py` is a re-exporter and is read-only for this OBPI. Decision recorded
  here so the audit-check sees a documented routing rationale.
- `src/gzkit/governance/req_coverage.py` (new module) — REQ parsing and
  `@covers` discovery; stays under 600 lines per `.claude/rules/pythonic.md`.
- `tests/governance/test_req_coverage.py` — unit tests for the new module.
- `tests/commands/test_obpi_complete_coverage_gate.py` — wire tests.
- `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/**` —
  parent ADR package scope (this plan's evidence section + brief evidence
  blocks at completion time).

Read-only access to `src/gzkit/traceability.py` and `src/gzkit/triangle.py`
(scanning machinery is reused, not edited).

## Plan steps

### Step 1: TDD RED — author failing tests for `req_coverage` module

File: `tests/governance/test_req_coverage.py` (new).

Each test decorated `@covers(REQ-0.0.25-01-NN)` per REQ-08. Use tempfile
fixtures per REQ-09.

| Test class | REQ | Setup | Asserts |
|---|---|---|---|
| `TestParseBriefReqs` | 06, 09 | tempfile brief with mixed `## Acceptance Criteria` shape (REQ rows + non-REQ rows + sub-bullets) | only canonical `- [ ] REQ-X.Y.Z-NN-MM:` rows extracted; ordering preserved; non-REQ items skipped |
| `TestParseBriefReqsEmpty` | 06 | tempfile brief with no acceptance criteria section | returns `[]`; no exception |
| `TestParseBriefReqsMalformed` | 06 | tempfile brief with malformed REQ-IDs (`REQ-X-Y-Z`, `REQ-`) | malformed entries skipped, valid ones returned |
| `TestDiscoverCoversFinds` | 01, 05, 09 | tempfile tests root with one test file decorated `@covers("REQ-9.9.9-99-01")` | returns one `TestRef` carrying `module:class:test_method` shape; no test module imported |
| `TestDiscoverCoversMultiple` | 07, 09 | tempfile tests root with two tests decorated for same REQ | returns both refs; duplicate REQ → multiple refs |
| `TestDiscoverCoversNoMatch` | 01 | tempfile tests root with no covering tests | returns `[]` |
| `TestDiscoverCoversAstSafety` | 05 | tempfile tests root with a syntactically broken `.py` file plus a valid covering test | broken file logged + skipped, valid covering test still returned |

Run `uv run -m unittest tests/governance/test_req_coverage.py -v` and observe RED.

### Step 2: TDD GREEN — author `src/gzkit/governance/req_coverage.py`

The module exposes two pure functions and one Pydantic model. Pydantic over
dataclass per `.claude/rules/models.md`. Module size <600 lines, function
size <50 lines per `.claude/rules/pythonic.md`.

```python
"""REQ-coverage discovery for the OBPI completion gate.

Parses ``## Acceptance Criteria`` REQ-IDs from a brief and discovers
``@covers(REQ-...)``-decorated tests via AST without importing test
modules. Supports the gate at ``gz obpi complete`` (ADR-0.0.25, OBPI-01).

@covers OBPI-0.0.25-01-implement-coverage-gate
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.traceability import scan_test_tree


_REQ_ID_PATTERN = re.compile(r"REQ-\d+\.\d+\.\d+-\d+-\d+")
_ACCEPTANCE_HEADING = re.compile(r"^\s*##\s+Acceptance\s+Criteria\s*$", re.IGNORECASE)
_NEXT_H2 = re.compile(r"^\s*##\s+\S+")
_REQ_LINE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*(REQ-\d+\.\d+\.\d+-\d+-\d+)\s*:",
)


class TestRef(BaseModel):
    """Reference to a single ``@covers``-decorated test function."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    module: str = Field(..., description="Dotted module path or file path")
    qualified_name: str = Field(..., description="module.TestClass.test_method")
    file_path: str = Field(..., description="POSIX-rendered path to .py file")
    line: int = Field(..., description="Decorator line number")


def parse_brief_reqs(brief_path: Path) -> list[str]:
    """Return REQ-IDs declared in the brief's ``## Acceptance Criteria`` section.

    Tolerates the canonical brief shape ``- [ ] REQ-X.Y.Z-NN-MM: <description>``;
    skips checklist items that do not match the REQ-ID pattern. Returns IDs in
    document order, deduplicated. Returns ``[]`` if the section is missing or
    empty.
    """
    if not brief_path.is_file():
        return []
    text = brief_path.read_text(encoding="utf-8")
    in_section = False
    found: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        if _ACCEPTANCE_HEADING.match(raw):
            in_section = True
            continue
        if in_section and _NEXT_H2.match(raw):
            break
        if not in_section:
            continue
        match = _REQ_LINE.match(raw)
        if match is None:
            continue
        req_id = match.group(1)
        if req_id in seen:
            continue
        seen.add(req_id)
        found.append(req_id)
    return found


def discover_covers(req_id: str, tests_root: Path) -> list[TestRef]:
    """Return every test decorated with ``@covers(<req_id>)`` under tests_root.

    AST-based; never imports the test module under audit. Reuses
    ``gzkit.traceability.scan_test_tree`` so every consumer of @covers
    discovery sees the same set (REQ-05 + #120).
    """
    if not tests_root.is_dir():
        return []
    records = scan_test_tree(tests_root)
    refs: list[TestRef] = []
    for record in records:
        if record.target.identifier != req_id:
            continue
        loc = record.evidence_path
        line = record.evidence_line or 0
        qualified = record.source.identifier
        # Render POSIX-form file path per .claude/rules/cross-platform.md
        file_posix = Path(loc).as_posix()
        refs.append(
            TestRef(
                module=Path(loc).stem,
                qualified_name=qualified,
                file_path=file_posix,
                line=line,
            )
        )
    return refs
```

Run `uv run -m unittest tests/governance/test_req_coverage.py -v` until GREEN.
Observe RED → GREEN per increment (one REQ at a time, not all at once — TDD
anti-pattern in `.claude/rules/tests.md`).

### Step 3: TDD RED — wire-test fixtures for the gate

File: `tests/commands/test_obpi_complete_coverage_gate.py` (new).

Mirror the fixture/mock rig from `tests/commands/test_obpi_complete.py`
(receipt-binding gate). Use `tempfile.TemporaryDirectory` + `unittest.mock.patch`
on `_enforce_human_attestation_authenticity` and `_enforce_attestation_receipt_gate`
so the new gate is exercised in isolation. Use `Ledger.append` patching to
capture emitted events.

| Test | REQ | Lane / Kind | Brief shape | Asserts |
|---|---|---|---|---|
| `test_heavy_all_reqs_covered_passes` | 01 | heavy / foundation | brief w/ 2 REQs, both with covering passing tests | exit 0; brief flips Completed; gate event recorded |
| `test_heavy_uncovered_req_exits_3` | 02 | heavy / foundation | brief w/ 1 covered REQ + 1 uncovered REQ | SystemExit(3); brief unchanged; structured message names the gap |
| `test_foundation_lite_uncovered_exits_3` | 03 | lite / foundation | brief w/ 1 uncovered REQ on a foundation-kind ADR | SystemExit(3) (foundation overrides lite) |
| `test_lite_nonfoundation_uncovered_warns` | 04 | lite / feature | brief w/ uncovered REQ | exit 0; warning emitted; brief flips Completed |
| `test_heavy_covered_test_fails_exits_3` | 05 | heavy / foundation | brief w/ REQ whose only covering test asserts False | SystemExit(3) (gate runs the test and observes failure) |
| `test_multiple_covers_one_passing_satisfies` | 06 | heavy / foundation | brief w/ REQ covered by two tests; one fails, one passes | exit 0 (any one passing test satisfies REQ-7) |

Run `uv run -m unittest tests/commands/test_obpi_complete_coverage_gate.py -v`
and observe RED.

### Step 4: TDD GREEN — wire the gate into `obpi_complete_cmd`

File: `src/gzkit/commands/obpi_complete.py`.

Add a new helper after `_enforce_attestation_receipt_gate`:

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
) -> None:
    """Refuse completion when any brief REQ has no passing covering test.

    Behavior matrix (REQ-0.0.25-01-02..04, mirrors the receipt-binding gate):

    | Lane / Kind                       | Coverage outcome | Outcome |
    |-----------------------------------|------------------|---------|
    | heavy / any                       | gap or red test  | exit 3  |
    | any / foundation                  | gap or red test  | exit 3  |
    | lite / non-foundation             | gap or red test  | warning, proceed |
    | any                               | all REQs green   | proceed |

    Runs AFTER the ADR-0.0.24 receipt-binding gate so a missing receipt
    short-circuits the (slower) test-discovery + scoped-run path. Plan
    REQ-11 acknowledged the ordering as parallel-or-sequential; we pick
    sequential-after-receipt-binding for cost discipline.
    """
    if dry_run:
        return
    from gzkit.governance.req_coverage import discover_covers, parse_brief_reqs

    reqs = parse_brief_reqs(brief_path)
    tests_root = project_root / "tests"
    gaps: list[str] = []
    failing: list[str] = []
    for req in reqs:
        refs = discover_covers(req, tests_root)
        if not refs:
            gaps.append(req)
            continue
        # Run the discovered tests scoped via unittest TestLoader; any single
        # green observation satisfies REQ-7. Subprocess-isolated so a buggy
        # test cannot poison the parent CLI process.
        if not _any_covering_test_passes(refs, project_root=project_root):
            failing.append(req)

    fail_closed = parent_lane.lower() == "heavy" or parent_kind.lower() == "foundation"
    if not gaps and not failing:
        return

    diagnostic_lines = [f"  - uncovered: {req}" for req in gaps]
    diagnostic_lines.extend(f"  - failing-cover: {req}" for req in failing)
    detail = "\n".join(diagnostic_lines)

    if fail_closed:
        _fail(
            "OBPI completion REQ-coverage gate failed (heavy/foundation policy).\n"
            f"{detail}\n"
            "Recovery: add a `@covers(REQ-X.Y.Z-NN-MM)` test for each gap, or fix "
            "the failing covering tests, then re-run completion.",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id or parent_adr,
        )
    console.print(
        "[yellow]Warning:[/yellow] REQ-coverage gate reported gaps "
        "(lite-non-foundation; warn-only):\n" + detail
    )
```

Add `_any_covering_test_passes(refs, project_root)` helper that invokes
`unittest.TestLoader.loadTestsFromName` against the qualified names and
returns True iff at least one runs to a successful conclusion. Subprocess
boundary: invoke `uv run -m unittest <qualified_name>` for each ref and
inspect `returncode` (0 = green). This honors `.claude/rules/cross-platform.md`
subprocess shape (list form, no `shell=True`, encoding="utf-8") and
`.claude/rules/tests.md` two-runner contract (we are not adding a third
runner — we are invoking the existing unittest runner programmatically).

Wire the helper between section 4a-bis (receipt-binding gate, line 526) and
section 4b (TTY authenticity gate, line 545):

```python
    # 4a-ter. ADR-0.0.25-01 REQ-coverage gate: heavy/foundation = fail-closed
    # on any uncovered or failing-covered REQ; lite-non-foundation = warn-only.
    # Runs AFTER the receipt-binding gate (ADR-0.0.24) — receipt-resolution is
    # cheap, REQ test execution is the expensive step.
    _enforce_req_coverage_gate(
        obpi_id=obpi_id,
        parent_adr=resolved_parent,
        parent_lane=parent_lane,
        parent_kind=parent_kind,
        brief_path=obpi_file,
        project_root=project_root,
        as_json=as_json,
        dry_run=dry_run,
    )
```

Re-run `uv run -m unittest tests/commands/test_obpi_complete_coverage_gate.py -v`
until GREEN.

### Step 5: REQ→@covers parity gate

```bash
uv run gz covers OBPI-0.0.25-01 --json
```

Expect `summary.uncovered_reqs == 0`. Each REQ-0.0.25-01-NN must carry a
`@covers` decorator on a test in either of the two new test files.

REQ ↔ test mapping (table appears verbatim in Stage 4 evidence):

| REQ | `@covers` location |
|---|---|
| REQ-0.0.25-01-01 | `tests/commands/test_obpi_complete_coverage_gate.py::test_heavy_all_reqs_covered_passes` |
| REQ-0.0.25-01-02 | `tests/commands/test_obpi_complete_coverage_gate.py::test_heavy_uncovered_req_exits_3` |
| REQ-0.0.25-01-03 | `tests/commands/test_obpi_complete_coverage_gate.py::test_foundation_lite_uncovered_exits_3` |
| REQ-0.0.25-01-04 | `tests/commands/test_obpi_complete_coverage_gate.py::test_lite_nonfoundation_uncovered_warns` |
| REQ-0.0.25-01-05 | `tests/commands/test_obpi_complete_coverage_gate.py::test_heavy_covered_test_fails_exits_3` |
| REQ-0.0.25-01-06 | `tests/commands/test_obpi_complete_coverage_gate.py::test_multiple_covers_one_passing_satisfies` |

Auxiliary REQs (07–12) are mechanism-level expectations that underwrite REQs
01–06; they are tested through the same test classes (precedent: same
strategy used by OBPI-0.0.24-02 — see test_obpi_complete.py header table).

### Step 6: Quality gates (Stage 3 baseline)

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

Heavy lane → also:

```bash
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
```

## Verification (per brief)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_req_coverage.py tests/commands/test_obpi_complete_coverage_gate.py -v
```

## Destination-in-mind disclosure (Step 6a)

**Conclusion already formed:**

1. New module `src/gzkit/governance/req_coverage.py` exporting
   `parse_brief_reqs(Path) -> list[str]`, `discover_covers(str, Path) -> list[TestRef]`,
   and a frozen Pydantic `TestRef` model. The discovery side reuses
   `gzkit.traceability.scan_test_tree` so AST safety (REQ-05) and the canonical
   `@covers` regex (#120) are preserved without re-implementation.
2. Wire a new `_enforce_req_coverage_gate` helper into `obpi_complete.py`,
   placed between section 4a-bis (receipt-binding gate) and section 4b (TTY
   authenticity gate). Mirror the receipt-binding gate's structure exactly —
   helper signature, fail-closed predicate (`heavy or foundation`), `_fail`
   shape, warn-only fallthrough — so the two gates read consistently when an
   auditor compares them. Run scoped unittest via `subprocess.run` of
   `uv run -m unittest <qualified_name>` per discovered ref; one green
   observation satisfies a REQ.
3. TDD discipline: REQ-by-REQ Red → Green → Refactor (no test-dump, no
   batched-RED-then-batched-GREEN). Tempfile fixtures for both brief and
   tests-root corpus per REQ-09.

**Rejected alternatives:**

1. **Duplicate the AST walk inside `req_coverage.py` instead of reusing
   `scan_test_tree`.** Considered: keeps the new module self-contained and
   independent of traceability changes. Rejected: REQ-05 is "AST parsing,
   not regex" — `scan_test_tree` already satisfies that and is the single
   source of truth for `@covers` discovery (#120). Reimplementing it in a
   second module creates the exact "two scanners disagree" failure the #120
   work closed. The dependency is correct, not gold-plating.
2. **Run discovered tests via `unittest.TestLoader` in-process rather than
   `subprocess.run`.** Considered: faster, no subprocess startup cost.
   Rejected: in-process runs share state with the parent CLI process — a
   covering test that monkey-patches a module, mutates ledger state, or
   leaves I/O handles open will poison the rest of `gz obpi complete`.
   Subprocess isolation is worth the latency cost on a runtime gate.
3. **Make the gate advisory (warn, not fail-closed) on heavy/foundation, with
   an `--accept-uncovered` flag in this OBPI.** Rejected: ADR-0.0.25
   § Decision item 1 explicitly says heavy/foundation fail-closed; the
   `--accept-uncovered` override is OBPI-02's scope. Bundling overrides into
   OBPI-01 violates the brief-boundary anti-pattern and the OBPI-decomposition
   mandate.
4. **Run the full unittest suite at completion time and inspect the pass list
   for covering tests.** Considered: simpler than per-REQ scoping; avoids
   subprocess fan-out. Rejected: ADR-0.0.25 § Alternatives item 2 already
   examined and rejected this — the global pass already runs at Gate 2; the
   REQ-specific signal a brief-level gate produces is exactly what the global
   pass cannot give.
5. **Edit `src/gzkit/commands/obpi.py` directly even though the actual
   handler is in `obpi_complete.py`.** Rejected: `obpi.py` is a re-exporter;
   editing it would not affect runtime behavior. The brief's allowlist
   pre-dates the OBPI-04 file split; routing to `obpi_complete.py` is the
   correct interpretation under § Coupled-surface coherence (Invariant 1a).
   This routing decision is recorded in the Allowed-surface section above.

## Notes

- Confidence ≥ 90% — the receipt-binding gate (OBPI-0.0.24-02) is a tight
  precedent for shape, ordering, fail-closed predicate, and test fixture rig.
  No `gz-justify` walkthrough required (Stage 1→2 gate).
- Heavy lane → all gates required at OBPI completion (Gate 5 attestation
  TTY+ATTEST; Gate 3 docs land in OBPI-03 per brief; Gate 4 BDD in OBPI-03).
- Foundation kind → brief-level Gate 5 attestation required regardless of
  lane. Lock claim: `OBPI-0.0.25-01-implement-coverage-gate` (full slug from
  brief frontmatter `id`).
- Allowed-path routing decision (`obpi.py` → `obpi_complete.py`) is
  documented above; the brief audit-check should observe the rationale
  rather than reject the edit location.
- Cross-platform discipline: render relative paths via `.as_posix()`
  (`.claude/rules/cross-platform.md` v0.2.0) — applied in `discover_covers`
  output. Subprocess invocations stay list-form, encoding="utf-8".
- `data/security_surfaces.json` is **not** touched; this brief's allowed
  paths do not overlap any registered security surface, so `sensitivity:`
  remains absent (correct per `gz validate --sensitivity` floor + escalate
  policy).
