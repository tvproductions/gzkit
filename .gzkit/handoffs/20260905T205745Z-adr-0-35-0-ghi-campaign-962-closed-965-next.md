---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-05T20:57:45Z'
agent: claude-code-5b1129ee
continues_from: 20260905T204755Z-adr-0-35-0-ghi-closeout-962-closed.md
---

## Current State Summary

CAMPAIGN: ADR-0.35.0 GHI closeout campaign. Context 1 complete. GHI #962 CLOSED (fixed).
This handoff SUPERSEDES 20260905T204755Z-adr-0-35-0-ghi-closeout-962-closed.md, whose two
recorded blockers are now BOTH CLEARED by operator ruling and by measurement.

Original 24-issue set, in operator-declared order:
Pipeline/evidence reliability: 962, 965, 964, 942, 941, 963, 888, 940, 849, 946, 877
ADR-0.35.0 obligations/sequencing: 611, 930, 894, 939, 922, 921, 815, 933
Ledger/session residuals: 953, 952, 951, 767, 766
Excluded incidentals (operator-named, NOT campaign members): 936, 871, 870, 818, 807, 799.

CLOSED (1 of 24):
- #962 codex config: .codex/config.toml is never read -- disposition FIXED.
  Destination: e43c55c9 (pre-existing; independently verified present in HEAD, NOT
  reimplemented per operator instruction) PLUS b90d0484 (this context -- closed the class
  in three live surfaces e43c55c9 had missed).
  Evidence: uv run gz check exit 0, 9423 tests OK (skipped=4). Three ARB receipts, each
  exit_status 0 and resolved on disk: arb-ruff-e54535b479084bd9842bacf424eb0874,
  arb-step-typecheck-02cc92f08c2548f9877f94bf131a2232,
  arb-step-unittest-32656900482049ccbb4659311f39556f.
  Close comment: https://github.com/tvproductions/gzkit/issues/962

REMAINING (23), order unchanged from the operator's brief: 965, 964, 942, 941, 963, 888,
940, 849, 946, 877, 611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766.
All 23 verified OPEN on GitHub at this handoff.

NEXT GHI: #965 -- "obpi present-evidence: multi-line Demo command is split into per-line
commands". No reordering was performed in context 1; no dependency requiring one was found.

CAMPAIGN IS CLEAR TO PROCEED. No blocker outstanding. Not yet PATCH ADVANCE READY --
that state requires 24/24 and is 23 closures away.

## Important Context

WHY #962 WAS NOT CLOSED ON THE PRE-EXISTING COMMIT ALONE.

gzkit generates .codex/config.toml carrying project_doc_max_bytes. Codex never reads that
file -- it loads $CODEX_HOME/config.toml, and nothing sets CODEX_HOME. Both delivery
remedies are closed: writing to the user-global Codex home is an adopter surface the
operator ruled out 2026-09-04, and repointing CODEX_HOME moves auth.json with it, leaving
the tier-1 adversary unauthenticated. So the setting is inert and the cap in force is
Codex's own 32768 default.

e43c55c9 corrected FOUR surfaces: render_codex_config's docstring,
CodexDocCapCoherenceTest's docstring, the data/vendor-manifest.json value, and the
generated .codex/config.toml value. It was a PARTIAL fix. ghi-close Phase 3 step 7b
(class-of-failure) found the same disproved claim still live in THREE more surfaces:
  - src/gzkit/schemas/vendor_manifest.json content_type_delivery_caps description
  - .gzkit/rules/agents-md-map-doctrine.md section Budget
  - src/gzkit/rules/agents-md-map-doctrine.md (wheel mirror of the same sentence)

b90d0484 corrected all three, regenerated .claude/rules/agents-md-map-doctrine.md via
gz agent sync control-surfaces, bumped the rule 0.9.0 to 0.10.0 with its
rule-version-history entry, re-scored the advisory-scorecard Coverage Ledger, and added
scorecard row 58c (Judgment). Two governance witnesses fired during that work and were
satisfied rather than worked around: the rule-version block-quote/marker coherence check,
and the advisory-scorecard unscored-bump fail-close.

ROW 58c MATTERS FOR LATER CAMPAIGN ITEMS. It records that the promotion path for a
delivery witness here is CLOSED, not merely unbuilt: a witness would have to observe the
cap Codex actually applied, which is state outside this repo.
CodexDocCapCoherenceTest is explicitly NOT that witness -- it fail-closes only when two
authored numbers disagree with EACH OTHER, which is the presence-check shape AGENTS.md
names. Do not cite it as a delivery witness in a later close.

STILL TRUE AFTER THIS CLOSE, DELIBERATELY: AGENTS.md is 46876 B against a 32768 B cap --
14108 B OVER. The operator's verbatim canon, IRON LAW at byte 40734, does not reach the
cross-vendor adversary. That is GHI #815 (OPEN/REOPENED), a campaign member, and #962's
close comment states explicitly that it does not claim that scope.

CONCURRENT-SESSION EPISODE, NOW RESOLVED. A Codex session wrote to this tree throughout
context 1 (adr-evaluation, airlock permitted-entry, obpi_created for OBPI-0.35.0-11 and
-12, then substantive authoring of both briefs). The agent initially held the briefs back
and framed their authorship as an open IRON LAW question, and pushed a mid-authoring
scaffold snapshot of brief 11 in 4d2bd3e3. The operator ruled the session done and
directed the briefs be committed; c64678e1 lands their completed authoring and corrects
the snapshot. ADR-0.35.0 now reads 5/13 with the 13-item checklist and 13 briefs
reconciled -- the "Checklist count (13) != OBPI file count (11)" scorecard finding is
gone.

## Decisions Made

- [operator-ruled] 2026-09-05, verbatim: "the codex session is done, commit the briefs and
  continue, update handoff with this GHI campaign and I'll reset context with new session.
  git sync". This cleared both blockers the superseded handoff recorded.

- [operator-ruled] 2026-09-04, verbatim, on gzkit writing to the user-global Codex home:
  "such locations are global to an adopter's project, i think the right answer is no."
  Carried forward: remedy (b) for #962 is permanently closed.

- [operator-ruled] Campaign brief item 5, verbatim: "Items 11 and 12 already exist for
  #922 and #921; preserve their declared intent." Their briefs are now landed at c64678e1
  and their declared intent is preserved unedited.

- [operator-ruled] Campaign brief, verbatim: "If a target is already fixed, such as #962
  at commit e43c55c9, independently verify that the commit is present and satisfies the
  issue, then close it through ghi-close; do not reimplement it." Honored -- e43c55c9 was
  verified as an ancestor of HEAD and left untouched; only the uncovered remainder of its
  class was fixed.

- [agent-chose] Treated #962 as the PARTIAL-fix shape rather than already-resolved,
  because verification found three live surfaces still carrying the disproved claim.

- [agent-chose] Routed #962 to DIRECT FIX on computed facts: 3 files, about 5 source
  lines; single named surface; 491 fix( commits in 60 days; defect surfaced in flight;
  doc/schema prose so no new BDD. Precondition check ran FIRST -- grepped
  docs/design/adr/*/*/obpis/*.md for the surface paths; 8 briefs matched, ALL TERMINAL,
  so no live brief owned the work.

- [agent-chose] Scored the new binding sentence as advisory-scorecard row 58c JUDGMENT
  rather than Promotable, because the state a witness would observe lies outside the repo.

- [agent-chose] Left sealed historical records untouched -- terminal OBPI briefs, prior
  handoffs, chore proofs, return-to-health-plan, pool ADRs all still carry the old claim.
  They state what was believed on their date and are not defects.

- [agent-corrected] The agent over-called the concurrent authoring as an open IRON LAW
  question and snapshot-committed an actively-written file. Recorded as an improvement
  insight at 2026-09-05T20:54:15Z, scope ghi-close/concurrent-session-artifacts, per
  AGENTS.md Behavior Rules Always #11, and discharged by c64678e1.

## Immediate Next Steps

1. Re-establish repository truth per the campaign protocol: git status; HEAD vs
   origin/main; uv run gz obpi lock list; then confirm the closed/remaining accounting in
   this handoff still matches GitHub.

2. Read the ghi-close SKILL.md before any command or edit.

3. Begin GHI #965 -- "obpi present-evidence: multi-line Demo command is split into
   per-line commands". FIRST COMMAND FOR THE NEXT CONTEXT:
   gh issue view 965 --json number,title,body,state,labels,comments,url

4. Apply the ghi-close protocol end to end. Note two things context 1 learned that will
   recur: (a) run the OBPI-brief ownership grep BEFORE routing, since a live brief makes
   routing operator-level; (b) pipe gz check through a file with an explicit exit capture,
   because the verifier-pipe-gate hook refuses a bare pipe and PIPESTATUS is unreliable
   after an intermediate command. Use:
   uv run gz check > <file> 2>&1; echo "REAL EXIT: $?"

5. Close only #965 in that context. If its fix also resolves a sibling campaign issue,
   leave the sibling OPEN and record the shared evidence here for independent verification.

6. Author the next campaign handoff before reporting safe-to-reset.

## Pending Work / Open Loops

NO BLOCKER OUTSTANDING. Both blockers recorded in the superseded handoff are cleared:
- Concurrent Codex writer: operator ruled it done. No repo file has changed outside this
  session since.
- Red gate on OBPI-0.35.0-12: the authoring session resolved the unregistered
  `gz content onboard-rules` reference with the documented escape marker for a
  planned-but-unlanded CLI surface, at both call sites. Re-derived rather than assumed:
  uv run gz validate --cli-alignment exits 0, and uv run gz check exits 0.

OPEN LOOPS CARRIED FORWARD, none blocking the campaign:

- CONTRADICTORY INSIGHT LEFT STANDING BY DESIGN. .gzkit/insights/agent-insights.jsonl
  carries an entry at 2026-09-05T20:34:30Z, scope ADR-0.35.0-readiness, asserting "Treat
  Codex project_doc_max_bytes as configurable; a local 32768-byte witness declaration is
  not an immutable vendor limit." That is the exact claim #962 [settled] disproved by measurement.
  Acting on it would re-raise the cap and re-create the false-headroom reading. Preserved
  rather than removed -- insights are append-only and never hand-edited (AGENTS.md
  Behavior Rules Always #11) -- and contradicted in 4d2bd3e3's commit body, in #962 [settled]'s
  close comment, and here.

- GHI #815 (OPEN/REOPENED) is a campaign member and carries the REMAINING truncation work.
  #962 [settled]'s close explicitly does not claim it. When #815 comes up, the fix is content
  (getting must-survive canon above the 32768 cut), never raising the cap.

- ADR-0.35.0 closeout is BLOCKED on 8 OBPIs missing ledger proof of completion: 05, 06,
  07, 08, 10 (tracked defect GHI-737), 11, 12, 13. Briefs 11 and 12 are Draft, freshly
  authored, never worked. IRON LAW: only the operator initiates OBPI work.

- PUSH FLAKINESS OBSERVED, not yet tracked. Two of three pushes in context 1 failed on
  the first attempt with "Stashed changes conflicted with hook auto-fixes, Rolling back
  fixes" followed by "failed to push some refs", while the pre-push gz check gate had
  reported PASSED. Both succeeded on immediate retry. It occurred only with a dirty tree.
  If it recurs on a clean tree, that is a real defect worth a GHI.

NO OPERATOR ATTESTATION WAS REQUIRED OR TAKEN. #962 [settled] is a GHI; operator canon: a GHI is
its own work order and receipt and needs no Gate 5. No OBPI was worked, locked, started,
or completed in context 1.

## Verification Checklist

Re-run at the start of the next context and confirm each:

- gh issue view 962 --json state,stateReason  -> CLOSED/COMPLETED
- git merge-base --is-ancestor b90d0484 HEAD  -> exit 0
- git merge-base --is-ancestor e43c55c9 HEAD  -> exit 0
- git merge-base --is-ancestor c64678e1 HEAD  -> exit 0
- uv run gz validate --instructions-files-budget -> reports 46876 B against the codex
  delivery cap 32768 B, 14108 B OVER. If it instead reports HEADROOM, the cap was
  re-raised and #962 has regressed -- treat that as a campaign-blocking regression.
- grep -c "no route to deliver it" .gzkit/rules/agents-md-map-doctrine.md -> 1
- The advisory-rules-audit Coverage Ledger row for agents-md-map-doctrine.md reads 0.10.0
- uv run gz obpi lock list -> No active locks
- uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing -> read the live OBPI
  count and closeout readiness from the command; do not compare against a number
  transcribed here
- The 23 remaining campaign GHIs are all still OPEN except any the next context closes.

CAMPAIGN ACCOUNTING RECONCILED AGAINST GITHUB at this handoff: #962 CLOSED/COMPLETED; the
other 23 campaign members all OPEN (#815 carries stateReason REOPENED). Non-member
references resolved at the #962 close: #961 CLOSED/COMPLETED 2026-09-05, #851 OPEN.

## Evidence / Artifacts

Branch: main. No feature branch was created (operator directive).
Active OBPI locks: NONE (uv run gz obpi lock list reports "No active locks").
Working tree at handoff authoring: clean apart from this handoff and the ledger row its
own creation appends; both land in the sync that follows.

Commits authored in context 1, in order:
- b90d0484 fix(codex-cap-doctrine): close the class -- two live surfaces still claimed
  gzkit sets the Codex cap (GHI #962). 6 files, +24/-14.
- 4d2bd3e3 chore(ledger,adr-0.35.0): take custody of a concurrent Codex session's
  ADR-0.35.0 artifacts. 6 files, +649/-9. Its framing of the authorship question was
  over-cautious and its brief-11 content was a mid-authoring snapshot; both corrected by
  c64678e1.
- ce369eec chore(handoffs): campaign handoff -- ADR-0.35.0 GHI closeout, #962 closed
  (1/24). The handoff this document supersedes.
- c64678e1 chore(adr-0.35.0): land the completed OBPI-0.35.0-11 and -12 authoring.
  6 files, +576/-487.
All four passed every pre-commit hook. No --no-verify anywhere in this campaign.

ADR-0.35.0 state at this handoff (uv run gz adr status): lane heavy, lifecycle Pending,
closeout phase pre_closeout, 5/13 OBPI, Closeout BLOCKED, QC PENDING. Closeout blockers,
all "ledger proof of completion is missing": OBPI-0.35.0-05, -06, -07, -08, -10 (tracked
defect GHI-737), -11, -12, -13. OBPI-0.35.0-09-codex-playback-wiring is attested and
completed; it was confirmed terminal before #962 routed to direct fix.

ARB receipts for the #962 close, each resolved on disk with exit_status 0:
- artifacts/receipts/arb-ruff-e54535b479084bd9842bacf424eb0874.json
- artifacts/receipts/arb-step-typecheck-02cc92f08c2548f9877f94bf131a2232.json
- artifacts/receipts/arb-step-unittest-32656900482049ccbb4659311f39556f.json

Gate evidence: uv run gz check exit 0, "All checks passed", run after the brief authoring
landed. Earlier in the context the same command ran 9423 tests OK (skipped=4).

Observed output proving #962's substance, uv run gz validate --instructions-files-budget:
  WARNING [surface-delivery-witness] AGENTS.md: 46876 B rendered against the codex
  delivery cap 32768 B -- 14108 B OVER
  WARNING [surface-delivery-witness] AGENTS.md: must-survive section 'operator-doctrine-verbatim-canon' spans 30020-43941,
  straddles the codex cap 32768 B
  WARNING [surface-delivery-witness] AGENTS.md: must-survive section 'architectural-boundaries' starts 46281, past the codex cap
Before e43c55c9 that line read "18660 B of headroom" against a cap not in force.

## Settled Rulings

725 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
