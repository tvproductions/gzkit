---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-27T09:49:30Z'
agent: claude-code
session_id: d7d3a98e-af0f-41f4-8008-e9fb984068e6
continues_from: .gzkit/handoffs/20260827T083027Z-session-closed-879-and-887-landed.md
---

## Current State Summary

GHI #856 is CLOSED and pushed; GHI #890 was authored from this session's gate
measurement and is OPEN with a blocker. Tree clean, branch `main` synced 0/0 at
`9eadc012`, no active OBPI locks. No OBPI or ADR work was started or touched.

**#856 (closed, `21ade055`).** The canonical "Tests pass" attestation command was
the serial stdlib runner while every gate ran `unittest-parallel`, so the command
agents run most often was the slow one. Now swapped, with `quality.run_tests`
DERIVING from `CANONICAL_STEP_COMMANDS["unittest"]` instead of re-spelling it --
the class fix, matching what `run_typecheck` has done since GHI #199. Measured at
`2c81cb7d`, 10-core M-series, same 8,912 tests, both exit 0: 144.23s serial vs
41.34s pinned-parallel, a 3.49x cut of roughly 103s per attestation.

**#890 (open).** `uv run gz validate --surfaces` rewrites 101 canonical files on
every run -- `AGENTS.md`, `CLAUDE.md`, all 25 `.claude/rules/`, 17
`.claude/hooks/`, every vendor mirror -- because it proves sync parity by
performing `sync_all()` rather than rendering and comparing. That write is what
classes `Validate default scopes` as a writer, which makes four read-only gate
steps wait on it. Drift-masking was tested and DISPROVEN: planted drift fails
closed (exit 1) and is left in place.

Gate composition, measured at `9eadc012` via the live `_build_check_steps()`
registry: total serial cost 125.19s across 57 steps; serial writers sum 42.10s
(n=3); read-only 83.08s of work (n=54) collapsing to the 43.54s of its slowest
member, `Test`. The gate's floor is therefore 85.64s against an observed 106.86s.

## Important Context

- **The #856 swap was blocked by a LATER operator ruling, not by the issue's own
  blocker.** #856's 2026-08-22 plan sequenced the swap after #857; `c67d3b25`
  (2026-08-26) then ratified the SERIAL form on dependency-provenance grounds and
  said "do not optimise it without re-ruling the argument above". Two operator
  surfaces disagreed, which is Behavior Rules -- Always #9 territory, so it was
  surfaced rather than resolved by the agent.
- **The precedent that argued against pinning did not exist.** GHI #512 and
  `.pre-commit-config.yaml` both cited "the un-pinned xenon/gitleaks precedent";
  `xenon` is a pinned `dev` entry invoked as `uv run xenon`, and `gitleaks` is a
  native binary, not a Python package. `unittest-parallel` was the ONLY Python
  verifier wielded via `--with`, so pinning it is conformance, not a stdlib-first
  departure. Recorded as an insight.
- **Pinning was also faster than `--with`** (41.34s vs 52.02s): `--with` paid a
  network resolve on every invocation.
- **`CANONICAL_STEP_COMMANDS` is READ, not merely documented.**
  `verifier_pipe_gate._canonical_program_names()` derives `VERIFIER_PROGRAMS` from
  it, so the swap silently DROPPED bare `unittest` from the pipe gate's protected
  set while `uv run -m unittest` remains how a scoped run is spelled at ~3,100 call
  sites. `_DECLARED_BEYOND_ARB` now carries it. The pre-existing registry-coherence
  test is structurally blind to this direction -- it iterates what the table names,
  so a verifier LEAVING the table is invisible to it.
- **Order-independence is a precondition of attesting with a parallel runner**, and
  it was measured rather than assumed: #857's shuffle harness re-run at `2c81cb7d`
  across three seeds, 8,912 tests, zero failures each. Re-run that probe before
  widening the canonical entry again.
- **Behave tiering is NOT an available remedy for gate cycle time.** GHI #182
  removed the third tier; #860 deleted the `@slow` tag and armed `audit_test_tiers`
  against tier-shaped tags in `features/**`. Do not re-propose it.
- **Validator-level gate optimisation is exhausted.** #835 moved 54 steps into a
  concurrent phase; they now contribute roughly nothing to wall time beyond
  `Test`'s shadow. Two of 57 steps (`Behave` 34.10s, `Test` 43.54s) carry 62% of
  total step cost and neither is reducible by scheduling.
- **Mutation testing can silently verify stale bytecode.** A same-length constant
  edit landing inside one mtime second defeats CPython's (mtime, size) `.pyc`
  invalidation, so a "restored" run re-executes the mutant. Clear `__pycache__`
  between cycles. The tell is a runtime value that `grep` cannot find in the source
  file the module reports as its own.
- **AGENTS.md is played back from a committed rendition.** Hand-editing it fails
  `gz validate --invariant-coherence`; the governed seam is `gz content compose` ->
  `gz content commit` -> `gz agent sync control-surfaces`. Attestation fail-closes
  only if the CORPUS moved; a rendition-only change carries the standing
  attestation forward.

## Decisions Made

- [operator-ruled] Pin `unittest-parallel`, then swap the canonical attestation
  command (verbatim selection: "Pin the runner, then swap"). This DISCHARGES the
  2026-08-26 dependency-provenance objection rather than overriding it. Rejected:
  affirming the serial path and closing #856 `withdrawn`; and swapping while the
  runner stayed un-pinned, which would have re-opened the ratified objection.
- [operator-ruled] Measure the gate's step composition and file it (verbatim:
  "measure the gate's step composition and file it").
- [agent-chose] Left GHI #890 OPEN with a blocker naming the next concrete action,
  rather than fixing in-session: the remedy sits in the validate path and is larger
  than the 3.66s it recovers, and the operator ask was measure-and-file.
- [agent-chose] Did NOT widen `strip_uv_run` to parse `uv run` option tokens.
  Pinning removed `--with` from the canonical command, so the argv head is the
  program again and the parser change became speculative.
- [agent-chose] Scored advisory-scorecard row 87 **Mechanical** citing
  `NC:smoke-tier`, and stated in the row that the control plants an EMPTY tier and
  therefore witnesses only that arm -- no control plants a real 60s breach. A row
  reading as fully witnessed when half of it is not is the false-Mechanical shape
  that column's freeze was ruled against.
- [agent-chose] Set the `RETIRED_STEP_COMMANDS` boundary at 2026-08-27T00:00:00Z,
  derived from the newest serial receipt's `timestamp_utc` (2026-08-26T09:45:39Z)
  measured across all 1110 `arb-step-unittest-*` receipts -- by field, never by
  mtime, which a checkout rewrites.

## Immediate Next Steps

1. **Rule on GHI #890.** The next concrete action is named in the issue: make
   `validate_surfaces` render candidate surfaces to memory (or a temp tree) and
   byte-compare, instead of establishing parity by running `sync_all()`. That
   removes the write, which removes the `writes` classification, which frees the
   four read-only steps that wait on it; `data/check_step_concurrency.json` then
   reclassifies `Validate default scopes` to `read_only`. The reason to do it is
   the Layer-1/derived-view boundary, not the 3.66s.
2. **Then GHI #886** -- Stage-2 dispatch credit lives only in the Layer-3 pipeline
   marker, so the sanctioned clear-stale recovery destroys it. Carried from the
   prior handoff and still the strongest pull; #887 [settled] already established the
   Layer-2 pattern to mirror, including the graph handler and disclosure
   discipline.
3. **Then GHI #883, then #882.** #883 is the two canonical ledger readers
   disagreeing on explicit null and on array item types, across all 54 event
   types. #882 is labelled enhancement and its own body calls it new capability,
   so routing there is a judgment rather than a threshold result.
4. **GHI #889 still needs a scoping ruling before any code.** Its check globs the
   project's whole receipt history, so "are the receipts green" is undefined until
   "which receipts are this OBPI's evidence" is settled. Candidate scopings are in
   the issue body; none was chosen.
5. **Do NOT promote `ADR-pool.validator-scope-registration-seam`.** Ascending-semver
   order binds and ADR-0.35.0 is still in flight; read its landed count from
   `uv run gz adr status ADR-0.35.0`, never from a figure transcribed here.

## Pending Work / Open Loops

- **GHI #890 -- OPEN with a blocker.** Filed this session; writer isolated to
  `gz validate --surfaces` by bisect; drift-masking tested and disproven. Awaiting
  an operator ruling on whether to take the remedy now.
- **Two findings disclosed on #890 but deliberately NOT filed** (one GHI, one class
  of failure): `Docs build` is a writer with NO consumer (4.34s serial for no
  dependency reason, self-declared isolated in `data/check_step_concurrency.json`);
  and possible oversubscription in the concurrent phase -- `Test` spawns 10
  `unittest-parallel` workers inside a phase running up to 8 steps on a 10-core
  host, the likeliest explanation for the ~21s between the 85.64s floor and the
  106.86s observed wall. The second is an UNTESTED hypothesis, stated as such.
- **GHI #886, #883, #882, #889 remain OPEN**, unchanged by this session.
- **OBPI-0.35.0-03 stays HELD and OBPI-0.35.0-08 stays in_progress.** Resuming
  either is operator-initiated work under the IRON LAW; nothing in this session
  touched them.
- **`data/check_step_concurrency.json` `why` prose understates one entry.** The
  `Validate default scopes` rationale names only "vendor persona mirrors under
  .agents/personas/" -- 7 of the 102 files actually written. Its `paths` array IS
  accurate, so the classification is right and this is a prose-vs-data mismatch,
  not a correctness defect. Noted in #890 rather than filed separately.

## Verification Checklist

- [ ] Tree clean and branch synced: `git status --short` empty, and both
      `git rev-list --count origin/main..HEAD` and
      `git rev-list --count HEAD..origin/main` return `0`
      (two-dot form on purpose: a three-dot ref trips the authoring
      gate's elision scan, which once refused a handoff prescribing
      `git rev-list` in its own Verification Checklist)
- [ ] Gate green: `uv run gz check` exits 0 (last observed 106.86s at `9eadc012`)
- [ ] `uv run gz obpi lock list` reports no active locks before starting anything
- [ ] GHI states before acting on step 1: `gh issue view 890 --json state,title`
      and the same for #886, #883, #882, #889 -- resolve at read time, never
      transcribe from this document
- [ ] If the canonical test invocation is touched again, RE-RUN the #857 shuffle
      probe first: flatten the discovered suite, shuffle under a recorded seed,
      three seeds, expect zero failures. Order-independence is the precondition
      for attesting with a parallel runner.
- [ ] Working discipline that held: `git add -A` before `uv run gz check` so the
      pre-push gate can reuse the pass; `set -o pipefail` on every verifier;
      mutation-test each new guard AND clear `__pycache__` between cycles;
      read the surface before honouring a blocker comment; pass `--limit 200` to
      `gh issue list`

## Evidence / Artifacts

Commits: `21ade055` (the fix) and `9eadc012` (ledger backstop row), both pushed to
`main`.

ARB receipts, the unittest one emitted through the NEW canonical invocation so the
swap is proven end to end:

- `arb-ruff-bdcd52a1c8f1498aad994d2d8786c3ec`
- `arb-step-typecheck-a0e9f91bd2c1490484f669574b653a4c`
- `arb-step-unittest-81b962001611403784139df66ea09050` (8,927 tests, OK, 47.76s)
  -- `artifacts/receipts/arb-step-unittest-81b962001611403784139df66ea09050.json`

Source surfaces changed:

- `pyproject.toml`, `uv.lock` -- `unittest-parallel` pinned, resolved 1.8.6
- `src/gzkit/canonical_steps.py` -- table entry plus rewritten rationale
- `src/gzkit/quality.py` -- `run_tests` derives from the canonical table
- `src/gzkit/arb/validator.py` -- `RETIRED_STEP_COMMANDS["unittest"]` row
- `src/gzkit/verifier_pipe_gate.py` -- `unittest` into `_DECLARED_BEYOND_ARB`
- `.pre-commit-config.yaml` -- the copy that cannot derive, pinned by equality

Tests added or changed:

- `tests/arb/test_unittest_runner_lockstep.py` (new, 9 tests)
- `tests/arb/test_validator_provenance.py` (supersession class)
- `tests/hooks/test_verifier_pipe_gate.py` (verifier-left-the-table class)

Governance surfaces:

- `docs/governance/advisory-rules-audit.md` -- row 87 added for a clause that had
  never been scored; Coverage Ledger row bumped to 0.18.0
- `.gzkit/rules/tests.md` -- rule version 0.17.0 to 0.18.0, figures restated as a dated record
- `data/check_step_concurrency.json` -- read, not changed; source of the writer
  classification this session measured against
- `src/gzkit/validate_pkg/surface.py` -- the writer isolated for GHI #890
- `.gzkit/handoffs/20260827T083027Z-session-closed-879-and-887-landed.md` -- predecessor

## Settled Rulings

557 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
