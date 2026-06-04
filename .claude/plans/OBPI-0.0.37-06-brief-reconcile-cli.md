# Implementation Plan — OBPI-0.0.37-06-brief-reconcile-cli

**OBPI:** OBPI-0.0.37-06-brief-reconcile-cli
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy (foundation kind) → all gates + universal Gate 5 human attestation
**Prerequisites:** OBPI-04 (BriefStructure) + OBPI-05 (reconcile engine) — both `attested_completed`

## Objective

Land the operator-runnable CLI surface `gz brief reconcile <OBPI-ID> [--apply --attestor "<name>"]`
that wraps OBPI-05's already-shipped `reconcile_brief` engine: every run prints the per-dimension
delta summary and emits a `brief_reconciled` ledger event; drift additionally emits
`brief_reconcile_drift_detected`; `--apply --attestor` writes operator-attested amendments back
into the brief frontmatter. Consume the engine — never modify it (OBPI-05 owns it).

## Grounded integration surfaces (read, not guessed)

| Need | Surface | Exact contract |
|------|---------|----------------|
| Engine (consume only) | `src/gzkit/governance/brief_reconcile.py:124` | `reconcile_brief(brief_path: Path, project_root: Path) -> ReconcileResult` |
| Result model | same, `:91-102` | `ReconcileResult{ brief_id, allowlist_delta, discovery_delta, verification_delta, req_count_delta, citation_delta, has_drift: bool }` — frozen Pydantic |
| Brief id→path | `src/gzkit/pipeline_markers.py:508` | `find_obpi_brief(docs_root: Path, obpi_id: str) -> Path \| None` |
| Event factory | `src/gzkit/ledger_events.py` | factory fns return `LedgerEvent(event=..., id=..., extra={...})`; `*_ts` auto-injected — do NOT pass |
| Event emit | `src/gzkit/governance/events.py` | `emit_*` helper: `Ledger(root/".gzkit"/"ledger.jsonl").append(<factory>(...))` |
| Event schema | `.gzkit/schemas/ledger_events.json` | top key `event_types[]`; entry keys `id, name, schema, required_fields` |
| Verb registration | `src/gzkit/cli/parser_artifacts.py` | new TOP-LEVEL `brief` parser → `reconcile` subparser (pattern mirrors `p_obpi`/`obpi_commands` at `:916`) |
| `--apply`/`--dry-run` | `src/gzkit/commands/specify_cmd.py:720` | dry-run branch prints preview + early return; write branch writes + appends ledger |
| Module template | `src/gzkit/commands/governance_render.py` (73 lines), `obpi_lock.py:24` | keyword-only handler, dual json/human output, ledger emit |

### Brief↔reality reconciliations (baked in, mechanical — no operator decision)

1. **Delta-count derivation.** REQ-01's event payload names scalar `*_delta_count` fields, but the
   engine returns structured delta objects (`allowlist_delta.missing_on_disk/missing_in_brief`,
   `verification_delta.unresolved_verbs`, `req_count_delta.delta`, `citation_delta.stale_citations`,
   `discovery_delta.unresolved_paths`). The CLI derives the scalar counts from these objects.
2. **`--attestor` is conditionally required** (only with `--apply`) — NOT argparse `required=True`
   (that pattern in `attest.py`/`obpi complete` is unconditional). Manual check: `if args.apply and
   not args.attestor: parser.error("--apply requires --attestor")` → argparse exit 2.
3. **`gz brief reconcile` is a new top-level `brief` verb group**, not nested under `obpi`.

## Files (Allowed Paths — exact)

Creates these files:

- `src/gzkit/commands/brief_reconcile.py` **CREATE** — CLI handler (no collision: `gzkit.commands.brief_reconcile` is a different package from the engine `gzkit.governance.brief_reconcile`)
- `tests/commands/test_brief_reconcile.py` **CREATE** — CLI tests (RGR)
- `docs/user/manpages/gz-brief.md` **CREATE** — NAME/SYNOPSIS/DESCRIPTION/OPTIONS/EXAMPLES (real output)

Modifies:

- `src/gzkit/cli/parser_artifacts.py` — register top-level `brief` → `reconcile`
- `src/gzkit/ledger_events.py` — `brief_reconciled_event`, `brief_reconcile_drift_detected_event` factories
- `src/gzkit/governance/events.py` — `emit_brief_reconciled`, `emit_brief_reconcile_drift_detected` helpers
- `.gzkit/schemas/ledger_events.json` — two new `event_types[]` entries
- `features/brief_reconcile.feature` — CLI scenarios tagged `@REQ-0.0.37-06-*`
- `docs/user/runbook.md` — "When briefs drift: `gz brief reconcile <OBPI-ID>` then `--apply`"

## TDD sequence (RED → GREEN per REQ; commit each GREEN)

1. **Event factories + schema** (REQ-07): add two factories + two `event_types[]` entries. Test:
   factories produce schema-conformant events; `gz validate` events-schema passes. GREEN.
2. **Emit helpers** (REQ-01/02 support): `emit_brief_reconciled`, `emit_brief_reconcile_drift_detected`.
3. **Handler default mode** (REQ-01/02): resolve brief via `find_obpi_brief`, call `reconcile_brief`,
   print delta summary, emit `brief_reconciled`; on `has_drift` also emit drift event + exit 3, else
   exit 0. Test both no-drift (exit 0) and drift (exit 3, both events) paths.
4. **Verb registration** (REQ-06): top-level `brief` → `reconcile`; `gz brief reconcile --help` resolves.
5. **`--apply` guards** (REQ-03/05): `--apply` without `--attestor` → `parser.error` exit 2;
   `--apply --dry-run` previews without writing.
6. **`--apply --attestor` write** (REQ-04): append allowlist additions to `## Allowed Paths`,
   REQ-count fixes to Acceptance Criteria, unresolved-verb notes to `## Tracked Defects` (never
   silent verb rewrite); emit `brief_reconciled` with `applied: true` + attestor. Test write + event.
7. **Manpage + runbook + feature** (REQ-08, Gate 3/4): author `gz-brief.md` with real EXAMPLES
   output; runbook entry; `@REQ-0.0.37-06-*` scenarios; `mkdocs --strict` + `behave` green.

## Gates (Heavy)

- Gate 1: CLI-verb ADR paragraph quoted (Discovery Checklist).
- Gate 2: `tests/commands/test_brief_reconcile.py` covers no-drift/drift/`--apply`-without-attestor/
  `--apply`-with-attestor; canonical unittest receipt.
- Gate 3: `gz-brief.md` manpage (real output) + runbook entry; `mkdocs build --strict`.
- Gate 4: `features/brief_reconcile.feature` CLI scenarios; `behave` passes.
- Gate 5: **Foundation-kind universal human attestation** — pipeline stops here; cannot self-close.

## Risks / watch-items

- **No silent verb rewrite** (REQ-04): unresolved-verb amendments are notes only, operator judgment.
- **Self-reconcile zero-drift** (Completion Checklist): on completion,
  `gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli` must report zero drift (dogfood the verb).
- **Pipeline Stage-1 reconcile gate is NOT yet active** (that is OBPI-07/08) — so OBPI-06's own
  pipeline will not require a reconcile receipt to enter Stage 2.

## Execution

After plan approval: `uv run gz obpi pipeline OBPI-0.0.37-06-brief-reconcile-cli`
(runtime owns implement → verify → ceremony → guarded git-sync → completion; stops at Gate 5).
