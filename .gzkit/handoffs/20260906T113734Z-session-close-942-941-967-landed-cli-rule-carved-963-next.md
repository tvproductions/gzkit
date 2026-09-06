---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T11:37:34Z'
agent: claude-code-2a5779f2
session_id: 2a5779f2-39e4-4c24-9d36-646ae24fb112
continues_from: .gzkit/handoffs/20260906T105828Z-session-close-942-landed-adr-status-reviewed-941-next.md
---

## Current State Summary

SESSION-CLOSE. FINAL STATE: HEAD 126c5d09, tree clean, nothing unpushed, uv run gz check exit 0, gz preflight clean, gz skill audit Blocking 0, no active locks. SEVEN COMMITS this session: 718b8f33 (#942 fix), aa90ce6b (gz-adr-status review), 114b772f (handoff), 3d30f916 (#942 concealment hardening), 1740442b (cli.md 0.6.0 carve-out), 77546da9 (#967 both arms), 126c5d09 (#941 arms 1-2). THREE GHIs CLOSED: #942, #967, #941. Campaign: 6 of 24 closed across four sessions (#962, #965, #964, #942, #941, plus #967 which is not a campaign member). Remaining campaign order: 963, 888, 940, 849, 946, 877, 611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766. NEXT WORK ITEM: GHI #963, "mutation sweeps: byte-identical mutations collide in the pyc cache, so a sweep can report a false PASS". Open GHI queue measured 30; re-derive before citing.

## Important Context

=== #963 IS NEXT AND THIS SESSION IS EVIDENCE FOR IT ===

I ran mutation sweeps on every fix this session (that is now the working method — see
Decisions). #963 says byte-identical mutations collide in the pyc cache and a sweep can
report a false PASS. Reason about the DIRECTION before trusting or distrusting my sweeps:

- A mutant reported CAUGHT means the suite FAILED, which requires the mutation to have
  taken effect. Catches are trustworthy.
- A mutant reported SURVIVING is the falsifiable one: if the mutation never took effect,
  the suite passes and you wrongly conclude "no test covers this".
- This session had 3 survivors. Two (#967: filename ownership, archive verification) were
  investigated and turned out to be REAL coverage gaps; tests were added. One (#941: a
  Field description string) is genuinely non-behavioral.

So a false-survivor bug makes an agent ADD tests it did not need, never skip ones it did.
That is the safe direction, and it bounds the severity — worth stating in #963. My sweeps
used `cp` restore plus rewrite, so mtimes changed on every mutation; whether that is
sufficient is exactly what #963 is about. DO NOT assume my sweeps were unaffected. Measure.

=== THE STAGE-4 PACKET SURFACE CHANGED TWICE ===

Step 4a-v exists (`uv run gz obpi verify-packet <path>`), and it HARDENED mid-session:

  A non-zero exit is now a BLOCKER outright.

The first version deliberately allowed it ("a packet may legitimately show a RED run").
The operator asked whether selective omission could conceal a failure while presenting
success. IT COULD, confirmed by running the shipped code: a command exiting 1 whose packet
quoted only its success lines reported VERIFIED with missing_lines empty. Every quoted line
was genuine; the omission was the lie, and no per-line check can see it.

Escape for an honest RED run: `$ <cmd>; echo "exit $?"` — exits 0, status reproduces.

Adjacent vector, partially closed: a piped verifier reports the FILTER's status. Handled by
reusing masked_verifier() from gzkit.verifier_pipe_gate, the Bash hook's own predicate.
ITS SCOPE IS VERIFIERS ONLY and was NOT widened — a generic non-verifier command piped
without pipefail still masks its status and is NOT blocked. Disclosed in the module
docstring and the skill. Closing it is a scope decision (may this surface be stricter than
canon?), not a bug fix.

=== THE CLI RULE NO LONGER CONTRADICTS OPERATOR CANON ===

.gzkit/rules/cli.md 0.5.1 to 0.6.0. § Adding CLI Features said contract-bearing CLI work
"runs gz obpi pipeline, not a freeform direct fix" with no carve-out. Under the IRON LAW an
agent could proceed by NEITHER route. It now says "planned", with the GHI direct-repair
exception quoted verbatim. Lane is unchanged: a new verb is still Heavy and still owes the
seven obligations.

EDITED AT .gzkit/rules/, never .claude/rules/ — the mirror is generated. The version bump
made the advisory scorecard fail closed (cli.md scored at 0.5.1 against a rule at 0.6.0),
which is the coupling working. Scored as row 88 (Judgment); Summary roll-up corrected
61 to 62, denominator 158 to 159.

=== A FABRICATION I COMMITTED AND CAUGHT ===

I cited commit 1c1e5f2b in #941's close comment. NO SUCH COMMIT EXISTS. The real SHA is
126c5d09. I typed it from memory instead of reading it back — the exact failure class #942
is about. Corrected by a follow-up comment on the issue rather than a silent edit, and
recorded via gz insights remember (type defect, scope ghi-close).

THE RULE THAT FOLLOWS: resolve every SHA with `git log -1 --format='%H %s' <sha>` before it
enters a close comment, the same way ARB receipt ids are confirmed on disk. I verified all
seven of this session's cited SHAs afterwards; only that one was wrong.

=== THE CANON TRAP ===

The harness supplied a 'Claude-Session:' commit trailer again. .claude/rules/task-discovery.md
closes the trailer set (operator verbatim 'never'). NO commit this session carries it —
grepped after each. IT WILL BE SUPPLIED AGAIN.

## Decisions Made

- [operator-ruled] 2026-09-06, verbatim: 'Proceed with #941.' Done, arms 1 and 2.

- [operator-ruled] 2026-09-06, verbatim: '`gz preflight --apply` may automatically archive an orphaned FAIL receipt, provided it preserves the complete contents and provenance, verifies the archive before removing the operational copy, and leaves the finding and FAIL verdict unresolved. If preservation fails, retain the original and fail closed. Moving evidence is not resolving its finding; no new retirement verb is needed. Fix the matcher disagreement too, without treating incidental OBPI mentions as plan ownership.' Implemented exactly; the four constraints ARE the implementation.

- [operator-ruled] 2026-09-06, verbatim: 'Correct the CLI rule's canonical source to state the GHI direct-repair exception, then regenerate and validate its mirrors. Don't edit .claude/rules/cli.md directly. Canon already settles that contradiction.' Done at .gzkit/rules/cli.md; mirrors regenerated and validated.

- [operator-ruled] 2026-09-06, verbatim: 'For #942, retain the narrower claim: replay verifies displayed output against command output; it does not prove the packet is complete or its interpretation correct. Confirm that selective omission cannot conceal a command failure while presenting success.' Confirmed it COULD; fixed; the narrower claim is now written into the module docstring and the skill's Step 4a-v.

- [agent-chose] Ownership by DECLARATION (filename, H1, or an OBPI label; the declaration block ends at the first H2) rather than a first-N-lines window. Both would have excluded the reproduction, but the window only because that mention sits at line 19 — correctness by accident of placement. Measured across 306 plans: 304 declare in H1, 217 in filename, ZERO in filename but not H1.

- [agent-chose] KEPT filename ownership though it is redundant against today's corpus and a mutant proved it unwitnessed. The filename is the tool-generated declaration; the H1 is authored prose. Dropping it would make ownership depend solely on a heading an agent typed. Pinned with a test instead of deleted.

- [agent-chose] Reviewer capability is READ from .claude/agents/*.md, never asserted in prose. A hardcoded 'read-only' would contradict the file the moment the grant changed, which is exactly remedy 3. Reading it makes the operator's ruling a one-line change either way.

- [agent-chose] reviewer_capability fails safe toward the RESTRICTIVE claim: an unreadable definition reports no execution. Promising a capability the reviewer may not have is the direction that produces the unrunnable ask.

- [agent-chose] Did NOT widen masked_verifier's scope for the packet surface. A stricter local rule on the same subject is how two surfaces fall out of agreement. Residual disclosed rather than closed quietly.

- [agent-chose] REPLACED a shipped test rather than adding around it: test_a_failing_command_is_not_a_blocker_when_its_output_reproduces asserted the behavior 3d30f916 removes. Leaving it and adding a sibling would have left the suite asserting both.

- [agent-chose] UPDATED four pre-existing plan-discovery fixtures rather than relaxing the new rule. Each is a one-line synthetic plan with no heading, a shape no live plan has; none of the four is about ownership. Stated plainly in the commit because rewriting a test to pass is the failure that note exists to rule out.

- [agent-corrected] #941's body states 'handle_review_cycle routes on the verdict, so CONCERNS vs PASS is a gate signal'. It routes on review_blocks_advancement, which is FAIL, or CONCERNS WITH A CRITICAL FINDING. The observed instance's findings were all info, so it did NOT block. Corrected in the close; the fix is still needed because nothing stopped a reviewer rating its own gap critical.

- [agent-chose] Did NOT take #941 remedy 3 (grant reviewers Bash). The personas declare themselves 'Read-only independent review'; granting execution is a doctrine change AND weakens the independence that grant buys. Surfaced on the issue as an operator ruling.

- [agent-erred, self-caught] Fabricated SHA 1c1e5f2b in #941's close. Corrected by follow-up comment; insight recorded. See Important Context.

- [agent-chose] Ran a MUTATION SWEEP after every GREEN this session. It caught two hollow tests of my own in #967 that a passing suite had hidden. This is now the working method, not a flourish — but read the #963 note before trusting a SURVIVING result.

## Immediate Next Steps

1. Re-establish repository truth BEFORE staging anything:
     git status --short
     git log --oneline -1        # expect 126c5d09 or later
     uv run gz obpi lock list    # expect: No active locks

2. Confirm the gate:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   Expect exit 0.

3. WORK GHI #963. FIRST COMMAND:
     gh issue view 963 --json number,title,body,state,labels,comments,url
   "mutation sweeps: byte-identical mutations collide in the pyc cache, so a sweep can
   report a false PASS". READ THE #963 NOTE IN IMPORTANT CONTEXT FIRST: this session
   produced fresh evidence about which direction the false PASS runs, and that bounds the
   severity. Re-derive every precondition against the tree; two issue bodies this session
   carried stale or imprecise premises (#942 [settled]'s scope hint, #941 [settled]'s gate claim).

4. TDD, then MUTATE. Write the failing test, watch it fail for the right reason, and after
   GREEN break each production behavior in turn and confirm a test catches it. That sweep
   caught two hollow tests of mine this session that the passing suite had hidden.

5. Capture exits explicitly. A PreToolUse hook BLOCKS piping a verifier into a filter; use
   `set -o pipefail` or redirect to a file:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"

6. BEFORE any SHA enters a close comment, resolve it:
     git log -1 --format='%H %s' <sha>
   I fabricated one this session. Confirm ARB receipt ids on disk the same way.

7. Close ONLY #963. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

- GHI #963 (OPEN, campaign member) -- NEXT WORK ITEM. Nothing blocks it.

- #941 [settled] REMEDY 3 IS OPEN AND IS AN OPERATOR RULING, carried on that issue's close comment:
  should reviewers be granted Bash? AGENTS.md § Operator Doctrine assigns the two-stage
  review the duty of catching hollow tests, and the sharpest detection is perturbing
  production code to see whether the test still passes, which no read-only persona can do.
  Granting Bash contradicts both personas' own 'Read-only independent review' description
  AND weakens the independence that grant buys. The disclosure now tracks the file, so the
  ruling is a one-line change either way. Worth a fresh GHI if the operator wants it
  tracked separately rather than carried on a closed issue.

- PACKET REPLAY RESIDUAL (disclosed, untracked): a generic non-verifier command piped
  without pipefail still masks its exit status in a Step-4a transcript and is NOT blocked.
  masked_verifier's scope is recognized verifiers and was deliberately not widened. Closing
  it is a scope decision (may this surface be stricter than canon?), not a bug fix.

- AN ERROR MESSAGE THAT CONTRADICTS ITS OWN COMMAND (untracked, small, carried forward):
  'gz adr promote --kind foundation' fails with guidance to re-run using --kind feature or
  --kind pool, but --kind pool is rejected by that same command.

- SKILL STALENESS: gz-deps-upgrade blocks 2026-09-20; the only non-blocking warning.

- GHI #966, #933, #815, #930, #611, #894, #939, #922, #921, #952, #953, #940, #919 (OPEN):
  unchanged. #966 is documented inside gz-adr-status as a known-stale arm of that command.

- ADR-0.35.0 closeout BLOCKED on 8 OBPIs missing ledger proof: 05, 06, 07, 08, 10, 11, 12,
  13. Measured at this handoff: 5/13, lifecycle Pending, closeout pre_closeout, BLOCKED,
  QC PENDING. Unchanged; every commit this session was GHI/rule/skill work touching no
  OBPI. IRON LAW: ONLY THE OPERATOR INITIATES OBPI WORK.

NO OPERATOR ATTESTATION REQUIRED for #942 [settled], #967 [settled] or #941 [settled] -- all GHIs, and a GHI is its own
work order and receipt. The cli.md and skill commits are rule/docs work, not OBPI/ADR
completion.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- git status --short                          -> clean
- git log --oneline -1                        -> 126c5d09 or later
- git log --oneline origin/main..HEAD         -> empty
- git merge-base --is-ancestor 3d30f916 HEAD  -> exit 0 (#942 concealment hardening)
- git merge-base --is-ancestor 1740442b HEAD  -> exit 0 (cli.md 0.6.0)
- git merge-base --is-ancestor 77546da9 HEAD  -> exit 0 (#967 both arms)
- git merge-base --is-ancestor 126c5d09 HEAD  -> exit 0 (#941 arms 1-2)
- gh issue view 942/967/941 --json state      -> all CLOSED/COMPLETED
- gh issue view 963 --json state              -> OPEN (the work item)

THE GATE:
- uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"   -> exit 0
- uv run gz preflight                                     -> Preflight scan: clean
- uv run gz skill audit                                   -> Blocking: 0, Non-blocking: 1
- uv run gz cli audit                                     -> exit 0, 142/142

#942's CONCEALMENT GUARD IS LIVE (behavior, temp files only):

  uv run python -c '
import sys, tempfile; sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from gzkit.governance.stage4_packet import verify_packet
td = Path(tempfile.mkdtemp()); p = td/"c.md"
p.write_text("```\n$ python3 -c \"import sys; print(chr(111)*2); sys.exit(1)\"\noo\n```\n", encoding="utf-8")
r = verify_packet(Path("."), p)
print("verified:", r.verified, "| missing:", r.transcripts[0].missing_lines)
print(r.blockers[0][:60] if r.blockers else "NO BLOCKER")
'

  -> verified: False | missing: []
  -> Command exited 1 (expected 0)

  An empty missing-list with verified False is the whole point: every pasted line was
  genuine and the packet still fails. If this reports verified True, the guard regressed.

#967's OWNERSHIP RULE IS LIVE:

  uv run python -c '
import sys, tempfile; sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from gzkit.pipeline_markers import plan_declares_obpi
td = Path(tempfile.mkdtemp()); f = td/"x-OBPI-0.1.0-04.md"
f.write_text("# Plan - OBPI-0.1.0-04\n\nDoes NOT ship OBPI-0.1.0-05.\n", encoding="utf-8")
print("owns 04:", plan_declares_obpi(f, "OBPI-0.1.0-04"))
print("owns 05:", plan_declares_obpi(f, "OBPI-0.1.0-05"))
'

  -> owns 04: True / owns 05: False
  If 05 reports True, the any-mention rule regressed and receipts will self-orphan again.

#967's ARCHIVE PRESERVED TWO REAL RECEIPTS (re-checkable):
- shasum -a 256 .claude/plans/archive/.plan-audit-receipt-OBPI-0.25.0-27.json
    -> dff2d72155f61d5ff5d3bde2492b284639f91ccd9d7d99fc37a80b7e6d83a4a0
- its .provenance.json sidecar must read "finding_resolved": false

#941's DISCLOSURE IS LIVE:
- uv run python -c 'from pathlib import Path; from gzkit.pipeline_dispatch import reviewer_capability; c=reviewer_capability(Path("."),"spec-reviewer"); print(c.tools, c.can_execute)'
    -> ['Read', 'Glob', 'Grep'] False
  If can_execute reports True the operator granted Bash (remedy 3): the composed prompt
  follows automatically, and the skill's read-only persona rows need updating.

CODEX DELIVERY (still green):
- uv run gz validate --instructions-files-budget
    -> NOTE [codex-delivery-witness] AGENTS.md: 46876 B of 46876 B delivered.

- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read live counts from the
  command. Its tracked-defect annotations are KNOWN STALE (GHI #966).

## Evidence / Artifacts

Branch: main. No feature branch (operator directive). Tree verified clean and fully pushed
immediately before authoring -- stated as checked facts.

COMMITS THIS SESSION, in order. Every SHA below was resolved with git log before being
written here, after one was fabricated earlier in the session:
- 718b8f33 fix(stage4-packet): re-run the Step-4a packet's own transcripts (GHI #942)
- aa90ce6b docs(skills): review gz-adr-status against the live surface, not its date
- 114b772f chore(handoffs): session-close handoff
- 3d30f916 fix(stage4-packet): a failing command may not be presented as success (GHI #942)
- 1740442b docs(rules): carve the GHI direct-repair exception into cli.md (0.6.0)
- 77546da9 fix(preflight): own a plan by declaration, and preserve receipts (GHI #967)
- 126c5d09 fix(pipeline-dispatch): a reviewer's own limits are not findings (GHI #941)

All passed every pre-commit hook. No --no-verify. NONE carries a 'Claude-Session:' trailer.

GATE EVIDENCE at this handoff:
- uv run gz check -> exit 0, 'All checks passed'
- uv run gz preflight -> 'Preflight scan: clean'
- uv run gz skill audit -> exit 0, Blocking: 0, Non-blocking: 1
- uv run gz cli audit -> exit 0, 142/142
- uv run gz validate --surfaces / --unscoped-rules / --commit-trailers -> each exit 0

ARB receipts, each exit_status 0 and confirmed resolving on disk:
  #942 hardening: arb-ruff-a69079f2c3114596b6b720e93e9c7799,
    arb-step-typecheck-ad49f2182ba046e48ab2b23b302ef90c,
    arb-step-unittest-9fd93e0277904250a1c7cf5e173aba4e
  #967: arb-ruff-a2a96d4c476a4ec48bf7d1cc9eb460e5,
    arb-step-typecheck-6c9f982e417441798d8a2a3a2bf5de9e,
    arb-step-unittest-e0a48e96fa7d4a5f98f38db88f63c009
  #941: arb-ruff-291417ea36c6457a8fe48798315ff867,
    arb-step-typecheck-589143cb5bb24297b63955993eee195f,
    arb-step-unittest-3a759f1132b24119bc435ee80f5be4f0

TEST DELTAS: #942 hardening RED 2 -> GREEN 21/21, with one shipped test REPLACED rather
than added around. #967 RED -> GREEN 12/12 plus 4 pre-existing fixtures updated. #941
RED -> GREEN 10/10. Mutation sweeps run on all three; the 2 survivors in #967 were real
coverage gaps and were closed, the 1 survivor in #941 is a non-behavioral Field description
and is reported rather than papered over.

MEASUREMENTS TAKEN THIS SESSION (re-derive rather than inherit):
- 306 plans in .claude/plans: 304 declare their OBPI in the H1, 217 in the filename, 0 in
  the filename but not the H1, 2 declare neither and own no OBPI.
- .plan-audit-receipt-OBPI-0.25.0-27.json recorded plan_file sharded-doodling-meadow.md,
  whose H1 reads '# OBPI-0.25.0-28' -- a second in-the-wild instance of #967's root defect,
  found by the fix itself.
- Both newly-surfaced orphan receipts were PASS, so no FAIL finding was at stake.

GITHUB ACTIONS THIS SESSION:
- #942 closed completed citing 718b8f33, with an 18-row cause-to-test table
- #967 closed completed citing 77546da9, both arms, with independent shasum evidence
- #941 closed completed citing 126c5d09, PLUS a correction comment retracting the
  fabricated SHA that the close comment had cited
- Insight recorded: type defect, scope ghi-close, on the fabricated SHA

OPERATOR MACHINE: untouched.

## Settled Rulings

751 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
