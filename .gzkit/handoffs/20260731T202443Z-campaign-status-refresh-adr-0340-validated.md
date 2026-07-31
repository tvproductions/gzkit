---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-31T20:24:43Z'
agent: claude-code
session_id: a7d9d6b9-db29-49a3-8f87-f333222230a6
continues_from: .gzkit/handoffs/20260731T090547Z-campaign-sync-adr-0340-at-5of5.md
---

## Current State Summary

Status-report session. No ADR or OBPI work, no source changes, no commits. The operator asked for handoff and campaign status; the resume gate held every mutating call until the ruling was booked. Live reads established a clean working tree at 7dc9ea6b8 on main, ahead 0 behind 0, no active OBPI locks, no in-progress ADR pipelines, 20 open GHIs. The material finding is that the predecessor handoff (20260731T090547Z) was classified Fresh by timestamp while its first two advised steps had already been discharged: the ADR-0.34.0 closeout ceremony attested at 11:46:09Z and the audit ceremony emitted its receipt at 12:26:25Z, both after that handoff was written, and neither ceremony produced a handoff of its own. The campaign stands at 4 of 18 boxes with the Movement A capstone now checked.

## Important Context

Freshness is computed from the handoff timestamp, not from whether its advice was executed, so a same-day ceremony can spend a handoff without aging it. That is the gap this session hit and it is the same class the campaign already tracks as Movement D box 3 (the campaign body as a rendered Layer-3 view). The ADR-0.34.0 audit recorded THREE shortfalls as open rather than resolved, which qualifies the Foundation Sunset closure claim: S1, 15 of 26 @covers decorations on REQ-0.34.0-03-01 are unrelated tests so 58 percent of reported coverage is inert; S2, REQ-0.34.0-01-01 and -01-02 mandate exit 3 but no test asserts _POLICY_BREACH_ERROR_TYPES membership for foundation_kind_closed or grandfather_dangling, the same defect OBPI-03 fixed for foundation_limbo and never back-filled; S3, the shipped guards refuse foundation authoring unconditionally with no config key, which is the adopter carve-out alternative the ADR explicitly REJECTED, so the assembled system contradicts attested canon. S3 is filed as GHI #740. Movement A item 3 is a one-line operator canon call, deliberately fenced rather than blocking, because holding a gate green over a known-red tree is the staging-flag anti-pattern.

## Decisions Made

- [operator-ruled] refresh handoff (verbatim) — booked via gz handoff authorize against the 20260731T090547Z handoff for session a7d9d6b9-db29-49a3-8f87-f333222230a6. This is the ruling that lifted the resume gate; it authorizes the handoff refresh and nothing beyond it.
- [agent-chose] Omitted --adr on this handoff. The session did no ADR-scoped work: ADR-0.34.0 is Validated and closed, and no ADR-0.35.0 brief was opened. GHI #709 makes adr_id optional and mode the discriminator. Discovery still works because the SessionStart orientation selects the newest file under .gzkit/handoffs/ by path rather than by adr_id; a resuming agent running gz handoff resume --adr will not surface it, which is the accepted cost.
- [agent-chose] Seated the two ADR-0.34.0 ceremony rulings as late settled rulings via --settled rather than leaving them unhomed. Both arrived after the predecessor handoff was written and neither ceremony authored one, so without seating they would drop out of the carried set entirely.
- [agent-chose] Did not file a GHI for the Fresh-but-spent handoff gap. It is the fifth recurrence of hand-carried Layer-1 campaign prose going stale and the predecessor already booked that as standing evidence for the Movement D box; a fresh GHI would be reflexive filing under the 2026-06-01 moratorium.

## Immediate Next Steps

1. Rule on Movement A item 3, the foundation-adr-registers-invariant disposition. One line of operator canon. It is the cheapest open box and it unfences tests/governance/test_invariant_witness.py so --invariant-witness can rejoin gz check.
2. Open ADR-0.35.0-canon-entry-corpus-landing and begin landing its 9 briefs. This is the topmost unchecked campaign item and the campaign governs pull order. OBPI-05 carries the corpus-to-candidate generator, OBPI-06 the rendition-subset-of-corpus lineage gate, OBPI-07 the gz content land orchestrator.
3. Route GHI #740 (audit shortfall S3). The shipped taxonomy guards implement the alternative the ADR rejected, so attested canon and running behavior disagree.
4. Route GHI #734 (third adr_created ingress via register_adr_in_ledger) and audit shortfalls S1 and S2, which have no GHI of their own yet.
5. Consider whether closeout and audit ceremonies should author a handoff mechanically the way gz obpi complete already does under token-block Sub-Invariant 6. Both currently leave their rulings unhomed, which is what stranded two Gate-5 rulings this session.

## Pending Work / Open Loops

- Movement A item 2 open: ADR-0.35.0-canon-entry-corpus-landing at 0 of 9 briefs landed, all nine Draft, closeout BLOCKED on missing ledger proof for every one.
- Movement A item 3 open: foundation-adr-registers-invariant disposition awaits a one-line operator canon call.
- ADR-0.34.0 audit shortfalls S1 and S2 recorded open with no GHI of their own; S3 is GHI #740.
- 20 GHIs open, including #740, #739, #738, #737, #736, #735, #734, #732, #731, #730.
- ADR-0.44.0-vendor-alignment IN_PROGRESS at 1 of 6 under Housekeeping, tracked by no campaign edition.
- Movement B carries the largest ungoverned surface: 470 fix commits in 90 days with zero airlock transits, and 23 airlock_in against 10 airlock_out.
- Movement C surface mirroring: 703 of 810 chore commits regenerate five copies of every skill and rule.
- The campaign body remains hand-carried Layer-1 prose; Movement D box 3 unbuilt, and this session is the fifth data point.

## Verification Checklist

- git rev-parse --short HEAD resolves to 7dc9ea6b8 or the operator explains drift. Branch is main; no feature branch was created (operator canon).
- grep -n handoff_resume_authorized .gzkit/ledger.jsonl surfaces the refresh handoff ruling for session a7d9d6b9-db29-49a3-8f87-f333222230a6.
- The campaign file carries 18 checklist boxes with 4 checked; line 131 is checked and lines 129 and 130 are open.
- ls docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/ lists 9 briefs.
- gh issue view 740 reports state OPEN.
- uv run gz check exits 0 with ADR taxonomy as the last step.

## Evidence / Artifacts

- `.gzkit/handoffs/20260731T090547Z-campaign-sync-adr-0340-at-5of5.md` — the predecessor this handoff continues from; its advised steps 1 and 2 are spent.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — Magna Carta; line 9 Topmost banner, line 131 the checked capstone, lines 129 and 130 the two open Movement A items.
- `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/audit/AUDIT.md` — audit record carrying shortfalls S1, S2 and S3 as open.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — the successor ADR, Draft, 0 of 9 landed.
- `.gzkit/ledger.jsonl` — the handoff_resume_authorized event with the operator verbatim, the attested event at 11:46:09Z, and the audit_receipt_emitted at 12:26:25Z.

## Settled Rulings

- attest completed — OBPI-0.34.0-05 activates the permanent Foundation Sunset closure gate: ("ADR taxonomy", run_taxonomy_audit) is the LAST step in _build_check_steps() and `gz check --json` reports "ADR taxonomy": true, while the registration membrane refuses an un-grandfathered `kind: foundation` package at both adr_created ingresses (gz register-adrs and first-run gz init) with the 51-entry grandfathered roster still booking normally (GHI #706 discharged). 4/4 REQs proven on their correct ADR-0.0.59 channels with behavior_uncovered_reqs 0; REQ-0.34.0-05-01 was re-kinded BEHAVIOR->SUPPORT…
- "update handoff and campaign, then git sync" — booked verbatim via gz handoff authorize as the ruling on the resumed handoff. The predecessor's advised step (continue the ADR-0.34.0 checklist or open the next OBPI) was NOT authorized and remains unexecuted.
- The same words ratify the campaign amendment under section 8, in the same shape as the 2026-07-29 "fix discrepancy" ratification.
- attest completed — ADR-0.34.0 Foundation Sunset closeout, g0 verbatim, 11-step ceremony attested 2026-07-31T11:46:09Z; lifecycle transitioned to Validated and released as v0.34.0 on bump commit 551366064. Receipts arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1 (7685 OK), arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4, arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c, arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2.
- accept audit — ADR-0.34.0 Foundation Sunset validated with three shortfalls recorded open, accepted after each was presented with its verification evidence, g0 verbatim 2026-07-31T12:26:25Z. Bound fidelity gate 2/2, gz validate --taxonomy exits 0 on the terminal tree, gz cli audit 132/132 commands covered, 18/20 REQs covered with 2 SUPPORT REQs proof-exempt by ADR-0.0.59 channel. Shortfalls open: S1 inert @covers coverage, S2 missing exit-3 membership assertions, S3 framework-wide closure is the rejected alternative (GHI #740).
