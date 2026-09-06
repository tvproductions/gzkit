---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T10:25:21Z'
agent: claude-code-93c307d6
session_id: 93c307d6-9434-42d5-ad33-f03d5238f4b4
continues_from: .gzkit/handoffs/20260906T095752Z-ghi-965-closed-964-next-skill-timebomb-cleared.md
---

## Current State Summary

GHI #964 is CLOSED/COMPLETED at 3c543d1a; #965 closed earlier this session at baa0df93. CAMPAIGN: 3 of 24 closed (#962, #965, #964). 21 remain, order unchanged: 942, 941, 963, 888, 940, 849, 946, 877, 611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766. NEXT WORK ITEM: GHI #942 -- 'obpi-pipeline Stage 4a: pasted command output is unverified, and Step 4b does not check it'. It is the adjacent cut to #965 and was deliberately left open across two closes; nothing blocks it. gz check is exit 0 and the tree is synced. ONE NEW GHI WAS FILED THIS SESSION: #967, the sibling cut of #964 on the gz preflight side -- open, unrouted, and NOT a campaign member.

## Important Context

=== WHAT CHANGED FOR OBPI COMPLETION (read before running any pipeline) ===

A heavy-lane brief whose Step 4b history holds a discharged refutation can now declare
which verdict stands, with ONE line in the Step 4b section:

  **Standing verdict:** not-refuted (round N; receipt arb-step-...)

gz obpi precomplete reads it and believes it in BOTH directions -- a declared refutation
still blocks, two declarations that disagree are refused as ambiguous, and a declared
token outside the completion vocabulary is a FAILED declaration rather than an absent
one. With NO declaration the pre-existing fail-closed behavior of GHI #879 is unchanged.
Nothing was weakened: a brief must SAY which verdict stands to get credit for it.

THE DECLARATION MUST OWN ITS LINE. Indentation, a list dash and a blockquote marker are
fine; a heading is not. This was found by running the check against the real
OBPI-0.35.0-04 brief, NOT by the unit fixtures, all of which passed. That brief carries
three round headings shaped '#### Round 12 - THE STANDING VERDICT: NOT-REFUTED, the
acceptance round', and a colon-only rule read all three as declarations, then refused the
brief for conflicting verdicts it had invented out of ordinary prose. Pinned now by
test_headings_and_prose_using_the_words_are_not_declarations.

gz-obpi-pipeline SKILL.md documents this where it already says 'preserve earlier rounds
as history' (6.44.0 -> 6.45.0). An agent following the skill will find it.

WHAT THE FIX DOES NOT DO: the declaration is TRUSTED, not verified. The check does not
confirm a declared not-refuted corresponds to a real round or a resolvable receipt. That
is deliberate -- the check reads the brief; the ledger receipt is the durable witness at
the chokepoint. Stated plainly in the #964 close comment rather than left implied.

=== THE ORPHAN RECEIPT IS RESOLVED (the prior handoff's open item) ===

Operator-authorized 2026-09-06, cleanup only. The Codex-authored FAIL plan-audit receipt
for OBPI-0.35.0-05 was archived UNCHANGED beside its review report at
docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/OBPI-0.35.0-05-PLAN-AUDIT-RECEIPT.json,
byte identity verified by sha256, cmp, and git's own rename detection; the archive record
in OBPI-0.35.0-05-PLAN-REVIEW.md preserves its original path, timestamp and FAIL
disposition. Only the operational copy was removed; the other 293 receipts in
.claude/plans/ are untouched. gz preflight is clean and gz check is exit 0.

THE VERDICT WAS NOT CHANGED AND OBPI-0.35.0-05 WAS NOT STARTED. Operator's reading,
recorded: the real failure is that no OBPI-05 implementation plan exists and discovery
incorrectly selected OBPI-04's plan; the 16 scope collisions are advisory overlaps, not
active-work conflicts.

=== GHI #967, FILED THIS SESSION, OPEN AND UNROUTED ===

The underlying defect the operator asked to be tracked. Root cause is sharper than 'no
retirement path', and was measured: discovery matches an OBPI's SHORT form
(pipeline_markers.py:139, 'short_form not in content and obpi_id not in content') while
orphan detection matches only the FULL slug (preflight.py:38). So the same plan file is
at once 'the plan for OBPI-05' and 'no plan exists for OBPI-05', and a
FAIL-because-no-plan-exists receipt orphans itself by construction -- guaranteed, because
the way a sibling plan mentions an unplanned OBPI is the short-form exclusion sentence.

Second arm: preflight._apply_cleanup unlinks an orphan receipt raw, and its own docstring
says 'orphan receipts are plain artifacts -- a raw unlink is correct' three lines above
code that routes an expired lock through a ceremony explicitly to avoid 'a silent bypass
of that audit coupling'. A FAIL verdict is audit content, not a plain artifact.

#967 is OPEN with a routing blocker: arm (b) may add a CLI surface, so operator chooses
direct fix vs ceremony. Cross-linked to #964 as a sibling cut, and a cross-link comment
was posted on #964 at authoring time.

=== SKILL STALENESS -- STILL A LIVE COUNTDOWN ===

gz-adr-status (last_reviewed 2026-06-10) BLOCKS 2026-09-10 -- four days out. Currently a
non-blocking warning. When it crosses, gz skill audit fails blocking and takes 13 unit
tests plus a behave shard with it, exactly as gz-adr-promote and gz-status did on
2026-09-05. REVIEW it, never merely re-stamp it: gz-adr-promote turned out to carry real
--kind drift against the Foundation Sunset. gz-deps-upgrade blocks 2026-09-20.

## Decisions Made

- [operator-ruled] 2026-09-06: archive the FAIL receipt unchanged alongside the OBPI-05 review report, verify byte identity, remove only the operational orphan, preserve original path/timestamp/disposition in the archive record. Explicitly scoped: 'This authorizes receipt cleanup only -- not starting OBPI-05 or changing its verdict.'

- [operator-ruled] 2026-09-06: 'Track the underlying defect' -> GHI #967, filed through /ghi-author with the full Step-0 pre-flight (both issue queries plus the OBPI-brief ownership grep; every matching brief was terminal).

- [operator-ruled] 2026-09-06: 'then proceed with GHI #964', which also resolved that issue's own recorded routing blocker ('operator to choose direct fix vs. chore'). Worked as a direct fix per operator canon: a GHI is its own work order and receipt.

- [agent-chose] Did NOT run 'gz preflight --apply' when the orphan first blocked the gate, before authorization. It would have deleted a FAIL-verdict finding about an OBPI on this ADR. Surfaced instead and left the gate red.

- [agent-chose] Made the standing verdict a DECLARATION rather than a position rule. A first-token rule would have read both cited briefs correctly and is exactly the inference GHI #879 removed; correctness on two samples is not a contract.

- [agent-chose] A declaration naming a token outside the vocabulary FAILS rather than being ignored. Ignoring it would let '**Standing verdict:** shipped' fall through to the history scan as though nothing had been claimed.

- [agent-chose] Did NOT edit any OBPI brief to demonstrate the fix. IRON LAW reserves brief edits to the operator, so the real-brief demonstration ran on temp copies. OBPI-0.35.0-04 is attested_completed and never needs to pass precomplete again; it does NOT carry the new declaration line.

- [agent-chose] Updated gz-obpi-pipeline SKILL.md in the same commit as the check (coupled-surface coherence, DO IT RIGHT 1a), with the skill-version and last_reviewed bumps that rule requires.

- [carried forward] The 'Claude-Session:' trailer is CLOSED-SET canon and must be stripped whenever the harness supplies it. It did again this session; no commit carries it.

## Immediate Next Steps

1. Re-establish repository truth BEFORE staging anything:
     git status --short
     git log --oneline -1        # expect 3c543d1a or later
     uv run gz obpi lock list    # expect: No active locks

2. Confirm the gate is still green before starting:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   Expect exit 0. It was exit 0 at this handoff, with the orphan receipt resolved.

3. Check the skill countdown FIRST if the date is 2026-09-10 or later:
     uv run gz skill audit
   A blocking SKA-LAST-REVIEWED-STALE on gz-adr-status must be cleared by REVIEWING it
   (read it, verify its verbs resolve, fix drift found) and then re-stamping. Never
   stamp without reviewing.

4. WORK GHI #942. FIRST COMMAND:
     gh issue view 942 --json number,title,body,state,labels,comments,url
   It is the adjacent cut to #965 [settled] (hand-pasted Stage 4a evidence vs the tool-generated
   packet #965 [settled] fixed), so read #965 [settled]'s close comment for what was already covered before
   scoping it. Re-derive every precondition against the tree; route per AGENTS.md
   Defect-fix routing. A GHI is its own work order and receipt -- no Gate 5.

5. Verify with an explicit exit capture; a trailing filter reports its own exit, not the
   verifier's. Emit ARB receipts and confirm each resolves on disk before citing it.

6. Close ONLY #942. Leave #967 open unless the operator routes it.

7. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

- GHI #942 (OPEN, campaign member) -- NEXT WORK ITEM. Adjacent cut to #965 [settled].

- GHI #967 (OPEN, NOT a campaign member) -- filed this session; sibling cut of #964 [settled] on
  the gz preflight side. Carries a routing blocker: arm (b) may add a CLI surface, so the
  operator chooses direct fix vs ceremony. Do NOT pull it ahead of campaign order without
  a ruling.

- SKILL STALENESS COUNTDOWN -- gz-adr-status blocks 2026-09-10 (four days out),
  gz-deps-upgrade blocks 2026-09-20. Both non-blocking warnings now.

- AN ERROR MESSAGE THAT CONTRADICTS ITS OWN COMMAND (untracked, small) --
  'gz adr promote --kind foundation' fails with guidance to re-run using --kind feature
  or --kind pool, but --kind pool is rejected by the same command. Argparse advertises
  choices pool, foundation, feature while its help says pool is rejected. Noted in the
  #967-adjacent space but NOT filed; worth a GHI if a future session has room.

- GHI #966, #933, #815, #930, #611, #894, #939, #922, #921, #952, #953 (OPEN) --
  unchanged.

- ADR-0.35.0 closeout BLOCKED on 8 OBPIs missing ledger proof: 05, 06, 07, 08, 10, 11,
  12, 13. Unchanged by this session; nothing here touched an OBPI. OBPI-08 is the only
  one in_progress. IRON LAW: ONLY THE OPERATOR INITIATES OBPI WORK -- no lock, no marker,
  no TASK, no dispatch, no brief edit.

- OPEN-QUEUE COUNT still unreconciled (48 measured 2026-09-05 against 32 in orientation).
  Re-derive before citing either.

NO OPERATOR ATTESTATION REQUIRED for #942, #964 [settled], #965 [settled] or #967 -- all GHIs, and a GHI is
its own work order and receipt.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- git status --short                          -> clean; check for a concurrent session
- git merge-base --is-ancestor 3c543d1a HEAD  -> exit 0 (the #964 fix)
- git merge-base --is-ancestor baa0df93 HEAD  -> exit 0 (the #965 fix)
- uv run gz obpi lock list                    -> No active locks
- gh issue view 964 --json state,stateReason  -> CLOSED/COMPLETED
- gh issue view 965 --json state,stateReason  -> CLOSED/COMPLETED
- gh issue view 942 --json state,stateReason  -> OPEN (the work item)
- gh issue view 967 --json state,stateReason  -> OPEN (filed this session)

THE GATE:
- uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"   -> exit 0, all checks passed
- uv run gz preflight                                     -> Preflight scan: clean
- uv run gz skill audit                                   -> Blocking: 0

THE #964 FIX IS LIVE (behavior, not a transcribed claim). Run this; it edits no brief:

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
print("unmodified:", _check_adversarial_validation(a).message)
print("declared:  ", _check_adversarial_validation(b).ok, _check_adversarial_validation(b).message)
'

  -> unmodified: Step 4b records refuted
  -> declared:   True Step 4b declares standing verdict 'not-refuted'

THE ARCHIVED RECEIPT (byte identity, re-checkable at any time):
- shasum -a 256 docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/OBPI-0.35.0-05-PLAN-AUDIT-RECEIPT.json
    -> 3b879346d3844017e57726054869a88b082b0963719dba45f310c3c7c1f12931

CODEX DELIVERY (still green):
- uv run gz validate --instructions-files-budget
    -> NOTE [codex-delivery-witness] AGENTS.md: 46876 B of 46876 B delivered.
- grep project_doc_max_bytes .codex/config.toml -> 65536

- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read the live OBPI count
  and closeout readiness from the command, never from a number transcribed here.

## Evidence / Artifacts

Branch: main. No feature branch (operator directive). Working tree verified clean via
'git status --short' immediately before authoring.

COMMITS THIS SESSION, in order:
- 4a86dd4b chore(handoffs): record the prior session's mechanical exit bookmark
- baa0df93 fix(stage4-evidence): join multi-line Demo commands before running them (GHI #965)
- 036d3947 fix(skills): correct gz-adr-promote --kind guidance and re-stamp two stale reviews
- e41b79cc chore(handoffs): campaign handoff -- #965 closed (2/24), #964 next
- fac07fb0 chore(plan-audit): archive the OBPI-05 FAIL receipt, clear the operational orphan (GHI #967)
- 3c543d1a fix(obpi-precomplete): let a brief declare which Step 4b verdict stands (GHI #964)
All passed every pre-commit hook. No --no-verify anywhere. No commit carries a
'Claude-Session:' trailer; the harness supplied one and it was stripped per closed-set canon.

NOTE: baa0df93 and 4a86dd4b replace earlier SHAs ba34c448 and c1277e1d, soft-reset and
re-committed to strip that trailer before anything was pushed.

GATE EVIDENCE at this handoff:
- uv run gz check -> exit 0, 'All checks passed'
- uv run gz preflight -> 'Preflight scan: clean'
- uv run gz skill audit -> exit 0, Blocking: 0, 70 canonical skills across 3 roots
- ARB receipts for #964, each exit_status 0 and confirmed resolving on disk:
  artifacts/receipts/arb-ruff-3775f9795c58488aaedb5e9e5056c0cd.json
  artifacts/receipts/arb-step-typecheck-be25625744cc40b885c50a4ccd2bb10b.json
  artifacts/receipts/arb-step-unittest-b921bd0943794d13b7f591ee803d9d22.json
- ARB receipts for #965 (earlier this session), each exit_status 0:
  artifacts/receipts/arb-ruff-7f560ed742cb43de89753fed33df3071.json
  artifacts/receipts/arb-step-typecheck-0729b16affc942fd9ab856dbfc8dd556.json
  artifacts/receipts/arb-step-unittest-eec8e25f131a4e42b8ee900089a1ac7f.json

#964 EVIDENCE: RED 7 failures -> GREEN 59/59. New surfaces _STANDING_VERDICT_RE,
_step_4b_section and _declared_standing_verdicts in src/gzkit/commands/obpi_precomplete.py;
11 new tests in tests/commands/test_obpi_precomplete.py. The ten pre-existing GHI #879
verdict-reading tests still pass unchanged -- that is the guard proving the check was not
weakened.

#965 EVIDENCE: RED 12 failures -> GREEN 27/27. Reproduction brief now ATTESTABLE with
both Demo probes exit 0, where it previously produced roughly 50 blockers.

ADR-0.35.0 AT THIS HANDOFF: lane heavy, lifecycle Pending, closeout pre_closeout, 5/13
OBPI, Closeout BLOCKED, QC PENDING. Unchanged -- every fix this session was a GHI direct
fix touching no OBPI.

OPERATOR MACHINE: untouched.

## Settled Rulings

739 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
