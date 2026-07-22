---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-22T11:22:35Z'
agent: claude-code
session_id: 9d05f608-b4bb-4301-b798-5c4772b8337b
continues_from: .gzkit/handoffs/20260721T114824Z-ghi-triage-2026-07-21.md
---

## Current State Summary

Session scope was a git-sync only, per operator ruling 'sync only — do not work the handoff's GHI list'. Four commits pushed to origin/main (c32f9b3d, fc4fa00f, dcf29b95, 48a5f799); local and remote converged at 0/0, tree clean. No governance work was performed. This handoff supersedes the 2026-07-21 GHI-triage handoff, whose advised step 1 is now void: that step directed the next session at the corpus-spine pair GHI #654 and #635, and both verified CLOSED via gh issue view, alongside #623.

## Important Context

Handoffs are append-only; a stale one is superseded by a successor carrying continues_from, never edited in place, because load_handoff_chain reconstructs lineage from that link. Two divergences surfaced during claim verification and are the reason this handoff exists beyond the supersede. First, session orientation reports ADR-0.35.0 as 'Pending' but its frontmatter reads status: Draft — orientation is a Layer-3 derived view and the frontmatter is Layer-1, so the ADR has not actually been moved off Draft. Second, work for OBPI-0.35.0-03 and OBPI-0.35.0-08 pre-landed as direct fixes in commits 42ba6c25, 48a5f799 and dcf29b95, but gz obpi status reports both as Runtime State PENDING with 'ledger proof of completion is missing'. Code is ahead of the ledger for those two briefs.

## Decisions Made

Superseded rather than edited the prior handoff, preserving the audit chain via continues_from. Did not work any GHI from the triage list, honoring the operator ruling that scoped this session to sync alone. Did not reconcile the two PENDING OBPIs or correct the ADR-0.35.0 status field, because both are governance mutations outside the ruled scope — they are recorded here as findings for operator ruling instead. Verified every claim of the prior handoff individually against Layer-2 rather than trusting the orientation banner, which is what surfaced the Draft-vs-Pending drift.

## Immediate Next Steps

1. Operator ruling on whether ADR-0.35.0 frontmatter status should move from Draft to Pending, reconciling it with what session orientation reports. 2. Operator ruling on reconciling OBPI-0.35.0-03 and OBPI-0.35.0-08, whose implementations landed in commits but carry no ledger proof of completion. 3. Resume the campaign's Movement A topmost item: ADR-0.35.0 remains 0 of 9 OBPIs landed, with OBPI-05 carrying the corpus-to-candidate generator and OBPI-07 the gz content land orchestrator. 4. Verify-and-close the four stale GHIs still open from the prior triage: #480, #561, #563, #564, plus #538. 5. Rule on GHI #696, still open, cross-linked as the downstream symptom of the handoff decision-state root cause.

## Pending Work / Open Loops

GHI #696 open — handoff decision state lost across the session boundary. GHI #480, #561, #563, #564, #538 open and unverified since the 2026-07-21 triage. Prior handoff's step 3 is discharged: GHI #709 verified CLOSED. Prior handoff's step 4 is untouched: the 2026-04-26 harness-engineering handoff still carries mode:DESIGN and fails validation. ADR-0.35.0 stands at 0 of 9 OBPIs landed against a Draft-status parent.

## Verification Checklist

gh issue view 654 and 635 both return state CLOSED, confirming the prior handoff's step 1 is void. uv run gz obpi lock list returns 'No active locks'. git rev-list --left-right --count origin/main...main returns 0 0. git status --short is empty. uv run gz obpi status on OBPI-0.35.0-03 and -08 both report Runtime State PENDING against Current HEAD c32f9b3. Resuming agents should re-run these before acting, since GHI state and ledger state both move independently of this document.

## Evidence / Artifacts

`.gzkit/handoffs/20260721T114824Z-ghi-triage-2026-07-21.md`, `docs/governance/ghi-triage-2026-07-21.md`, `docs/governance/build-to-1.0-campaign-2026-07-18.md`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
