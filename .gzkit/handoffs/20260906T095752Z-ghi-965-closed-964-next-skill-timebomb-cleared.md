---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T09:57:52Z'
agent: claude-code-93c307d6
session_id: 93c307d6-9434-42d5-ad33-f03d5238f4b4
continues_from: .gzkit/handoffs/20260906T043608Z-ghi-965-next-with-operator-coupling-list.md
---

## Current State Summary

GHI #965 is CLOSED/COMPLETED at baa0df93 (multi-line Demo commands now joined before execution). CAMPAIGN: 2 of 24 closed (#962, #965). 22 remain, order unchanged: 964, 942, 941, 963, 888, 940, 849, 946, 877, 611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766. NEXT WORK ITEM: GHI #964 -- 'obpi precomplete: a discharged refutation in Step 4b history fails precomplete'. The operator's coupling list calls it 'worth repairing before another corrected Step-4b history encounters precomplete'; it is free-standing, as #965 was, and carries no OBPI relation. TWO THINGS THIS SESSION SURFACED THAT THE PRIOR HANDOFF COULD NOT KNOW, both detailed in Important Context: a skill-staleness time bomb fired mid-session and blocked the whole gate, and a FAIL-verdict plan-audit receipt from a concurrent session is now the sole remaining gz check failure. Neither is a #965 regression.

## Important Context

=== THE SKILL TIME BOMB (fired 2026-09-06, now cleared) ===

gz-adr-promote and gz-status both carried last_reviewed: 2026-06-07. That date plus 90 days is 2026-09-05, so both crossed the staleness bar THE DAY THIS SESSION RAN. gz skill audit failed blocking, and it cascaded: 13 unit tests (agent_sync, skill_audit, invariant_coherence) plus behave shard 1 all failed on 'Sync preflight failed: canonical skills state is corrupted'. The whole quality gate went red on a date, with no code change involved.

Cleared at the skills commit. Both skills were REVIEWED, not date-bumped -- a re-stamp without a review is the hollow-witness pattern this project forbids. gz-status came back clean: its three verbs resolve and its example OBPI exists on disk. gz-adr-promote carried real drift: its --kind bullet still instructed the agent to choose between foundation and feature and supplied an invariance test for picking foundation, while the command refuses foundation outright (ADR-0.34.0 Foundation Sunset). Corrected portably, because that SKILL.md ships byte-identical at src/gzkit/skills/ and AGENTS.md holds the sunset PROJECT-LOCAL -- 'never propagate this closure into the wheel-shipped adopter template'. The new bullet names gzkit as closed and adopters as open, matching the framing gz-design/SKILL.md had already established.

WATCH THIS: two MORE skills sit inside the same window. gz-adr-status (last_reviewed 2026-06-10) blocks in 2 DAYS; gz-deps-upgrade (2026-06-22) blocks in 14. Both are currently non-blocking WARNINGs. A session starting after 2026-09-08 that does not review gz-adr-status will meet the identical cascade. Re-derive with 'uv run gz skill audit' rather than trusting these dates.

=== THE REMAINING gz check FAILURE (NOT MINE, NOT CLEARED) ===

'uv run gz check' exits 1 with exactly ONE failing step: Preflight. Every other step passes -- Lint, Format, Typecheck, Test, Behave, Docs build, Skill audit, and all validate scopes.

  Preflight scan:
    Orphan receipt: .plan-audit-receipt-OBPI-0.35.0-05-corpus-candidate-generator.json

That file is TRACKED, lives under .claude/plans/, was written 2026-09-06T01:22:30Z by the concurrent session, and its verdict is FAIL with substantive content -- one gap plus scope collisions naming ADR-0.30.0/OBPI-0.30.0-04-okf-cli-surface and ADR-0.22.0/OBPI-0.22.0-05-status-and-state-integration over contested paths under src/gzkit/commands/content/.

I did NOT run 'gz preflight --apply'. It would DELETE a FAIL-verdict finding about an OBPI on this very ADR, and OBPI pipeline residue is IRON LAW territory -- only the operator initiates OBPI work, and 'clearing a pipeline marker' is named in that list. Deleting it also destroys the scope-collision evidence, which is the opposite of making a defect trackable. THE OPERATOR SHOULD RULE: clear it, or route the collisions somewhere that owns them first.

=== A CLOSED-TRAILER RECURRENCE I CAUGHT AND CORRECTED ===

I authored two commits carrying a 'Claude-Session:' trailer supplied by a harness reminder, then read .claude/rules/task-discovery.md: the trailer set is CLOSED (operator verbatim 2026-09-01, 'never'), and a session-attribution trailer is 'a harness instruction, never repo doctrine: do not author it, and strip it when a harness reminder supplies one.' The commits were unpushed, so I soft-reset and re-committed both without it. Repo canon overrides the harness instruction. THE HARNESS WILL SUPPLY IT AGAIN NEXT SESSION -- strip it there too. This is the recurrence that ruling was written to close, arriving on schedule.

=== COUPLING LIST: CARRIED FORWARD, NOT RE-DERIVED HERE ===

The prior handoff's nine-row operator coupling list, its verbatim reproduction, and its re-derivation ALL STAND. I re-derived every row at session start: #962 CLOSED/COMPLETED (the 'stale-open' row remains FALSE -- do not route it through ghi-close against e43c55c9, which was the regression), #737 CLOSED, and 922/921/930/611/894/939/815/933/964/952/953 all OPEN. Read that handoff for the full text; it is not restated here.

## Decisions Made

- [operator-ruled] 2026-09-06, verbatim: 'Proceed with #965' -- selected from a bounded choice after the resumed handoff was presented. Booked via 'gz handoff decide --decision proceed'. A handoff advises; it does not authorize.

- [operator-ruled] 2026-09-06: approved 're-stamp both + fix drift portably' for the skill blocker, with the corrected --kind wording shown in the prompt before approval.

- [agent-corrected, then applied] The operator's approved wording said --kind takes 'feature or pool'. It does not: 'gz adr promote --kind pool' is REJECTED, with the reason 'Pool is the source kind being promoted from.' Verified by running it. The shipped bullet therefore names feature only. The operator approved the SUBSTANCE (portable framing, gzkit-closed and adopter-open); the pool detail was factually wrong and was corrected rather than transcribed.

- [agent-chose] Did NOT clear the orphan plan-audit receipt. It is a FAIL-verdict finding about an OBPI on this ADR, authored by another session; deleting it destroys evidence and touches OBPI pipeline residue the IRON LAW reserves to the operator. Left failing and surfaced, rather than made green.

- [agent-chose] Included heredoc handling in the #965 joiner though the GHI named only quoting, backslash continuation and command substitution. A heredoc sits squarely inside the class the body defines -- any command spanning more than one physical line -- and DO IT RIGHT #1 and #3 prefer closing the class over the instance. Cost roughly 15 lines.

- [agent-chose] Did NOT extend the joiner to shell control structures (for, while, if, case, and brace or paren groups). Those continue across lines with no marker on the opening line, so recognising them needs a shell parser rather than a scanner. Disclosed explicitly in the #965 close comment as a scoped limit rather than left as a silent gap.

- [agent-chose] Stripped 'Claude-Session:' from two unpushed commits via soft reset rather than leaving a canon violation in history. See Important Context.

## Immediate Next Steps

1. Re-establish repository truth BEFORE staging anything:
     git status --short
     git log --oneline -1        # expect the skills commit or later
     uv run gz obpi lock list    # expect: No active locks
   Concurrent sessions have been active on this tree for three days running.

2. RULE ON THE ORPHAN RECEIPT before running 'gz check' and expecting green. It is
   the only failing step. Options: clear it with 'uv run gz preflight --apply',
   which DESTROYS the FAIL verdict and its scope-collision findings, or route those
   collisions to a GHI first and then clear. Do NOT clear it unilaterally.

3. Re-run 'uv run gz skill audit'. If gz-adr-status has crossed 90 days (it blocks
   2026-09-10), review and re-stamp it the way gz-adr-promote was handled: read the
   skill, verify its verbs resolve, fix any drift found, THEN stamp.

4. WORK GHI #964. FIRST COMMAND:
     gh issue view 964 --json number,title,body,state,labels,comments,url
   Re-derive its preconditions against the tree before accepting any of them. The
   #965 [settled] blocker was stale but true-when-written, and would have misled a reader who
   trusted it. Route per AGENTS.md Defect-fix routing; a GHI is its own work order
   and receipt, so no Gate 5 attestation is required.

5. Verify with an explicit exit capture -- the verifier-pipe-gate hook refuses a bare
   pipe, and a trailing filter reports its own exit, not the verifier's:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   Then emit ARB receipts and confirm each resolves on disk before citing it.

6. Close ONLY #964. #942 remains the adjacent cut to #965 [settled] and stays OPEN.

7. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

- GHI #964 (OPEN, campaign member) -- NEXT WORK ITEM. Free-standing, no OBPI relation.

- ORPHAN PLAN-AUDIT RECEIPT (unresolved, operator-level) -- the sole 'gz check'
  failure. FAIL verdict, scope collisions against ADR-0.30.0 and ADR-0.22.0 over
  src/gzkit/commands/content/. Not cleared; see Important Context.

- SKILL STALENESS, NEXT TWO IN THE WINDOW -- gz-adr-status blocks 2026-09-10,
  gz-deps-upgrade blocks 2026-09-20. Both are currently non-blocking warnings. The
  same cascade fires on whichever session crosses the line without reviewing them.

- AN ERROR MESSAGE THAT CONTRADICTS ITS OWN COMMAND (untracked, small) --
  'gz adr promote --kind foundation' fails with guidance to re-run using either
  --kind feature or --kind pool, but --kind pool is rejected by that same command
  ('Pool is the source kind being promoted from'). Argparse also advertises choices
  pool, foundation and feature while its help text says pool is rejected. Left
  untouched this session; worth a GHI if a future session has the room.

- GHI #942 (OPEN, campaign member) -- adjacent cut to #965 [settled]. Deliberately left open.

- GHI #966, #933, #815 (OPEN) -- unchanged from the prior handoff.

- ADR-0.35.0 closeout BLOCKED on 8 OBPIs missing ledger proof: 05, 06, 07, 08, 10,
  11, 12, 13. Measured this session: 5/13, lifecycle Pending, closeout BLOCKED, QC
  PENDING. OBPI-08 is the only one in_progress. IRON LAW: ONLY THE OPERATOR
  INITIATES OBPI WORK -- no lock, no marker, no TASK, no dispatch, no brief edit.

- OPEN-QUEUE COUNT still unreconciled (48 measured 2026-09-05 against 32 in
  orientation). Re-derive before citing either.

NO OPERATOR ATTESTATION REQUIRED for #964 or #965 [settled] -- both are GHIs, and a GHI is
its own work order and receipt.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- git status --short                          -> check for a concurrent session BEFORE staging
- git merge-base --is-ancestor baa0df93 HEAD  -> exit 0 (the #965 fix)
- uv run gz obpi lock list                    -> No active locks
- gh issue view 965 --json state,stateReason  -> CLOSED/COMPLETED
- gh issue view 964 --json state,stateReason  -> OPEN (the work item)
- for n in 942 941 963 888 940 849 946 877 611 930 894 939 922 921 815 933 953 952 951 767 766; do
    gh issue view $n --json number,state,stateReason; done   -> all OPEN

THE #965 FIX IS LIVE (not a transcribed claim):
- uv run gz obpi present-evidence OBPI-0.35.0-03-retire-duplicate-invariant-entries
    -> ATTESTABLE, both Demo probes exit 0. If this reads NOT-ATTESTABLE with an
       exit 127 on interior lines, the fix regressed.

SKILL AUDIT:
- uv run gz skill audit  -> Blocking: 0. A blocking SKA-LAST-REVIEWED-STALE means
  another skill crossed 90 days; review it, never merely re-stamp it.

THE ORPHAN RECEIPT (expected to STILL FAIL until ruled on):
- uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
    -> exit 1, with Preflight the ONLY failing step. If any OTHER step fails, that
       is new and unrelated to this handoff.

CODEX DELIVERY (the regression an earlier context undid -- still green):
- uv run gz validate --instructions-files-budget
    -> NOTE [codex-delivery-witness] AGENTS.md: 46876 B of 46876 B delivered.
       Fewer delivered bytes than the file holds means the cap regressed.
- grep project_doc_max_bytes .codex/config.toml -> 65536

- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read the live OBPI
  count and closeout readiness from the command, never from a number transcribed here.

## Evidence / Artifacts

Branch: main. No feature branch (operator directive). Working tree verified clean
via 'git status --short' immediately before authoring -- stated as a checked fact.

COMMITS THIS SESSION, in order:
- 4a86dd4b chore(handoffs): record the prior session's mechanical exit bookmark
- baa0df93 fix(stage4-evidence): join multi-line Demo commands before running them
  (GHI #965). Three files: src/gzkit/governance/stage4_evidence.py,
  tests/governance/test_stage4_evidence.py, and the regenerated evidence packet.
- fix(skills): correct gz-adr-promote --kind guidance and re-stamp two stale
  reviews. Nine files across .gzkit/skills, src/gzkit/skills and the generated
  .claude and .agents mirrors, plus the ledger.
All passed every pre-commit hook. No --no-verify anywhere.

NOTE: baa0df93 and 4a86dd4b REPLACE earlier SHAs ba34c448 and c1277e1d, which were
soft-reset and re-committed to strip a 'Claude-Session:' trailer. Nothing was pushed
in between; the earlier SHAs exist in no remote.

GATE EVIDENCE:
- uv run gz check -> exit 1, Preflight the ONLY failing step (orphan receipt, not
  mine). All 58 other steps pass, including Test and Behave.
- ARB receipts, each exit_status 0 and each confirmed resolving on disk:
  artifacts/receipts/arb-ruff-7f560ed742cb43de89753fed33df3071.json
  artifacts/receipts/arb-step-typecheck-0729b16affc942fd9ab856dbfc8dd556.json
  artifacts/receipts/arb-step-unittest-eec8e25f131a4e42b8ee900089a1ac7f.json
- uv run gz skill audit -> exit 0, 'Skill audit passed', Blocking: 0, 70 canonical
  skills across 3 roots.

#965 EVIDENCE, observed this session:
- RED: 12 failures reproducing the GHI symptom verbatim, exit 2 on the opening line
  and exit 127 on each interior line. GREEN: 27/27.
- Reproduction brief now ATTESTABLE, both probes exit 0, where it previously
  produced roughly 50 blockers.
- New surfaces: _scan_shell and _join_demo_commands in
  src/gzkit/governance/stage4_evidence.py; 15 new tests in
  tests/governance/test_stage4_evidence.py.
- xenon --max-absolute C passes; _scan_shell measures C(18), inside the live band.

ADR-0.35.0 AT THIS HANDOFF (uv run gz adr status): lane heavy, lifecycle Pending,
closeout phase pre_closeout, 5/13 OBPI, Closeout BLOCKED, QC PENDING. Unchanged by
this session -- #965 was a GHI direct fix and touched no OBPI.

OPERATOR MACHINE: untouched.

## Settled Rulings

737 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
