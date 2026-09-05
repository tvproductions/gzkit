---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-05T12:52:47Z'
agent: claude-code
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: 29614bbc-0808-4532-934b-4d1e10490a14
continues_from: .gzkit/handoffs/20260905T105626Z-obpi-0-35-0-04-round-11-refuted-d-plus-e-ruling-owed.md
---

## Current State Summary

**EXECUTION IS PAUSED BY OPERATOR INSTRUCTION.** Verbatim: *"Stop implementation and all reviewer/adversary dispatches for OBPI-0.35.0-04. Cancel active subagents. Preserve the current edits; do not revert, commit, or mark the OBPI complete. Do not propose another correction or request another ruling."* Nothing in this handoff authorizes resumption. Under the IRON LAW only the operator initiates OBPI work, and this pause is explicit on top of it.

OBPI-0.35.0-04-section-ownership-and-ratchet is `in_progress`, brief `status: Active`, lane Heavy, parent `ADR-0.35.0-canon-entry-corpus-landing`. **All work is UNCOMMITTED at HEAD `397301c6`** — zero commits this session, origin/main 0 ahead 0 behind. Read `git status --porcelain` rather than trusting any list.

This session began as a `/git-sync` request that could not proceed: the sweep guard (GHI #708) refuses `git add -A` over `src/**`, and the pre-commit `xenon --max-absolute C` gate rejected the staged tree because `_replay_pending_transition` was rank D (22). The operator then ruled on the owed Step-4b round-11 HIGH and directed a full correction, which became five dispatched implementation tasks with two-stage review after each of the first four.

Step 4b round 11 remains the STANDING VERDICT: **REFUTED / NOT-CORROBORATED**, receipt `arb-step-codexadversary-cc9aa913064b4550807e717c51982f4b`. **Round 12 was never dispatched.** The tree has changed substantially since round 11 observed it, so that verdict describes a tree that no longer exists.

## Important Context

**The lock is held by a PRIOR session's agent id.** `gz obpi lock claim` reports CONFLICT: `claude-code-00f58c14`, claimed 2026-09-05T05:34:27Z, TTL 1440m. This session deliberately did NOT churn it — commit `204e8c2c` shows a prior reclaim, and lock churn produced the residue incident recorded in the IRON LAW. Stage 5 will need ownership resolved; nothing else does.

**Both pipeline markers are present and untouched**, `current_stage: implement`, so `.claude/hooks/pipeline-gate.py` permits `src/**` writes. That hook is NOT the authority here — the IRON LAW is, and the operator's pause is on top of it.

**Five implementation tasks were dispatched, each to an `implementer` subagent, with `spec-reviewer` + `quality-reviewer` after tasks 1-4.** All dispatches are recorded via `gz obpi dispatch` (ledger `stage2_dispatch_recorded`). **Task 5 has had NO review** — that is the largest open gap in the evidence chain.

**Reviewers in this repo have no shell.** Both personas are Read/Glob/Grep only, so every complexity, test and exit-code claim they make is a static trace. All such claims this session were re-run independently in the primary session; a future session must do the same rather than inheriting a review's numbers.

**Two implementer judgment calls were disclosed rather than hidden, and both matter:**
- Task 4 RETARGETED a pre-existing fixture's fault selector (`test_a_post_swap_durability_failure_keeps_the_journal_and_says_so`, from directory-fsync call count to `_failing_directory_barrier_after_replace("Doc.md.json")`). The spec review independently traced that the retarget NARROWS rather than moves the window and that the original RED was the injection shifting, not a masked regression. Cleared.
- Task 5 introduced `BARRIER_UNSUPPORTED_ERRNOS = {EINVAL, ENOSYS, ENOTSUP, EOPNOTSUPP}`, on which an unavailable barrier WARNS AND EXITS 0 instead of preserving-and-refusing. **This is UNRESOLVED against the ruling's literal text** *"Failure to establish that boundary preserves the files and exits non-zero."* The implementer flagged it itself as a judgment converting a refusal into a success on a durability path, and said it is a one-line revert plus deleting `_warn_barrier_unavailable` and one test. It was escalated to the operator and the pause arrived before any ruling. **Do not resolve this without the operator.**

## Decisions Made

**Operator rulings this session (all verbatim in `.gzkit/handoffs/rulings.jsonl` and `.gzkit/insights/agent-insights.jsonl`):**

1. **"D beats E" is REJECTED.** *"Keep three obligations separate: the transition is durably witnessed; the source is reconciled; recovery cleanup is complete. Establishing one does not discharge the others."* The orthogonality observation the retired resolution was built on STANDS; only the resolution was wrong. Recorded in the plan's § CORRECTION beside the superseded first attempt, and in the brief's § Round 11.
2. **Four demonstrations gate the next adversarial round** — repeated retries, the executed recovery sequence, cleanup surviving failure and interruption, extraction-artifact containment. Written into the plan as PRECONDITIONS ON DISPATCH, not as things the adversary is asked to check.
3. **Escalation response — orphan residue vs current-transaction cleanup.** Current-transaction cleanup failure stays non-success; unrelated orphan residue may warn and permit fresh work, but ONLY after durable journal absence is established, and that durability boundary is MANDATORY on both entries including when the journal is absent on entry. This SUPERSEDED the implementation's argued no-barrier position, which both Task-2 reviewers had found addressed only a single removal's own durability while the invariant actually relied upon is cross-file ordering across two directories. Plan binding constraints 8 and 9.

**Agent scope decisions (mine, not the operator's):**

- The quality review's criterion-7 finding — the recovery machine is mis-housed, classification fused to prose rendering behind ~27 in-helper `sys.exit` calls in a 2,500-line module — was treated as OUT OF SCOPE under *"Preserve the existing scope and rulings"* and left unrecorded in the brief's Tracked Defects. **That recording was not completed before the pause.**
- The spec review's narrow TOCTOU (`journal_path.exists()` evaluated twice; a non-gzkit actor deleting the journal mid-transaction could let `_commit_transition` reuse `journal_source_path` unbarriered) was recorded, not fixed — it requires write access to `.gzkit/`, which the brief's Threat Model puts out of scope as a disclosed residual.
- 13 pre-existing `ty` diagnostics under `features/steps/` are outside the canonical `gz arb typecheck` scope; logged as a `defect` insight rather than fixed.

## Immediate Next Steps

**NOTHING BELOW IS AUTHORIZED.** Execution is paused by explicit operator instruction and OBPI work is operator-initiated only. These are the states the work was left in, not a queue to start.

1. **The barrier-unavailable disposition is owed a ruling** (see § Important Context). It is the only item where the implemented behavior and the operator's ruling text disagree. Nothing downstream should be treated as settled while it stands, because it changes an operator-visible exit code.
2. **Task 5 is unreviewed.** Its ten items include four majors and it touched three files, one of them `src/gzkit/content/ownership.py`. It also fixed SIX "Nothing written" sites where I named four — extending to `_load_declaration_or_exit`'s ValueError branch and `_refuse_surface_changed_under_us` — and TWO of those six carry no covering test. It also loosened-then-retightened an existing assertion, re-pinning `_assert_refused_without_transaction_writes` off the literal `"Nothing written."` onto `"no declaration byte changed and no witness was appended"`. That is the single assertion edit most worth an independent eye.
3. **`docs/user/manpages/content.md` is STALE against Task 5.** The primary session refreshed it after Tasks 1-4 (exit table, state table, three-obligations prose, recovery-artifacts table, and a real captured D+E console block), but Task 5 then changed six refusal messages AND added a new warning path that exits 0. The runbook-code covenant obligation for those output and exit-code changes is UNDISCHARGED.
4. **Stage 3 receipts were never emitted.** No `arb-ruff-*`, `arb-step-unittest-*`, `arb-step-mkdocs-*` or `arb-step-behave-*` for the final tree. Two `arb-step-typecheck-*` receipts exist from mid-run (`749a48e45b9641a98993a6efa3a30ef7`, `7f62a3cf5f524acd954d7d997bcdea76`) and describe earlier trees.
5. **The mutation sweep is NOT rebound to the final SHA** — operator ruling point 5, deliberately left last because every fix moves the SHA. The brief's § Evidence Gate 2 table still records the 18-guard sweep against source SHA `a4c2e3ad…`, which round 11 already caught as stale. `src/gzkit/commands/content/unown.py` has changed many times since.
6. **Step 4b round 12 was never dispatched.** The round-11 prompt base is preserved at the scratchpad path in § Evidence; its state list still says "D beats E" and must not be reused verbatim.

## Pending Work / Open Loops

- **Barrier-unavailable disposition** — implemented as warn-and-exit-0; unresolved against the ruling's literal "exits non-zero". Escalated; no ruling received.
- **Task 5 two-stage review** — not dispatched.
- **Manpage** — stale against Task 5's six changed refusal messages and the new exit-0 warning path.
- **Mutation sweep** — still bound to superseded SHA `a4c2e3ad…`; must be re-executed against the final source and its guard count recorded honestly (a 22-guard sweep was run in a PRIOR session and reported in a subagent message but never written into the brief; do not transcribe it — re-run it).
- **Brief § Round 11 dispositions** — findings 1, 2 and 3 are still marked OPEN. The work addressing them landed but the dispositions were never updated, and no round has been run to confirm.
- **Brief Tracked Defects** — the criterion-7 housing finding and the TOCTOU were both decided to be recorded there; NEITHER was written.
- **Two untested branches** — `_load_declaration_or_exit`'s OSError and ValueError entry-sweep caveat sites (need a chmod/corrupt-file fixture the implementer judged out of proportion).
- **Barrier classification has ZERO Windows witness** — three of Task 5's five new tests are POSIX-only by the file's established convention, so `BARRIER_UNSUPPORTED_ERRNOS` behavior is unwitnessed off POSIX. Same structural gap the six pre-existing barrier tests already carry.
- **Housing finding (out of scope, unrecorded)** — recovery machine fused to prose rendering; quality review recommended extracting a pure classifier returning a frozen `RecoveryDecision`.
- **`features/steps/` typecheck gap** — 13 diagnostics outside the canonical gate; insight logged 2026-09-05T12:08:09Z.
- **Original `/git-sync` request is UNSATISFIED.** Nothing has been committed or pushed. The sweep guard still blocks `git add -A` while `src/**` is dirty, so the governed route remains: commit the governed work under its own `fix(<scope>): …` message with a `Task:` trailer, then `gz git-sync --apply`.

## Verification Checklist

Last observed on the preserved tree, all run in the primary session with real exit statuses (never a piped filter's — the `verifier-pipe-gate` hook blocks that and fired twice this session):

| Command | Result |
|---|---|
| `uv run ruff check .` | EXIT 0 — "All checks passed!" |
| `uv run -m unittest tests.commands.test_content_unown -q` | EXIT 0 — Ran 105, OK |
| `uv run -m unittest discover -s tests/content -t . -q` | EXIT 0 — Ran 354, OK |
| `uv run xenon --max-absolute C --max-modules C --max-average C src/` | EXIT 0 |
| `uv run gz arb typecheck` | EXIT 0 — receipt `arb-step-typecheck-7f62a3cf5f524acd954d7d997bcdea76` |
| `uv run mkdocs build --strict` | EXIT 0 (before Task 5) |
| `uv run gz validate --cli-alignment` | EXIT 0 (before Task 5) |

Scoped suite grew 82 → 105 across the five tasks. `_replay_pending_transition` went D (22) → B (8); file max is `_refuse_incoherent_landed_state` at C (12), inside the `--max-absolute C` ceiling but ABOVE the canonical `radon_cc` block band of 11.0 in `.gzkit/rules/complexity-thresholds.json` — a disclosed, operator-routed authority conflict, not this work's doing.

**Re-run everything before trusting any of it.** `mkdocs --strict` and `cli-alignment` predate Task 5's doc-affecting changes.

## Evidence / Artifacts

**Governed records written this session:** `handoff_resume_decided` (ledger, 2026-09-05T11:02:29Z, the operator's full ruling verbatim in `operator_text`); four `gz insights remember` records — 11:02:34Z improvement (D+E), 11:25:04Z improvement (four demonstrations), 11:59:18Z improvement (orphan/durability ruling), 12:08:09Z defect (behave-step typecheck gap); `stage2_dispatch_recorded` events for Implementer x5 and SpecReviewer/QualityReviewer x4 pairs.

**Artifacts:**
- Plan: `.claude/plans/section-ownership-and-ratchet-OBPI-0.35.0-04.md` — its CORRECTION section carries the superseded "D beats E" beside the ruling that replaced it; binding constraints 5 through 9; the Demonstration obligations section carries the four preconditions on dispatching Step 4b.
- Brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md` — the Round 11 section carries the operator ruling verbatim.
- Plan-audit receipt: `.claude/plans/.plan-audit-receipt-OBPI-0.35.0-04-section-ownership-and-ratchet.json`, verdict PASS.
- Round-11 adversary receipt id `arb-step-codexadversary-cc9aa913064b4550807e717c51982f4b`, exit_status 0, 925s.
- Typecheck receipt ids `arb-step-typecheck-749a48e45b9641a98993a6efa3a30ef7` and `arb-step-typecheck-7f62a3cf5f524acd954d7d997bcdea76`, both describing earlier trees.

**Session-scratchpad material that will NOT survive** (regenerate rather than hunt): the round-11 adversary prompt base, and a small capture harness that reproduces the real state D+E console block for the manpage by reusing the test module's own fixture helpers. The prompt base must NOT be reused verbatim — its recovery-state list still asserts the retired "D beats E". The capture harness patches the commit-transition helper and needs its double widened whenever that signature changes; it broke once this session for exactly that reason, which is how the manpage block was caught predating Tasks 3 and 4.

**Verified by observation, not assumed:** the ignore rules now cover the final extract and the atomic writer's staging twin at EVERY depth. The earlier root-anchored form missed the rules surface under `.gzkit/rules/`, which is a live content surface — its corpus store exists under `.gzkit/corpus/`. Confirmed with `git check-ignore -v` against four real files, all exit 0.

**Sharpest single finding of the session:** Task 3 item 8's RED showed the unescaped glob in the staging-residue sweep did not merely MISS its own residue — for a surface whose name contains a bracket metacharacter it MATCHED A DIFFERENT SURFACE'S, so the sweep would have deleted a stranger's copy of measured source bytes while keeping its own. The review that predicted it had rated the issue inert for today's names. Now escaped and pinned by a test.

## Settled Rulings

724 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
