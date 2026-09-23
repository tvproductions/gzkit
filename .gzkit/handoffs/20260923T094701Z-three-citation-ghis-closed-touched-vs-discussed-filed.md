---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-23T09:47:01Z'
agent: g0
continues_from: 20260923T025538Z-ieee-phase3-complete-all-questions-ruled.md
---

## Current State Summary

Three GHIs fixed and closed this session (#1082, #1083, #1081), one filed and OPEN (#1084). The IEEE Phase 3 work is unchanged from the prior handoff and remains COMPLETE with all fifteen questions ruled; the only register change since was reconciling a parallel agent's Dex Horthy deposit, which moved no finding status. PHASE 4 REMAINS UNAUTHORISED. Tree clean, main level with origin at f58f27f5b.

## Important Context

This handoff continues 20260923T025538Z, which remains the record for the IEEE Phase 3 closeout; do not re-derive that work here. WORKFLOW FRONTS (campaign docs/governance/build-to-1.0-campaign-2026-09-20.md, section Workflow fronts): ghi triage advanced - three closes and one file; the other three fronts (handoff system, adr/obpi campaign, new R&D) are untouched. ADR-0.35.0 remains campaign TOPMOST with closeout BLOCKED under GHI #930. THE THREE FIXES ARE ONE FAMILY, which is why they are worth reading together: each is a citation or pointer whose evidence did not witness its claim. #1082 - handoff next steps dropped when a preamble preceded an inline enumeration. #1083 - governance prose citing src/gzkit paths that do not resolve. #1081 - commit anchors shape-checked, never resolved. #1084 is the residue of #1081: an anchor that DOES resolve but names an artifact the commit never touched. TWO STANDING CAUTIONS carried unchanged: D-01 (F-006) and D-05 (F-021) are UNRESOLVED disagreements on load-bearing findings and must not be read as settled; and an OPEN finding row is settled under Q-14 but NOT confirmed - nothing challenged it.

## Decisions Made

[operator] Fix #1082, then #1083, then #1081, each closed with evidence. [operator] Allow gh issue comment in .gzkit/rules/gh-cli.md - landed as rule version 0.6.0 with the 0.5.2 note lifted to rule-version-history.md and the Coverage Ledger row bumped. [operator] Accept the parallel agent's Dex Horthy deposit and reconcile it against the register. Verified mechanically rather than on its word: the status distribution is unchanged across 35 rows, so its claim that no finding gains a status from that testimony holds. [operator] File the touched-vs-discussed gap as a GHI - now #1084. [agent] #1083's filed invariant was AMENDED before implementation: 'every cited path resolves' was too strong, because an unexecuted spec legitimately names a module it proposes to build. Four exemption categories, not two. [agent] #1081's framing was corrected on the issue: the truncation is a SECOND DEFECT, not a second symptom - the aliased id resolves successfully, so the existence check alone would have passed it. Its negative control arithmetic was also corrected; the original scan read git show, which includes the commit message carrying the bad trailer itself.

## Immediate Next Steps

Nothing is REQUIRED next. Everything below is available without entering Phase 4.
1. Decide #1084's route before building anything: relabelling the trailer to 'Governance anchors referenced:' makes today's behaviour honest for about five lines, where path-derivation is about a hundred. The issue records both estimates and argues the relabelling should be weighed FIRST. What 'touched' means is genuinely unsettled - a commit implementing an OBPI's REQ touches that OBPI's subject while touching none of its files.
2. Run a measurement item from M-A to M-H (README.md section The measurement program). M-H is DISCHARGED; seven outstanding. M-B settles D-03, M-C bears on D-01, M-G settles D-04. M-F is independent and cheap and is the home of D-08. M-D is gated on its own method problem and must NOT be started until that is settled.
3. Decide whether a finding should be authored for D-08, and for the three independently observed D2 rows in consequence-bands.md.
4. Decide whether to lift PROVISIONAL from consequence-bands.md. No band moved during reconciliation, but the file rests partly on F-021, which is DISPUTED.
5. Phase 4 requires EXPLICIT OPERATOR AUTHORISATION and the full triad when it opens.
Unrelated and untouched: the version_sync kind guard (GHI-sized, unblocked) and ADR-0.35.0 closeout, BLOCKED under GHI #930.

## Pending Work / Open Loops

GHI #1084 is OPEN, eligible and unselected - authored only, per the ghi-author invocation boundary. RESIDUE RECORDED, NOT FIXED, on closed issues: shape plus existence still does not mean 'touched' (#1084 carries it); a cited path:line that resolves to the WRONG lines is still unchecked, since #1083 [settled]'s arm is deliberately the existence half only; and fenced-block distinction in the commit-anchor scanner was deferred from #1081 [settled] and may be subsumed by whatever #1084 resolves to. D-01 and D-05 remain UNRESOLVED standing conditions, not open tasks. Agent 2 Act 2 does not exist until Phase 4 is authorised, and Act 1 cannot be retaken. A CONCURRENT SESSION was writing to this branch during this one; it committed 01dba0857 and 2c12285dc. Its work was accepted by operator ruling and reconciled, but a resuming agent should not assume it is the only writer.

## Verification Checklist

uv run gz check exits 0 - verified on the tree of each fix commit, reading REAL EXIT immediately after the verifier, never a notification's exit code. uv run ruff check and ruff format --check exit 0 across src/ and tests/. Working tree clean and main level with origin at f58f27f5b, verified with git ls-remote rather than a sync's exit status. FINDINGS.md holds 35 rows: 2 CONFIRMED, 15 QUALIFIED, 2 DISPUTED, 14 OPEN, 2 REJECTED - unchanged by the Dex Horthy reconciliation, which is how that deposit's boundary claim was checked. Re-derive any figure rather than trusting one transcribed here.

## Evidence / Artifacts

Commits: f34f7be23 (#1082 handoff next-step extractor); 394da5969 (gh-cli.md 0.6.0); 216e404ec (Dex Horthy reconciliation); 074a8a504 (#1083 doc code citations); f58f27f5b (#1081 commit anchor resolution). Issues: #1082, #1083, #1081 CLOSED with evidence; #1084 OPEN. ARB receipts cited in each close were resolved on disk before quoting; they live under artifacts/, which is gitignored - F-022's durability finding, which is why they are checked rather than trusted. Register: docs/governance/ieee/ - README.md is the entry point and now carries the measurement program, the binding-terms section, and the Dex Horthy register-level mapping.

## Settled Rulings

1028 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
