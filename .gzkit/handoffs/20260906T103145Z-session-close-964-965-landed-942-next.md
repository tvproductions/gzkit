---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T10:31:45Z'
agent: claude-code-93c307d6
session_id: 93c307d6-9434-42d5-ad33-f03d5238f4b4
continues_from: .gzkit/handoffs/20260906T102521Z-ghi-964-closed-942-next-receipt-archived.md
---

## Current State Summary

SESSION-CLOSE handoff. Supersedes 20260906T102521Z, which was authored BEFORE the final git-sync and therefore records neither the sync outcome nor the true final HEAD. Everything in it stands; this one closes the loop. FINAL STATE: HEAD e4fe11d8, tree clean, nothing unpushed, uv run gz check exit 0, gz preflight clean, no active locks. CAMPAIGN: 3 of 24 closed this session and the one before (#962, #965, #964). 21 remain, order unchanged: 942, 941, 963, 888, 940, 849, 946, 877, 611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766. NEXT WORK ITEM: GHI #942 -- 'obpi-pipeline Stage 4a: pasted command output is unverified, and Step 4b does not check it'. Nothing blocks it. ONE GHI WAS OPENED THIS SESSION AND LEFT OPEN ON PURPOSE: #967, sibling cut of #964, carrying a routing blocker only the operator can clear.

## Important Context

=== WHAT CHANGED FOR OBPI COMPLETION (read before running any pipeline) ===

A heavy-lane brief whose Step 4b history holds a DISCHARGED refutation can now say so,
with one line in the Step 4b section:

  **Standing verdict:** not-refuted (round N; receipt arb-step-...)

gz obpi precomplete reads it and believes it in BOTH directions: a declared refutation
still blocks, two declarations that disagree are refused as ambiguous, and a declared
token outside the completion vocabulary is a FAILED declaration rather than an absent one.
With NO declaration, GHI #879's fail-closed behavior is unchanged. Nothing was weakened --
a brief must SAY which verdict stands to get credit for it. The ten pre-existing #879
verdict-reading tests still pass unchanged, and that is the guard proving it.

THE DECLARATION MUST OWN ITS LINE. Indentation, a list dash and a blockquote marker are
accepted; a heading is not. THIS CAME FROM THE REAL BRIEF, NOT THE FIXTURES -- every unit
test passed against a first version that keyed on the label plus a colon. OBPI-0.35.0-04
carries three round headings shaped '#### Round 12 - THE STANDING VERDICT: NOT-REFUTED,
the acceptance round', and that version read all three as declarations, then refused the
brief for conflicting verdicts it had invented out of ordinary prose -- a check
manufacturing the ambiguity it exists to refuse. Pinned now by
test_headings_and_prose_using_the_words_are_not_declarations.

WHAT THE FIX DOES NOT DO: the declaration is TRUSTED, not verified. The check does not
confirm a declared not-refuted corresponds to a real adversary round or a resolvable
receipt. Deliberate -- the check reads the brief; the ledger receipt is the durable
witness at the chokepoint. Stated in #964's close comment rather than left implied.

gz-obpi-pipeline SKILL.md documents the declaration where it already tells authors to
'preserve earlier rounds as history' (6.44.0 -> 6.45.0). An agent following the skill
finds it without reading this handoff.

=== THE ORPHAN RECEIPT IS RESOLVED ===

Operator-authorized 2026-09-06, cleanup only. The Codex-authored FAIL plan-audit receipt
for OBPI-0.35.0-05 is archived UNCHANGED beside its review report at
docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/OBPI-0.35.0-05-PLAN-AUDIT-RECEIPT.json.
Byte identity verified four ways -- sha256, cmp, git's own rename detection, and once more
against git's committed blob AFTER removal. The archive record in
OBPI-0.35.0-05-PLAN-REVIEW.md preserves original path, timestamp and FAIL disposition.
Only the operational copy was removed; the other 293 receipts in .claude/plans/ are
untouched.

THE VERDICT WAS NOT CHANGED AND OBPI-0.35.0-05 WAS NOT STARTED. Operator's reading,
recorded: the real failure is that no OBPI-05 implementation plan exists and discovery
incorrectly selected OBPI-04's plan; the 16 scope collisions are advisory overlaps, not
active-work conflicts.

=== GHI #967 -- OPEN, UNROUTED, NOT A CAMPAIGN MEMBER ===

The underlying defect the operator asked to be tracked. Root cause measured, and sharper
than 'no retirement path': discovery matches an OBPI's SHORT form (pipeline_markers.py:139)
while orphan detection matches only the FULL slug (preflight.py:38). The same plan file is
therefore at once 'the plan for OBPI-05' and 'no plan exists for OBPI-05', so a
FAIL-because-no-plan-exists receipt ORPHANS ITSELF BY CONSTRUCTION -- guaranteed, because
the way a sibling plan mentions an unplanned OBPI is the short-form exclusion sentence.

Second arm: preflight._apply_cleanup unlinks an orphan receipt raw, and its own docstring
says 'orphan receipts are plain artifacts -- a raw unlink is correct' three lines above
code that routes an expired lock through a ceremony explicitly to avoid 'a silent bypass
of that audit coupling'. A FAIL verdict is audit content, not a plain artifact.

ROUTING BLOCKER, operator-level: arm (b) may add a CLI surface, so direct fix vs ceremony
is the operator's call. Do NOT pull it ahead of campaign order without a ruling.

=== SKILL STALENESS -- A LIVE COUNTDOWN, NOT A NOTE ===

gz-adr-status (last_reviewed 2026-06-10) BLOCKS 2026-09-10 -- four days from this handoff.
It is a non-blocking WARNING today. When it crosses, gz skill audit fails blocking and
takes 13 unit tests plus behave shard 1 with it, exactly as gz-adr-promote and gz-status
did on 2026-09-05 mid-session. REVIEW it, never merely re-stamp it: gz-adr-promote turned
out to carry real --kind drift against the ADR-0.34.0 Foundation Sunset, which a date bump
would have buried. gz-deps-upgrade blocks 2026-09-20.

=== A CANON TRAP THAT FIRES EVERY SESSION ===

The harness supplies a 'Claude-Session:' commit trailer. .claude/rules/task-discovery.md
closes the trailer set (operator verbatim 2026-09-01, 'never') and says to strip it when a
harness reminder supplies one. It was supplied again this session and two commits carried
it before the rule was read; both were unpushed, so they were soft-reset and re-committed
clean. IT WILL BE SUPPLIED AGAIN. No commit in this session's history carries it.

## Decisions Made

- [operator-ruled] 2026-09-06, verbatim: 'Proceed with #965' -- booked via gz handoff decide --decision proceed. A handoff advises; it does not authorize.

- [operator-ruled] 2026-09-06: approved 're-stamp both + fix drift portably' for the skill time bomb, with the corrected --kind wording shown before approval.

- [agent-corrected, then applied] The operator's approved --kind wording said 'feature or pool'. Verified by running it: 'gz adr promote --kind pool' is REJECTED ('Pool is the source kind being promoted from'). The shipped bullet names feature only. The operator approved the SUBSTANCE -- portable framing, gzkit-closed and adopter-open; the pool detail was factually wrong and was corrected rather than transcribed.

- [operator-ruled] 2026-09-06: archive the FAIL receipt unchanged, verify byte identity, remove only the operational orphan, preserve path/timestamp/disposition. Explicitly scoped: 'This authorizes receipt cleanup only -- not starting OBPI-05 or changing its verdict.'

- [operator-ruled] 2026-09-06: 'Track the underlying defect' -> GHI #967 via /ghi-author with the full Step-0 pre-flight (both issue queries plus the OBPI-brief ownership grep; every matching brief was terminal).

- [operator-ruled] 2026-09-06: 'then proceed with GHI #964', which also cleared that issue's own recorded routing blocker. Worked as a direct fix per operator canon: a GHI is its own work order and receipt.

- [agent-chose] Did NOT run 'gz preflight --apply' when the orphan first blocked the gate, before authorization existed. It would have deleted a FAIL-verdict finding about an OBPI on this ADR. Surfaced instead and left the gate red rather than making it green by deletion.

- [agent-chose] Made the standing verdict a DECLARATION, never a position rule. A first-token rule would have read both cited briefs correctly, and that is exactly the inference GHI #879 removed -- correctness on two samples is not a contract.

- [agent-chose] A declaration naming a token outside the vocabulary FAILS rather than being ignored; ignoring it would let '**Standing verdict:** shipped' fall through to the history scan as though nothing had been claimed.

- [agent-chose] Did NOT edit any OBPI brief. IRON LAW reserves brief edits to the operator, so the real-brief demonstration ran on temp copies. OBPI-0.35.0-04 is attested_completed, never needs to pass precomplete again, and does NOT carry the new declaration line.

- [agent-chose] Updated gz-obpi-pipeline SKILL.md in the SAME commit as the check (DO IT RIGHT 1a, coupled-surface coherence), with the skill-version and last_reviewed bumps that rule requires.

- [agent-chose] Included heredoc handling in #965's joiner though the GHI named only quoting, backslash continuation and command substitution -- a heredoc is inside the class the body defines. Did NOT extend it to shell control structures (for/while/if/case, brace and paren groups): those continue across lines with no marker, so recognising them needs a parser. Disclosed in the close comment as a scoped limit rather than left silent.

- [agent-chose] Did NOT force-push to recover a lost commit message. The 20260906T102521Z handoff commit landed under gz git-sync's generic message because the trailing-whitespace hook modified the file and aborted the authored commit; content is intact and pushed. Rewriting pushed history over a message was not worth it. Recorded here instead.

## Immediate Next Steps

1. Re-establish repository truth BEFORE staging anything:
     git status --short
     git log --oneline -1        # expect e4fe11d8 or later
     uv run gz obpi lock list    # expect: No active locks

2. Confirm the gate before starting anything:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   Expect exit 0. It was exit 0 at this handoff with a clean, fully pushed tree.

3. IF THE DATE IS 2026-09-10 OR LATER, do this FIRST:
     uv run gz skill audit
   A blocking SKA-LAST-REVIEWED-STALE on gz-adr-status must be cleared by REVIEWING the
   skill -- read it, verify its gz verbs resolve, fix any drift -- and only then
   re-stamping last_reviewed. A bare date bump is the hollow-witness pattern.

4. WORK GHI #942. FIRST COMMAND:
     gh issue view 942 --json number,title,body,state,labels,comments,url
   It is the adjacent cut to #965 [settled]: that one fixed the TOOL-GENERATED Stage 4a packet,
   #942 is about HAND-PASTED 4a evidence being unverified. Read #965 [settled]'s close comment
   first so you do not re-scope what already landed. Re-derive every precondition against
   the tree before accepting it. Route per AGENTS.md Defect-fix routing; a GHI is its own
   work order and receipt, so no Gate 5 attestation.

5. TDD is not optional. Write the failing test first and watch it fail for the right
   reason. Then verify with an explicit exit capture -- a trailing filter reports its own
   exit, not the verifier's:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   Emit ARB receipts and confirm each resolves on disk before citing it.

6. Close ONLY #942. Leave #967 open unless the operator routes it.

7. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

- GHI #942 (OPEN, campaign member) -- NEXT WORK ITEM. Adjacent cut to #965 [settled]; deliberately
  left open across two closes.

- GHI #967 (OPEN, NOT a campaign member) -- filed this session. Sibling cut of #964 [settled] on the
  gz preflight side. Routing blocker: arm (b) may add a CLI surface, so the operator
  chooses direct fix vs ceremony. Do NOT pull ahead of campaign order without a ruling.

- SKILL STALENESS COUNTDOWN -- gz-adr-status blocks 2026-09-10 (four days out),
  gz-deps-upgrade blocks 2026-09-20. Both non-blocking warnings now. See Important Context.

- AN ERROR MESSAGE THAT CONTRADICTS ITS OWN COMMAND (untracked, small) --
  'gz adr promote --kind foundation' fails with guidance to re-run using --kind feature or
  --kind pool, but --kind pool is rejected by that same command. Argparse advertises
  choices pool, foundation, feature while its help text says pool is rejected. Observed
  and verified this session; NOT filed. Worth a GHI if a future session has room.

- GHI #966, #933, #815, #930, #611, #894, #939, #922, #921, #952, #953 (OPEN) -- unchanged
  this session.

- ADR-0.35.0 closeout BLOCKED on 8 OBPIs missing ledger proof: 05, 06, 07, 08, 10, 11, 12,
  13. Measured at this handoff: 5/13, lifecycle Pending, closeout pre_closeout, BLOCKED,
  QC PENDING. Unchanged -- every fix this session was a GHI direct fix touching no OBPI.
  OBPI-08 is the only one in_progress. IRON LAW: ONLY THE OPERATOR INITIATES OBPI WORK --
  no lock, no marker, no TASK, no dispatch, no brief edit.

- OPEN-QUEUE COUNT still unreconciled (48 measured 2026-09-05 against 32 in orientation).
  Re-derive before citing either.

NO OPERATOR ATTESTATION REQUIRED for #942, #964 [settled], #965 [settled] or #967 -- all GHIs, and a GHI is
its own work order and receipt.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- git status --short                          -> clean; check for a concurrent session
- git log --oneline -1                        -> e4fe11d8 or later
- git log --oneline origin/main..HEAD         -> empty (everything pushed)
- git merge-base --is-ancestor 3c543d1a HEAD  -> exit 0 (the #964 fix)
- git merge-base --is-ancestor baa0df93 HEAD  -> exit 0 (the #965 fix)
- git merge-base --is-ancestor fac07fb0 HEAD  -> exit 0 (the receipt archive)
- uv run gz obpi lock list                    -> No active locks
- gh issue view 965 --json state,stateReason  -> CLOSED/COMPLETED
- gh issue view 964 --json state,stateReason  -> CLOSED/COMPLETED
- gh issue view 942 --json state,stateReason  -> OPEN (the work item)
- gh issue view 967 --json state,stateReason  -> OPEN (filed this session)

THE GATE:
- uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"   -> exit 0, All checks passed
- uv run gz preflight                                     -> Preflight scan: clean
- uv run gz skill audit                                   -> Blocking: 0

THE #964 FIX IS LIVE (behavior, not a transcribed claim). This edits no brief:

  uv run python -c '
import sys, tempfile, shutil
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from gzkit.commands.obpi_precomplete import _check_adversarial_validation
real = Path("docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md")
td = Path(tempfile.mkdtemp()); text = real.read_text(encoding="utf-8")
m = "### Step 4b — Independent Adversarial Validation\n"
a = td/"a.md"; shutil.copyfile(real, a)
b = td/"b.md"; b.write_text(text.replace(m, m+"\n**Standing verdict:** not-refuted\n", 1), encoding="utf-8")
ra, rb = _check_adversarial_validation(a), _check_adversarial_validation(b)
print("unmodified:", ra.ok, ra.message)
print("declared:  ", rb.ok, rb.message)
'

  -> unmodified: False Step 4b records refuted
  -> declared:   True  Step 4b declares standing verdict 'not-refuted'

  If 'unmodified' reports a CONFLICT rather than 'records refuted', the line-start anchor
  regressed and the check is reading round headings as declarations again.

THE #965 FIX IS LIVE:
- uv run gz obpi present-evidence OBPI-0.35.0-03-retire-duplicate-invariant-entries
    -> ATTESTABLE, both Demo probes exit 0. NOT-ATTESTABLE with exit 127 on interior
       lines means the joiner regressed.

THE ARCHIVED RECEIPT (byte identity, re-checkable at any time):
- shasum -a 256 docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/OBPI-0.35.0-05-PLAN-AUDIT-RECEIPT.json
    -> 3b879346d3844017e57726054869a88b082b0963719dba45f310c3c7c1f12931

CODEX DELIVERY (the regression an earlier context undid -- still green):
- uv run gz validate --instructions-files-budget
    -> NOTE [codex-delivery-witness] AGENTS.md: 46876 B of 46876 B delivered.
       Fewer delivered bytes than the file holds means the cap regressed; read GHI #962.
- grep project_doc_max_bytes .codex/config.toml -> 65536

- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read the live OBPI count
  and closeout readiness from the command, never from a number transcribed here.

## Evidence / Artifacts

Branch: main. No feature branch (operator directive). Tree verified clean and fully
pushed via 'git status --short' and 'git log origin/main..HEAD' immediately before
authoring -- stated as checked facts.

COMMITS THIS SESSION, in order:
- 4a86dd4b chore(handoffs): record the prior session's mechanical exit bookmark
- baa0df93 fix(stage4-evidence): join multi-line Demo commands before running them (GHI #965)
- 036d3947 fix(skills): correct gz-adr-promote --kind guidance and re-stamp two stale reviews
- e41b79cc chore(handoffs): campaign handoff -- #965 closed (2/24), #964 next
- fac07fb0 chore(plan-audit): archive the OBPI-05 FAIL receipt, clear the operational orphan (GHI #967)
- 3c543d1a fix(obpi-precomplete): let a brief declare which Step 4b verdict stands (GHI #964)
- e4fe11d8 chore: update .gzkit (2 files) (gz git-sync)  <- carries the 102521Z handoff

All passed every pre-commit hook. No --no-verify anywhere. No commit carries a
'Claude-Session:' trailer.

TWO HISTORY NOTES, both benign and both stated rather than hidden:
1. baa0df93 and 4a86dd4b REPLACE earlier SHAs ba34c448 and c1277e1d, soft-reset and
   re-committed to strip the closed-set 'Claude-Session:' trailer. Nothing was pushed in
   between; the earlier SHAs exist in no remote.
2. e4fe11d8 carries the 20260906T102521Z handoff under gz git-sync's GENERIC message. The
   authored message was lost when the trailing-whitespace hook modified the file and
   aborted the commit, and git-sync then re-added and committed it. Content is intact and
   pushed; no force-push was performed to recover a message.

GATE EVIDENCE at this handoff:
- uv run gz check -> exit 0, 'All checks passed'
- uv run gz preflight -> 'Preflight scan: clean'
- uv run gz skill audit -> exit 0, Blocking: 0, 70 canonical skills across 3 roots
- ARB receipts for #964, each exit_status 0 and confirmed resolving on disk:
  artifacts/receipts/arb-ruff-3775f9795c58488aaedb5e9e5056c0cd.json
  artifacts/receipts/arb-step-typecheck-be25625744cc40b885c50a4ccd2bb10b.json
  artifacts/receipts/arb-step-unittest-b921bd0943794d13b7f591ee803d9d22.json
- ARB receipts for #965, each exit_status 0 and confirmed resolving on disk:
  artifacts/receipts/arb-ruff-7f560ed742cb43de89753fed33df3071.json
  artifacts/receipts/arb-step-typecheck-0729b16affc942fd9ab856dbfc8dd556.json
  artifacts/receipts/arb-step-unittest-eec8e25f131a4e42b8ee900089a1ac7f.json

#964: RED 7 failures -> GREEN 59/59. New surfaces _STANDING_VERDICT_RE, _step_4b_section
and _declared_standing_verdicts in src/gzkit/commands/obpi_precomplete.py; 11 new tests in
tests/commands/test_obpi_precomplete.py. The ten pre-existing GHI #879 verdict-reading
tests still pass unchanged.

#965: RED 12 failures -> GREEN 27/27. New surfaces _scan_shell and _join_demo_commands in
src/gzkit/governance/stage4_evidence.py; 15 new tests. Reproduction brief now ATTESTABLE
with both probes exit 0, where it previously produced roughly 50 blockers. xenon
--max-absolute C passes; _scan_shell measures C(18), inside the live band.

GITHUB ACTIONS THIS SESSION:
- #965 closed completed citing baa0df93, with a 15-row cause-to-test table
- #964 closed completed citing 3c543d1a, with an 11-row cause-to-test table
- #967 created (defect, runtime), OPEN with a routing blocker
- #964 received a sibling cross-link comment naming #967 at authoring time

ADR-0.35.0 AT THIS HANDOFF: lane heavy, lifecycle Pending, closeout pre_closeout, 5/13
OBPI, Closeout BLOCKED, QC PENDING. Unchanged by this session.

OPERATOR MACHINE: untouched. ~/.codex/config.toml is byte-identical to how this session
found it.

## Settled Rulings

742 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
