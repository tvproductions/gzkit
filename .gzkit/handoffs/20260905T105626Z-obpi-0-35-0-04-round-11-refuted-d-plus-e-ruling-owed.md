---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-05T10:56:26Z'
agent: claude-code
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: d4d2277b-017d-4d46-8b07-588a19ff4d2e
continues_from: .gzkit/handoffs/20260905T054210Z-obpi-0-35-0-04-run-round-9-against-current-tree.md
---

## Current State Summary

OBPI-0.35.0-04-section-ownership-and-ratchet is `in_progress`, brief `status: Active`, lane Heavy, parent `ADR-0.35.0-canon-entry-corpus-landing`. **Work is UNCOMMITTED on a dirty tree at HEAD `397301c6`** (origin/main 0 ahead, 0 behind). Ten files modified plus two untracked pipeline markers — read `git status --porcelain` rather than trusting this list.

This session ran Step 4b rounds 9, 10 and 11 and landed two operator-ruled corrections. **Round 11 is the STANDING VERDICT: REFUTED / NOT-CORROBORATED**, receipt `arb-step-codexadversary-cc9aa913064b4550807e717c51982f4b`, `exit_status: 0`, 925s, `stdout_truncated: False`, no failure markers. One high and two medium in-scope findings, no critical.

Rounds 9 and 10's findings are ALL DISCHARGED. Round 9's identity root was closed by the operator-ruled fixed-target correction and CORROBORATED by round 10's positive demonstrations. Round 10's two high recovery findings were closed by the operator-ruled recovery protocol.

**The round-11 high is a consequence of a correction this session made.** After round 10, a quality reviewer found that state E shadowed state D; the plan was corrected to "D beats E" on the reasoning that a witnessed transition is complete and the source no longer matters. The second half was wrong. Round 11's weakest point, verbatim: *"the protocol still treats completion of the declaration/ledger transition as completion of all recovery obligations. D does not establish source reconciliation, and attempted unlink does not establish cleanup."*

`uv run gz obpi precomplete` will report BLOCKED on `adversarial_validation` — correctly, on a genuinely refuted round. `gz obpi complete` refuses a refuted verdict outright (GHI #960), so there is no completing around it.

Lock is HELD by session `claude-code-00f58c14` (claimed 2026-09-05T05:34:27Z, TTL 1440m) — that is a PRIOR session's id, not this one. Read the lock file directly; `gz obpi lock list` REAPS expired locks as a side effect and must not be used as a status query.

## Important Context

**THE OPERATOR RULED THE SCOPE TWICE AND BOTH RULINGS BIND.** No split, no successor OBPI, no scope renegotiation; the existing ledger exception (GHI #952/#953) stands as a disclosed precondition of the claim. Do not re-open either. Operator verbatim: *"Do not use successive adversary rounds as the process for discovering the recovery design."*

**THE ACCEPTANCE BOUNDARY APPLIES TO REVIEW FINDINGS, NOT JUST ADVERSARY FINDINGS.** The brief's § Threat Model places an actor with `.gzkit/` write access outside the boundary. This session escalated a review finding whose reproduction hand-edited `.gzkit/` and minted ledger evidence, and the operator corrected it: retain such fixtures as DEFENCE IN DEPTH, never present them as in-scope blockers. Every reviewer and adversary prompt must demand the required access be stated per finding.

**THE FIVE RECOVERY STATES ARE NOT A PARTITION.** A-D are mutually exclusive positions in the commit sequence; E (source changed) is an ORTHOGONAL axis. The plan says so at `.claude/plans/section-ownership-and-ratchet-OBPI-0.35.0-04.md` § Recovery Protocol. B and C are INDISTINGUISHABLE from disk by design — no prose may claim to tell them apart.

**MUTATION SWEEPS IN THIS REPO CAN LIE (GHI #963, filed this session, OPEN).** Two mutations deleting byte-identical-length text within the same second collide on CPython's `(mtime-seconds, size)` pyc invalidation, so one subprocess imports the other's bytecode. It manufactures false FAILs as readily as false PASSes. Bind a fresh `PYTHONPYCACHEPREFIX` per mutation subprocess. GHI #963 is open pending an operator ruling on remedy shape (doctrine in `.gzkit/rules/tests.md` vs a shared sweep runner).

**SUBAGENT TURN LIMITS ARE A REAL CONSTRAINT HERE.** Implementers stall at 25 turns, reviewers at 15. Six stalls this session, two of them before any work began — reading the plan, the brief and a 1,300-line module consumes the budget. Mitigations that worked: inline the essential facts INTO the dispatch message rather than by reference, order review checks by priority and instruct the reviewer to emit a verdict naming what it did not reach, and tell implementers to bank each RGR cycle green before starting the next.

**A PRESENCE CHECK READS GREEN ON THE `.gitignore` CLASS.** `**/*.journal` looks like it covers `.journal.source` and does not. The artifact test shells out to real `git check-ignore` over paths derived from `_target_for` — keep that shape; a string-presence assertion would have passed.

## Decisions Made

- [operator-ruled] Proceed on the resumed handoff and run Step 4b round 9 against the current tree (verbatim: "Proceed — run round 9"), booked via `gz handoff decide`.
- [operator-ruled] Adopt the fixed-target correction inside OBPI-0.35.0-04 — one canonical transaction target carrying identity plus fixed surface, declaration and journal paths; scope and the ledger exception remain binding; no split, successor OBPI, or scope renegotiation.
- [operator-ruled] Address recovery as ONE COMPLETE PROTOCOL, enumerating the interruption states with evidence, retry action, retained recovery data and truthful operator instructions for each — rather than repairing one adversary finding at a time.
- [operator-ruled] Prefer preserving the measured source bytes as immutable recovery material. The agent's objection that a snapshot creates "a second copy of canon" was ruled UNSOUND: historical recovery data does not become another authority merely because it contains copied bytes, and the journal already copies the successor declaration. A snapshot without a usable recovery route is incomplete.
- [operator-ruled] The identity-swap fixtures hand-edit `.gzkit/` and mint ledger evidence; retain them as defence-in-depth tests but never present them as proof of an in-scope blocker. Their corrected expectation is deterministic refusal without transaction writes after the injected mismatch, with a separate positive test proving legitimate aliases succeed.
- [operator-ruled] Verify behavior, not narrative: execute and retain mutation witnesses; reasoning about deleting a guard is not an executed check.
- [operator-ruled] Launch the pipeline rather than asking again (verbatim: "launch it, what are we doing here? why are you going 'lame' like this?") — a design-route ruling initiates its own mechanical prerequisites.
- [agent-chose] Corrected the plan to say state E is ORTHOGONAL to A-D and that D beats E, after a quality reviewer found E shadowed D. **Round 11 shows the correction overreached** — D establishes that the transition was witnessed, not that source reconciliation is finished. The next ruling should settle whether D+E becomes its own reported state or D hands off the snapshot and refuses to complete while E stands.
- [agent-chose] Did not run a third two-stage review after the recovery-protocol fix cycle, on the operator's instruction not to start an indefinite patch loop; went to Stage 3 receipts and round 11 instead. Both review majors were closed and independently verified.
- [agent-chose] Dispatched a FRESH implementer for the recovery protocol rather than resuming the one at 414k tokens that had stalled twice.
- [agent-chose] Filed GHI #963 for the mutation-sweep bytecode contamination and left it OPEN with a blocker comment naming the operator decision, rather than picking a remedy shape unilaterally.

## Immediate Next Steps

1. **OBTAIN THE OPERATOR'S RULING ON THE ROUND-11 HIGH BEFORE ANY CODE CHANGE.** The question is settled in shape, not in content: when a transition is in state D (witness present) AND state E (source changed), does D+E become its own reported state, or does D hand off the reconciliation snapshot and refuse to complete while E stands? The adversary's recommendation is to keep D's idempotent witness handling but preserve or explicitly hand off the snapshot when E remains, report the unresolved source condition, and give a recovery sequence that actually passes the loader. Do NOT dispatch an implementer before this is ruled — the previous correction went wrong precisely by settling a lifecycle distinction without one.
2. **Refresh the brief's § Evidence Gate 2 mutation table.** It records source SHA `a4c2e3ad…`; `src/gzkit/commands/content/unown.py` is now `49b2ad58…`. A 22-guard sweep was executed during the last fix cycle and reported in a subagent message but never written into the brief, so the recorded 18-guard sweep does not establish mutation coverage of the current recovery protocol. Round 11 caught this. Refresh it before the next acceptance round is dispatched.
3. **Fix the two round-11 mediums, which are unambiguous.** (a) `_clear_recovery_state` at `unown.py:1370-1376` suppresses every `OSError` over all three unlinks, so journal deletion can fail while its snapshot is deleted; suppress only expected absence, report other cleanup failures as state-D cleanup pending, retain remaining material when journal removal fails. (b) `.gitignore` covers `<surface>.unowning-recovery` but not the atomic writer's staging file `.<surface>.unowning-recovery.<n>.tmp`; verified independently — `git check-ignore` returns exit 0 for the former and exit 1 for the latter.
4. **Then re-run Stage 3 receipts and dispatch round 12** through `codex-companion.mjs adversarial-review --wait --scope branch --base 5108d7cf`, ARB-wrapped as `uv run gz arb step --name codexadversary`. Reuse the round-11 prompt at `scratchpad/round11-prompt.txt` as the base; keep the claim EXACTLY as rounds 9-11 stated it and do not strengthen it.
5. **Read the receipt, not the summary line.** Confirm `exit_status: 0` in the emitted `arb-step-codexadversary-*` receipt AND grep both streams for `Turn failed`, `Codex error`, `flagged for possible` and content-filter markers before believing any verdict. A prior receipt printed "No material findings" while dying on a content filter with a real finding above the cut.

## Pending Work / Open Loops

- **OBPI-0.35.0-04 is BLOCKED on `adversarial_validation`** and nothing else. `gz obpi complete` refuses a refuted verdict outright (GHI #960 [settled]); the only exits are to fix and re-run, or to bound a finding out of scope and re-run.
- **Round-11 findings, all OPEN:** one high (D+E loses the reconciliation material — awaiting operator ruling) and two mediums (silently consumed cleanup failures; extraction staging files outside the ignore rules).
- **Round-9 mediums 3 and 4 remain UNDISCHARGED and were disclosed to rounds 10 and 11 as known.** (a) Three schema-rejection fixtures in `tests/content/test_ownership.py` omit a required `floor_event_id`, so each fails on `required` before reaching the constraint it names. (b) `test_replay_refuses_to_complete_into_a_state_the_loader_would_reject` asserts only a non-zero exit and a retained journal, so the digest guard can satisfy it in place of the landed-span check it names.
- **GHI #963 is OPEN** with a blocker comment: the mutation-sweep pyc contamination. Awaiting an operator ruling on remedy shape — doctrine in `.gzkit/rules/tests.md` versus a shared sweep runner with the isolation built in.
- **GHI #952 and #953 remain OPEN** as the disclosed ledger-atomicity precondition of the bounded claim. `_ledger_witness_present`'s `ValueError` arm escaping `_append_event_once` as a raw traceback is part of that residual, not a new defect.
- **GHI #941 remains OPEN** — reviewers cannot execute, so unrunnable asks degrade the verdict. Mitigated this session by ordering review checks by priority.
- **`docs/user/manpages/content.md`** still carries older AGENTS.md figures in the corpus-attestation block (`8637 → 10977`); re-verifying them would mutate real project ownership state, which a quality reviewer assessed as correct restraint rather than a defect.
- **The lock is held under a PRIOR session's id** (`claude-code-00f58c14`, TTL 1440m from 2026-09-05T05:34:27Z). If the TTL lapses, a reap will re-create the `orphaned_implementation` finding.
- **The tree is dirty and unpushed.** Ten modified files plus two untracked pipeline markers. Nothing is committed from this session's work.

## Verification Checklist

Every claim in this document is narrative and unverified until checked. Run these before acting.

    uv run gz obpi precomplete OBPI-0.35.0-04-section-ownership-and-ratchet
    cat .gzkit/locks/obpi/OBPI-0.35.0-04-section-ownership-and-ratchet.lock.json
    uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
    git status --porcelain
    git rev-list --left-right --count origin/main...HEAD
    git rev-parse --short HEAD
    shasum -a 256 src/gzkit/commands/content/unown.py
    git check-ignore -v .AGENTS.md.unowning-recovery.abc123.tmp
    gh issue view 963 --json state,title
    gh issue view 952 --json state,title
    gh issue view 953 --json state,title

Expected: precomplete BLOCKED with `adversarial_validation` the only failure; lock held by `claude-code-00f58c14`; a dirty tree with ten modified files and two untracked pipeline markers; zero ahead and zero behind; HEAD `397301c6`; `unown.py` at `49b2ad58…` which DIFFERS from the `a4c2e3ad…` recorded in the brief's Gate 2 table; `git check-ignore` on the staging file exits 1 (NOT ignored — this is round-11 medium 3); #963, #952 and #953 all OPEN.

DO NOT run `uv run gz obpi lock list` as a status query — it REAPS expired locks as a side effect. Read the lock file directly.

To re-derive the standing verdict rather than trusting this document, read the brief's `### Step 4b` section and its `#### Round 11` subsection; `gz obpi precomplete` reads that section and cannot infer supersession from prose.

## Evidence / Artifacts

Nothing from this session is committed. HEAD is `397301c6`; all work below is uncommitted on a dirty tree.

Surfaces changed this session:

- `src/gzkit/commands/content/unown.py` — fixed-target correction and the five-state recovery protocol
- `src/gzkit/content/ownership.py` — `write_bytes_atomically` extraction; `write_declaration_atomically` delegates to it
- `tests/commands/test_content_unown.py` — 79 scoped tests including the TestRecoveryProtocolState A, B, D and E classes, TestWitnessSourceIsTheFixedDestination, TestRecoveryArtifactsAreIgnored, and TestMovedSurfaceRefusalNamesItsStateAndPaths
- `docs/user/manpages/content.md` — state table, two new exit-2 rows, recovery-artifacts table, state-E console capture
- `.gitignore` — journal-source and unowning-recovery ignore rules added (the staging-file rule is still MISSING; round-11 medium 3)
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md` — rounds 9, 10 and 11 recorded; § Evidence Gate 2 mutation table is STALE against the current source SHA
- `.claude/plans/section-ownership-and-ratchet-OBPI-0.35.0-04.md` — § Recovery Protocol, the five-state table, and the orthogonality correction
- `.gzkit/insights/agent-insights.jsonl` — three `improvement` records from operator course-corrections

Step 4b receipts, all `exit_status: 0` with `stdout_truncated: False` and no failure markers:

- Round 9 — `arb-step-codexadversary-dd8d6bbcb51c4f4a8d1042687a90964b` (REFUTED; 1 high, 3 medium)
- Round 10 — `arb-step-codexadversary-658c8ce606114de39730cd01a66e5f3d` (REFUTED; 2 high — the fixed-target correction CORROBORATED)
- Round 11 — `arb-step-codexadversary-cc9aa913064b4550807e717c51982f4b` (REFUTED; 1 high, 2 medium — THE STANDING VERDICT)

Stage 3 receipts against the final tree, all `exit_status: 0`:

- `arb-step-unittest-4887815abb9444289613559dde35236c` — 9371 tests
- `arb-ruff-e616d948dfa94883a68e558eb0cdda03`
- `arb-step-typecheck-5a9c0ed0e5b842bcb7b04e6123871520`
- `arb-step-mkdocs-650468572d174fd4921f23883e1f8fe1`

Scratch artifacts (session-local, not repo-bound): the round-9, round-10 and round-11 prompts and dispatch logs under the session scratchpad directory.

## Settled Rulings

717 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
