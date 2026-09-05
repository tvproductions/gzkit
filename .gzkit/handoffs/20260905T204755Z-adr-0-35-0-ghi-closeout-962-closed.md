---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-05T20:47:55Z'
agent: claude-code-5b1129ee
continues_from: 20260902T042217Z-trailer-closed-config-gate-render-order-absorbed.md
---

## Current State Summary

CAMPAIGN: ADR-0.35.0 GHI closeout campaign. Context 1 of N. GHI #962 CLOSED (fixed).

Original 24-issue set, in operator-declared order:
Pipeline/evidence reliability: 962, 965, 964, 942, 941, 963, 888, 940, 849, 946, 877
ADR-0.35.0 obligations/sequencing: 611, 930, 894, 939, 922, 921, 815, 933
Ledger/session residuals: 953, 952, 951, 767, 766
Excluded incidentals (operator-named, NOT campaign members): 936, 871, 870, 818, 807, 799.

CLOSED SO FAR (1 of 24):
- #962 codex config: .codex/config.toml is never read -- disposition FIXED.
  Destination: e43c55c9 (numeric surfaces + 2 docstrings, pre-existing, independently
  verified present in HEAD) and b90d0484 (this context -- closed the class).
  Evidence: gz check exit 0, 9423 tests OK (skipped=4). ARB receipts, all exit_status 0
  and resolved on disk: arb-ruff-e54535b479084bd9842bacf424eb0874,
  arb-step-typecheck-02cc92f08c2548f9877f94bf131a2232,
  arb-step-unittest-32656900482049ccbb4659311f39556f.

REMAINING (23), unchanged order: 965, 964, 942, 941, 963, 888, 940, 849, 946, 877,
611, 930, 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766.

NEXT GHI: #965 (obpi present-evidence: multi-line Demo command is split into
per-line commands). No reordering was performed; no dependency requiring one was found.

## Important Context

WHAT #962 WAS, AND WHY e43c55c9 WAS NOT THE WHOLE FIX.

gzkit generates .codex/config.toml carrying project_doc_max_bytes. Codex never reads
that file -- it loads $CODEX_HOME/config.toml, and nothing sets CODEX_HOME. Both
delivery remedies are closed: writing to ~/.codex/ is an adopter global surface the
operator ruled out 2026-09-04, and repointing CODEX_HOME moves auth.json with it,
leaving the tier-1 adversary unauthenticated. So the setting is inert and the cap in
force is Codex's own 32768 default.

e43c55c9 (pre-existing, operator-named in the campaign brief) corrected FOUR surfaces:
render_codex_config's docstring, CodexDocCapCoherenceTest's docstring, the
data/vendor-manifest.json value, and the generated .codex/config.toml value. It was a
PARTIAL fix. Independent verification at this close found the same disproved claim
still live in THREE more surfaces, which is why the GHI was not closed on the existing
commit alone:
  - src/gzkit/schemas/vendor_manifest.json content_type_delivery_caps description
  - .gzkit/rules/agents-md-map-doctrine.md section Budget
  - src/gzkit/rules/agents-md-map-doctrine.md (wheel mirror of the same sentence)

b90d0484 corrected all three, regenerated .claude/rules/agents-md-map-doctrine.md via
gz agent sync control-surfaces, bumped the rule 0.9.0 to 0.10.0 with its
rule-version-history entry, re-scored the advisory-scorecard Coverage Ledger, and added
scorecard row 58c (Judgment).

Row 58c matters for later campaign items: it records that the promotion path for a
delivery witness here is CLOSED, not merely unbuilt. A witness would have to observe
the cap Codex actually applied, which is state outside this repo.
CodexDocCapCoherenceTest is explicitly NOT that witness -- it fail-closes only when two
authored numbers disagree with each other.

STILL TRUE AFTER THIS CLOSE: AGENTS.md is 46876 B against a 32768 B cap -- 14108 B
OVER. The operator's verbatim canon, IRON LAW at byte 40734, does not reach the
cross-vendor adversary. That is GHI #815 (OPEN/REOPENED), a campaign member, and it was
deliberately NOT closed here.

## Decisions Made

- [agent-chose] Treated #962 as a PARTIAL-fix shape, not already-resolved. The operator's
campaign brief said to verify e43c55c9 and not reimplement. Verification found the class
still open in three live surfaces, so ghi-close Phase 3 step 7b (class-of-failure) forced
Phase 2 execution rather than a straight close. e43c55c9 was NOT reimplemented.

- [agent-chose] Routed to DIRECT FIX. Routing facts computed mechanically: 3 files, about 5
source lines; single named surface (the codex delivery-cap claim); 491 fix( commits in
60 days; defect surfaced in flight; doc/schema prose so no new BDD scenario. Precondition
check ran first: grepped docs/design/adr/*/*/obpis/*.md for the surface paths -- 8 briefs
matched, ALL TERMINAL (Completed/Abandoned), so no live brief owned the work. Operator
canon also rules it: a GHI-tracked defect repair routes to direct fix always.

- [agent-chose] Scored the new binding sentence as advisory-scorecard row 58c Judgment
rather than Promotable, because the state a witness would observe lies outside the repo.
Recorded the reasoning, not only the verdict.

- [agent-chose] Left sealed historical records untouched -- terminal OBPI briefs, handoffs,
chore proofs, return-to-health-plan, pool ADRs all still contain the old claim. They state
what was believed on their date and are not defects.

- [canon-ruled] Did NOT edit OBPI-0.35.0-12 to clear the red gate. AGENTS.md IRON LAW names
editing an OBPI brief as an arm only the operator initiates. Canon ruled; no question was
put to the operator.

[agent-chose, NEEDS OPERATOR REVIEW] Commit 4d2bd3e3 took custody of a concurrent Codex
session's artifacts and framed their authorization as an OPEN IRON LAW QUESTION. That
framing was OVER-CAUTIOUS and is corrected here: both briefs carry Gate 1 evidence reading
"Authored on 2026-09-05 at the operator's request to rectify the thirteen-item
decomposition," and the operator's own campaign brief item 5 says items 11 and 12 already
exist for #922 and #921. The authoring is operator-directed. 4d2bd3e3 ALSO captured a
MID-AUTHORING SCAFFOLD SNAPSHOT of OBPI-0.35.0-11 and pushed it to origin; the completed
authoring of both briefs is still uncommitted on disk. See Pending.

## Immediate Next Steps

1. OPERATOR DECISION FIRST -- do not start #965 until the concurrency question is settled.
   A Codex session (app-server PID 36432, --cwd this repo, started 11:35 local) was writing
   to this tree throughout context 1. Ask the operator whether it is still running and
   whether this campaign should continue while it does.

2. Clear the RED GATE on OBPI-0.35.0-12 before any further git-sync. Measured:
   uv run gz check exits 1 with 2 failures, both one defect --
   OBPI-0.35.0-12-rules-corpus-onboarding.md:154 cites "gz content onboard-rules", which is
   not a registered subcommand (available: advise-rendition, commit, compose, edit, import,
   list, reconcile-retirements, remember...). Governed recovery per
   .claude/rules/governance-core.md section Operator-doc verb resolution: register the verb,
   rename the reference, or -- for a planned-but-unlanded CLI surface -- file a GHI and mark
   the reference speculative with the gz-validate-skip command-shape marker on the preceding
   line. THE AGENT MAY NOT DO THIS UNILATERALLY: editing an OBPI brief is an IRON LAW arm.

3. Commit the completed authoring of OBPI-0.35.0-11 and -12 once the operator rules,
   correcting the mid-authoring scaffold snapshot that 4d2bd3e3 pushed for brief 11.

4. Then begin GHI #965. First command for the next context:
   gh issue view 965 --json number,title,body,state,labels,comments,url

## Pending Work / Open Loops

BLOCKER 1 -- CONCURRENT WRITER. A Codex session wrote to this repo during context 1.
Ledger events it appended (none from this session): adr-evaluation plus adr_eval_completed
for ADR-0.35.0 at 20:29:24Z; airlock_in and airlock_out permitted-entry on the ADR-0.35.0
package at 20:34:41Z; obpi_created for OBPI-0.35.0-11-corpus-shape-witness and
OBPI-0.35.0-12-rules-corpus-onboarding at 20:35:14Z. It then substantively authored both
briefs (brief 11 at 20:40:40Z, brief 12 at 20:41:48Z) -- AFTER this session had already
committed and pushed their scaffold state in 4d2bd3e3. This session's own ledger rows in
that window are only the two agent_sync_completed events at 20:29:09Z and 20:31:47Z.
Concrete action to clear: operator confirms whether the Codex session is finished.

BLOCKER 2 -- RED GATE, TREE NOT CLEAN. uv run gz check exits 1 on the
"gz content onboard-rules" unresolvable verb in OBPI-0.35.0-12 line 154 (detail in
Immediate Next Steps item 2). Working tree is therefore NOT clean: two modified files,
OBPI-0.35.0-11-corpus-shape-witness.md and OBPI-0.35.0-12-rules-corpus-onboarding.md,
both the concurrent session's completed authoring. Concrete action to clear: operator
rules on the escape marker or verb registration, then the briefs commit and the gate goes
green.

CONTRADICTORY INSIGHT LEFT STANDING BY DESIGN. .gzkit/insights/agent-insights.jsonl
carries an entry at 20:34:30Z, scope ADR-0.35.0-readiness, asserting "Treat Codex
project_doc_max_bytes as configurable; a local 32768-byte witness declaration is not an
immutable vendor limit." That is the exact claim GHI #962 [settled] disproved by measurement.
Acting on it would re-raise the cap and re-create the false-headroom reading. It is
preserved rather than removed -- insights are append-only and never hand-edited
(AGENTS.md Behavior Rules Always #11) -- and is flagged in 4d2bd3e3's commit body so the
next reader meets the correction alongside it.

NO OPERATOR ATTESTATION WAS REQUIRED OR TAKEN in this context. #962 [settled] is a GHI; operator
canon: a GHI is its own work order and receipt and needs no Gate 5.

OPERATOR RULINGS ALREADY IN HAND, VERBATIM, CARRIED FORWARD:
- On gzkit writing to the user-global Codex home (2026-09-04): "such locations are global
  to an adopter's project, i think the right answer is no."
- Campaign brief item 5: "Items 11 and 12 already exist for #922 and #921; preserve their
  declared intent."
- Campaign brief: "If a target is already fixed, such as #962 [settled] at commit e43c55c9,
  independently verify that the commit is present and satisfies the issue, then close it
  through ghi-close; do not reimplement it."

## Verification Checklist

Re-run at the start of the next context and confirm each:

- gh issue view 962 --json state,stateReason  -> CLOSED/COMPLETED
- git merge-base --is-ancestor b90d0484 HEAD  -> exit 0
- git merge-base --is-ancestor e43c55c9 HEAD  -> exit 0
- uv run gz validate --instructions-files-budget -> reports 46876 B against the codex
  delivery cap 32768 B, 14108 B OVER (NOT headroom). If it reports headroom, the cap was
  re-raised and #962 has regressed.
- grep -c "no route to deliver it" .gzkit/rules/agents-md-map-doctrine.md -> 1
- grep "0.10.0" in the advisory-rules-audit Coverage Ledger row for agents-md-map-doctrine.md
- uv run gz obpi lock list -> No active locks
- Remaining-count check: the 23 listed in Summary are all still OPEN except any the next
  context closes.

CAMPAIGN ACCOUNTING RECONCILED AGAINST GITHUB at context 1 open: all 24 were OPEN.
#815 carried stateReason REOPENED. Verified again at the #962 close: #961 CLOSED/COMPLETED
(2026-09-05), #815 OPEN/REOPENED, #922 OPEN, #921 OPEN, #851 OPEN.

## Evidence / Artifacts

HEAD at handoff authoring: 4d2bd3e3bf2e78cabf1175b86ca1f43a9a77dac5
origin/main at handoff authoring: 4d2bd3e3bf2e78cabf1175b86ca1f43a9a77dac5 (equal)
Branch: main. No feature branch was created (operator directive).
Active OBPI locks: NONE (uv run gz obpi lock list reports "No active locks")

Commits authored in context 1:
- b90d0484 fix(codex-cap-doctrine): close the class -- two live surfaces still claimed
  gzkit sets the Codex cap (GHI #962). 6 files, +24/-14. All pre-commit hooks passed;
  no --no-verify.
- 4d2bd3e3 chore(ledger,adr-0.35.0): take custody of a concurrent Codex session's
  ADR-0.35.0 artifacts. 6 files, +649/-9. See Decisions -- its framing of the
  authorization question is corrected in this handoff, and it captured a mid-authoring
  scaffold of brief 11.

ADR-0.35.0 state (uv run gz adr status, read at context 1): lane heavy, lifecycle
Pending, closeout phase pre_closeout, 5/11 OBPI, Closeout BLOCKED, QC PENDING.
Closeout blockers, all "ledger proof of completion is missing": OBPI-0.35.0-05, -06, -07,
-08, -10 (tracked defect GHI-737), -13. OBPI-0.35.0-09-codex-playback-wiring is
attested/completed and was confirmed terminal before routing #962 to direct fix.
NOTE: that 5/11 reading predates briefs 11 and 12 landing on disk; the Feature Checklist
carries 13 items (ADR body lines 346-359). The regenerated EVALUATION_SCORECARD reports
a checklist-count 13 versus OBPI-file-count 11 mismatch and weighted total 3.55 to 3.40.

ARB receipts for the #962 close, each resolved on disk with exit_status 0:
- artifacts/receipts/arb-ruff-e54535b479084bd9842bacf424eb0874.json
- artifacts/receipts/arb-step-typecheck-02cc92f08c2548f9877f94bf131a2232.json
- artifacts/receipts/arb-step-unittest-32656900482049ccbb4659311f39556f.json

Close comment: https://github.com/tvproductions/gzkit/issues/962

Working tree at handoff authoring: NOT CLEAN. Modified:
docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-11-corpus-shape-witness.md
docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-12-rules-corpus-onboarding.md
Both are the concurrent Codex session's completed brief authoring. See Pending, Blocker 2.

## Settled Rulings

725 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
