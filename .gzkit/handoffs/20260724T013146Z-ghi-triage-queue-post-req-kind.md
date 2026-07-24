---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-24T01:31:46Z'
agent: claude-code
---

## Current State Summary

Cleared the req_kind.py GHI cluster (5 closed) plus a Dependabot security bump, all pushed to main with pre-push 'gz check' green each time. Then ran /ghi-triage: 23 GHIs remain OPEN (the queue was NOT drawn down — the cluster was only the prior handoff's named subset). Tree clean, synced (ahead=0 behind=0), HEAD=ecacb309. Next work is the triage-ranked queue, headed by two blocking fail-closed validator states (#565, #682).

## Important Context

This session worked the ranked open-GHI queue as direct-fixes under operator canon (GHIs route direct-fix + close-citing-SHA; no OBPI ceremony for defect repair). The req_kind cluster #547/#546/#652/#545/#551 is complete. A fresh /ghi-triage ranked the remaining 23 open GHIs into .gzkit/cache/triage/rank.json. All 23 route direct-fix (279 fix() commits of 60-day precedent). No active ADR/OBPI is in flight. Per the Build-to-1.0 campaign, the next Magna Carta item once the defect queue is drawn down is ADR-0.35.0 (canon-entry-corpus-landing, 0/9 OBPIs).

## Decisions Made

Forks resolved this session (capture rich per #696): (1) #547 suite-invariance REQs are STRUCTURAL-FENCE, not SUPPORT (operator ruling) — proof channel is a parent-ADR ## Boundary Invariants entry. (2) #546 DOCUMENT the validate/covers bypass asymmetry rather than add a flag — 'gz validate --req-kind-discipline' stays a strict read-only CI gate with no ledger-write; the bypass lives on gz covers (completion flow). (3) #545 RETIRE (resolution B'), not wire (A): verification showed CoverageEntry is a COMPLETE superset of ReqCoverageRecord/Summary and is already the wired 'gz covers --json' output, so the A/B premise inverted on verification — retired the parallel duplicate + its 7 isolation tests, annotated OBPI-0.0.59-03 REQ-03-03 superseded. (4) #551 is a CORRECTION (doc catch-up), landed via the ADR-0.0.34 rendition path: gz content compose then gz content commit (operator-attested g0), then gz governance render regenerated AGENTS.md. (5) CORRECTION internalized (operator): GHIs carry NO attestation ceremony — the attestation on #551 attached to the CONTROL-SURFACE change (gz content commit is Gate-5 by the tool's deterministic contract), never to the GHI. (6) Triage severity model: #565/#682 = blocking (active fail-closed validator states); the middle run = degrading direct-fix defects; enhancements = latent.

## Immediate Next Steps

1. #565 (blocking): fix 40 active-brief Verification compound-command shell-less-contract violations — reproduce with 'uv run gz validate --brief-command-shape' (template .gzkit/templates/obpi.md, briefs.py). 2. #682 (blocking): 2 post-cutover briefs fail 'uv run gz validate --sensitivity' floor over security-surface overlap — declare 'sensitivity: security' or grandfather (data/sensitivity_floor_grandfather.json). 3. Then the degrading direct-fix run in rank order: #532 (broken manpage ref gz-validate.md->validate.md), #650 (MX marker path code .gzkit/mx.json vs docs .gzkit/mx-active), #665, #641, #696, #615, #581, #577, #573, #669, #607, #614. 4. Latent enhancements last: #611 #594 #691 #579 #580 #670 #567 #533 #644. 5. Re-run /ghi-triage after any batch of closes. Full ranked list: .gzkit/cache/triage/rank.json.

## Pending Work / Open Loops

None blocking. #533 is blocked on ADR-0.0.37 completion (5k AGENTS.md budget target). #611 (general corrective-action primitive) and #644 (test-scale strategy) are design-shaped — escalate GHI->ADR (never GHI->OBPI), operator decision. #696 itself flags handoff decision-state loss (authored 3-5 next steps, consumed 1); this handoff counters it by capturing the full decision set above. 5 Dependabot alerts (#8-#12) still read 'open' pending GitHub's async re-scan of the pushed lockfile — the fix landed in ecacb309 (gitpython 3.1.55, setuptools 83.0.0).

## Verification Checklist

gh issue view 547 546 652 545 551 --json number,state (all CLOSED); git log --oneline ecacb309~7..ecacb309 (session commits); uv run python -m unittest discover -s tests -t . -q (expect 7316 OK); uv run gz validate --brief-command-shape (reproduces #565's 40 errors); uv run gz validate --sensitivity (reproduces #682 exit 3); uv run python .claude/skills/ghi-triage/scripts/triage.py --format rank --rank-input .gzkit/cache/triage/rank.json (re-render the 23-item ranking).

## Evidence / Artifacts

Session commits: #547 d2f0b1b4, #546 a38b1a37, #652 4960daef, #545 d5052460, #551 29ba3823, state 17969919, deps ecacb309. HEAD=ecacb309, branch main, synced. Full suite 7316 tests OK; typecheck receipts arb-step-typecheck-*; pre-push 'gz check' green on all 3 pushes. Rank input: .gzkit/cache/triage/rank.json (23 GHIs, 2 blocking / 12 degrading / 9 latent). Insights logged to .gzkit/insights/agent-insights.jsonl (2026-07-24): #545 verify-premise-before-forking + GHIs-carry-no-attestation-ceremony.
