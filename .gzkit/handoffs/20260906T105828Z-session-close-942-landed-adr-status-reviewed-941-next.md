---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T10:58:28Z'
agent: claude-code-2a5779f2
session_id: 2a5779f2-39e4-4c24-9d36-646ae24fb112
continues_from: .gzkit/handoffs/20260906T103145Z-session-close-964-965-landed-942-next.md
---

## Current State Summary

SESSION-CLOSE. FINAL STATE: HEAD aa90ce6b, tree clean, nothing unpushed, uv run gz check exit 0, gz preflight clean, gz skill audit Blocking 0, no active locks. TWO COMMITS: 718b8f33 (GHI #942 fix) and aa90ce6b (gz-adr-status skill review). CAMPAIGN: #942 closed — 4 of 24 closed across three sessions (#962, #965, #964, #942). Remaining order unchanged: 941, 963, 888, 940, 849, 946, 877, 611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766. NEXT WORK ITEM: GHI #941 — 'obpi-pipeline review gate: reviewers cannot execute, so unrunnable asks degrade the verdict'. Nothing blocks it. Open GHI queue measured 30 at this handoff (re-derive before citing). #967 remains OPEN and unstarted by operator direction.

## Important Context

=== WHAT LANDED FOR STAGE 4 (read before running any pipeline) ===

A NEW STEP exists between 4a and 4b: **Step 4a-v**. Write the composed Step-4a packet to
.gzkit/evidence/<OBPI-ID>.stage4a.md and run:

  uv run gz obpi verify-packet .gzkit/evidence/<OBPI-ID>.stage4a.md

Exit 0 VERIFIED, exit 3 NOT-VERIFIED, exit 1 packet not found. It re-executes every
$-prompted transcript in the packet and reports which pasted lines the command did not
produce. Present the verdict alongside 4a and 4b.

THE AUTHORING CONTRACT, because it changes how you write a packet:
- A `$` prompt is now a CLAIM that gets re-run. Paste only what the command produced.
- Comparison is CONTAINMENT, one direction: abridging and re-indenting are fine; a line
  the command never wrote is a blocker.
- Elide what cannot reproduce (timestamps, fresh receipt ids) with `...`. That escape is
  load-bearing — without it the check would false-block honest evidence.
- A silent assert-shaped probe is written `$ <cmd>; echo "exit $?"` so the status shows.
- A fenced shell block with NO `$` claims no output and is NEVER re-run. That is what the
  `arb:` incantation blocks are. They are listed back as citations.

WHAT IT DOES NOT DO: it does not verify a command cited without a prompt, and it does not
know whether a transcript is the RIGHT proof for the REQ above it. That stays with Step 4b
and the operator. Stated in the close comment, not left implied.

=== A NEAR-MISS WORTH INHERITING ===

While reviewing gz-adr-status I measured `gz adr report --help` exiting 2 and was one step
from filing a CLI defect. It was MY TEST HARNESS: zsh does not word-split unquoted
parameters, so `for v in "adr report"; do gz $v --help; done` runs `gz "adr report" --help`
— an invalid choice, exit 2. Use `${=v}` in zsh, or just don't loop over multi-word verbs.
Every nested subcommand's --help exits 0. No defect exists; none was filed.

=== THE CANON TRAP STILL FIRES EVERY SESSION ===

The harness supplied a 'Claude-Session:' commit trailer again this session.
.claude/rules/task-discovery.md closes the trailer set (operator verbatim 2026-09-01,
'never') and says to strip it. Neither commit carries it — verified by grep after each.
IT WILL BE SUPPLIED AGAIN.

=== SKILL STALENESS ===

gz-adr-status is REVIEWED and re-stamped 2026-09-06 (1.12.2 -> 1.13.0), so its countdown is
cleared. gz-deps-upgrade blocks 2026-09-20 and is now the ONLY non-blocking warning
(Blocking 0, Non-blocking 1, down from 2). Review it, never merely re-stamp it — both
skills reviewed under this discipline (gz-adr-promote last session, gz-adr-status this one)
carried real drift a date bump would have buried.

## Decisions Made

- [operator-ruled] 2026-09-06, verbatim: 'Proceed with #942. Keep #967 tracked, but "may add a CLI surface" alone does not require new ADR/OBPI ceremony: GHI-tracked corrections are authorized for direct repair. Surface any actual unresolved design decision.' Booked via gz handoff decide --decision proceed.

- [operator-ruled] 2026-09-06, verbatim: 'Also complete a substantive review of gz-adr-status before September 10; don't merely refresh its date.' Done — three verified drifts corrected, not a date bump.

- [operator-ruled] 2026-09-06, verbatim: 'Leave the pushed handoff commit intact. Its generic message does not justify rewriting history.' No force-push was performed; e4fe11d8 stands as it landed.

- [operator-ruled] 2026-09-06, verbatim: 'OBPI-05 remains unstarted, and its archived FAIL verdict stands.' Untouched this session.

- [agent-chose] Built #942's remedy 2 (re-execute the packet) over remedy 1 (never let a composing agent render output). Remedy 1 removes the surface but has NO witness — an agent that will fabricate output will fabricate a file citation, which is the doctrine-declared-without-mechanism family the campaign is trying to close. Remedy 3 was declined by the issue's own reasoning.

- [agent-chose] Containment, not equality, and in ONE direction. Equality would false-block a packet that dropped a trailing comma or re-indented a nested object; the fabrication direction is showing what the command did not write. The `...` elision escape exists so unreproducible output has an honest form — without it the gate would false-block honest evidence, and a gate that false-blocks is one agents route around.

- [agent-chose] A non-zero exit is NOT a blocker. A packet may legitimately show a RED run, and blocking on status would false-block an honest failure transcript. The witness is whether the OUTPUT reproduces.

- [agent-chose] Bare (non-`$`) fences are reported, never re-run. Re-running the `arb:` blocks would spend a full unittest sweep to witness a claim nobody made. Citation fences require an explicit shell info string so a pasted JSON block is not misread as commands.

- [agent-chose] Reused _join_demo_commands from stage4_evidence rather than writing a second command parser. GHI #965's class arrives in this surface: splitting at newlines would read a quoted program's own body as claimed output and report every interior line as fabricated.

- [agent-chose] Did NOT gate `gz obpi complete` on the packet verification. The witness must land BEFORE attestation, and complete already re-derives the tool packet. Enforcement matches Step 4b's model — a skill barrier, with the operator as the gate — and the close says so rather than claiming a gate that was not built.

- [agent-chose] Declared the new verb in config/doc-coverage.json mirroring its nearest sibling (`obpi present-evidence`: all doc surfaces false, governance_relevant false). Same category — pipeline-internal, invoked by the skill, not browsed by operators. `gz cli audit` exits 0 at 142/142.

- [agent-chose] Did NOT file a GHI for the `--help` exit-2 observation. Re-derived it and found the fault in my own zsh test loop, not in gz. Reporting it would have been a phantom.

- [agent-noted, NOT fixed] `.claude/rules/cli.md` § Adding CLI Features states verbatim that 'contract-bearing CLI work runs gz obpi pipeline, not a freeform direct fix', with no carve-out for GHI-tracked defect repair. That contradicts operator canon ('GHIs are AUTHORIZED for direct repair, always... those criteria gate planned ADR work, not defect repair') and the operator's ruling this session. The ruling governs and the fix landed as a direct fix; the RULE TEXT still reads the other way. Surfaced here rather than edited unilaterally — a rule file disagreeing with operator canon is the operator's to resolve.

## Immediate Next Steps

1. Re-establish repository truth BEFORE staging anything:
     git status --short
     git log --oneline -1        # expect aa90ce6b or later
     uv run gz obpi lock list    # expect: No active locks

2. Confirm the gate:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   Expect exit 0. It was exit 0 at this handoff on a clean, fully pushed tree.

3. WORK GHI #941. FIRST COMMAND:
     gh issue view 941 --json number,title,body,state,labels,comments,url
   'obpi-pipeline review gate: reviewers cannot execute, so unrunnable asks degrade the
   verdict'. Same family as #942 [settled]/#940/#919 — a signal that does not mean what its surface
   says. Re-derive every precondition against the tree before accepting it; the #942 [settled] body's
   own scope hint had gone stale in two places. Route per AGENTS.md Defect-fix routing; a
   GHI is its own work order and receipt, so no Gate 5 attestation.

4. TDD is not optional, and RED-for-the-right-reason is not enough on its own. After GREEN,
   MUTATE each production behavior in turn and confirm a test catches it. That sweep is
   what proves the tests are not hollow — it caught nothing this session because the tests
   were sound, but the handoff before this one records five covering tests that survived
   deliberately broken production behavior.

5. Capture exits explicitly — a trailing filter reports its own exit, not the verifier's:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   A PreToolUse hook now BLOCKS piping unittest into another process; use `set -o pipefail`
   or redirect to a file. Emit ARB receipts and confirm each resolves on disk before citing.

6. Close ONLY #941. Leave #967 open unless the operator routes it.

7. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

- GHI #941 (OPEN, campaign member) -- NEXT WORK ITEM. Nothing blocks it.

- GHI #967 (OPEN, NOT a campaign member) -- routing blocker CLEARED by operator ruling
  (direct fix, both arms), but the work is UNSTARTED by direction ('Keep #967 tracked').
  A comment posted this session records the ruling and surfaces the ONE genuinely
  unresolved design decision: may `gz preflight --apply` archive a terminal FAIL verdict
  unattended (no new CLI verb needed), or must retirement of an audit finding be
  operator-invoked (verb needed)? Canon does not settle it — the 2026-09-06 archive was a
  scoped one-off, and the reap_expired_locks analogy is weaker than it looks because a lock
  is a token whose surrender is routine while a FAIL verdict is a finding. ARM (a) — the
  id-match predicate reconciliation — has NO such question and can land ahead of the ruling.

- `.claude/rules/cli.md` CONTRADICTS OPERATOR CANON on defect-fix routing (untracked; see
  Decisions Made, last entry). Not filed as a GHI: the operator may prefer to rule on the
  rule text directly rather than have an agent open an issue against their own canon.

- AN ERROR MESSAGE THAT CONTRADICTS ITS OWN COMMAND (untracked, small, carried forward
  unchanged) -- 'gz adr promote --kind foundation' fails with guidance to re-run using
  --kind feature or --kind pool, but --kind pool is rejected by that same command.

- SKILL STALENESS -- gz-deps-upgrade blocks 2026-09-20, now the only non-blocking warning.

- GHI #966, #933, #815, #930, #611, #894, #939, #922, #921, #952, #953 (OPEN) -- unchanged
  this session. #966 is now DOCUMENTED IN gz-adr-status as a known-stale arm of that
  command's output, with the re-resolve instruction, so an agent reading the skill will not
  relay a closed GHI as a live defect.

- ADR-0.35.0 closeout BLOCKED on 8 OBPIs missing ledger proof: 05, 06, 07, 08, 10, 11, 12,
  13. Measured at this handoff: 5/13, lifecycle Pending, closeout pre_closeout, BLOCKED,
  QC PENDING. Unchanged -- both commits this session were GHI/skill work touching no OBPI.
  IRON LAW: ONLY THE OPERATOR INITIATES OBPI WORK -- no lock, no marker, no TASK, no
  dispatch, no brief edit.

NO OPERATOR ATTESTATION REQUIRED for #942 [settled] or #967 -- both GHIs, and a GHI is its own work
order and receipt. The skill review is a docs/skill commit, not an OBPI/ADR completion.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- git status --short                          -> clean; check for a concurrent session
- git log --oneline -1                        -> aa90ce6b or later
- git log --oneline origin/main..HEAD         -> empty (everything pushed)
- git merge-base --is-ancestor 718b8f33 HEAD  -> exit 0 (the #942 fix)
- git merge-base --is-ancestor aa90ce6b HEAD  -> exit 0 (the skill review)
- uv run gz obpi lock list                    -> No active locks
- gh issue view 942 --json state,stateReason  -> CLOSED/COMPLETED
- gh issue view 941 --json state,stateReason  -> OPEN (the work item)
- gh issue view 967 --json state,stateReason  -> OPEN (ruled, unstarted)

THE GATE:
- uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"   -> exit 0, All checks passed
- uv run gz preflight                                     -> Preflight scan: clean
- uv run gz skill audit                                   -> Blocking: 0, Non-blocking: 1
- uv run gz cli audit                                     -> exit 0, 142/142 covered

THE #942 FIX IS LIVE (behavior, not a transcribed claim). Writes only to a temp file:

  uv run python -c '
import sys, tempfile; sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from gzkit.governance.stage4_packet import verify_packet
td = Path(tempfile.mkdtemp())
bad = td/"bad.md"
bad.write_text("```\n$ printf \"a\\nb\\n\"\na\nNEVER-PRODUCED\n```\n", encoding="utf-8")
good = td/"good.md"
good.write_text("```\n$ printf \"a\\nb\\n\"\na\n...\n```\n", encoding="utf-8")
for p in (bad, good):
    r = verify_packet(Path("."), p)
    print(p.name, "verified:", r.verified, r.blockers[:1])
'

  -> bad.md  verified: False ['Command did not produce 1 pasted line(s) ...']
  -> good.md verified: True  []

  If bad.md reports verified True, the containment check regressed. If good.md reports
  False, the `...` elision escape regressed and the gate will false-block honest packets.

THE CITATION BOUNDARY HOLDS (the expensive-rerun guard):
- A ```bash fence with no `$` must appear in `citations` and NOT in `transcripts`.
  If an arb incantation ever shows up under "Transcripts (re-run)", the boundary broke
  and Stage 4 will start spending a full unittest sweep per packet.

THE gz-adr-status REVIEW IS LIVE:
- grep 'Layer 3 derived view' .gzkit/skills/gz-adr-status/SKILL.md   -> 1 hit
- grep -c 'json' .gzkit/skills/gz-adr-status/SKILL.md  -> the --json line must name
  `gz adr status` only; `gz adr report` does not take --json (verified against the parser)

CODEX DELIVERY (the regression an earlier context undid -- still green):
- uv run gz validate --instructions-files-budget
    -> NOTE [codex-delivery-witness] AGENTS.md: 46876 B of 46876 B delivered.

- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read the live OBPI count
  and closeout readiness from the command, never from a number transcribed here. Its
  `tracked defects:` annotations are KNOWN STALE (GHI #966) -- re-resolve any GHI it names
  against live GitHub before repeating it as a live defect.

## Evidence / Artifacts

Branch: main. No feature branch (operator directive). Tree verified clean and fully pushed
via 'git status --short' and 'git log origin/main..HEAD' immediately before authoring --
stated as checked facts.

COMMITS THIS SESSION, in order:
- 718b8f33 fix(stage4-packet): re-run the Step-4a packet's own transcripts (GHI #942)
- aa90ce6b docs(skills): review gz-adr-status against the live surface, not its date (1.13.0)

Both passed every pre-commit hook. No --no-verify. NEITHER carries a 'Claude-Session:'
trailer -- grepped after each commit. Pushed via 'uv run gz git-sync --apply --lint --test',
exit 0 (fetch, lint, test, push, post-sync lint).

GATE EVIDENCE at this handoff:
- uv run gz check -> exit 0, 'All checks passed'
- uv run gz preflight -> 'Preflight scan: clean'
- uv run gz skill audit -> exit 0, Blocking: 0, Non-blocking: 1, 70 canonical skills
- uv run gz cli audit -> exit 0, 'Cross-coverage: 142/142 commands fully covered'
- uv run gz validate --commit-trailers -> exit 0
- ARB receipts for #942, each exit_status 0 and confirmed resolving on disk:
  artifacts/receipts/arb-ruff-6d196365742241b089b5cc33fe8a3ff4.json
  artifacts/receipts/arb-step-typecheck-6cb74786e9c9426abf56986e69cb6a43.json
  artifacts/receipts/arb-step-unittest-1a7e1acd5e2f46a1b233edcba834338f.json

#942: RED (import failure) -> 18 tests -> GREEN 18/18, then a MUTATION SWEEP: eight
production behaviors broken in turn, every mutant caught by a test. New surfaces
stage4_packet.py (extract_transcripts, extract_citation_commands, verify_packet) and
commands/obpi_verify_packet.py; new verb `gz obpi verify-packet`; gz-obpi-pipeline
SKILL.md 6.45.0 -> 6.46.0 gains Step 4a-v.

Reproduced against the LIVE repo using the issue's verbatim fabricated block:
  exit 3, naming exactly "obpi_id" and "coverage_pct" as not produced, NOT flagging the
  correct figures beside them, and reporting the arb sweep as a citation rather than
  running it. The issue's second instance, authored as a transcript, exits 3 with
  'Transcript witnesses nothing'.

A DEFECT THE SUITE CAUGHT IN THIS PATCH, disclosed rather than quietly fixed: the new print
sites interpolated free-form command output straight into Rich's markup parser
(tests/policy/test_rich_markup_escaping.py). Escaped at the print sites.

gz-adr-status review: three verified drifts corrected -- (1) the Output Contract claimed
'--json on either verb' but `gz adr report` has no --json; (2) `gz adr report` had gained
an optional positional [adr] and a --type {foundation,feature,pool} filter, neither
documented; (3) References omitted adr-report.md though that manpage exists and adr report
is the skill's own summary verb. Added the Layer-3 caveat with GHI #966's live instance
quoted from observed output. VERIFIED AND NOT CHANGED: the locked test exists at
tests/commands/test_status.py:1272; both cited manpages exist; --show-gates is real.

GITHUB ACTIONS THIS SESSION:
- #942 closed completed citing 718b8f33, with an 18-row cause-to-test table and an explicit
  'what this close does NOT claim' section
- #967 received a routing-ruling comment; left OPEN by operator direction

ADR-0.35.0 AT THIS HANDOFF: lane heavy, lifecycle Pending, closeout pre_closeout, 5/13
OBPI, Closeout BLOCKED, QC PENDING. Unchanged by this session.

OPERATOR MACHINE: untouched.

## Settled Rulings

747 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
