---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-25T01:05:46Z'
agent: claude-code
---

## Current State Summary

Resumed the 2026-07-24T11:49Z handoff under explicit operator authorization and worked the degrading triage tier to completion. Closed GHI #696 (all five defects) across two commits this session: d96a81cd landed defect 2, the step-reference verification seam; 33a36de0 landed defects 3 and 4, settled-ruling carry-forward and decision attribution. Closed GHI #614 (ae233bbd) with miner run telemetry. GHI #580 stays open: I built its ordering policy, measured it against live AGENTS.md, and the measurement refuted the signal the GHI proposes, so nothing shipped. Open GHI count 16 to 14. Tree clean, main synced at 33a36de0 plus the lineage-coherence fix in this commit. No active OBPI lock, no in-flight ADR or pipeline.

## Important Context

REPRODUCE-BEFORE-TRUSTING paid for itself three times, and every payment was a STALE BLOCKER. #614's blocker (2026-06-13) routed it to OBPI ceremony; the operator canon 'GHIs are AUTHORIZED for direct repair, always' landed 2026-06-16 in dbaa9b94, THREE DAYS LATER, so the blocker's decisive claim was written under the prior rule. #580's blocker named a destination (new OBPI under ADR-0.0.37) that became impossible when ADR-0.0.37 went terminal 2026-07-18 (Split-and-Supersede). #696's blocker deferred defects 3/4 to an unbuilt ADR on the same ceremony reasoning the canon overrides. A GHI blocker comment describes the tree on the day it was written and carries no freshness signal; #696 mechanizes that check for handoffs and NOTHING does it for GHI blockers. Two attested Boundary Invariants constrained #614 and one CONTRADICTED the GHI's own proposal: BI 2 fences the miner to write only to its proofs directory, so the proposed .gzkit/sensors/ location would have violated attested canon; BI 3 pins the module stdlib-only, so the run record is a plain dict not Pydantic; and attested REQ-0.70-02-08 fences --dry-run to write nothing, which is why telemetry lands on write runs only. For #696, Settled Rulings had to be OPTIONAL: run_handoff_document_audit validates every post-cutover entry in .gzkit/handoffs/, so a new REQUIRED_SECTIONS member would fail the entire corpus.

## Decisions Made

- [operator-ruled] Work the degrading tier starting with #696 (verbatim authorization booked via gz handoff authorize, session 81765765).
- [operator-ruled] Finish what is on the plate rather than deferring items for later sequencing rulings.
- [operator-ruled] Do not assert campaign-movement intent without reading it; the claim that Movement C is shrinking the pre-1.0 board was fabricated and is withdrawn. Movement C is Reduce the accretion.
- [operator-ruled] #696 defect 2 was the buildable cut; defects 3/4 were NOT to be left to an unbuilt ADR.
- [agent-chose] Routed #696 defects 3/4 and #614 as direct fixes under the GHI-direct-repair canon rather than authoring any ADR or OBPI, leaving campaign Movement D box 3 its full scope.
- [agent-chose] Made Settled Rulings self-populating by construction instead of a hand-filled section, which answers the prior sessions' objection rather than overriding it.
- [agent-chose] Put #614's run log in the miner's proofs directory instead of the GHI-proposed .gzkit/sensors/, to honor attested Boundary Invariant 2.
- [agent-chose] Deleted the #580 criticality module rather than commit a mechanism whose only signal produces a worse ordering than the status quo.

## Immediate Next Steps

1. Rule on #580's criticality signal: it must be operator-declared per section. Measurement proved Bullet.classification and Bullet.witness cannot serve, because gzkit's most binding material (the Attestation canonical-invocations table, the Defect-fix routing thresholds table) is TABLES not bullets and therefore ranks 0. Two hard constraints are recorded on the issue for whoever picks it up.
2. Decide #580's destination. ADR-0.0.37 is terminal so its recorded route is void, and ADR-0.35.0's Intent scopes the corpus-to-candidate generator and gz content land, not render-order policy. My prior pool recommendation rested on the withdrawn Movement C claim and should be re-derived, not reused.
3. Consider mechanizing GHI-blocker freshness. Three stale blockers were found by hand this session; #696 fixed the same decay class for handoffs and the GHI surface has no equivalent.
4. Resume the latent tier from .gzkit/cache/triage/rank.json if the campaign does not take precedence. #607 remains GOVERNANCE-PARKED and needs an operator ruling on attested REQ-0.14.0-04-04 before any code is touched.
5. The campaign RULES sequencing: Movement A is topmost (ADR-0.35.0 at 0/9, ADR-0.34.0 capstone at 1/5). This tier was operator-authorized triage work, not a campaign amendment.

## Pending Work / Open Loops

GHI #580 open with the refutation recorded and no registered destination; needs an operator-declared criticality signal. GHI #607 governance-parked, unchanged, needs the REQ-0.14.0-04-04 ruling plus an advisory channel in the validate framework. GHI #641 (Movement IV), #594 (post-release design), #581 and #615 remain annotated-deferred from prior sessions. #611 stays open as the append-only corrective-action primitive sharing #696's mechanism; #575 is the positive-proposal cut of #614's surface and is untouched. Latent tier (ranks 5-16 in rank.json) unworked by design. Campaign Movement D box 3 retains its full scope: typed ruling_issued/ruling_superseded events, a gz ruling verb, and the campaign body as a rendered Layer-3 view; the two handoff sections added this session become projections of those events when they land. No active OBPI locks, no blockers. Four course-correction insights logged.

## Verification Checklist

gh issue view 696 614 --json state (both CLOSED); gh issue view 580 --json state (OPEN, refutation recorded); git log --oneline d96a81cd~1..HEAD (session commits d96a81cd / ae233bbd / 33a36de0 plus this handoff commit); uv run gz handoff resume (renders 4 steps with per-reference live state, was 1 before d96a81cd); uv run python -m gzkit.insights.correction_mining --dry-run (reports scanned/matched/cluster counts, not a bare 0 cluster line); uv run python -m unittest tests.governance.test_handoff_api tests.test_handoff_cli tests.chores.test_session_correction_mining (49 plus 21 green); uv run -m unittest -q (expect 7369 or more OK); uv run gz check (expect exit 0).

## Evidence / Artifacts

Session commits: d96a81cd (#696 defect 2), ae233bbd (#614), 33a36de0 (#696 defects 3/4). Changed surfaces: `src/gzkit/handoff_api.py`, `src/gzkit/commands/handoff.py`, `src/gzkit/handoff_validation.py`, `src/gzkit/insights/correction_mining.py`, `.gitignore`. Docs: `docs/user/manpages/handoff-resume.md`, `docs/user/manpages/handoff-create.md`, `.gzkit/chores/session-correction-mining/CHORE.md`. Skill 6.15.0 to 6.17.0: `.gzkit/skills/gz-session-handoff/SKILL.md`, `.gzkit/skills/gz-session-handoff/assets/handoff-template.md`. Tests: `tests/governance/test_handoff_api.py`, `tests/test_handoff_cli.py`, `tests/chores/test_session_correction_mining.py`. Insights: `.gzkit/insights/agent-insights.jsonl`. Triage cache: `.gzkit/cache/triage/rank.json`. Receipts: arb-step-unittest-bac122aa33ac4695aeef54b606b3626a, arb-ruff-f157b77aedd94062b4ee612a7767064b, arb-step-typecheck-78a804871707450e9a500af17087fb82.
