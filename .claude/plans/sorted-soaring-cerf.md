# Plan: OBPI-0.0.16-04 Backfill and GHI Closure

## Context

ADR-0.0.16 (frontmatter-ledger coherence guard) introduced a validator (OBPI-01),
gate wiring (OBPI-02), a reconciliation chore (OBPI-03), and a status-vocab
mapping (OBPI-05) — all attested-completed. OBPI-04 is the **dogfooding run**:
execute the chore once against the live repo to clear ~94.7% governed-frontmatter
drift, capture the receipt as evidence, and close the five upstream GHIs (#162,
#167, #168, #169, #170) that motivated the ADR. No new product code — only
chore invocation, evidence capture, an idempotence regression test, and
issue-closure comments. This OBPI unblocks ADR-0.0.16 closeout (currently
`BLOCKED` per `gz adr status ADR-0.0.16` because OBPI-04 is the only
non-completed sibling).

Mode: **Normal** — parent ADR has no `## Execution Mode: Exception (SVFR)`
section, so Stage 4 ceremony requires human attestation.

## Approach

Execute the 10 brief requirements sequentially. Two operator pauses are
expected: REQ-02 (sign-off on dry-run plan before live run) and Stage 4
(ceremony attestation). Everything else is autonomous within the pipeline.

## Steps

1. **Prerequisites gate (REQ-01).** Confirm OBPIs 01, 02, 03, 05 are
   `attested_completed` via `uv run gz adr status ADR-0.0.16`. STOP-on-BLOCKERS
   if any are pending.

2. **Dry-run #1 (REQ-02).** Run
   `uv run gz chore run frontmatter-ledger-coherence --dry-run`. Capture the
   emitted receipt path under `artifacts/receipts/frontmatter-coherence/`. Read
   the receipt JSON, paste a summary (file count + per-file `field: before →
   after` diffs) into OBPI-04 brief Evidence section. **Present to operator
   for sign-off** before proceeding.

3. **Live run (REQ-03, REQ-08).** After sign-off, run
   `uv run gz chore run frontmatter-ledger-coherence` (no `--dry-run`). Capture
   live receipt path. Cite it in both the OBPI brief Evidence section and the
   parent ADR's Evidence section (line 225 of the ADR file). Do NOT hand-edit
   any frontmatter — every rewrite goes through the chore.

4. **Post-run validation (REQ-04).** Run `uv run gz validate --frontmatter`
   over the full repo. MUST exit 0. If exit 3, STOP and triage the chore — do
   not hand-fix residual drift. Record exit code in ADR Evidence.

5. **Idempotence check (REQ-05).** Run
   `uv run gz chore run frontmatter-ledger-coherence --dry-run` a second time.
   Receipt's `files_rewritten` array MUST be empty. Cite this receipt path in
   evidence as the idempotence proof.

6. **Regression test.** Create `tests/chores/test_frontmatter_coherence_backfill.py`
   with `@covers(REQ-0.0.16-04-04)` and `@covers(REQ-0.0.16-04-05)` decorators.
   Test pins post-backfill cleanliness: invokes
   `reconcile_frontmatter(project_root, dry_run=True)` against the real repo
   and asserts `receipt.files_rewritten == []`. Also create
   `tests/chores/__init__.py` (mechanical prerequisite for unittest discovery
   — implicitly required by the test file's allowed path).

7. **GHI closures (REQ-06).** Close issues #162, #167, #168, #169, #170 via
   `gh issue close <N> --comment "..."`. Each comment MUST cite (a) `ADR-0.0.16`,
   (b) the live-run receipt path from Step 3, (c) a one-line statement of how
   the guard+chore closes the issue (per the per-GHI text already in the
   brief at REQ-06 lines 60–63). Capture closure timestamps from
   `gh issue view <N> --json closedAt`. Do NOT close GHI #166 (out of scope —
   REQ-09).

8. **ADR Evidence + Closeout-Form updates (REQ-07, REQ-10).** Edit the parent
   ADR (line 225+ Evidence section) to record: dry-run receipt path, live-run
   receipt path, second-dry-run receipt path, the five GHI numbers + closure
   timestamps, and the `gz validate --frontmatter` post-run exit code. Edit
   `ADR-CLOSEOUT-FORM.md` line 37 to flip OBPI-04 status to `Completed` and
   line 53 to flip the proof status from `PENDING` to `EVIDENCE`.

9. **Stage 3 quality verification.** Run `uv run gz lint`, `uv run gz typecheck`,
   `uv run gz test --obpi OBPI-0.0.16-04-backfill-and-ghi-closure`. Heavy lane
   adds `uv run gz test --obpi OBPI-0.0.16-04-backfill-and-ghi-closure --bdd`,
   `uv run gz validate --documents`, and `uv run mkdocs build --strict`. Then
   `uv run gz covers OBPI-0.0.16-04-backfill-and-ghi-closure --json` to verify
   `uncovered_reqs == 0` (parity gate per pipeline Stage 3 Phase 1b).

10. **Stage 4 ceremony.** Present evidence template (value narrative, key proof
    — the live-run receipt + post-validate exit 0, full evidence table, REQ
    coverage table, files created/modified). Heavy lane → wait for human
    attestation.

11. **Stage 5 sync.** `uv run gz obpi complete
    OBPI-0.0.16-04-backfill-and-ghi-closure --attestor <name> --attestation-text
    "<verbatim>"`. Release lock. Two-sync git cycle. Reconcile.
    `uv run gz adr status ADR-0.0.16` to confirm the ADR moves from BLOCKED to
    closeout-ready.

## Critical Files

**Created:**
- `tests/chores/test_frontmatter_coherence_backfill.py` (regression test)
- `tests/chores/__init__.py` (unittest package marker)

**Modified:**
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md` (Evidence section line 225)
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-CLOSEOUT-FORM.md` (lines 37, 53)
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/obpis/OBPI-0.0.16-04-backfill-and-ghi-closure.md` (Evidence section)

**Generated (untracked artifacts):**
- `artifacts/receipts/frontmatter-coherence/<ISO8601>-dry-run-1.json`
- `artifacts/receipts/frontmatter-coherence/<ISO8601>-live.json`
- `artifacts/receipts/frontmatter-coherence/<ISO8601>-dry-run-2.json`

## Reused Implementation Surfaces

- Chore handler: `src/gzkit/commands/frontmatter_reconcile.py:26` (`frontmatter_reconcile_cmd`) — already wired through `gz chore run` registry at `config/gzkit.chores.json:220-225`
- Reconciliation library: `gzkit.governance.frontmatter_coherence.reconcile_frontmatter` + `ReconciliationReceipt` Pydantic model
- Validator: `src/gzkit/cli/parser_maintenance.py:329-340` (`gz validate --frontmatter`) — exit 0 = clean, exit 3 = drift
- Test fixture pattern: `tests/commands/test_chores.py` (existing chore-test conventions)
- Coverage decorator: `@covers` from existing test infrastructure

## Verification

- Step 4 outcome: `gz validate --frontmatter` exits 0 (no drift).
- Step 5 outcome: second dry-run receipt has `len(files_rewritten) == 0`.
- Step 6 outcome: `uv run -m unittest tests.chores.test_frontmatter_coherence_backfill -v` passes.
- Step 7 outcome: each `gh issue view <N> --json state` returns `CLOSED`.
- Stage 3 final: `gz covers OBPI-0.0.16-04-backfill-and-ghi-closure --json` shows `uncovered_reqs == 0`.
- Stage 5 final: `gz adr status ADR-0.0.16` shows OBPI-04 `attested_completed`, closeout no longer `BLOCKED`.

## Risks / Notes

- **Operator pause expected at Step 2 (REQ-02 sign-off).** The pipeline does
  not auto-proceed from dry-run to live run; operator must approve the
  list of files-to-be-rewritten.
- **`tests/chores/__init__.py` is not in the brief's allowed paths** but is
  a mechanical prerequisite for unittest discovery of the regression test.
  Treating as in-scope inferred requirement; if challenged at review,
  alternative is to colocate the test under `tests/commands/` (less clean).
- **Receipt timestamps appear in ADR Evidence** — receipts themselves live
  under `artifacts/receipts/` (typically gitignored). Evidence cites paths,
  not file content.
- **GHI closure is irreversible from this session's perspective** but the
  comments are factual and reversible by reopening if needed.
