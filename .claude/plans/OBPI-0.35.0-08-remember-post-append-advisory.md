# Plan — OBPI-0.35.0-08-remember-post-append-advisory (remaining REQ-04, REQ-06, REQ-02 OSError arm)

## Context

Operator initiated this pipeline on 2026-10-03 (`/gz-obpi-pipeline OBPI-0.35.0-08`). It supersedes
the 2026-08-23 coverage-only plan, written when `gz content land` did not exist. OBPI-0.35.0-07 has
since landed (`uv run gz content land --help` exits 0, measured 2026-10-03), so REQ-04 is unblocked.

`gz covers` measured 2026-10-03: 8 REQs, 5 covered. Uncovered: REQ-04 and REQ-06 (both `[behavior]`)
and REQ-07 (`[structural-fence]`, audited at ADR closeout, never a unit test). `gz obpi brief-drift`
is clean on all five dimensions.

## Steps

1. **REQ-0.35.0-08-04 — retarget the advisory prose.** In `src/gzkit/commands/content/_drift.py`
   the advisory currently recovers via `gz content compose` + `gz content commit` per consumer and
   does not cite the ADR-0.0.37 corpus->rendition seam. Change it to emit three parts: the count and
   named drifted renditions (unchanged), the seam cited by ADR-0.0.37 (not paraphrased), and a runnable
   `uv run gz content land <surface>` invocation. Keep the floor-risk sentence for invariant-tier
   appends. RED first: a test in `tests/commands/test_content_remember.py` that fails on the current
   prose for the seam citation and the land invocation, bound `@covers("REQ-0.35.0-08-04")`.
2. **Retire half of the shared advisory.** `src/gzkit/commands/content/retire.py` calls the same
   function, so `tests/commands/test_content_retire.py` assertions on the old compose/commit text are
   updated in the same change (coupled surface, DO IT RIGHT 1a). The retire advisory floor
   distinction is preserved.
3. **REQ-0.35.0-08-06 — byte-identical rows and identical exit code.** Author a paired-fixture test
   with the clock and entry identity controlled: the same append performed once with drift present and
   once without, comparing the corpus rows byte-for-byte and the exit codes. Bind
   `@covers("REQ-0.35.0-08-06")`. Stream separation is not claimed (struck 2026-08-24, operator-ruled).
4. **REQ-0.35.0-08-02 — add the OSError arm.** The Verification Clarifications require both
   exception branches through the production advisory call; only the ValueError branch is exercised.
   Add a test that makes drift detection raise OSError and asserts the append and exit 0, bound to
   REQ-02.
5. **Docs (heavy lane).** Update the `remember` advisory contract in `docs/user/manpages/content.md`
   to the new three-part prose, with real captured output.
6. **BDD (heavy lane).** Add a scenario to `features/content_remember.feature` (steps in the existing
   steps module) for the advisory naming `gz content land` and the append surviving.
7. **Brief evidence.** Update the PARTIALLY PRE-LANDED table, REQ-04 and REQ-06 rows, and the
   evidence sections of the brief; add a `### Change Log` under `## Evidence`.

## Files

- `src/gzkit/commands/content/_drift.py`
- `tests/commands/test_content_remember.py`
- `tests/commands/test_content_retire.py`
- `features/content_remember.feature`
- `docs/user/manpages/content.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md`

Read-only: `src/gzkit/content/rendition_store.py`, `src/gzkit/content/vendors.py`. Every path the
brief denies is left untouched; the advisory only names the land verb and never invokes it.

## Verification

- `uv run gz covers OBPI-0.35.0-08-remember-post-append-advisory --json` — expect REQ-04 and REQ-06
  covered, only REQ-07 remaining (structural-fence, ADR closeout).
- `uv run gz arb ruff`, `uv run gz arb typecheck`, the full unittest sweep through `gz arb step`.
- `uv run gz validate --req-kind-discipline`, `uv run gz cli audit`, `uv run mkdocs build --strict`.
- `uv run gz arb red --req REQ-0.35.0-08-04 --obpi OBPI-0.35.0-08-remember-post-append-advisory`
  and the same for REQ-06, run while the production change is uncommitted.

## Notes — Step 6a disclosures

**Destination-in-mind.** I expected REQ-04 to be a prose retarget in one function. Reading the retire
tests showed the same function is shared, so the change is two test files, not one.

**Rejected alternatives.** (a) Keep the compose/commit recovery lines beside the land line: rejected,
because `gz content land` is the governed single step under one attestation and two recoveries would
leave the operator a choice the ADR removed. (b) Add a stderr-split runner to prove REQ-06's stream
claim: rejected, the operator ruled reword over changing the runner on 2026-08-24. (c) Edit the
read-only rendition-store predicate: rejected, REQ-08 binds the advisory to it as written.
