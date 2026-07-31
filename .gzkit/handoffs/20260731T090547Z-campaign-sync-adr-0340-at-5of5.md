---
mode: CREATE
adr_id: ADR-0.34.0
branch: main
timestamp: '2026-07-31T09:05:47Z'
agent: claude-code
session_id: 9d803466-4624-4ca9-9207-26f94345db60
continues_from: .gzkit/handoffs/20260731T083202Z-OBPI-0.34.0-05-activate-standing-taxonomy-gate-complete.md
---

## Current State Summary

Governance-maintenance session, no OBPI work. Booked the operator ruling on the resumed OBPI-0.34.0-05 completion handoff, then corrected the Magna Carta to live state and synced. ADR-0.34.0 is now 5/5 attested_completed with Gates 1-4 pass and Gate 5 pending; the ADR itself is lifecycle Pending, closeout READY, validated false. Working tree was clean at session start (HEAD dcdd47fb8); the only changes authored this session are to docs/governance/build-to-1.0-campaign-2026-07-18.md.

## Important Context

Campaign section 8 makes amendments operator-ratified and requires they append to section Amendments, never interleave. Section 9a scope decision 3 (CARRIED) sets the per-ADR done-bar at Validated or operator-parked, which is why the Movement A capstone box stays open at 5/5 OBPIs. The capstone count line is hand-carried Layer-1 prose that the SessionStart banner quotes verbatim, so every landed OBPI re-stales the top of every session and costs an operator ruling to clear. This is the fourth occurrence of that drift on that one line. Movement D box 3 (campaign body as a rendered Layer-3 view) is the structural fix and is unbuilt.

## Decisions Made

- [operator-ruled] "update handoff and campaign, then git sync" — booked verbatim via gz handoff authorize as the ruling on the resumed handoff. The predecessor's advised step (continue the ADR-0.34.0 checklist or open the next OBPI) was NOT authorized and remains unexecuted.
- [operator-ruled] The same words ratify the campaign amendment under section 8, in the same shape as the 2026-07-29 "fix discrepancy" ratification.
- [agent-chose] Left the Movement A capstone checkbox UNCHECKED at 5/5, on section 9a scope decision 3. Verified via gz adr status ADR-0.34.0 --json: validated false, lifecycle_status Pending, gate 5 pending. Reverse freely if the operator reads 5/5 as the bar.
- [agent-chose] Rewrote the remainder clause from "remaining is OBPI-04 and OBPI-05 alone" to "the closeout ceremony alone" rather than only bumping the digit, because bumping the digit alone would have left the line prescribing work already landed.
- [agent-chose] Booked the fourth recurrence as standing evidence for the existing Movement D box instead of filing a GHI. The defect already has a tracked home; a fresh GHI would be reflexive filing under the 2026-06-01 moratorium.

## Immediate Next Steps

1. Present ADR-0.34.0 for closeout and obtain an operator ruling. It is 5/5 with Gates 1-4 pass, Gate 5 pending, Closeout READY; the ceremony is /gz-adr-closeout-ceremony and it is the only thing between Movement A's capstone and Validated.
2. On Validated, check the Movement A capstone box with its receipt citation and repoint the Topmost banner line to Movement A item 2.
3. Movement A items 2 and 3 remain open ahead of Movement B: ADR-0.35.0-canon-entry-corpus-landing is 0/9 with closeout BLOCKED, and the foundation-adr-registers-invariant disposition awaits a one-line operator canon call.
4. Route GHI #734 — OBPI-05 sealed the foundation membrane at two adr_created ingresses and #734 names a third that still bypasses it, so the closure is not yet total.

## Pending Work / Open Loops

- ADR-0.34.0 Gate 5 outstanding; the ADR is Pending, not Validated, despite 5/5 OBPIs.
- GHI #734 OPEN — register_adr_in_ledger is a third adr_created ingress bypassing the foundation membrane. Material: it qualifies OBPI-05's sealed-membrane claim.
- GHI #735 OPEN — a leading BOM silently hides the whole frontmatter block in parse_frontmatter_value.
- GHI #736 OPEN — three ad-hoc frontmatter decoders disagree; no shared tri-state reader.
- ADR-0.35.0 at 0/9, all nine briefs draft, closeout BLOCKED on missing ledger proof for every one.
- ADR-0.44.0-vendor-alignment still IN_PROGRESS at 1/6 under Housekeeping.
- The campaign body remains hand-carried Layer-1 prose; Movement D box 3 unbuilt, and this handoff is the fourth data point.

## Verification Checklist

- git rev-parse --short HEAD resolves to the gz git-sync commit authored above dcdd47fb8, or the operator explains drift.
- Branch is main. No feature branch was created (operator canon).
- uv run gz adr status ADR-0.34.0 renders OBPI 5/5, Closeout READY, QC PENDING (pending: Human attestation).
- uv run gz adr status ADR-0.35.0 renders OBPI 0/9, Closeout BLOCKED.
- gh issue view 734 / 735 / 736 each report state OPEN.
- The Movement A capstone line and the Topmost banner line both read 5/5 and agree with the governed read.

## Evidence / Artifacts

- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — Topmost line, Movement A capstone item, and the new 2026-07-31 amendment block.
- `.gzkit/handoffs/20260731T083202Z-OBPI-0.34.0-05-activate-standing-taxonomy-gate-complete.md` — the predecessor handoff this one continues from.
- `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md` — the capstone ADR awaiting Gate 5.
- `.gzkit/ledger.jsonl` — the handoff_resume_authorized event carrying the operator's verbatim ruling.

## Settled Rulings

- attest completed — OBPI-0.34.0-05 activates the permanent Foundation Sunset closure gate: ("ADR taxonomy", run_taxonomy_audit) is the LAST step in _build_check_steps() and `gz check --json` reports "ADR taxonomy": true, while the registration membrane refuses an un-grandfathered `kind: foundation` package at both adr_created ingresses (gz register-adrs and first-run gz init) with the 51-entry grandfathered roster still booking normally (GHI #706 discharged). 4/4 REQs proven on their correct ADR-0.0.59 channels with behavior_uncovered_reqs 0; REQ-0.34.0-05-01 was re-kinded BEHAVIOR->SUPPORT…
