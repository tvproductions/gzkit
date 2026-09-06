---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T04:36:08Z'
agent: claude-code-cd687e4f
session_id: session_01HyRu7YBa3W2XpUsUFD1US1
continues_from: .gzkit/handoffs/20260906T012722Z-codex-cap-corrected-962-reclosed-965-next.md
---

## Current State Summary

NEXT WORK ITEM: GHI #965 -- "obpi present-evidence: multi-line Demo command is split
into per-line commands". OPEN, unblocked, direct-fix shaped, ~30 lines.

This handoff continues 20260906T012722Z-codex-cap-corrected-962-reclosed-965-next.md
and carries forward every retraction it recorded. Nothing in it is withdrawn.

It adds one thing that document did not have: THE OPERATOR'S COUPLING LIST for the
ADR-0.35.0 campaign, supplied 2026-09-06 and reproduced VERBATIM in Important
Context, with a re-derivation of every row against live GitHub state seated beside
it -- never in place of it.

TWO ROWS OF THAT LIST ARE FALSE AS WRITTEN. They are preserved unedited because the
operator's words pass through unchanged; the re-derivation is where the correction
lives. A future reader who acts on the list without reading the re-derivation will
re-walk the exact regression this campaign spent two contexts undoing. Read both.

CAMPAIGN: 1 of 24 closed (#962). 23 remain, order unchanged:
965, 964, 942, 941, 963, 888, 940, 849, 946, 877, 611, 930, 894, 939, 922, 921,
815, 933, 953, 952, 951, 767, 766.

#965 is NOT ADR-scoped. This handoff carries the ADR-0.35.0 id so `gz handoff
resume --adr` finds it, but #965's fix touches stage4_evidence.py and belongs to no
OBPI. Do not sequence it inside ADR-0.35.0's work.

## Important Context

=== OPERATOR'S COUPLING LIST, VERBATIM (2026-09-06) ===

Reproduced exactly as supplied. Do not edit these lines; corrections live in the
re-derivation below (AGENTS.md § OPERATOR ECONOMY OF EFFORT #3 -- operator verbatim
phrasing is preserved; the agent's role is to seat it correctly, not rewrite it).

  #922 and #921: direct checklist obligations requiring OBPI-11 and OBPI-12 briefs.
  #930, #611, and #894: must be resolved or sequenced before OBPI-08 resumes.
  #939: decide before OBPI-10 starts.
  #815 and #933: couple directly to OBPI-13.
  #965: its “wait until OBPI-03 lands” condition is now satisfied, so it is ready for direct repair.
  #964: worth repairing before another corrected Step-4b history encounters precomplete.
  #962: stale-open; its fix is already committed at e43c55c9, so it should go through ghi-close.
  #737 is already closed, although gz adr status still displays it beside OBPI-10.
  #952 and #953 remain real ledger-security residuals, but were explicitly bounded out of the completed OBPI-04/03 claims.

=== RE-DERIVATION AGAINST LIVE STATE (2026-09-06, gh issue view per row) ===

#922 OPEN, #921 OPEN -- HOLDS, with one update the list predates. The briefs the row
  calls for NOW EXIST: OBPI-0.35.0-11-corpus-shape-witness and
  OBPI-0.35.0-12-rules-corpus-onboarding, landed 2026-09-05 at c64678e1, status
  Draft, never worked. `gz adr status` confirms the coupling directly, rendering
  "[tracked defects: GHI-922]" on OBPI-11 and "[tracked defects: GHI-921]" on
  OBPI-12. So the AUTHORING obligation is discharged; the WORK is not.

#930 OPEN, #611 OPEN, #894 OPEN -- HOLDS. OBPI-0.35.0-08-remember-post-append-advisory
  is the only OBPI on this ADR in state in_progress (brief Draft), so "before OBPI-08
  resumes" is live rather than hypothetical. IRON LAW applies to resuming it.

#939 OPEN -- HOLDS. OBPI-0.35.0-10 is pending/draft; nothing has started.

#815 OPEN/REOPENED, #933 OPEN -- HOLDS BUT HALVED for #815. Its DELIVERY arm was
  fixed 2026-09-05 at e702060e and is now observed green by two independent
  witnesses. What remains is the CONTENT arm -- whether AGENTS.md should be shorter,
  and whether must-survive ordering should hold under ANY cap rather than the one
  currently configured. That second question is exactly OBPI-0.35.0-13's subject and
  its premise still stands: an adopter on a default cap, or in a directory they have
  not trusted, gets no project-local config at all. #933 is unchanged.

#965 OPEN -- CONDITION SATISFIED, BUT THE ROW MIS-DESCRIBES WHY, AND THE DIFFERENCE
  MATTERS. Every other row above states a CONTENT dependency: the GHI's substance
  must be settled for that OBPI's work. #965's blocker was not that. Verbatim from
  its only comment (2026-09-05T19:25:32Z):
    "src/gzkit/** is a Denied Path of the OBPI whose pipeline surfaced this
     (OBPI-0.35.0-03, marker active at Stage 4), so the fix cannot land in that
     transaction."
  That is a WRITE-FENCE ON AN ACTIVE PIPELINE TRANSACTION. #965 fixes multi-line
  Demo parsing in stage4_evidence.py; OBPI-0.35.0-03 retires duplicate invariant
  entries. They share nothing but the accident of one surfacing the other. #965
  became repairable when that transaction ENDED, not when OBPI-03 LANDED -- the two
  coincided, which is why the row reads as correct. Filing it beside "#922 ->
  OBPI-11" invites the next session to sequence it inside ADR-0.35.0. It is free-
  standing. Its sibling row for #964 is the tell: same category, described with no
  OBPI relation at all.

#964 OPEN -- HOLDS. No change.

#962 -- FALSE IN BOTH HALVES. It is NOT stale-open: CLOSED/COMPLETED 2026-09-05.
  And its fix is NOT e43c55c9 -- THAT COMMIT WAS THE REGRESSION. e43c55c9 lowered
  the Codex project_doc_max_bytes cap from 65536 to Codex's own 32768 default on a
  finding since disproved by measurement, re-creating the truncation GHI #815 was
  filed to stop; for about a day 14108 B of AGENTS.md, the IRON LAW included,
  reached no Codex session. The real fix is e702060e (2026-09-05), which restored
  65536, swept the retracted claim from eight surfaces, re-scored advisory-scorecard
  row 58c, and landed an observed-delivery witness. #962 was reopened, corrected and
  re-closed on that commit. DO NOT ACT ON THIS ROW. Routing it "through ghi-close"
  against e43c55c9 would re-close it on the regression.

#737 -- HOLDS, and is now tracked. CLOSED/COMPLETED 2026-08-03, still rendered by
  `gz adr status` beside OBPI-0.35.0-10 as "[tracked defects: GHI-737]". The cause
  was measured 2026-09-05: status_obpi_inspect.py reads a tracked defect's state
  from a literal (open)/(closed) token authored into the brief's prose, and
  OBPI-0.35.0-10's line carries none, so state resolves to "unknown" and renders
  bare -- indistinguishable from live. No live-state resolver exists in that module.
  FILED AS GHI #966, open, cross-linked to sibling #933. The list spotted the
  symptom; #966 owns the cause.

#952 OPEN, #953 OPEN -- HOLDS. Not re-investigated this context; the bounded-out
  claim is carried forward from the operator's own framing and was not re-derived
  against the OBPI-04/03 completion records. Treat as unverified rather than
  confirmed.

=== READING RULE FOR THIS LIST ===

Both false rows were TRUE WHEN WRITTEN and went stale without a freshness signal --
the same decay that produced the three retractions in the superseded handoff. The
list is a dated snapshot, never live state. AGENTS.md § governance-core:
"A value written in a Markdown doc is ILLUSTRATIVE, never authoritative." Re-derive
every row with `gh issue view <N> --json state,stateReason` before acting on it.

## Decisions Made

- [operator-ruled] 2026-09-06, verbatim: "write 965 to a handoff, this list should be
  there too" -- followed by the nine-row coupling list. This handoff is that.

- [agent-chose] Reproduced the list VERBATIM and seated the re-derivation beside it
  rather than editing the rows. AGENTS.md § OPERATOR ECONOMY OF EFFORT #3: operator
  phrasing passes through unchanged; the agent seats it correctly, never rewrites it.
  Silently "fixing" the #962 row would have destroyed the evidence that the row
  existed and was acted on -- and the whole lesson of the last two contexts is that a
  claim carried forward without a freshness signal is how the regression happened.

- [agent-chose] Did NOT drop the two false rows. A handoff that quietly omits what a
  prior surface asserted teaches the next reader nothing about why to re-derive.

- [operator-ruled] 2026-09-06, verbatim: "its fine" -- closing the question of the
  concurrent session's ADR-0.35.0 work absorbed into 7ff97fd1 by `git add -A`.
  Provenance recorded at b69de3d6; no history rewritten.

- [carried forward, unchanged] Every decision in
  20260906T012722Z-codex-cap-corrected-962-reclosed-965-next.md stands: the three
  retractions, the trust mechanism, the regression chain, the row-58c re-score, the
  cap at 65536, and the IRON LAW position that no OBPI work was initiated.

- [agent-chose] Scoped this handoff to ADR-0.35.0 so `gz handoff resume --adr` finds
  it, while stating plainly that #965 itself belongs to no OBPI. The alternative --
  omitting --adr -- would have made the campaign's own resume path miss it.

- [agent-chose] Left #952/#953's "bounded out of the completed OBPI-04/03 claims"
  unverified rather than asserting it. It came from the operator's framing and was
  not re-derived against the completion records this context; claiming otherwise
  would manufacture a verification that did not happen.

## Immediate Next Steps

1. Re-establish repository truth BEFORE staging anything:
     git status --short          # another session may be writing; check first
     git log --oneline -1        # expect b69de3d6 or later
     uv run gz obpi lock list    # expect: No active locks
   7ff97fd1 absorbed 14 files of a concurrent session's work because `git add -A`
   ran without this check. Stage selectively on ceremony commits.

2. Re-derive the coupling list in Important Context. Do not act on any row you have
   not re-run `gh issue view <N> --json state,stateReason` against. TWO ROWS ARE
   FALSE AS WRITTEN -- #962 [settled] especially: routing it "through ghi-close" against
   e43c55c9 would re-close it on the regression commit.

3. Read `.gzkit/skills/ghi-close/SKILL.md` before any command or edit.

4. WORK GHI #965. FIRST COMMAND:
     gh issue view 965 --json number,title,body,state,labels,comments,url

   THE DEFECT: `extract_demo_commands`
   (src/gzkit/governance/stage4_evidence.py:86-114) returns every "non-empty,
   non-comment line" of the ## Demo fence, and `_run_demo` (:123) executes each one
   with shell=True. A command spanning physical lines -- a quoted
   `uv run python -c 'PROGRAM'`, a backslash continuation, a multi-line command
   substitution -- is not
   modelled, so the fence shatters at line boundaries. Observed: ~50 blockers from
   two probes, exit 2 on the opening line and exit 127 on each interior line, while
   both probes exit 0 when run as written.

   WHY IT MATTERS: the tool reports NOT-ATTESTABLE for a state that is green, and it
   does so precisely for the briefs whose Demo is MOST assert-shaped -- which is the
   shape stage4_evidence.py:19-22 itself prescribes ("MUST be assert-shaped -- exit
   non-zero on a bad state"). The Stage-4a packet is the artifact the Step-4b
   adversary is handed (`gz-obpi-pipeline` SKILL.md § Step 4b dispatch contract), so
   the failure lands on the review gate.

   THE FIX: a quote/continuation-aware line joiner in `extract_demo_commands`, plus a
   unit test driving a quoted multi-line `python -c` probe. ~30 lines.
   Reproduction brief: OBPI-0.35.0-03-retire-duplicate-invariant-entries.md § Demo
   (it already carries `<!-- gz-validate-skip: command-shape -->` for this shape).
   Covering tests live in tests/governance/test_stage4_evidence.py.

   ROUTING, computed: 1 module + 1 test file, single named surface, defect surfaced
   in flight, unit-testable without a new BDD scenario -> DIRECT FIX. No live brief
   owns the surface (both matches are terminal: OBPI-0.0.65-02, OBPI-0.35.0-03).
   Re-run the ownership grep on the SYMBOL anyway before routing.

   TDD IS NOT OPTIONAL HERE: write the failing test against a multi-line probe FIRST.
   A joiner is exactly the kind of change that can be made to pass by reshaping the
   test instead of the parser.

5. Verify with an explicit exit capture -- the verifier-pipe-gate hook refuses a bare
   pipe and PIPESTATUS is unreliable after an intermediate command:
     uv run gz check > <file> 2>&1; echo "REAL EXIT: $?"
   Then emit ARB receipts (arb ruff / arb typecheck / arb step unittest) and confirm
   each resolves on disk before citing it.

6. Close ONLY #965. #942 is its adjacent cut (hand-pasted 4a evidence vs. this one's
   tool-generated packet) -- if the fix touches it, leave #942 OPEN and record the
   shared evidence for independent verification.

7. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

NO BLOCKER OUTSTANDING for #965 or the campaign.

- GHI #966 (OPEN, not a campaign member) -- adr status renders a closed GHI as a live
  tracked defect; owns the cause the list's #737 [settled] row spotted. Unblocked, direct-fix
  shaped, cross-linked to #933. Do NOT pull it ahead of campaign order without a
  ruling.

- GHI #815 (OPEN/REOPENED, campaign member) -- delivery arm fixed and observed; only
  the content arm remains, and it now stands on its own merits rather than being
  forced by an unraisable cap.

- ADR-0.35.0 closeout BLOCKED on 8 OBPIs missing ledger proof of completion:
  05, 06, 07, 08, 10, 11, 12, 13. OBPI-08 is the only one in_progress; 11 and 12 are
  freshly authored Drafts. IRON LAW: ONLY THE OPERATOR INITIATES OBPI WORK -- no
  lock, no marker, no TASK, no implementer dispatch, no brief edit. #965 is a GHI
  direct fix and is NOT OBPI work.

- STALE ANNOTATION VISIBLE RIGHT NOW: `gz adr status` renders "[tracked defects:
  GHI-737]" on OBPI-0.35.0-10 though #737 [settled] closed 2026-08-03. That is #966's
  reproduction case, not a live blocker.

- CONCURRENT SESSIONS ARE ACTIVE ON THIS TREE. Two episodes in two days (2026-09-05
  briefs 11/12; 2026-09-06 00:57-01:18 evaluation + reconcile + plan-review). Check
  `git status` before staging. Operator has ruled both fine.

- OPEN-QUEUE COUNT: 48 measured 2026-09-05, against 32 in session orientation and
  campaign prose. Still unreconciled; re-derive before citing either.

- #952/#953's "bounded out of the completed OBPI-04/03 claims" is UNVERIFIED -- it
  came from the operator's framing and was not checked against the completion
  records. Verify before relying on it.

NO OPERATOR ATTESTATION REQUIRED. #965 and #966 are GHIs; operator canon: a GHI is
its own work order and receipt and needs no Gate 5.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- git status --short                       -> check for a concurrent session BEFORE staging
- git merge-base --is-ancestor e702060e HEAD -> exit 0 (the real #962 fix)
- uv run gz obpi lock list                 -> No active locks

COUPLING LIST -- re-derive every row, never transcribe:
- gh issue view 965 --json state,stateReason  -> OPEN   (the work item)
- gh issue view 962 --json state,stateReason  -> CLOSED/COMPLETED
    If this reads OPEN, someone acted on the false list row. Read #962's close
    comment before touching anything.
- gh issue view 737 --json state,closedAt     -> CLOSED, closed 2026-08-03
- gh issue view 966 --json state              -> OPEN
- for n in 922 921 930 611 894 939 815 933 964 952 953; do
    gh issue view $n --json number,state,stateReason; done   -> all OPEN

CODEX DELIVERY -- the regression this campaign undid:
- uv run gz validate --instructions-files-budget  -> MUST report BOTH:
    NOTE [surface-delivery-witness] AGENTS.md: <rendered> B rendered against the
      codex delivery cap 65536 B -- <n> B of headroom.
    NOTE [codex-delivery-witness] AGENTS.md: <n> B of <n> B delivered by Codex --
      the whole surface reaches the agent.
  "delivery unobserved" means the witness could not run (codex absent, or this
  directory not trusted). That is NOT a pass and NOT a regression -- re-derive.
  FEWER DELIVERED BYTES THAN THE FILE HOLDS means the cap regressed: campaign-
  blocking, read GHI #962 before proceeding.
- grep project_doc_max_bytes .codex/config.toml   -> 65536

#965 TARGET SURFACE, before editing:
- sed -n '86,114p' src/gzkit/governance/stage4_evidence.py  -> extract_demo_commands
  still appends per-line with no quote/continuation handling
- ls tests/governance/test_stage4_evidence.py               -> exists
- grep -rln "stage4_evidence" docs/design/adr/*/*/obpis/*.md -> both hits terminal
  (OBPI-0.0.65-02 attested_completed, OBPI-0.35.0-03 Completed). A LIVE hit makes
  routing operator-level -- stop and surface it.

- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read the live OBPI
  count and closeout readiness from the command; never from a number transcribed
  into this document.

## Evidence / Artifacts

Branch: main. No feature branch (operator directive).
HEAD at authoring: b69de3d6. Working tree: verified clean via `git status --short`
immediately before authoring -- stated as a checked fact this time, because the
previous handoff asserted it without checking and was wrong (corrected at b69de3d6).

COMMITS THIS SESSION, in order:
- e702060e fix(codex-cap-doctrine): gzkit does set the Codex cap -- restore 65536 and
  witness delivery (GHI #962). 23 files, +690/-66.
- 7ff97fd1 chore(handoffs): supersede the 20260905T205745Z handoff -- three claims
  retracted. Absorbed 14 files of a concurrent session's ADR-0.35.0 work via
  `git add -A`; operator ruled "its fine".
- b69de3d6 chore(handoffs): record the provenance 7ff97fd1's message omitted.
All passed every pre-commit hook. No --no-verify anywhere in this campaign.

GITHUB ACTIONS THIS SESSION:
- #962 reopened with the correction, then closed completed citing e702060e
- #815 comment retracting its standing "never raise the cap" guidance
- #966 created (defect, runtime) + routing note
- #933 cross-link comment naming the sibling-cut relationship

GATE EVIDENCE (from e702060e): uv run gz check exit 0, "All checks passed",
9437 tests OK (skipped=4). ARB receipts, each exit_status 0 and resolved on disk:
- artifacts/receipts/arb-ruff-727ab139a52a4bab81cb1ce8151b04ba.json
- artifacts/receipts/arb-step-typecheck-ae09017a5a66430697f2aba3145daef3.json
- artifacts/receipts/arb-step-unittest-6d0a642089e04f1794ff7241879cc574.json

ADR-0.35.0 AT THIS HANDOFF (uv run gz adr status): lane heavy, lifecycle Pending,
closeout phase pre_closeout, 5/13 OBPI, Closeout BLOCKED, QC PENDING. OBPI-08 in
state in_progress; 11 and 12 Draft.

#965 EVIDENCE, read this context rather than recalled:
- src/gzkit/governance/stage4_evidence.py:86-114 `extract_demo_commands` -- appends
  each stripped non-comment line; no quote or continuation state.
- src/gzkit/governance/stage4_evidence.py:123 `_run_demo` -- executes each returned
  string with shell=True.
- Only comment on #965 (2026-09-05T19:25:32Z) is the write-fence blocker, verbatim
  in Important Context. It is NOT a content dependency on OBPI-0.35.0-03.

OPERATOR MACHINE: untouched. ~/.codex/config.toml is byte-identical to how this
session found it; the delivery route is the repo's own .codex/config.toml and needs
nothing outside the repository.

## Settled Rulings

735 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
