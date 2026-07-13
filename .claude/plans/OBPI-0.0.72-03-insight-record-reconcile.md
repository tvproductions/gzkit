# Plan — OBPI-0.0.72-03-insight-record-reconcile

**OBPI:** OBPI-0.0.72-03-insight-record-reconcile
**Parent ADR:** ADR-0.0.72-meta-governance-coherence (foundation, heavy)
**Lane:** Heavy

## Context

Close contradiction C4 and GHI #575: the insight-append path is hand-authored
(agents write `.gzkit/insights/agent-insights.jsonl` by hand and drift from the
`InsightRecord` schema that gates the file), and there is no governed author
verb. Deliver both halves of a governed authoring path:

- **Core (domain):** `src/gzkit/insights/append.py` — a mechanical writer that
  constructs an `InsightRecord` first, then serializes exactly one JSONL line,
  so the append cannot omit `ts`/`type`.
- **Adapter (CLI):** `gz insights remember` — the `gz <verb>` surface agents
  invoke, mirroring `gz content remember`, wrapping the core helper.

Then reconcile the Behavior-Rule-11 prose to name the model's required fields
and direct agents at `gz insights remember` instead of a raw jsonl append.

**Coherence re-scope note:** OBPI-01's global `--writer-model-roundtrip`
validator was withdrawn (2026-07-13); the coherence check is realized as a
LOCALIZED per-writer round-trip test (REQ-03-02) — the helper's real emitted
output re-validated against `InsightRecord` directly, never a happy-path stub.

## Files

Core + adapter (CREATE):
- `src/gzkit/insights/append.py` — mechanical writer `append_insight(...)`
- `src/gzkit/commands/insights.py` — `register_insights_parsers` + `remember` handler
- `tests/governance/test_insight_append.py` — core TDD tests (REQ-03-01, 03-02)
- `tests/commands/test_insights_cmd.py` — verb TDD tests (REQ-03-05)
- `docs/user/manpages/gz-insights.md` — manpage (cli-audit parity)
- `features/insights_remember.feature` — behave scenario (Gate 4)

Wire + prose (EDIT):
- `src/gzkit/cli/main.py` — call `register_insights_parsers(commands)`
- `src/gzkit/insights/model.py` — read only (InsightRecord is the contract)
- `.gzkit/templates/agents.md` — Behavior Rule 11 composition source → required fields + point at `gz insights remember`
- `src/gzkit/templates/agents.md` — keep byte-equivalent (distribution invariant)
- `docs/governance/agent-contract-rationale.md` — Rule 11 'Required fields' prose

## Steps (TDD — Red-Green-Refactor per behavior)

1. **REQ-03-01 (BEHAVIOR)** — RED: test that `append_insight` writes a line that
   parses as JSON and validates against `InsightRecord` (ts/type/scope/summary +
   evidence list). Watch it fail on the assertion (stub the symbol first to
   avoid an import-only red). GREEN: implement `append_insight` — construct
   `InsightRecord(...)`, then `model_dump_json(exclude_none=True)` + append one
   line with `encoding="utf-8"`.
2. **REQ-03-02 (BEHAVIOR)** — RED: localized round-trip — the helper's ACTUAL
   emitted line re-validates against `InsightRecord`; and a line missing a
   required field raises `ValidationError`. GREEN: rely on construct-then-serialize
   (validation at construction) + a re-parse assertion in the test.
3. **REQ-03-05 (BEHAVIOR)** — RED: test `gz insights remember` appends exactly one
   valid line via the helper; empty `--summary` or out-of-enum `--type` exits
   non-zero and writes no line. GREEN: `register_insights_parsers` + `remember`
   handler wrapping `append_insight` (mirror `commands/content` remember); wire
   `register_insights_parsers(commands)` into `cli/main.py`.
4. **REQ-03-03 (SUPPORT)** — Edit `.gzkit/templates/agents.md` Behavior Rule 11:
   name required fields (ts/type/scope/summary; evidence a list) and direct agents
   to `gz insights remember`. Mirror to `src/gzkit/templates/agents.md`. Re-render
   via `uv run gz governance render --target agents-md`. Verify `--invariant-coherence`.
5. **REQ-03-04 (SUPPORT)** — Align `docs/governance/agent-contract-rationale.md`
   'Required fields' prose with the model envelope. Verify `--documents`.
6. **Docs/BDD** — Author `docs/user/manpages/gz-insights.md` (verify `gz cli audit`)
   and `features/insights_remember.feature` tagged `@REQ-0.0.72-03-05` (Gate 4).

## Verification

- `uv run gz validate --documents`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run gz test`
- `uv run gz validate --invariant-coherence`
- `uv run gz validate --insights-shape`
- `uv run gz cli audit`
- `uv run gz covers OBPI-0.0.72-03-insight-record-reconcile --json` (REQ→@covers parity)

## Notes

- **Composition-source discipline (ADR-0.0.37):** NEVER hand-edit rendered
  `AGENTS.md`. Edit `.gzkit/templates/agents.md`, mirror to `src/gzkit/templates/agents.md`,
  re-render. `--invariant-coherence` and `--distribution` must stay green.
- **Hexagonal:** helper = core (stdlib + Pydantic only); verb = CLI adapter.
  No new runtime dependency (STDLIB-FIRST).
- **cli-alignment:** `gz insights remember` becomes registered, so brief/ADR/Rule-11
  references resolve.
- Known #581 false-positive: brief-reconcile `req_count` heuristic (fail-closed
  Requirements vs Acceptance count) — documented, not gamed.
