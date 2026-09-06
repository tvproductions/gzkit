---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-06T01:27:22Z'
agent: claude-code-cd687e4f
session_id: session_01HyRu7YBa3W2XpUsUFD1US1
continues_from: .gzkit/handoffs/20260905T205745Z-adr-0-35-0-ghi-campaign-962-closed-965-next.md
---

## Current State Summary

CAMPAIGN: ADR-0.35.0 GHI closeout. Context 2 complete.

THIS HANDOFF SUPERSEDES 20260905T205745Z-adr-0-35-0-ghi-campaign-962-closed-965-next.md
AND RETRACTS THREE OF ITS CLAIMS BY NAME. Read section "Important Context" BEFORE
acting on anything carried forward from it. The superseded document is not merely
stale -- three of its statements are the exact inverse of measured truth, and one of
them instructs the next session not to do the thing that turned out to be correct.

GHI #962 was REOPENED, corrected, and re-closed at e702060e. The prior handoff
recorded it closed at b90d0484 with a finding that has since been disproved by
measurement. Its close was not wrong to happen; its REASONING was wrong, and the
commit that reasoning licensed (e43c55c9) was a regression.

GHI #966 filed this context: "adr status: a closed GHI still renders as a live
tracked defect". Not a campaign member; open, unblocked, direct-fix shaped.

CAMPAIGN ACCOUNTING, re-derived against GitHub at this handoff:
Original 24-issue set, operator-declared order:
  Pipeline/evidence reliability: 962, 965, 964, 942, 941, 963, 888, 940, 849, 946, 877
  ADR-0.35.0 obligations/sequencing: 611, 930, 894, 939, 922, 921, 815, 933
  Ledger/session residuals: 953, 952, 951, 767, 766
  Excluded incidentals (operator-named, NOT members): 936, 871, 870, 818, 807, 799

CLOSED (1 of 24): #962 -- disposition FIXED at e702060e. Unchanged count from the
prior handoff; what changed is that the closure is now true.

REMAINING (23), order unchanged: 965, 964, 942, 941, 963, 888, 940, 849, 946, 877,
611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766.

NEXT: #965. Its row in circulating campaign summaries is MIS-TAXONOMISED -- see
Important Context. It is unblocked and always was.

NOT PATCH ADVANCE READY: that requires 24/24, and is 23 closures away.

## Important Context

=== THREE RETRACTIONS FROM THE SUPERSEDED HANDOFF ===

RETRACTED 1 -- superseded handoff lines 171-172, verbatim:
  "That is the exact claim #962 [settled] disproved by measurement. Acting on it
   would re-raise the cap and re-create the false-headroom reading."
The insight it quarantined -- agent-insights.jsonl 2026-09-05T20:34:30Z, scope
ADR-0.35.0-readiness, "Treat Codex project_doc_max_bytes as configurable; a local
32768-byte witness declaration is not an immutable vendor limit" -- was CORRECT.
The prior handoff preserved it while instructing the next session not to act on it.
Acting on it was the fix.

RETRACTED 2 -- same lines: raising the cap does not re-create a false-headroom
reading. The witness now reports 18660 B of headroom and a SECOND, independent
witness confirms the whole surface is delivered. The 2026-09-04 reading was false
headroom because nothing observed delivery; that is now observed.

RETRACTED 3 -- superseded handoff line 179, verbatim:
  "When #815 comes up, the fix is content (getting must-survive canon above the
   32768 cut), never raising the cap."
Raising the cap was legitimate and is what gzkit had already been doing correctly
since 344f7189. A correcting comment is posted on #815 itself.

=== WHY: THE MECHANISM #962 MISSED ===

Codex loads a project-local .codex/config.toml in ANY DIRECTORY THE OPERATOR HAS
TRUSTED, and that file WINS over $CODEX_HOME/config.toml. Codex's own trust prompt,
verbatim from the codex-cli 0.153.4 binary:
  "Do you trust the contents of this directory? Working with untrusted contents
   comes with higher risk of prompt injection. Trusting the directory allows
   project-local config, hooks, and exec policies to load."

#962 inferred non-delivery from `codex doctor` naming a single config source.
Doctor names the GLOBAL config and does not enumerate the project-local overlay.
Its silence was read as absence -- AGENTS.md verbatim: "A search is not a read --
never report that something is absent, undocumented, or unruled on the strength of
keyword queries."

MEASURED 2026-09-05 via `codex debug prompt-input`, trust held constant, varying
only the repo-local value:
  project_doc_max_bytes = 32768  ->  32768 B delivered
  project_doc_max_bytes = 65536  ->  46876 B delivered (whole surface)
  project_doc_max_bytes = 12000  ->  12000 B delivered

=== THE REGRESSION CHAIN -- DO NOT RE-WALK IT ===

344f7189 (GHI #815) set the cap to 65536. IT WORKED.
e43c55c9 lowered it to Codex's 32768 default on #962's false finding, re-creating
  the truncation #815 was filed to stop.
b90d0484 propagated "gzkit has no route to set it" into three more live surfaces
  and scored advisory-scorecard row 58c Judgment with the promotion path
  "genuinely closed rather than merely unbuilt".
e702060e reversed all of it.

For roughly a day, 14108 B of AGENTS.md -- including the IRON LAW -- reached no
Codex session. Noted without claiming causation: on 2026-09-05 a concurrent Codex
session authored OBPI-0.35.0-11 and -12 on its own initiative, and the rule
forbidding exactly that sits in the truncated tail.

=== #965 IS MIS-TAXONOMISED IN CIRCULATING SUMMARIES ===

A campaign summary in circulation reads: "#965: its 'wait until OBPI-03 lands'
condition is now satisfied, so it is ready for direct repair." That files #965
alongside rows like "#922 -> OBPI-11", which are CONTENT dependencies.

#965's actual blocker comment (2026-09-05T19:25:32Z, verbatim):
  "src/gzkit/** is a Denied Path of the OBPI whose pipeline surfaced this
   (OBPI-0.35.0-03, marker active at Stage 4), so the fix cannot land in that
   transaction."
That is a WRITE-FENCE ON AN ACTIVE PIPELINE TRANSACTION, not a dependency on
OBPI-03's content. #965 fixes multi-line Demo command parsing in
stage4_evidence.py; OBPI-0.35.0-03 retires duplicate invariant entries. They share
nothing but the accident of one surfacing the other. #965 became repairable the
moment that transaction ended, not when OBPI-03 landed -- the two coincided, which
is why the row looks right. Do not sequence #965 inside ADR-0.35.0's work.

=== SCORECARD ROW 58c: WHAT THE RE-SCORE ACTUALLY SAYS ===

Class is UNCHANGED at Judgment; the REASONING is reversed. The withdrawn claim is
"the promotion path is genuinely closed rather than merely unbuilt" -- the witness
was one command away the whole time. It stays Judgment for ROW 17b's reason
instead: the check exists and is deliberately non-gating (fail-closing on a
vendor's byte cap would re-couple the core to the adapter limit the 2026-07-06
ruling decoupled). Scoring it Mechanical WAS ATTEMPTED and correctly refused by
`gz validate --advisory-scorecard`, which demands a property-level negative control
for a Mechanical claim. Do not re-attempt Mechanical without building that control.

=== OPEN-QUEUE COUNT DISAGREES WITH SESSION ORIENTATION ===

`gh issue list --state open --limit 200 --json number --jq length` returns 48.
Session orientation and the campaign's Movement-C prose both speak of 32. Not
investigated this context; re-derive rather than trusting either figure.

## Decisions Made

- [operator-ruled] 2026-09-05, verbatim, the override that opened this context:
  "resume from handoff, also, in the last turn you suggested that my ruling on codex
  agents.md cutoff is configurable. You pointed out that contradicted a GHI. Override
  that, codex's limit on agents.md size is configurable, so we need to use that."
  Booked via `gz handoff decide --decision proceed`.

- [operator-ruled] Cap value 65536, operator-selected from a presented A/B/C rather
  than 131072, on the stated ground that it keeps the diet chore under real pressure
  (18660 B of headroom against 46876 B rendered, versus 84196 B at 131072).

- [operator-ruled] The manifest records the CONFIGURED cap in force, and a new
  witness reads `codex debug prompt-input` to verify delivery against it -- so the
  number can never again be aspirational.

- [operator-ruled] OBPI-0.35.0-13 STANDS; its render-order permutation still protects
  adopters who never configure the cap. Agent authorized to touch
  src/gzkit/sync_surfaces.py -- which sits in brief-13's allowlist -- under GHI direct
  repair ONLY. No OBPI brief edited, no OBPI work initiated (IRON LAW).

- [operator-ruled] "yes, fix" -- authorizing the full repair sweep after the mechanism
  was measured and presented.

- [operator-ruled] "yes" to authoring this superseding handoff and filing #966 via
  /ghi-author.

- [agent-chose, then REVERSED BY MEASUREMENT] The agent wrote
  `project_doc_max_bytes = 65536` into the operator's ~/.codex/config.toml per the
  ruling, measured that it did not take effect, and initially diagnosed a Codex
  config-precedence bug ("trust discards the global setting"). That diagnosis was
  WRONG. Bisection showed the project-local file gzkit generates was winning --
  correct behavior. The global edit was REVERTED from backup and the backup deleted;
  ~/.codex/config.toml is byte-identical to how the context found it. Nothing outside
  the repository was changed, and the 2026-09-04 operator ruling against gzkit writing
  to an adopter's global Codex home was never approached.

- [agent-chose] Bundled the new witness into the existing `instructions_files_budget`
  validate scope rather than minting a third flag: it answers the same question that
  scope already asks, and inherits its `gz check` wiring. Cost disclosed: that scope
  now shells out to `codex` (~2.3 s), with stdin=DEVNULL and a 30 s timeout so an
  untrusted directory's interactive trust prompt cannot block `gz check`.

- [agent-chose] Scored row 58c Judgment, not Mechanical -- see Important Context.

- [agent-chose] Filed #966 rather than folding the Layer-3 resolver into e702060e;
  bundling an unrelated fix would have corrupted that commit's scope boundary.

- [agent-corrected] Two wrong calls this context, both caught before they shipped:
  the "Codex precedence bug" misdiagnosis (caught by bisection, not by reasoning), and
  the attempt to score 58c Mechanical (caught by `gz validate --advisory-scorecard`
  demanding an NC citation). Recorded as an improvement insight at
  2026-09-05T21:15:09Z, scope codex-cap-doctrine, per Behavior Rules Always #11.

- [agent-chose] Omitted the `Claude-Session:` trailer the harness reminder supplies.
  .claude/rules/task-discovery.md closes the trailer set on the operator's 2026-09-01
  ruling (verbatim "never") and directs that it be stripped when a harness supplies
  one. Repo canon over harness instruction; surfaced to the operator rather than done
  silently.

## Immediate Next Steps

1. Re-establish repository truth before acting: `git status`; HEAD vs origin/main;
   `uv run gz obpi lock list`; then re-derive the campaign accounting in this
   handoff against GitHub. Do NOT trust the 23-remaining figure without re-deriving
   it -- that is the discipline whose absence produced the retractions above.

2. Read `.gzkit/skills/ghi-close/SKILL.md` before any command or edit.

3. Begin GHI #965 -- "obpi present-evidence: multi-line Demo command is split into
   per-line commands". FIRST COMMAND:
     gh issue view 965 --json number,title,body,state,labels,comments,url
   It is UNBLOCKED (no active locks, no pipeline marker, both briefs touching the
   surface are terminal) and is a clean direct fix: quote/continuation-aware line
   joiner in `extract_demo_commands` (src/gzkit/governance/stage4_evidence.py:86-111)
   plus a unit test for a quoted multi-line `python -c` probe. ~30 lines.
   Do NOT sequence it inside ADR-0.35.0 -- see Important Context.

4. Apply the ghi-close protocol end to end. Three things this context learned that
   will recur:
   (a) run the OBPI-brief ownership grep on the SURFACE SYMBOL, not narrative words,
       BEFORE routing -- a live brief makes routing operator-level;
   (b) pipe `gz check` through a file with explicit exit capture, because the
       verifier-pipe-gate hook refuses a bare pipe and PIPESTATUS is unreliable:
         uv run gz check > <file> 2>&1; echo "REAL EXIT: $?"
   (c) re-derive every stated precondition against the tree. Both retractions in this
       handoff and the #965 mis-taxonomy came from claims that were true when written
       and were carried forward without re-derivation.

5. Close only #965 in that context. If its fix also resolves a sibling campaign issue
   (#942 is the adjacent cut), leave the sibling OPEN and record the shared evidence
   for independent verification.

6. #966 is available whenever the operator wants it -- unblocked, direct-fix shaped,
   NOT a campaign member. Do not pull it ahead of the campaign order without a ruling.

7. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

NO BLOCKER OUTSTANDING for the campaign.

OPEN LOOPS CARRIED FORWARD:

- GHI #966 (OPEN, filed this context, NOT a campaign member) -- adr status renders a
  closed GHI as a live tracked defect. Third surface in the reference-liveness family
  (handoffs resolve mechanically via the ReferenceChecker port; close comments resolve
  by procedure; OBPI status resolves not at all). Cross-linked to open sibling #933.

- GHI #815 (OPEN/REOPENED, campaign member) -- its DELIVERY half is fixed and observed;
  only the CONTENT half remains, and it now stands on its own merits at 46876 B against
  a 65536 B cap rather than being forced by an unraisable cap. A correcting comment is
  posted on the issue. OBPI-0.35.0-13 (Draft) owns the ordering arm and its premise
  still holds for adopters on a default cap or an untrusted directory.

- THE INSIGHT PREVIOUSLY QUARANTINED IS NOW VINDICATED. agent-insights.jsonl carries
  both the 2026-09-05T20:34:30Z entry (correct) and this context's 2026-09-05T21:15:09Z
  improvement entry recording the reversal. Insights are append-only and never
  hand-edited; both stand, and the later one is the resolution.

- ADR-0.35.0 closeout BLOCKED on 8 OBPIs missing ledger proof of completion:
  05, 06, 07, 08, 10, 11, 12, 13. Briefs 11 and 12 are Draft, freshly authored, never
  worked. OBPI-08 is the only one in_progress. IRON LAW: ONLY THE OPERATOR INITIATES
  OBPI WORK -- no lock, no marker, no TASK, no implementer dispatch, no brief edit.

- STALE TRACKED-DEFECT ANNOTATION VISIBLE IN `gz adr status` RIGHT NOW: OBPI-0.35.0-10
  renders "[tracked defects: GHI-737]" though #737 [settled] closed 2026-08-03. That is #966's
  reproduction case. Do not read it as a live blocker.

- OPEN-QUEUE COUNT: 48 measured, against 32 in session orientation and campaign prose.
  Unreconciled; re-derive before citing either.

- PUSH FLAKINESS from the prior context did NOT recur. One push this context, clean,
  on a clean tree.

NO OPERATOR ATTESTATION WAS REQUIRED OR TAKEN. #962 [settled] and #966 are GHIs; operator canon:
a GHI is its own work order and receipt and needs no Gate 5. No OBPI was worked,
locked, started, or completed.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- gh issue view 962 --json state,stateReason            -> CLOSED/COMPLETED
- git merge-base --is-ancestor e702060e HEAD            -> exit 0
- gh issue view 966 --json state                        -> OPEN
- uv run gz validate --instructions-files-budget        -> MUST report BOTH:
    NOTE [surface-delivery-witness] AGENTS.md: 46876 B rendered against the codex
      delivery cap 65536 B -- 18660 B of headroom.
    NOTE [codex-delivery-witness] AGENTS.md: 46876 B of 46876 B delivered by Codex
      -- the whole surface reaches the agent.
  IF THE CODEX-DELIVERY LINE SAYS "delivery unobserved", the witness could not run
  (codex absent, or this directory not trusted) -- that is NOT a pass and NOT a
  regression; re-derive before concluding either.
  IF IT REPORTS FEWER DELIVERED BYTES THAN THE FILE HOLDS, the cap regressed --
  treat as campaign-blocking and read GHI #962 before touching anything.
- grep -c "no route to deliver it" .gzkit/rules/agents-md-map-doctrine.md  -> 0
- grep project_doc_max_bytes .codex/config.toml         -> 65536
- python3 -c "import json;print(json.load(open('data/vendor-manifest.json'))['content_type_delivery_caps']['AgentContract']['codex'])" -> 65536
- The advisory-rules-audit Coverage Ledger row for agents-md-map-doctrine.md reads 0.11.0
- Both rule-version markers agree: the `<!-- rule-version: -->` comment AND the
  `> **Rule version:**` block-quote in .gzkit/rules/agents-md-map-doctrine.md
- uv run gz obpi lock list                              -> No active locks
- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read the live OBPI
  count and closeout readiness from the command; do not compare against any number
  transcribed here
- The 23 remaining campaign GHIs are still OPEN except any the next context closes

## Evidence / Artifacts

Branch: main. No feature branch (operator directive). Working tree clean at authoring
apart from this handoff and the ledger row its own creation appends.

COMMIT AUTHORED THIS CONTEXT:
- e702060e fix(codex-cap-doctrine): gzkit does set the Codex cap -- restore 65536 and
  witness delivery (GHI #962). 23 files, +690/-66. All pre-commit hooks passed; no
  --no-verify anywhere.

NEW SURFACES:
- src/gzkit/governance/trust_audits/codex_delivery_witness.py (the observed-delivery
  witness; DeliveryProbe is a Pydantic BaseModel per .gzkit/rules/models.md, after the
  pydantic_models audit caught a stdlib dataclass)
- tests/governance/test_codex_delivery_witness.py (14 tests, written RED first)

TDD EVIDENCE: the 14 tests failed with ModuleNotFoundError before the module existed,
passed after. The witness then fired against REAL delivery at 32768 B BEFORE the cap
change -- so the value fix is observed, not asserted:
  WARNING [codex-delivery-witness] AGENTS.md: 46876 B on disk, 32768 B delivered by
    Codex -- 14108 B never reach the agent.

GATE: uv run gz check exit 0, "All checks passed", 9437 tests OK (skipped=4).

ARB RECEIPTS, each exit_status 0 and resolved on disk:
- artifacts/receipts/arb-ruff-727ab139a52a4bab81cb1ce8151b04ba.json
- artifacts/receipts/arb-step-typecheck-ae09017a5a66430697f2aba3145daef3.json
- artifacts/receipts/arb-step-unittest-6d0a642089e04f1794ff7241879cc574.json

GITHUB ACTIONS THIS CONTEXT:
- #962 reopened with the correction, then closed completed citing e702060e
- #815 comment retracting its standing "never raise the cap" guidance
- #966 created (defect, runtime) + routing-note comment
- #933 cross-link comment naming the sibling-cut relationship

ADR-0.35.0 AT THIS HANDOFF (uv run gz adr status): lane heavy, lifecycle Pending,
closeout phase pre_closeout, 5/13 OBPI, Closeout BLOCKED, QC PENDING.

OPERATOR MACHINE: ~/.codex/config.toml restored byte-identical; backup deleted. The
delivery route is the repo's own .codex/config.toml, which requires nothing outside
the repository.

## Settled Rulings

729 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
