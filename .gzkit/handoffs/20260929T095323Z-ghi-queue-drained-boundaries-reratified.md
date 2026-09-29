---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-29T09:53:23Z'
agent: claude-code
session_id: 0be90540-45e2-41fb-b0e1-6db00f8ffcde
continues_from: .gzkit/handoffs/20260929T072302Z-ghi-queue-step1-landed.md
---

## Current State Summary

Resumed the ghi-queue handoff (operator: 'yes, proceed as recommended'). Closed with evidence: #832 (d109230fc: 22 tags were already reachable; waiver 34->12; audit now refuses stale exemptions), #968 (a33932761: reviewer descriptions aligned on all three surfaces), #818 (abc81677e: Architectural Boundaries re-ratified in the AGENTS.md corpus, 1-3 retired, 4-6 kept with witnesses), #871 (4d230eec0: corrections to a Validated ADR exempt from strict order, canon at five skill carriers plus Magna Carta amendment 2026-09-29), #1063 (0bd4268e9: both ratchets are gz check steps), #803 (d266be9ff: dead links fail closed; docs gate asserts its mkdocs validation floor), #927 (79ae773f2: gz arb red --commit, commit-keyed falsifiability witness). #611 (b)(c) applied via gz ledger correct; (a) still held. ADR-0.35.0 justify walkthrough written (96b43cef1), so its OBPI launches are unblocked. main is 0/0 with origin.

## Important Context

Another session is active in the main checkout: it staged .gzkit/handoffs/20260929T091935Z-session-exit-bookmark.md and docs/governance/ieee/* (incl. FAA-AR-08-32.pdf); they were never included in this session's commits (pathspec commits, worktree pushes). The ascending-order ruling lives verbatim in five skills (gz-obpi-pipeline, gz-adr-create, gz-design, gz-plan, gz-status) since GHI #921, not in root AGENTS.md; an invariant corpus entry for it would force it back into the root contract. .gzkit/renditions/AGENTS.md/codex.md is a sealed record by OBPI-0.35.0-09 Req 4a, not a leftover. gz validate --evaluation-justify-binding still flags terminal ADR-0.33.0 (insight recorded). Subagent worktrees under .claude/worktrees/ (agent-a65628323286b1c2a, ratchets-1063) can be removed. The verifier-pipe-gate hook refuses a verifier that is not the last statement; zsh does not word-split unquoted variables.

## Decisions Made

- [operator-ruled] Boundary 1 retired: 'I am not sure that this post 1.0 matters. I have since adopted a magna carta to govern current major release prioritization [elided] there is almost zero liability in keeping an ADR in the pool.'
- [operator-ruled] Boundary 2 retired with a tracked obligation: 'retire it, we can allow items in the pool without almost any limit. what we need, if we don't have it yet, is a skill/process that allows us to review the pool for triage (selection for promotion) in a manner that is similar to the ghi-triage skill/chore.'
- [operator-ruled] Boundary 3: 'on boundary 3, retire as fulfilled. also, we want to ensure that the ontology is mature enough. I am still considering graphify (a queryable knowledge graph) to augment this.'
- [operator-ruled] Boundary 4: 'keep it, name the witness'.
- [operator-ruled] Boundary 5: 'keep it, drop the phase condition.'
- [operator-ruled] Boundary 6: 'keep it, name the witnesses'.
- [operator-ruled] GHI #818 destination: 'yes, drop the ADR and use the corpus' (supersedes 'Pool ADR now').
- [operator-ruled] GHI #818 corpus attestation: 'attest: drop C1, C2, C3 as retired; keep 4–6 with witnesses'.
- [operator-ruled] GHI #871 vehicle: 'canon plus campaign'; corpus attestation: 'attest to this edit'.
- [operator-ruled] GHI #1063: 'Add both ratchets to gz check'.
- [operator-ruled] GHI #803 required level: 'A' (warn).
- [operator-ruled] GHI #927 ownership: 'A' (#927 owns it; #849 stays closed).
- [agent-chose] Landed #803 with the bullet_retention link-target loosening after the operator said 'after #803 lands, start #927' without choosing A or B; stated as reading A. Revert on the operator's word.
- [agent-chose] #1063 and #803 were built by worktree subagents and landed by pushing their commits from the worktree after verifying gz check, because the main checkout held another session's staged files.

## Immediate Next Steps

1. Ask the operator to amend OBPI-0.35.0-10's brief for the GHI #939 retention-scope fold, then close #939 superseded.
2. Remind the operator of GHI #802 (GitHub Pages custom domain and DNS) before re-measuring.
3. On the operator's initiation, author the correction ADR re-homing the two handoff_api.py findings (Magna Carta amendment 2026-09-29), parented on ADR-0.0.65.
4. Ask whether to file a GHI for the evaluation-justify-binding gate flagging terminal ADR-0.33.0 (currently an insight).
5. Offer to remove the two finished subagent worktrees under .claude/worktrees/.

## Pending Work / Open Loops

Pool promotion-triage facility owed by ADR-pool.pool-management section 9 (operator requirement 2026-09-29). #611 clause 4 and held item (a). #1149 and #1125 open. Insights recorded, not yet GHIs: justify-binding gate on terminal ADRs; gz obpi precomplete has no manpage; GovZero docs cite AirlineOps-era ADR-0.0.21/0.0.25 numbers; graphify and ontology maturity under ADR-pool.artifact-graph-navigation; moving the AirlineOps parity skill into airlineops. docs-build anchors/absolute/unrecognized links remain at info with no floor (operator call).

## Verification Checklist

uv run gz check (expect exit 0); git rev-list --left-right --count origin/main...HEAD (expect 0 0); gh issue view 927 --json state (expect CLOSED); uv run gz validate --evaluation-justify-binding (expect exit 3, only ADR-0.33.0); uv run mkdocs build --strict (expect exit 0).

## Evidence / Artifacts

Commits: d109230fc, a33932761, abc81677e, 96b43cef1, 4d230eec0, 0bd4268e9, d266be9ff, 79ae773f2. Files: `src/gzkit/commit_witness.py`, `tests/test_commit_witness.py`, `artifacts/justify/OBPI-0.35.0-08-20260929T082757Z.md`, `docs/design/adr/pool/ADR-pool.pool-management.md`, `docs/governance/build-to-1.0-campaign-2026-09-20.md`.

## Settled Rulings

1211 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
