---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-02T04:22:17Z'
agent: claude-code
continues_from: 20260901T221120Z-ghi-premises-corrected-config-and-unstart-gaps-filed.md
---

## Current State Summary

Resumed `.gzkit/handoffs/20260901T221120Z-ghi-premises-corrected-config-and-unstart-gaps-filed.md` and worked its unruled items to completion. Six operator rulings landed; four commits. HEAD is `807891b0`, tree clean, `git rev-list --left-right --count origin/main...HEAD` returns `0 0`. No locks, no pipeline marker, no OBPI drawn, no TASK opened.

THE SESSION'S PATTERN IS THAT EVERY MEASURED PREMISE MOVED. Three of the four questions ruled on were argued from figures that measurement corrected, and in each case the correction changed the answer rather than refining it. The commit trailer was not "21% consistent" but a step function tracking a harness setting. The config surface did not have "44 registries with no owner" — it had 41, and 24 of them already had an owner, a loader and a fail-closed gate. GHI #815's remedy was not "reorder plus shrink" in equal measure — reorder alone recovers 82 percent.

The resumed handoff was itself partly stale on arrival: it recorded HEAD as `f9bea3e0`, but two commits had landed after it was written, one of which discharged an item it listed as open (GHI #533, closed COMPLETED at 22:51:49Z).

## Important Context

THE CAP-BREACH MEASUREMENT IS THE MOST CONSEQUENTIAL THING HERE AND IT IS NOT WHAT PRIOR SESSIONS RECORDED. Measured live 2026-09-01: 11,768 B of must-survive canon is NOT delivered under the codex cap — `operator-doctrine-verbatim-canon` straddles it losing 11,173 B, and `architectural-boundaries` starts at 46281 and is lost entire. A PURE REORDER CLOSES 9,766 B OF THAT, 82 percent, leaving 2,002 B. The prior framing ("reorder is necessary but not sufficient") is true but understates reorder so badly that it invites the wrong remedy. Re-derive with `uv run gz validate --instructions-files-budget`; these are dated records, not authoritative values.

THE GROWTH VECTOR IS WHY A ONE-OFF SHRINK IS A STOPGAP BY CONSTRUCTION. `AGENTS.md` went 38,407 to 46,876 B between 2026-08-19 and 2026-08-27 across five canon-seating commits (`3ac1c7d0`, `4a919af1`, `ee709fc8`, `a80ed283`, `2dece0ce`). The operator-doctrine section is now 13,921 B — 40 percent of must-survive — is invariant tier, and grows with every `gz content remember`. On 2026-08-17 must-survive was 23,678 B with 9,090 B of headroom and a reorder would have FULLY solved it; fourteen days later it is 34,770 B and over by 2,002 B.

THAT GROWTH IS WHAT REOPENED A STANDING RULING, AND THE DISTINCTION MATTERS. The parked reorder's deferral trigger fired on 2026-08-17 and the operator ruled the parking should STAND — against a breach of 595 B, one section. It is now roughly twenty times that and is mostly verbatim operator canon. The 2026-09-02 ruling is not a re-litigation of the 2026-08-17 one; it is the same question asked against a premise that moved twentyfold.

THE POOL ADR'S REJECTION OF THE FOLD WAS CONDITIONAL, AND THE CONDITION IS THE HINGE. `ADR-pool.render-order-truncation-survival` rejected folding into ADR-0.35.0 because that ADR's Intent scoped the generator and orchestrator, "not render-order policy", and warned that asserting absorption "without an operator ruling would be inventing a destination". The qualifier is what made the fold available once the ruling existed. ADR-0.35.0 Intent was amended to STATE the absorption rather than leave it assumed.

ABSORBED SCOPE RAISES THE BASELINE, NOT A SPLIT ADDER. A first attempt recorded the new unit as an Absorbed Scope line and `gz specify` refused it — the validator computes expected as baseline plus splits. The ADR's own 2026-08-02 amendment moved the baseline 7 to 9 for folded scope, so the convention was matched (9 to 10, target 13) rather than forked.

THE CONFIG GATE'S DESIGN TURNS ON A DISTINCTION THIS REPO KEEPS RE-LEARNING. `data/config_registry.json` records a VERIFIED owner: the validator reads the declared owner and confirms it actually references the registry. A registry that merely LISTED owners would be the presence-check-standing-in-for-a-state-check failure AGENTS.md forbids — which is also exactly what GHI #932, filed this session against `pointer_integrity.py`, is about. Two instances of one shape surfaced in one session; GHI #888 is a third.

THE SCAFFOLD-COMMENT TRAP COSTS A CYCLE IF YOU DO NOT KNOW IT. `src/gzkit/hooks/obpi.py` line 486 fails any section body containing the literal substring "one-sentence", and the OBPI scaffold's own Objective comment contains it. An authored brief keeps failing `gz obpi validate --authored` with a non-substantive Objective until that scaffold comment is deleted, no matter how substantive the prose beneath it. The same class bit this handoff: a backticked HTML comment in an Evidence bullet is stripped to an empty backtick pair, which breaks path parity and reports a phantom missing file.

INHERITED CAUTIONS THAT STILL BIND. A verifier piped into another process is refused by the verifier-pipe-gate hook — capture to a file and echo the real exit. `uv run gz validate --transcribed-adr-counts` refuses a live ADR count transcribed into a handoff; cite `uv run gz adr status`. In zsh, a `$sha:AGENTS.md` expansion treats the colon-A as a path modifier — quote it or git reports 0 bytes for every revision.

## Decisions Made

- [operator-ruled] The commit-trailer set is CLOSED; a `Claude-Session:` trailer is never authored (verbatim: "Never"). Selected from a three-option picker after measurement showed a step function rather than a consistency rate. Landed as `7a375cf1`.
- [operator-ruled] GHI #929 routes to DIRECT REPAIR under the GHI, not a chore and not a config feature ADR (verbatim selection: "Direct repair under the GHI"). Ruled after the premise correction showed the pattern already existed in-repo. Landed as `450acbbf`; #929 closed.
- [operator-ruled] The render-order reorder is FOLDED INTO ADR-0.35.0 as checklist item 13, not promoted (verbatim selection: "Fold into ADR-0.35.0 as an OBPI"). Landed as `34122739`; OBPI-0.35.0-13 authored, not drawn.
- [operator-ruled] The residual 2,002 B is closed by the instructions-files-diet chore, NOT by re-ratifying the must-survive rank threshold (verbatim selection: "Shrink via the diet chore").
- [operator-ruled] GHI #930 is FOLDED INTO #611 rather than designed as a standalone un-start verb (verbatim selection: "Fold into #611"). Both GHIs cross-commented; #930 stays open as a cut of #611.
- [operator-ruled] OBPI-0.35.0-08 keeps its Active status and is ANNOTATED in place (verbatim selection: "Annotate the brief, leave the state"). Direct path, no lock, marker, TASK or dispatch, on the OBPI-0.35.0-01 precedent.
- [agent-chose] Filed the pointer-integrity defect as TWO GHIs (#931, #932) rather than one. They are opposite polarity — #931 produces false FAILURES, #932 produces false PASSES — which is two failure families under the one-GHI-one-class rule.
- [agent-chose] Matched the existing root-relative convention for the anchored lift pointer instead of fixing pointer_integrity.py in flight. Fixing it would invert which of two live conventions is legal and require converting three other files; tracked as #931 rather than forked silently.
- [agent-chose] Collapsed the six uniform rungs of `_dispatch_early_return_scopes` into a dispatch table when the added scope tipped it from C to D on xenon. Kept the inventory resolution lazy inside the branch so the table does not import that module on every dispatch.
- [agent-chose] Declared `data/frontier_model_cards.json` as doc-kind owned by CLAUDE.md rather than asserting a code owner. It has NO code reader; recording that honestly is the point of a verified-owner field.
- [agent-chose] Did NOT author briefs for ADR-0.35.0 checklist items 11 and 12. They have no briefs and that is a pre-existing 1:1 Synchronization Mandate drift, but authoring them is OBPI initiation reserved to the operator.
- [agent-chose] Corrected a concern raised in flight rather than letting it stand: the harness trailer was hypothesised to suppress the Task auto-stamp, and an empirical test against `has_task_trailer` showed it does not. The rule file's claim that an authored trailer of ANY form suppresses the stamp was false and was repaired in the same commit.

## Immediate Next Steps

1. RULE THE ATTESTATION DISPOSITION FOR THE RENDER-ORDER PERMUTATION BEFORE OBPI-0.35.0-13 IS DRAWN. The brief carries this as an OPEN OPERATOR QUESTION, deliberately unresolved. The pool ADR's constraint 2 requires operator Gate-5 attestation because it is a Layer-1 canon change; the attestation-granularity ruling of 2026-08-17 says a rerender of unchanged canon requires none, and an order-only permutation preserves every entry byte-identical. The two point different ways and only the operator can rule.
2. DRAW OBPI-0.35.0-03 OR OBPI-0.35.0-13 IF EITHER IS TO BE WORKED. ADR-0.35.0 is TOPMOST in the campaign. OBPI-0.35.0-03 is the brief in flight per the 2026-09-01 ruling. Only the operator initiates OBPI work.
3. RULE ON GHI #931 AND GHI #932, THE POINTER-INTEGRITY PAIR. Both carry blocker comments naming the next concrete action. #931 passes every direct-fix threshold but has a coupled surface of three link conversions; #932 is not a clean direct fix and its remediation surface should be measured before routing.
4. GHI #927 AND GHI #928 REMAIN ANSWERED-BUT-UNRULED, now across six sessions. ~~Agent recommendations are recorded on each: bind the falsifiability witness on the COMMIT via an ARB receipt for #927; REMOVE the ADR-checklist tick rather than regenerate it for #928.~~

   > **AMENDED 2026-09-02 — the struck sentence was false in both halves, and the successor session verified it against the issues before acting on it.** Neither GHI carries an agent recommendation. #928's body says verbatim *"Recommending neither."*; #927's blocker comment enumerates routes (a)/(b)/(c) and recommends none. Worse, the recommendation attributed to #927 — bind the witness on the COMMIT — is that issue's **direction 2**, which its own comment records as refuted: *"a diff-shape proxy that passes the very commit that motivated this issue"* (`3c255459` touched twelve test files while adding an undriven guard). A session trusting this line would have implemented the one option the evidence had already ruled out. The #928 half landed on the same disposition the operator later chose, but by coincidence of reading, not because anything recorded it.
   >
   > **Both are now ruled and discharged.** #927 folded into #849 as widened scope — open as a cut, both cross-commented. #928 fixed at `8db5e54f` and closed: disposition 2, implemented as freeze-the-box-empty rather than bracket deletion, because the checkbox also demarcates rows and 128 of 546 carry no OBPI id. Filed alongside: **#933**.
   >
   > Recorded as an amendment rather than a rewrite, because a handoff is a session record and the error is the point. This document's own § Current State Summary warns that *"every measured premise moved"*; this line is one more instance of it — a claim about two artifacts, written without reading them back.

5. DECIDE WHETHER ADR-0.35.0 CHECKLIST ITEMS 11 AND 12 GET BRIEFS. The ADR now carries 13 checklist items against 11 briefs. Items 11 (GHI #922) and 12 (GHI #921) have never been decomposed; the work is tracked by those GHIs but the 1:1 Synchronization Mandate is drifted.

## Pending Work / Open Loops

NOTHING UNPUSHED. `0 0` against origin, tree clean, no locks, no pipeline markers, HEAD `807891b0`. This session leaves no in-flight code work.

OPEN AND FILED THIS SESSION: GHI #931 (pointer-integrity resolves relative lift pointers against the repo root, so the only accepted form is a link broken in every markdown viewer) and GHI #932 (its back-pointer check is a bare file-level substring test, so any lifted-from comment satisfies every pointer into that file). Both carry blocker comments. #932 is the same shape as #888, cross-linked at authoring.

OPEN AND RE-MEASURED: GHI #815. The destination now exists as OBPI-0.35.0-13 but the work is undrawn, so the issue stays open until the witness reports zero must-survive sections past the cap.

OPEN AND FOLDED: GHI #930 into GHI #611. #930 stays open as a cut; it closes superseded when #611's destination artifact is authored. #611 has no destination artifact yet — a pool ADR was considered and NOT authored, because Architectural Boundary 2 says do not add more pool ADRs to the runtime track.

STUCK BY CONSTRUCTION, DELIBERATELY: OBPI-0.35.0-08 reads Active. It is now annotated so no agent reads that as a legitimate draw, and it is the only live reproduction of #930's missing transition edge.

PRE-EXISTING 1:1 DRIFT: ADR-0.35.0 carries 13 checklist items and 11 briefs. Untouched this session except that item 13 was added WITH its brief, so the gap did not widen.

PRE-EXISTING AND UNTOUCHED: the quality gate reports unlinked specs as advisory drift, and tautological operations stand outstanding behind GHI #808's green criteria.

UNSWEPT, deliberately: the sibling transition tables in `src/gzkit/core/lifecycle.py` were never checked for the same forward-only shape #930 names. The 17 policy registries now have owners, but no sweep was run for further two-registries-one-concept pairs beyond the vendor-manifest and instructions-files-budget pair now related symmetrically.

## Verification Checklist

Run these before trusting any claim above.

`git rev-list --left-right --count origin/main...HEAD` expects `0 0`. Anything else means work landed after this document was written — that was true of the predecessor and cost it a stale HEAD claim.

`git log --oneline -4` expects `807891b0`, `34122739`, `450acbbf`, `7a375cf1`.

`uv run gz obpi lock list` expects no active locks.

`uv run gz check` expects exit 0. Advisory spec-test-code drift on unlinked specs is expected and pre-existing.

`uv run gz validate --config-registry` expects exit 0 and a verified-owner green line. To prove the gate is not theater, write any `data/zz_probe.json` and re-run: it must exit 3. Delete the probe afterwards.

`uv run gz validate --instructions-files-budget` expects exit 0 with three advisory warnings. The byte figures it prints are the live measurement; every figure quoted in this document is a dated snapshot.

To re-derive the must-survive total rather than trust it, compute section spans with the `section_id` helper in `src/gzkit/content/parse` over the rendered level-two headings of `AGENTS.md`, sum the ids ranked at or below the must-survive threshold in `data/agents_md_survival_declaration.json`, and compare against the codex cap in `data/vendor-manifest.json`.

`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for lifecycle and landed count. Do NOT trust a count transcribed into any document, this one included — `uv run gz validate --transcribed-adr-counts` exists for that reason. Expect items 03 and 08 both in progress; 08 is annotated residue, not a draw.

`uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-13-render-order-truncation-survival.md` expects exit 0.

`gh issue list --state open --limit 100` re-derives the queue rather than trusting a count. Expect 34 unless the operator has ruled since.

`uv run gz handoff rulings --search "<topic>"` checks the settled corpus before re-arguing anything.

## Evidence / Artifacts

Commits landed this session:

- `7a375cf1` docs(rules): close the commit-trailer set and correct the auto-stamp clause
- `450acbbf` fix(config): give the policy/threshold registry family an owner and a gate (GHI #929)
- `34122739` docs(adr): absorb render-order scope into ADR-0.35.0 as item 13 (GHI #815)
- `807891b0` chore(adr-status): regenerate the derived index for ADR-0.35.0 item 13

Surfaces created:

- `data/config_registry.json` — 19 declared registries, each with a verified owner, a kind, and symmetric relates_to
- `src/gzkit/governance/trust_audits/config_registry.py` — the four-arm declaration gate
- `tests/governance/test_config_registry.py` — 8 tests, one per arm plus a live-tree assertion
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-13-render-order-truncation-survival.md` — authored, passing the authored gate, NOT drawn

Surfaces changed:

- `.gzkit/rules/task-discovery.md` — 0.7.1 to 0.8.0, closed trailer set plus the suppression-clause correction
- `docs/governance/rule-version-history.md` — 0.8.0 entry carrying the per-day trailer measurement, plus the lifted-from back-pointer the fidelity audit requires
- `docs/governance/advisory-rules-audit.md` — Coverage Ledger row to 0.8.0
- `docs/user/manpages/validate.md` — the config-registry flag section
- `src/gzkit/commands/validate_cmd.py` — new scope, handler, and the dispatch-table collapse
- `src/gzkit/qc_binding.py` — the step classified bound
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — the negative control the bound classification requires
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — Intent absorption, checklist item 13, BI-09, scorecard baseline 9 to 10
- `docs/design/adr/pool/ADR-pool.render-order-truncation-survival.md` — marked ABSORBED so the scope is not double-owned
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md` — annotated as residue

GHIs authored this session, both with blocker comments naming the next concrete action:

- GHI #931 pointer-integrity: relative lift pointers resolved against the repo root
- GHI #932 pointer-integrity: back-pointer check is a bare substring test

GHIs updated: #929 (premise correction, then closed), #815 (remedy measurement and destination), #930 and #611 (the fold), #888 (cross-link to #932).

## Settled Rulings

652 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
