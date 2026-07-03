# Plan: OBPI-0.31.0-02-withdraw-supersede-transitions

## Context

Parent ADR: `ADR-0.31.0-obpi-state-machine`. OBPI-01 (attested, completed
2026-07-03) delivered the model layer: `OBPIState` (8-value closed enum),
`Transition`/`State` Pydantic models, `CANONICAL_TRANSITIONS` in
`src/gzkit/core/obpi_state_machine.py`. This OBPI (item 2) elevates
`gz obpi withdraw` to consult that model before writing, and builds the
missing `gz obpi supersede` verb — both witnessed (`human_attested`, per
`CANONICAL_TRANSITIONS`'s declared witness for every transition into
`WITHDRAWN`/`SUPERSEDED`).

**Destination-in-mind (Step 6a disclosure):** Before writing this plan I had
already concluded, during brief authoring, that `obpi_supersede_cmd` should
be modeled directly on the existing `obpi_repudiate_cmd`
(`src/gzkit/commands/obpi_cmd.py:125`) — same `--attestor` + reason-text
witness shape, same dry-run/ledger-append structure — because ADR-0.0.71
explicitly named that function as the "proven transition" precedent this ADR
inherits. That conclusion is unchanged by this planning pass; what planning
added was the precise mechanics (reading `obpi_withdraw_cmd`'s actual current
implementation, the artifact-graph's `_apply_*_metadata` dispatch pattern in
`ledger.py`, and `CANONICAL_TRANSITIONS`'s exact witness/evidence shape).

**Rejected alternatives (Step 6a disclosure):**
1. Using `--attestation-text` (the heavier `gz obpi complete` Gate-5 flag)
   for the withdraw/supersede witness, matching the ADR's literal prose
   ("relayed verbatim via `--attestor-present`/`--attestation-text`").
   REJECTED: the codebase's actual precedent for this class of lighter,
   single-transition witness is `obpi_repudiate_cmd`'s `--attestor` +
   `--reason` pair, not the Gate-5 ceremony's flags. Importing
   `--attestation-text` here would fragment CLI convention without a
   corresponding need — `--attestor` is sufficient to satisfy
   `human_attested` requirement in `CANONICAL_TRANSITIONS`.
2. Resolving each OBPI's *exact* current `OBPIState` (one of the 6
   non-terminal values) before consulting `CANONICAL_TRANSITIONS`. REJECTED:
   the full state-derivation migration (mapping the legacy `runtime_state`
   vocabulary — `pending`/`in_progress`/`validated`/`attested_completed`/
   `completed`/`drift` — onto the new 8-value `OBPIState` enum) is explicitly
   deferred-in-keel by the parent ADR ("Migrate `gz obpi complete` /
   `gz obpi reconcile` / `gz frontmatter reconcile` from batch-reconciler
   shape to transition-emitter shape" is listed as a *later* OBPI, not this
   one). Since `CANONICAL_TRANSITIONS` declares a `withdrawn`/`superseded`
   transition from **every** non-terminal state (see the generator in
   `obpi_state_machine.py:136-155`), the only state distinction that matters
   for THIS classifier is terminal-vs-non-terminal — which the ledger graph
   already exposes today via `info.get("withdrawn")` (need to add
   `info.get("superseded")` alongside it). A binary terminal check is a
   genuine, correct consultation of `CANONICAL_TRANSITIONS`'s actual shape,
   not a shortcut around it.

## Files

- `src/gzkit/core/obpi_state_machine.py` — READ ONLY (import `OBPIState`,
  `CANONICAL_TRANSITIONS`, `OBPI_STATES`)
- `src/gzkit/commands/obpi_cmd.py` — MODIFY (`obpi_withdraw_cmd`,
  new `obpi_supersede_cmd`)
- `src/gzkit/ledger_events.py` — MODIFY (`obpi_withdrawn_event` gains
  `attestor`; new `obpi_superseded_event`)
- `src/gzkit/ledger.py` — MODIFY (new `_apply_obpi_superseded_metadata`,
  registered in the dispatch sequence at ~line 733-734)
- `src/gzkit/cli/parser_artifacts.py` — MODIFY (withdraw parser gains
  `--attestor`; new `supersede` subparser, lines ~1243-1306 region)
- `src/gzkit/cli/parser_handler_manifest.py` — MODIFY (register
  `obpi_supersede_cmd` lazy-import entry)
- `src/gzkit/schemas/ledger.json` — MODIFY (register `obpi_superseded`
  event; extend `obpi_withdrawn`'s extra schema with `attestor`)
- `tests/commands/test_obpi_withdraw_cmd.py` — MODIFY (elevation +
  witness + terminal-state-refusal tests)
- `tests/commands/test_obpi_supersede_cmd.py` — CREATE (new verb tests)
- `docs/user/manpages/obpi-withdraw.md` — MODIFY
- `docs/user/manpages/obpi-supersede.md` — CREATE

## Steps

1. **RED/GREEN — classifier.** Add a small pure classifier consumed by both
   commands: given `already_terminal: bool` and `to_state: OBPIState`,
   return whether a declared `CANONICAL_TRANSITIONS` entry permits the
   transition (True whenever `already_terminal` is False, since every
   non-terminal state has a declared edge into both `WITHDRAWN` and
   `SUPERSEDED`; False when already terminal, since the generator excludes
   terminal states as `from_state`). Land this inline in `obpi_cmd.py` next
   to the two commands (no new module — the classifier is a few lines, not
   worth a separate file for this tracer-bullet slice). Test: OBPI already
   withdrawn → refused; OBPI in any other state → allowed. Watch the refusal
   test fail for the right reason (assertion on exit code / raised error,
   not an import error) before implementing.

2. **RED/GREEN — elevate `obpi_withdraw_cmd`.** Add `attestor: str` param;
   validate non-empty (mirror `obpi_repudiate_cmd`'s `if not attestor.strip()`
   guard); consult the classifier from step 1 using the existing
   `info.get("withdrawn")` check (already present) plus a new
   `info.get("superseded")` check; on refusal, raise `GzCliError` with a
   message naming the already-terminal state. Elevate `obpi_withdrawn_event`
   in `ledger_events.py` to accept and record `attestor`.

3. **RED/GREEN — `obpi_supersede_cmd`.** New function in `obpi_cmd.py`,
   signature `(obpi: str, by: str, rationale: str, attestor: str,
   dry_run: bool)`. Validate `attestor`/`rationale` non-empty. Resolve both
   `obpi` (the superseded ID) and `by` (the superseding ID) via
   `ledger.canonicalize_id`; confirm `obpi` is not already terminal (same
   classifier). New `obpi_superseded_event(obpi_id, parent, superseded_by,
   rationale, attestor)` in `ledger_events.py`, mirroring
   `obpi_completion_repudiated_event`'s shape.

4. **Graph visibility.** Add `_apply_obpi_superseded_metadata` in
   `ledger.py` (mirrors `_apply_obpi_withdrawn_metadata`): sets
   `graph[id]["superseded"] = True` and `graph[id]["superseded_by"]`.
   Register the dispatch call alongside the existing two at line ~733-734.
   Test: emit an `obpi_superseded` event, rebuild the graph, confirm the
   flag is visible — this is what step 2/3's classifier calls depend on.

5. **CLI wiring.** `--attestor` added to the `withdraw` subparser (required,
   matching `repudiate`'s pattern). New `supersede` subparser: positional
   `obpi`, `--by` (required), `--rationale` (required), `--attestor`
   (required), `--dry-run`. Register the lazy-import handler in
   `parser_handler_manifest.py`.

6. **Schema.** Register `obpi_superseded` in `src/gzkit/schemas/ledger.json`
   (event name + extra-field shape: `superseded_by`, `rationale`,
   `attestor`). Extend `obpi_withdrawn`'s extra schema with `attestor`.

7. **Landing regression tests.** In `test_obpi_withdraw_cmd.py`: an
   already-withdrawn OBPI refuses a second withdraw (this is the concrete,
   OBPI-02-scoped analog of the GHI #348 shape — a state-affecting operation
   that the model doesn't declare a transition for gets refused, not
   silently applied). In new `test_obpi_supersede_cmd.py`: full happy-path
   (event shape, both IDs cited) + terminal-state refusal.

8. **Docs.** Update `obpi-withdraw.md` for the `--attestor` requirement and
   refusal behavior; create `obpi-supersede.md` following the manpage
   template used by `obpi-repudiate.md`.

9. **Present OBPI Acceptance Ceremony.** (Stage 4 human gate — mandatory
   last task.)

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.31.0-02-withdraw-supersede-transitions --json
```

## Notes

- Confidence in this plan: ≥90%. Every integration point (witness flag
  precedent, graph dispatch registration, classifier shape) was read from
  the actual source, not assumed — the Stage 1→2 Confidence Gate walkthrough
  (`gz justify`) is not needed.
- Scope boundary held: no runtime invariant monitor, no edits to
  `obpi_state_machine.py`, no edits to `invariants.py`/`trust_audits/**` —
  those remain OBPI-03's exclusive territory per Boundary Invariant #1.
