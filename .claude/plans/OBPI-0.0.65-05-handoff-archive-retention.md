# Plan — OBPI-0.0.65-05-handoff-archive-retention

**OBPI:** OBPI-0.0.65-05-handoff-archive-retention
**Parent ADR:** ADR-0.0.65-handoff-system-consolidation (§ Decision #3 — the `gz handoff` verb)
**Lane:** Heavy

## Context

`.gzkit/handoffs/` grows monotonically (GHI #585). It is append-only by design:
`gz handoff` exposes only create/list/resume, and three mechanical guards make a
hand-`rm` a fail-close risk. This OBPI adds a governed `gz handoff archive`
subcommand that MOVES (never deletes) handoffs older than a threshold into
`.gzkit/handoffs/archive/`, honoring all three guards.

Prerequisite satisfied: OBPI-0.0.65-03 landed the `gz handoff` verb
(create/list/resume) — confirmed via `uv run gz handoff --help`.

## Files (all within brief Allowed Paths)

- `src/gzkit/handoff_archive.py` — **new** runtime module (domain core, stdlib +
  Pydantic only): archive-eligibility selection honoring the three guards; a
  frozen Pydantic `ArchivePlan` result; a `plan_archive()` selector and an
  `execute_archive()` mover.
- `src/gzkit/commands/handoff_archive.py` — **new** thin CLI adapter (mirrors
  `commands/handoff.py`): builds a payload from the runtime API, renders human /
  `--json`, exits 0/1.
- `src/gzkit/cli/parser_maintenance.py` — register the `archive` subparser under
  the existing `gz handoff` sub-parser group (`--older-than`, `--dry-run`,
  `--json`).
- `tests/governance/test_handoff_archive.py` — **new** BEHAVIOR tests (REQ-01..05).
- `tests/governance/test_handoff_migration.py` — extend the floor test to count
  `canonical + archive/` (REQ-04).
- `docs/user/manpages/handoff-archive.md` — **new** manpage (SUPPORT REQ-06).
- `features/handoff_archive.feature` — **new** behave coverage (Heavy Gate 4).
- `.gzkit/handoffs/archive/` — runtime destination, created on first move.

## Read-only reuse (imports, never edits — brief Requirement 5)

- `gzkit.handoff_validation.parse_frontmatter` — timestamp + `continues_from`.
- `gzkit.ledger.Ledger.query(event_type="obpi_lock_released")` → `event.extra["handoff_path"]`
  (lock-coupling guard data source).

## Guard design (derived from REQs, not implementation)

1. **Move-not-delete (REQ-01):** `Path.rename` / `shutil.move` canonical→archive;
   byte content unchanged; source no longer present.
2. **Lock-coupling (REQ-02):** never archive a handoff whose project-relative path
   is any recorded `obpi_lock_released.handoff_path`. → report SKIPPED(locked).
3. **Chain-integrity (REQ-03):** never archive a handoff that is the
   `continues_from:` target of a still-canonical handoff. → SKIPPED(chained).
   (Resolver lives in a denied security surface; skip-target is the only in-scope
   design — it also keeps `test_continues_from_chains_resolve` green.)
4. **Floor (REQ-04):** move keeps `canonical + archive` count constant; the
   migration floor test is taught to count both dirs so the invariant is asserted.
5. **Dry-run (REQ-05):** `--dry-run` computes the plan and mutates nothing.

Eligibility = older-than-threshold AND not-locked AND not-chain-target AND
frontmatter-datable (undatable handoffs are conservatively skipped — never lose
an audit trail we cannot age).

## Steps (Red-Green-Refactor, one behavior per cycle)

1. Skeleton: create `handoff_archive.py` with `ArchivePlan` model + `plan_archive`
   / `execute_archive` stubs so tests import cleanly (avoids the false import-red).
2. REQ-05 (dry-run) → REQ-01 (move) → REQ-02 (lock skip) → REQ-03 (chain skip):
   one RED (assertion-level) → GREEN → refactor per REQ, using `tempfile` dirs and
   an injected `now`.
3. Wire `commands/handoff_archive.py` adapter + `--older-than/--dry-run/--json`.
4. REQ-04: extend `test_handoff_migration.py` floor to count archive subdir.
5. REQ-06: author manpage; run `gz cli audit` for verb coverage parity.
6. Author `features/handoff_archive.feature` with `@REQ-0.0.65-05-0N` scenario tags.

## Verification (brief § Verification — single-program invocations)

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.governance.test_handoff_archive -v
uv run -m unittest tests.governance.test_handoff_migration -v
uv run -m behave features/handoff_archive.feature
```

## Notes — Plan-Before-Exploration disclosures (audit Step 6a)

- **Destination-in-mind:** Before writing this plan I had already formed the
  approach: a pure `handoff_archive.py` domain module + thin `commands/` adapter,
  mirroring the OBPI-03 `handoff.py`/`handoff_api.py` split, with the three guards
  as pure selection predicates over frontmatter + ledger reads.
- **Rejected alternatives:**
  (a) *Make the resume resolver follow into `archive/`* (REQ-03 option b) — rejected:
  requires editing `handoff_validation.py`/`handoff_api.py`, both outside Allowed
  Paths (former is a denied security surface), forcing `sensitivity: security`.
  (b) *Copy-then-flag instead of move* — rejected: violates REQ-01 (move-not-delete
  means relocation, and a copy doubles the store rather than decluttering it).
  (c) *Delete-with-tombstone* — rejected outright: Requirement 1 forbids deletion.
  (d) *Put domain logic in the command module* — rejected: violates the hexagonal
  thin-adapter contract the OBPI-03 sibling establishes.
