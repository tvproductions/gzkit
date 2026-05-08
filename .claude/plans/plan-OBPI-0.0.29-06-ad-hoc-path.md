# Plan: OBPI-0.0.29-06-ad-hoc-path

**OBPI:** OBPI-0.0.29-06-ad-hoc-path
**Parent ADR:** ADR-0.0.29-complexity-advisor
**Lane:** Heavy
**Brief:** docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-06-ad-hoc-path.md

## Context

OBPI-03 landed the `gz complexity-advise` CLI verb with a single `_render_prose()` function.
OBPI-05 landed the auto-chain hook that calls `gz complexity-advise --auto-chain`.
This OBPI (06) adds the presentation-dispatch layer: two distinct presenter classes for the
ad-hoc pathway (verbose, full diagnostic detail) and the auto-chain pathway (concise one-line
summary + hint), dispatched from the CLI based on the `--auto-chain` flag.

The current `complexity_advise.py` already accepts `auto_chain: bool = False` but renders
the same prose regardless of that flag. This OBPI replaces that single-path render with
a dispatched Presenter pattern.

## Allowed Files

- `src/gzkit/commands/complexity_advise.py`
- `src/gzkit/complexity/advisor/presentation.py` (new)
- `tests/commands/test_complexity_advise_ad_hoc.py` (new)
- `features/complexity_advise_ad_hoc.feature` (new)
- `docs/user/manpages/gz-complexity-advise.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-06-ad-hoc-path.md`

## Steps

### Step 1: Create `presentation.py` — TDD Red first

Write failing tests for `AdHocPresenter` and `AutoChainPresenter` in
`tests/commands/test_complexity_advise_ad_hoc.py` before writing the module.
The tests must be decorated `@covers("REQ-0.0.29-06-NN")` for each REQ.

Tests must cover:
- REQ-01: Ad-hoc verbose output contains metric, crossing_band, crossing_value, archetype,
  doctrinal_frame (authority, citation, excerpt), per-proof source-line snippets,
  recommended_move, intrinsic_attestation reference (if any)
- REQ-02: Auto-chain concise output contains only one-line summary per diagnosis
  (metric, crossing band, archetype, file:line range, recommended_move headline)
  and ends with "run `gz complexity-advise <path>` for full detail" hint
- REQ-03: `--json` mode identical output regardless of pathway
- REQ-04: Clean file ad-hoc → "no crossings" with "checked N functions across M metrics"
- REQ-05: Clean file auto-chain → silent (empty string output)
- REQ-05 (presenter class): `AdHocPresenter` and `AutoChainPresenter` share a `Presenter`
  protocol and can be substituted independently

### Step 2: Implement `presentation.py` — Green

Create `src/gzkit/complexity/advisor/presentation.py` with:

```python
class Presenter(Protocol):
    def render(self, diagnoses: list[AdvisorDiagnosis], metrics_checked: int, functions_checked: int) -> str: ...

class AdHocPresenter:
    """Verbose presenter for operator ad-hoc invocation (preview-before-fail)."""

class AutoChainPresenter:
    """Concise presenter for auto-chain hook invocation (trigger-time fail-fast)."""
```

`AdHocPresenter.render()`:
- Empty diagnoses: "Complexity advisor: no crossings detected.\nchecked {N} functions across {M} metrics; no warn or block crossings"
- Each diagnosis: full verbose block including:
  - `metric=... value=... band=...`
  - `Archetype: ...`
  - `Authority: ... (citation: ...) — excerpt: ...`
  - Per-proof range with source-line snippets (read source lines from proof's file_path)
  - `Recommended move: ...`
  - `Intrinsic attestation: <reference>` (if diagnosis has intrinsic_attestation field)

`AutoChainPresenter.render()`:
- Empty diagnoses: "" (silent, per REQ-05)
- Each diagnosis: single line `metric={metric} band={band} archetype={archetype} {file}:{start}-{end} → {recommended_move_headline}`
- Footer: "\nRun `gz complexity-advise {path}` for full detail."

Ensure ≤300 lines per `.claude/rules/pythonic.md`.

### Step 3: Update `complexity_advise.py` — dispatch to presenter

Replace the `_render_prose()` call in `complexity_advise_cmd()` with:

```python
presenter = AutoChainPresenter() if auto_chain else AdHocPresenter()
output = presenter.render(diagnoses, metrics_checked=M, functions_checked=N)
if output:
    print(output)
```

Track `metrics_checked` (count of distinct metric keys checked) and `functions_checked`
(count of functions analyzed across all files) for the clean-file message.

JSON output path remains unchanged (identical regardless of `auto_chain` flag, REQ-03).

### Step 4: Create `features/complexity_advise_ad_hoc.feature` — BDD scenarios

Three scenarios tagged `@REQ-0.0.29-06-01`, `@REQ-0.0.29-06-02`, `@REQ-0.0.29-06-03`:
- Scenario 1 (`@REQ-0.0.29-06-01`): Ad-hoc against clean fixture — output contains "no crossings"
- Scenario 2 (`@REQ-0.0.29-06-02`): Ad-hoc against warn-band fixture — output contains archetype and authority
- Scenario 3 (`@REQ-0.0.29-06-03`): Auto-chain against warn-band fixture — output is concise (one-line per diagnosis)

Use fixture files from `tests/fixtures/complexity/` already created by prior OBPIs.

### Step 5: Extend `docs/user/manpages/gz-complexity-advise.md`

Add a new `## EXAMPLES` section (or extend existing) with at least one example each for:
- Ad-hoc preview: `gz complexity-advise src/foo.py`
- Auto-chain context: `gz complexity-advise --auto-chain src/foo.py` (invoked by hook)

Note: `--auto-chain` flag note should say "verbose vs concise" presentation distinction
is now active (not "reserved" as in the current OBPI-03 text).

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_complexity_advise_ad_hoc.py -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/complexity_advise_ad_hoc.feature
uv run gz complexity-advise tests/fixtures/complexity/warn_band.py
```

## Notes

- `presentation.py` must be ≤300 lines (REQ-09 / `.claude/rules/pythonic.md`)
- All tests use `@covers("REQ-0.0.29-06-NN")` decorator
- No email in code, tests, fixtures, or commit messages (REQ-11)
- The `--json` path short-circuits before presenter dispatch — identical output both pathways
- Auto-chain concise output exits 3 on block-band (same exit-code contract as ad-hoc)
- Destination-in-mind: Presenter protocol + two classes + CLI dispatch
- Rejected alternative: inline presenter logic in `complexity_advise.py` — rejected because
  REQ-05 mandates separable classes in `presentation.py`
