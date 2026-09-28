# Plan — OBPI-0.35.0-07-content-land-orchestrator

Brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-07-content-land-orchestrator.md`
Parent: ADR-0.35.0-canon-entry-corpus-landing, Decision 6 and checklist item 7; BI-03 and BI-10. Lane: Heavy.

## Context

`gz content commit` promotes one consumer at a time and writes its rendition and provenance
sidecar non-atomically. `gz content land <surface>` is the governed multi-consumer promotion:
one corpus attestation, a shared `landing_id`, a durable journal written before the first byte
and cleared last, per-file atomic replacement, fingerprint/hash-based `--status`, and a
non-destructive resume that never re-prompts. The operator's four 2026-09-27 rulings (brief
§ Change Log) add Requirement 12 / REQ-10 (the OBPI-14 retention gate on every consumer),
build the event with ledger_row(model) instead of editing the ledger-events module, allowlist
`src/gzkit/ontology/corpus.py` + `tests/test_schemas.py`, and ratify § Threat Model.

Reused by import, never modified (Denied or outside the allowlist): generate_candidate from the
composer module (05); verify_candidate_against_declaration from the rendition-lineage trust audit (06);
enforce_retention from the content commit command and retention_path from the retention module (14);
write_bytes_atomically and load_declaration from the ownership module; commit_directory_entry from the
durability module; exclusive_file_lock from the file-lock module; routes_for from the vendors module;
load_corpus from the corpus store; Ledger append/read_all and ledger_row from the ledger module.

## Files

- CREATE `src/gzkit/content/landing.py` — journal model, preparation, staging, publication, verification, completion, status, resume.
- CREATE `src/gzkit/commands/content/land.py` — CLI handler, recovery prose, exit codes.
- `src/gzkit/commands/content/__init__.py` — `_register_land` only.
- `src/gzkit/content/rendition_store.py` — additive optional `landing_id` on `RenditionProvenance`.
- `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json`, `src/gzkit/governance/events.py` — `RenditionLandedEvent` model, schema entry, `emit_rendition_landed` via `ledger_row`.
- `src/gzkit/ontology/corpus.py`, `tests/test_schemas.py` — disposition + model map for the new event.
- `config/doc-coverage.json`, `tests/content/test_tui_affordances.py` — new-verb coupled consumers.
- CREATE `tests/content/test_landing.py`, `tests/commands/test_content_land.py`, `features/content_land.feature`, `features/steps/content_land_steps.py`.
- `docs/user/manpages/content.md`, `docs/user/runbook.md`; the brief's evidence sections.

## Steps

Three verification groups (brief Requirement 1). One implementer per task, sequential, RGR with assertion-level RED.

### Task 1 — Preflight and staging (REQ-01, REQ-03, REQ-10; REQ-02 staging half)

1. `RenditionProvenance.landing_id: str | None = None` (additive; old sidecars load; `extra="forbid"` retained; no lineage fields — BI-03).
2. Landing-module models (Pydantic, frozen, `extra="forbid"`): `ArtifactTarget {kind: rendition|provenance|lineage|retention, path (relative, validated under the surface's rendition directory), old_sha256 | None, new_sha256 | None (None = removal)}`, `ConsumerPlan {consumer, old_corpus_fingerprint | None, artifacts, published}`, `LandingJournal {landing_id, surface, phase: prepared|publishing|verified|complete, new_corpus_fingerprint, corpus_entry_count, route_digest, ownership_digest, consumers, attestor, attestation_text, created_ts}`.
3. `prepare_landing(root, surface, *, attestor, attestation_text, retention_maps)`: resolve routed consumers for the surface's content type; for each, generate_candidate, verify_candidate_against_declaration (06; empty problem list required), enforce_retention against THIS invocation's attestation text (14; exit 3 on refusal, whole landing refused). Retention maps are matched to consumers by the map's own target. Build every artifact's bytes in memory (rendition, provenance with shared `landing_id` + `rendition_fingerprint`, lineage in the exact byte form the lineage staging writer produces, retention sidecar or removal). Pure: writes nothing.
4. Attestation resolution (Requirement 5): a new corpus delta without reusable evidence refuses empty/whitespace attestor or text (exit 1, nothing written). Unchanged corpus reuses evidence only when every consumer's sidecar exists, validates, carries the current corpus fingerprint and a `rendition_fingerprint` matching the committed bytes; missing/corrupt/mismatched sidecars are never proof (refuse with three-part prose).
5. CLI `gz content land <surface>` (required positional, REQ-01) with `--attestor` (config default like `commit`), `--attestation-text`, repeatable `--retention-map`, `--dry-run` (prints the plan, writes nothing), `--status <landing_id>`. Parser registration in `src/gzkit/commands/content/__init__.py`.
6. Staging failure (REQ-02 first half): an induced failure while staging consumer 2 of 3 leaves every committed artifact byte-identical and no journal.

### Task 2 — Durable publication and completion (REQ-04, REQ-05; REQ-02 replace half)

1. Surface-scoped exclusive_file_lock on a .landing.lock file in the surface's rendition directory; a second active landing cannot interleave.
2. Journal as a .landing.json file in the surface's rendition directory, written with write_bytes_atomically (fsync + directory barrier) BEFORE any artifact byte (phase `publishing`), carrying landing_id, full consumer set and corpus fingerprint (REQ-05).
3. Stage every artifact's bytes in a journal-owned staging dir, fsynced; then per-file write_bytes_atomically replacement (or unlink + directory barrier for a retention removal), marking each consumer published and re-persisting the journal after its last artifact.
4. Verified phase: re-hash every published artifact against `new_sha256`, re-check shared `landing_id` + attestation on every sidecar, and re-run 06 verification on the published pair.
5. RenditionLandedEvent (rendition_landed: surface, landing_id, corpus_fingerprint, attestor, consumers, new and old path-to-sha256 manifests) in `src/gzkit/events.py`, its entry in `src/gzkit/schemas/ledger.json`, and emit_rendition_landed via ledger_row in `src/gzkit/governance/events.py`. Event id derived deterministically from `landing_id`; before appending, read the ledger for that id so a crash after the event and before cleanup never duplicates it (exactly ONE event, REQ-04). Register the discriminator in `src/gzkit/ontology/corpus.py` and `tests/test_schemas.py`.
6. Clear the journal and staging dir LAST (after the event is durable), then directory barrier. A replace failure after the first file leaves the journal, emits no event, and exits 2 with three-part prose (REQ-02 second half).
7. Interruption tests at every boundary: before journal, after journal, between a rendition and its sidecars, after last file before event, after event before cleanup.

### Task 3 — Status, resume and recovery (REQ-06, REQ-07, REQ-08)

1. landing_status(root, surface, landing_id): read-only; manifest from the live journal, or from the `rendition_landed` event after cleanup; per consumer, hash actual rendition + lineage + provenance bytes and classify `new` (all match new manifest and provenance fingerprint/landing_id agree), `old` (all match old manifest), else `indeterminate` with three-part prose. Never reads mtime; a good sidecar copied beside altered bytes is `indeterminate`.
2. Resume: `land <surface>` with a journal present and no new attestation reuses the recorded attestor/text and `landing_id` (REQ-08; no `--force`). It requires identical corpus fingerprint, route digest and ownership digest; any drift, or an artifact matching neither old nor new hash, refuses automatic overwrite with the exact recovery path. Artifacts already at their new hash are never rewritten (REQ-07, byte-unchanged).
3. Malformed journal or an unsafe path is an error with recovery prose, never a silent restart.

### Task 4 — Docs, BDD and coupled consumers (REQ-09; Gate 3/4)

1. `docs/user/manpages/content.md`: land synopsis, options, exit codes, journal/status/resume contract, retention maps, and the named rollback: committed renditions have no prior-version retention, so recovery is a git checkout of the surface's rendition directory from a known-good revision, covering rendition, provenance, lineage and retention together, plus a check that the revision matches the current corpus.
2. `docs/user/runbook.md`: operator flow and the same rollback.
3. `config/doc-coverage.json`, `tests/content/test_tui_affordances.py` for the new verb.
4. `features/content_land.feature` and `features/steps/content_land_steps.py`: a scenario per BEHAVIOR REQ in an isolated synthetic three-consumer project, tagged `@REQ-0.35.0-07-NN`.
5. `artifact_edited` ledger event citing `docs/user/manpages/content.md` for REQ-09's SUPPORT channel.

## Verification

- `uv run -m unittest tests.content.test_landing tests.commands.test_content_land`
- `uv run -m behave features/content_land.feature`
- `uv run gz lint`, `uv run gz typecheck`, `uv run gz test`
- `uv run gz validate --documents`, `uv run gz validate --req-kind-discipline`, `uv run gz validate --rendition-freshness`
- `uv run gz cli audit`, `uv run mkdocs build --strict`
- Demo: `uv run gz content land --help`; `uv run gz content land AGENTS.md --dry-run`

## Notes — plan-before-exploration disclosure (gz-plan-audit Step 6a)

- **Destination in mind before writing:** a single landing-module state machine driven by a JSON journal beside the renditions, reusing the existing atomic writer, lock and 05/06/14 seams; a new ledger event for completion.
- **Rejected alternatives:** (a) atomic activation of an immutable generation directory (rejected by the ratified Publication Amendment; needs a new read protocol outside the allowlist); (b) emitting one rendition_committed event per consumer (violates REQ-04's single event; operator chose a new event); (c) a landing-private ledger writer or file-existence completion proof (forbidden by § Ledger Prerequisite); (d) calling validate_retention directly (BI-10 requires the complete enforce_retention); (e) mtime-based status (Requirement 7).
