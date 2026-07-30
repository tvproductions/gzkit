# Plan — OBPI-0.34.0-04-execute-migration-populate-and-resense

**OBPI:** `OBPI-0.34.0-04-execute-migration-populate-and-resense`
**Parent ADR:** `ADR-0.34.0-foundation-sunset`
**Lane:** Heavy · **Sensitivity:** security (`ledger_integrity`)
**REQs:** REQ-0.34.0-04-01 [BEHAVIOR] · REQ-0.34.0-04-02 [SUPPORT] · REQ-0.34.0-04-03 [BEHAVIOR]

## Context

Execute the migration DATA + graph-integrity half of the Foundation Sunset. The
ACTIVATION half (Layer-3 status-index reconcile + wiring `--taxonomy` into
`gz check`) is OBPI-05 and is out of scope here.

### Verified starting state (observed, not assumed)

| Fact | Observation |
|---|---|
| Foundation packages on disk | 74 |
| `uv run gz validate --taxonomy` | exit 3, 74 × `foundation_kind_closed` (manifest empty) |
| `data/foundation_grandfather.json` | `[]` (3 bytes) |
| `tests/governance/fixtures/foundation_grandfather_golden.json` | `[]` (3 bytes) |
| Partition computed from Layer-2 graph | **23 unstarted (0 completed OBPIs) + 51 grandfathered = 74** — matches the brief exactly |
| `src/gzkit/foundation/sunset_migrate.py` | does not exist (CREATE) |
| `foundation_grandfathered` producer surfaces | none — OBPI-03 shipped only the raw-JSONL reader (`taxonomy.py:214`) |
| `--taxonomy` in `gz check` | NOT wired (correct — OBPI-05 scope) |
| `gz validate --sensitivity` | exit 0; brief's `security` declaration satisfies the floor |

### Prerequisite gate (brief Requirement 1 — STOP-on-BLOCKERS) — CLEARED

All five Sunset steps 1–4 prerequisites are `Validated` / closeout `validated`:
`ADR-0.0.65` 5/5 · `ADR-0.0.72` 3/3 · `ADR-0.0.54` 4/4 · `ADR-0.0.64` 5/5 ·
`ADR-0.0.37` 15/15. Intra-ADR: OBPI-01/02/03 all `attested_completed`.

### Operator rulings obtained at plan time

1. **Allowlist amended** (surgical, approved): `src/gzkit/schemas/ledger.json` and
   `src/gzkit/ontology/corpus.py` added. Rationale recorded in the brief's
   Allowed Paths; staleness logged as an `improvement` insight.
2. **136-brief deletion authorized.** `adr_demote.py:333` `shutil.rmtree`s the
   source package, so the 23 demotions delete 136 OBPI brief files. This is the
   demote verb's deliberate design (module docstring, "Q1=b of the 2026-05-23
   get-out-of-jail prequel"); `obpi_parked` events preserve child lineage and the
   ADR body survives verbatim in `ADR-pool.<slug>.md`. The migration receipt will
   enumerate every deleted path so the action is auditable.

### Destination-in-mind disclosure (Step 6a)

**Conclusion formed before authoring this plan.** After the first surface sweep I
had already decided the migration must be a *library function plus a thin
`__main__` shim* rather than a script under `scripts/`, because the brief names
`src/gzkit/foundation/sunset_migrate.py` as the entrypoint and REQ-01/REQ-03 need
importable seams to test. I also decided before planning that the partition must
reuse `Ledger.get_artifact_graph()` rather than reimplement last-event-wins,
because that is the only place completion-vs-repudiation net state actually lives
(`ledger.py:673` sets `ledger_completed=True` and clears `repudiated`; `:775`
does the inverse).

**Rejected alternatives.**

- *Call `adr_demote_cmd` directly for the 23 demotions.* Rejected: it hardcodes
  `get_project_root() == Path.cwd()`, prints to a Rich console, and raises
  `SystemExit(3)`, making it untestable from a fixture tree. Using the lower
  `_build_demote_plan` / `_apply_demote` seams (which take `project_root` and
  `config` explicitly) is testable and cwd-independent. **Trade-off accepted:**
  those are private helpers, so this couples to a `_`-prefixed API. The
  alternative couples to `cwd` and `SystemExit`, which is worse for a migration
  that must dry-run.
- *Reimplement the net-OBPI partition inside `sunset_migrate.py`.* Rejected —
  re-inlining the negation set is exactly the "four-copies-of-the-instance" shape
  `obpi_lifecycle.py`'s docstring says caused the GHI #520 demotion bug.
- *Reuse `_summarize_obpi_rows` from `commands/status_obpi.py` for the N/M
  roll-up.* Rejected: it blends on-disk brief inspection with ledger truth
  (`_obpi_row_complete` falls back to `found_file`), which contradicts the ADR's
  binding "partition by Layer-2, NEVER frontmatter" constraint.
- *Put `foundation_grandfathered` in `_CORPUS_LINEAGE_EVENT_TYPES`.* Rejected: it
  materializes no node or edge, so claiming lineage projection would be a lie the
  fidelity report can't catch. It belongs in the acknowledged-non-corpus set.
- *Add a graph applier in `ledger.py` for the new event.* Rejected as scope
  creep — the event has genuinely no graph impact, so the `NO_GRAPH_IMPACT`
  waiver in `tests/` is the honest declaration and keeps `ledger.py` untouched.

## Files

**Create**

- `src/gzkit/foundation/sunset_migrate.py` — migration entrypoint.

**Modify (additive only)**

- `src/gzkit/events.py` — `FoundationGrandfatheredEvent` model + union member.
- `src/gzkit/ledger_events.py` — `foundation_grandfathered_event(...)` factory.
- `src/gzkit/schemas/ledger.json` — `foundation_grandfathered` registry entry.
- `src/gzkit/ontology/corpus.py` — one member in `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES`.
- `data/foundation_grandfather.json` — populate 51 identity-only entries.
- `tests/governance/fixtures/foundation_grandfather_golden.json` — byte-identical co-edit.
- `tests/governance/test_ledger_event_handler_coverage.py` — `NO_GRAPH_IMPACT` waiver.
- `tests/test_schemas.py` — `_EVENT_MODELS` parity entry (bidirectional guard).

**Create (tests)**

- `tests/test_sunset_migrate.py` — REQ-01 and REQ-03 `@covers` tests + partition tests.

**Untouched (denied):** `taxonomy.py`, `models/foundation_grandfather.py`,
`quality.py`, `register-adrs`, `plan create` / `adr promote`, `ledger.py`,
`cli/**`, `.gzkit/ledger.jsonl` by hand.

## Steps

Red-Green-Refactor per behavior. Each RED must be an **assertion-level** failure,
not an ImportError — so step 1 lands importable stubs first.

### Step 1 — Register the event type across all five surfaces (one complete unit)

Bidirectional guards (`audit_event_schemas`, `test_schemas.py`) mean model,
schema entry, and factory must land together or the suite is red either way.

1. RED: extend `tests/test_schemas.py::_EVENT_MODELS` with
   `"foundation_grandfathered": FoundationGrandfatheredEvent` → watch
   `test_all_schema_events_have_models` / `test_all_models_have_schema_events`
   fail on the *missing pair*, not on import.
2. GREEN: add `FoundationGrandfatheredEvent` to `events.py` (mirroring
   `ArtifactRenamedEvent:176`: `event: Literal[...]`, `adr_id`/`title`/`semver`/
   `frozen_at`/`attestor` as needed, `task_id` for TASK attribution) and its
   union member at `events.py:823-885`; add the `schemas/ledger.json` entry with
   `required` matching the model; add `foundation_grandfathered_event(...)` to
   `ledger_events.py` mirroring `artifact_renamed_event:329`.
3. Add the `NO_GRAPH_IMPACT` waiver so `audit_event_handlers` passes without
   touching `ledger.py`.
4. Add the `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES` member in alphabetical
   position (between `enforcement_claim_verified` and `gate_checked`).
5. Verify: `uv run gz validate --ledger`, `uv run -m unittest tests.test_schemas`,
   `uv run -m unittest tests.test_ontology_corpus`.

**Emitted-event contract to satisfy:** `taxonomy.py:214` reads only
`event == "foundation_grandfathered"` and a non-empty `id`. The `id` MUST be the
full slugged frontmatter form (`ADR-0.0.9-state-doctrine-source-of-truth`), since
the gate does exact set-difference against manifest ids and on-disk ids. Schema
top-level `required` is `["schema","event","id","ts"]`, so events need those too
— which `Ledger.append` supplies.

### Step 2 — The partition computation (Layer-2 pure)

1. RED: `tests/test_sunset_migrate.py::test_partition_reads_ledger_not_frontmatter`
   — a fixture foundation whose frontmatter says `status: Validated` but whose
   OBPIs have zero completions must land in the DEMOTE set. This is the negative
   control that proves the partition is not reading frontmatter.
2. GREEN: `compute_partition(project_root, ledger) -> Partition` in
   `sunset_migrate.py`, reusing `Ledger.get_artifact_graph()` for
   `ledger_completed` / `repudiated` / `withdrawn` and `obpi_lifecycle`'s
   `TERMINAL_EVENTS` / `created_children` / `rename_chain_target`. Never
   re-inline the negation set.
3. Assert the observed invariant: `len(demote) + len(grandfather) == 74`,
   `len(demote) == 23`, `len(grandfather) == 51`.

### Step 3 — REQ-01: body-preserving demotion round-trip

1. RED: `@covers("REQ-0.34.0-04-01")` test — build a fixture foundation package
   with a distinctive Intent/Decision body, demote it, assert the resulting
   `ADR-pool.<slug>.md` body is **byte-identical** to the source body and that
   frontmatter lost exactly `kind`/`semver`/`date` and gained `id: ADR-pool.<slug>`
   / `status: Pool`, with all other keys preserved.
2. GREEN: drive demotion through `_build_demote_plan` / `_apply_demote`.
   Correct `adr_demote.py` only if this exposes a genuine body-preservation gap.
3. Also assert the *documented* deletion: the source package directory is gone
   and one `obpi_parked` event exists per child, so the 136-file blast radius is
   pinned by a test rather than left as a surprise.

### Step 4 — REQ-02: populate + backfill (SUPPORT proof channel)

1. Build the 51 identity-only entries (`id`, `title`, `semver`, `frozen_at` as
   `YYYY-MM-DD` per fixture convention). **No lifecycle field** — `extra="forbid"`
   would reject it anyway, which is the model doing its job.
2. Emit exactly one `foundation_grandfathered` event per entry via the factory
   and `Ledger.append` — never a hand-edited ledger line.
3. Write the golden fixture byte-identically (same indent, same trailing newline).
4. **Proof is the ledger event + structural validator, not a `@covers` test**
   (ADR-0.0.59): assert the 1:1 bijection via `uv run gz validate --taxonomy`
   reaching exit 0 with zero findings. Authoring a unit test here to make the
   REQ "look covered" is the exact category error GHI #571 names.

### Step 5 — REQ-03: ontology graph integrity

1. Capture the pre-migration baseline with `uv run gz ontology sense` **before**
   any demotion (`resense` diffs against `.gzkit/ontology/last_sweep.json`).
2. RED: `@covers("REQ-0.34.0-04-03")` test asserting the post-migration graph has
   no dangling endpoints — `compute_seams(project_all().graph) == []` (or a
   non-increasing seam count). `ShapeDiff` carries **no** dangling signal, so
   `compute_seams` (`ontology.py:111`) is the correct predicate; `ShapeDiff` is
   used only for the 23-node rename delta.
3. GREEN: run `uv run gz ontology resense --json`; confirm `removed_nodes`
   accounts for exactly the 23 renamed ADRs with successors present, and that
   `@covers`/`@surface` edges (source subgraph, visible only via `project_all()`)
   have no new seams.

### Step 6 — Migration entrypoint assembly

`--dry-run` default / `--apply` explicit, mirroring
`scripts/backfill_adr_taxonomy.py:171-191`. Receipt to
`artifacts/receipts/foundation-sunset-migration-<ts>.json` with the
`%Y-%m-%dT%H-%M-%SZ` stamp. Receipt records: partition rosters, every path the
demotions delete (the 136), manifest entries written, event ids emitted, and any
BLOCKERS. **Fail-closed on blockers** (raise, per `scripts/migrate_handoffs.py:96`)
— not the tautological `return 0` of the taxonomy backfill.

### Step 7 — Full verification sweep

Per the brief's Verification block, ARB-wrapped for receipts.

## Verification

```bash
uv run gz validate --brief-headings
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --sensitivity
uv run gz validate --taxonomy
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers OBPI-0.34.0-04-execute-migration-populate-and-resense --json
uv run gz arb red --req REQ-0.34.0-04-01 --obpi OBPI-0.34.0-04-execute-migration-populate-and-resense
uv run gz arb red --req REQ-0.34.0-04-03 --obpi OBPI-0.34.0-04-execute-migration-populate-and-resense
```

REQ-02 is SUPPORT — no `@covers`, no RED receipt; its proof is the ledger event
plus `--taxonomy` exit 0.

## Notes

- **Ordering is load-bearing.** `gz ontology sense` baseline → demotions →
  populate + backfill → `resense`. Capturing the baseline after demotion would
  make the diff vacuous.
- **`obpi_abandoned` is a phantom** (tracked in the brief's Tracked Defects). No
  partition outcome changes.
- **Do not run `register-adrs` or touch `gz check` wiring** — OBPI-05 scope. The
  Layer-3 status index will be stale after this OBPI *by design*.
