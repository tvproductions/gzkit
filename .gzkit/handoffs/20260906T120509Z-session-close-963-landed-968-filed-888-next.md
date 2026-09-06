---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T12:05:09Z'
agent: claude-code-2a5779f2
session_id: 2a5779f2-39e4-4c24-9d36-646ae24fb112
continues_from: .gzkit/handoffs/20260906T113734Z-session-close-942-941-967-landed-cli-rule-carved-963-next.md
---

## Current State Summary

SESSION-CLOSE. FINAL STATE: HEAD 13084490, tree clean, nothing unpushed, uv run gz check exit 0, gz preflight clean, gz skill audit Blocking 0, no active locks. FOUR COMMITS since the last handoff: df1f7b77 (#942 RED-run escape negative control), df0c2387 (#963 mutation witness), a0b12f1d (#968 reviewer descriptions), 13084490 (corrects a wrong claim in the prior handoff). #963 CLOSED; #968 FILED and OPEN with a blocker. Campaign: 7 of 24 closed (#962, #965, #964, #942, #941, #963, plus #967 which is not a campaign member). Remaining campaign order: 888, 940, 849, 946, 877, 611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766. NEXT WORK ITEM: GHI #888, "req_kind_support: SUPPORT proof events are substring-scanned, so a denial reads as a citation". Open GHI queue measured 30. **CORRECTED 2026-09-06T13:09:18Z: the count was 45, not 30.** Re-derived by three independent methods (`gh issue list`, `gh search issues`, the REST API), all agreeing. ZERO issues were created and ZERO closed between this handoff's 12:05:09Z timestamp and that 13:09:18Z measurement, so 45 was also the count when this line was written — the figure was wrong when authored, never stale. (44 open as of 13:53Z, after #888 closed.) The instruction to re-derive before citing is what caught it; keep it.

## Important Context

=== THE MUTATION-SWEEP CONTRACT CHANGED. READ THIS BEFORE RUNNING ONE ===

A failing mutant run does NOT prove the mutation took effect or that a relevant
assertion caught it. Import errors, invalid mutations, unrelated failures and harness
failures all produce FALSE KILLS; a reported survivor can equally conceal ineffective
mutation or inadequate test execution. The prior handoff argued the opposite and has
been corrected in place (13084490).

Use gzkit.mutation_witness.run_mutation_sweep. It verifies baseline, mutation
activation, per-mutant PYTHONPYCACHEPREFIX isolation, and failure cause, and returns
FOUR outcomes:

  killed / survived   claims about the GUARD
  invalid             target absent, no-op edit, mutant does not import
  inconclusive        red baseline, no named failing test, or no EXPECTED test failed

Only a sweep whose is_conclusive is true may be cited as coverage evidence. Doctrine:
.gzkit/rules/tests.md § Mutation-sweep integrity (rule 0.20.0). Do NOT hand-roll a
shell loop — that is the shape that produced GHI #963's pyc collision.

Pass Mutation(expected_tests=[<covering test>]) whenever you can: without it, ANY failing test
counts as a kill, and the harness cannot force you to name the covering test.

=== THE STAGE-4 PACKET SURFACE CHANGED A THIRD TIME ===

`uv run gz obpi verify-packet <path>` now blocks three things, added in this order
across the session, each because the previous fix opened the next hole:

  1. a pasted line the command did not produce      (fabrication)
  2. a non-zero exit                                 (selective omission)
  3. an emitted non-zero status line the packet omitted   (the ESCAPE for 2)

THE THIRD IS THE ONE TO UNDERSTAND. `; echo "exit $?"` was documented in the skill as
the way to show an honest RED run. It works by moving the status OUT of the process —
the shell then exits 0 because echo succeeded — so the non-zero blocker cannot fire and
the failure survives only as a line of output. A packet appending the probe and omitting
the `exit 1` it printed was VERIFIED. The operator asked for that negative control
explicitly; I had shipped the bypass and documented it.

An elision cannot satisfy it either: the ellipsis marker is for output that cannot
reproduce, never for output you would rather not show.

=== REVIEWER CAPABILITY: THE POLICY IS MIS-SPECIFIED, AND THE FIX IS HALF-BLOCKED ===

Operator ruling: "'read-only' describes permitted effects, not the absence of Bash.
Read-only shell inspection is compatible with independent review; modifying the
implementation is not. Independence comes from separate judgment and evidence."

That retires the argument in #941's close that granting Bash "weakens independence".
It does not.

MEASURED, and this is why the grant did not change: nothing in this repo can express
"read-only Bash". permissions.allow is 0 rules; permissions.deny is 42 rules (6
git-bypass, 36 secret-file Read/Edit) with ZERO restricting writes via Bash; and NO hook
under .claude/hooks/ reads agent identity — the payload keys in use across all of them
are cwd, tool_input, tool_name, transcript_path. So a hook allowlist cannot be scoped to
reviewers, and granting Bash grants the orchestrator's Bash.

Disposition 1 LANDED (a0b12f1d): the persona descriptions now say what is enforced.
Disposition 2 is BLOCKED on a harness capability and is tracked at #968.

=== A FABRICATION FROM EARLIER IN THIS SESSION, ALREADY CORRECTED ===

I cited commit 1c1e5f2b in #941's close comment. No such commit existed; the real SHA is
126c5d09. Corrected by a follow-up comment on the issue and recorded as an insight.
RESOLVE EVERY SHA with `git log -1 --format='%H %s' <sha>` before it enters a close
comment, exactly as ARB receipt ids are confirmed on disk.

=== THE CANON TRAP ===

The harness supplied a 'Claude-Session:' commit trailer again. The trailer set is CLOSED
(.claude/rules/task-discovery.md, operator verbatim 'never'). No commit this session
carries it. IT WILL BE SUPPLIED AGAIN.

## Decisions Made

- [operator-ruled] 2026-09-06, verbatim: 'Proceed with #963, but correct the mutation-testing claim first. A failing mutant run does not prove the mutation took effect or that a relevant assertion caught it. Import errors, invalid mutations, unrelated failures, and harness failures can all produce false kills. A reported survivor can also conceal ineffective mutation or inadequate test execution. Verify the baseline, mutation activation, relevant test execution, and failure cause. Report invalid or inconclusive runs separately from killed and survived mutations.' Implemented as the module's four-way verdict; the prior handoff's wrong claim corrected in place at 13084490.

- [operator-ruled] 2026-09-06, verbatim: 'For #941, "read-only" describes permitted effects, not the absence of Bash. Read-only shell inspection is compatible with independent review; modifying the implementation is not. Independence comes from separate judgment and evidence. Assess the actual required commands and available enforcement before choosing the capability policy.' Assessed and recorded on #941; disposition 1 landed, disposition 2 filed as #968 with a measured blocker.

- [operator-ruled] 2026-09-06, verbatim: 'Finally, #942's explicit RED-run example needs a negative control: appending echo "exit $?" must not permit the packet to omit that exit line and present success again. Prove that case is rejected; documenting the authoring convention alone does not enforce it.' Proved it was NOT rejected, then fixed it (df1f7b77).

- [agent-erred, operator-corrected] I claimed a caught mutant is trustworthy because the suite failed, so the mutation must have taken effect. Wrong, and wrong against evidence in GHI #963's own body, which says the contamination cuts both ways. The correction is now the module's central claim rather than a footnote.

- [agent-erred, self-caught earlier in session] Fabricated SHA 1c1e5f2b in #941's close; real SHA 126c5d09. Corrected on the issue; insight recorded.

- [agent-chose] Four outcomes, not three. `invalid` (target absent, no-op, unimportable) and `inconclusive` (red baseline, no named failing test, no expected test failed) are claims about the RUN; killed/survived are claims about the GUARD. is_conclusive is deliberately NOT killed==len(witnesses) — a sweep may legitimately hold a survivor; what it may not hold, and still be cited, is a row that graded nothing.

- [agent-chose] Reused classify_failure from red_witness rather than restating it. That module already refuses to equate an error-failure with an assertion-failure; this is the same distinction one layer down.

- [agent-chose] NO CLI verb for the mutation sweep. The issue's scope hint offers one; library plus doctrine is what it asked for, and a verb pulls in seven coupled obligations for a surface nothing yet requires. Scorecard row 89 names the receipt-emitting shape as the reclassification trigger — that would also give the doctrine its first witness.

- [agent-chose] Applied #968's disposition 1 immediately rather than filing and waiting. Leaving a known-false persona description in place while filing an issue about it is filing a GHI as a substitute for a fix available now, which ghi-author § Constraints forbids.

- [agent-chose] Did NOT grant reviewers Bash. Not on the independence argument the operator retired, but on a measured one: no surface in this repo can express read-only Bash, so the grant would be unrestricted under a read-only label.

- [agent-chose] Blocked the omitted-status case on OUTPUT content (a standalone `exit N` line the command emitted and the packet did not show) rather than by detecting the echo idiom. Idiom detection misses any rephrasing; the output-side rule catches the concealment however the command was written.

- [agent-chose] Nonzero status lines only. Requiring `exit 0` to be quoted would make ordinary abridgement a blocker and teach authors to route around the check.

## Immediate Next Steps

1. Re-establish repository truth BEFORE staging anything:
     git status --short
     git log --oneline -1        # expect 13084490 or later
     uv run gz obpi lock list    # expect: No active locks

2. Confirm the gate:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"
   Expect exit 0.

3. WORK GHI #888. FIRST COMMAND:
     gh issue view 888 --json number,title,body,state,labels,comments,url
   "req_kind_support: SUPPORT proof events are substring-scanned, so a denial reads as a
   citation". Re-derive every precondition against the tree — three issue bodies this
   session carried stale or imprecise premises (#942 [settled]'s scope hint, #941 [settled]'s gate claim,
   and #963 [settled]'s severity, which its own body understated).

4. TDD, then sweep with the HARNESS, never a shell loop:
     uv run python -c '
     from pathlib import Path
     from gzkit.mutation_witness import Mutation, run_mutation_sweep
     s = run_mutation_sweep(Path("."), Path("src/gzkit/<module>.py"),
         [Mutation(find="<guard>", replace="<broken>", label="<name>",
                   expected_tests=["<covering test>"])],
         ["uv","run","-m","unittest","tests.<module>","-v"])
     print(s.killed, s.survived, s.invalid, s.inconclusive, s.is_conclusive)'
   Cite a sweep only when is_conclusive is true, and disclose invalid/inconclusive rows
   rather than dropping them.

5. Capture exits explicitly. A PreToolUse hook BLOCKS piping a verifier into a filter;
   use `set -o pipefail` or redirect:
     uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"

6. BEFORE any SHA enters a close comment, resolve it:
     git log -1 --format='%H %s' <sha>

7. Close ONLY #888. Leave #968 open unless the operator routes it. Author the next
   campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

- GHI #888 (OPEN, campaign member) -- NEXT WORK ITEM. Nothing blocks it.

- GHI #968 (OPEN, NOT a campaign member) -- filed this session, open WITH A BLOCKER
  comment, not dead-lettered. Reviewer personas declared "read-only" while enforcing "no
  execution"; disposition 1 (say what is enforced) landed at a0b12f1d. Disposition 2
  (permit read-only execution) is blocked on a harness capability that does not exist:
  either agent identity in the PreToolUse payload, or a per-agent permission scope.
  NEXT OPERATOR ACTION named on the issue: pursue disposition 2 upstream, or settle on
  disposition 1 permanently and record the residue -- that the hollow-test detection duty
  AGENTS.md § Operator Doctrine assigns the two-stage review is discharged by the
  ORCHESTRATOR via gzkit.mutation_witness, not by the independent reviewer. That is a real
  narrowing of the duty and is currently implied rather than stated in doctrine.

- PACKET REPLAY RESIDUAL (disclosed, untracked): a generic NON-VERIFIER command piped
  without pipefail still masks its exit status in a Step-4a transcript and is not blocked.
  masked_verifier's scope is recognized verifiers and was deliberately not widened -- a
  stricter local rule on the same subject is how two surfaces fall out of agreement.
  Closing it is a scope decision, not a bug fix.

- MUTATION-SWEEP RESIDUALS (disclosed on #963 [settled]'s close, untracked): the four checks bound
  the RUN, not the mutation SET -- a sweep that omits the guard which matters reports
  conclusive=True and proves nothing about it. And expected_tests is optional, so without
  it any failing test counts as a kill.

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

NO OPERATOR ATTESTATION REQUIRED for #963 [settled] or #968 -- both GHIs, and a GHI is its own work
order and receipt.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- git status --short                          -> clean
- git log --oneline -1                        -> 13084490 or later
- git log --oneline origin/main..HEAD         -> empty
- git merge-base --is-ancestor df1f7b77 HEAD  -> exit 0 (#942 negative control)
- git merge-base --is-ancestor df0c2387 HEAD  -> exit 0 (#963 mutation witness)
- git merge-base --is-ancestor a0b12f1d HEAD  -> exit 0 (#968 disposition 1)
- gh issue view 963 --json state              -> CLOSED/COMPLETED
- gh issue view 968 --json state              -> OPEN (blocked, not dead-lettered)
- gh issue view 888 --json state              -> OPEN (the work item)

THE GATE:
- uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"   -> exit 0
- uv run gz preflight                                     -> Preflight scan: clean
- uv run gz skill audit                                   -> Blocking: 0, Non-blocking: 1
- uv run gz cli audit                                     -> exit 0, 142/142

#942's THIRD GUARD IS LIVE (the escape may not conceal). Temp files only:

  uv run python -c '
import sys, tempfile; sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from gzkit.governance.stage4_packet import verify_packet
td = Path(tempfile.mkdtemp()); p = td/"e.md"
p.write_text("```\n$ python3 -c \"import sys; print(chr(111)); sys.exit(1)\"; echo \"exit $?\"\no\n```\n", encoding="utf-8")
r = verify_packet(Path("."), p)
print("verified:", r.verified, "| exit_status:", r.transcripts[0].exit_status)
print(r.blockers[0][:70] if r.blockers else "NO BLOCKER")
'

  -> verified: False | exit_status: 0
  -> Command emitted a non-zero status the packet does not show

  exit_status 0 with verified False is the point: the shell succeeded because echo did,
  and the failure was caught in the OUTPUT. If this reports verified True, the escape is
  a bypass again.

#963's HARNESS IS LIVE, and it grades itself:

  uv run python -c '
import sys; sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from gzkit.mutation_witness import Mutation, run_mutation_sweep
s = run_mutation_sweep(Path("."), Path("src/gzkit/mutation_witness.py"),
    [Mutation(find="env[\"PYTHONPYCACHEPREFIX\"] = str(pycache_prefix)", replace="pass",
              label="isolation",
              expected_tests=["test_each_mutation_runs_with_its_own_bytecode_cache"])],
    ["uv","run","-m","unittest","tests.test_mutation_witness","-v"])
w = s.witnesses[0]
print(w.outcome, w.failing_tests, "| conclusive:", s.is_conclusive)
'

  -> killed ['test_each_mutation_runs_with_its_own_bytecode_cache'] | conclusive: True

  If this reports SURVIVED, the isolation test has gone hollow again — that exact guard
  survived its first sweep because the test read a recorded field instead of what the
  subprocess saw.

#968's DISPOSITION 1 IS LIVE:
- grep -c "cannot execute commands" .claude/agents/spec-reviewer.md   -> 1
- uv run python -c 'from pathlib import Path; from gzkit.pipeline_dispatch import reviewer_capability; c=reviewer_capability(Path("."),"spec-reviewer"); print(c.tools, c.can_execute)'
    -> ['Read', 'Glob', 'Grep'] False
  can_execute True means the grant changed; the prompt follows automatically, and the
  skill's persona rows plus #968 need updating.

ENFORCEMENT MEASUREMENT (#968's blocker) — re-derive rather than inherit:
- python3 -c "import json; d=json.load(open('.claude/settings.json'))['permissions']; print(len(d.get('allow',[])), len(d.get('deny',[])))"
    -> 0 42
- grep -rl "agent" .claude/hooks/*.py | xargs grep -l "payload" ; -> no hook reads agent identity

CODEX DELIVERY (still green):
- uv run gz validate --instructions-files-budget
    -> NOTE [codex-delivery-witness] AGENTS.md: 46876 B of 46876 B delivered.

## Evidence / Artifacts

Branch: main. No feature branch (operator directive). Tree verified clean and fully pushed
immediately before authoring -- stated as checked facts.

COMMITS SINCE THE PRIOR HANDOFF, in order. Every SHA resolved with git log before being
written here:
- df1f7b77 fix(stage4-packet): the RED-run escape may not conceal the failure (GHI #942)
- df0c2387 fix(mutation-witness): a failing mutant run is not a kill (GHI #963)
- a0b12f1d docs(agents): reviewer descriptions state what is enforced (GHI #968)
- 13084490 chore(handoffs): correct the mutation-testing claim in the 113734Z handoff

All passed every pre-commit hook. No --no-verify. NONE carries a 'Claude-Session:' trailer.

GATE EVIDENCE at this handoff:
- uv run gz check -> exit 0, 'All checks passed'
- uv run gz preflight -> 'Preflight scan: clean'
- uv run gz skill audit -> exit 0, Blocking: 0, Non-blocking: 1
- uv run gz cli audit -> exit 0, 142/142

ARB receipts, each exit_status 0 and confirmed resolving on disk:
  #942 negative control: arb-ruff-a4b2af9c9e7844f79d7198394f15a54c,
    arb-step-typecheck-a8e3f5c2703c4c6e8b3af4e702052215,
    arb-step-unittest-c3ce1af1ae0c40a789cbf9f4a56c3218
  #963: arb-ruff-e37437cad60c446e93dc60174f9895ea,
    arb-step-typecheck-b1c5ad54814a4b8085bdb48db007596b,
    arb-step-unittest-8b99fd0a838749448542b94483b6739b

TEST DELTAS: #942 RED 2 -> GREEN 24/24. #963 RED -> GREEN 10/10.

THE #963 SELF-SWEEP, run under its own four checks (baseline green, source changed,
mutant imports, failure attributed to a NAMED expected test):
  KILLED absent-target / no-op / unimportable / attribution / isolation / baseline
  killed=6 survived=0 invalid=0 inconclusive=0 conclusive=True
Its FIRST run returned SURVIVED for the isolation guard, because that test asserted a
recorded field rather than what the subprocess saw. Replaced with an effect-observing
test; the guard now kills.

MEASUREMENTS TAKEN THIS SESSION (re-derive rather than inherit):
- permissions.allow: 0 rules. permissions.deny: 42 rules -- 6 git-bypass Bash patterns,
  36 secret-file Read/Edit, ZERO restricting writes via Bash.
- No file under .claude/hooks/ reads agent identity; keys in use across all hooks are
  cwd, tool_input, tool_name, transcript_path.
- src/gzkit/pipeline_dispatch.py is a registered entry in data/security_surfaces.json,
  which is why #968 carries the security label.

GITHUB ACTIONS THIS SESSION (second half):
- #963 closed completed citing df0c2387
- #968 created (defect, runtime, security) via /ghi-author with the full Step-0
  pre-flight: two issue queries plus the OBPI-brief ownership grep, every matching brief
  terminal. Left OPEN with a blocker comment naming the next operator action.
- #941 received a capability-assessment comment and a #968 cross-link
- #942's close comment stands; the negative control landed after it and is cited in
  df1f7b77 rather than by amending the close

OPERATOR MACHINE: untouched.

## Settled Rulings

755 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
