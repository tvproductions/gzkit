# Patch Release: v0.34.2

**Date:** 2026-08-09
**Previous Version:** 0.34.1
**Tag:** v0.34.1

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 533 | agents-md-budget: 5k recovery target requires ADR-0.0.37 completion + registry-projection migration | diff_only | GHI #533 has commits touching src/gzkit/ but no 'runtime' label |
| 581 | brief-reconcile: existence-only checks miss dead surfaces & code couplings | qualified |  |
| 589 | gz-obpi-pipeline: Stage 3 verification can be masked by a tail-piped exit code | qualified |  |
| 594 | arb: no archive/purge half — 1875 receipts accumulate unbounded | open_upstream | GHI #594 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |
| 669 | obpi-monitor: no mechanical audit that every OBPI-status writer consults the terminal rule (convention-only) | qualified |  |
| 678 | gz-obpi-pipeline: Step 4b Codex-first tier preference is not mechanically bound | qualified |  |
| 708 | git-sync: add -A absorbs staged src/tests work into a ceremony chore commit | qualified |  |
| 719 | interview: pool ADR interview JSON is unschema'd (non-pool is validated) | qualified |  |
| 732 | handoff-resume-gate: plain-shell read allowlist has no membership predicate (4th miss) | qualified |  |
| 743 | chores: acceptance criteria don't gate the chore's own subject | qualified |  |
| 754 | advisory-scorecard: filename-level audit lets clauses land unscored | qualified |  |
| 755 | handoff-resume-gate: authoring a handoff revokes author's clearance | qualified |  |
| 756 | handoff: write surface has no trigger — continuity depends on recall | qualified |  |
| 757 | handoff: entry advisement is passive and gated by attestation ceremony | qualified |  |
| 758 | handoff resume: machine floor bookmarks shadow every authored handoff | qualified |  |
| 760 | session-exit: skip predicate is defeated by the handoff's own landing commit | qualified |  |
| 761 | orientation: SessionStart lists handoff evidence but never assembles the account | label_only | GHI #761 has 'runtime' label but no commits touching src/gzkit/ |
| 762 | handoff delta rule is carried by convention; each reader relearns it separately | qualified |  |
| 763 | token block: register entries are named and stored as session handoffs | qualified |  |
| 764 | exchange record: observation report is unwired; 4 of 7 sections are boilerplate | qualified |  |
| 765 | obpi-complete: Step-4b tier-1 is asserted by the caller, never proven | qualified |  |
| 768 | governance-docs: OBPI count changes couple to no surface that quotes them | qualified |  |
| 769 | adr-evaluate: scorecard writer fights the workflow its own skill prescribes | qualified |  |
| 770 | dispatch-attestation: the audit checks an absorption marker, not dispatch | qualified |  |
| 771 | ghi-close: close-comment claims are restated, never re-derived | qualified |  |
| 772 | failure-class-index: depth counts GHIs carrying no class statement | qualified |  |
| 773 | governance: ADR-0.44.0 is a second live feature ADR, contradicting one-feature-at-a-time | qualified |  |
| 774 | ledger: 13 OBPIs are parked while their parent ADR is live; obpi_unparked has never fired | qualified |  |
| 775 | gz adr demote: no non-lossy collision policy when the promoted ADR diverged from its pool intake | qualified |  |
| 776 | gz adr demote: H1 keeps the pre-demotion id, and 8 of those ids are now live ADRs | qualified |  |
| 777 | pool ADRs: demoted files still instruct against their old id (7 runnable commands) | qualified |  |
| 778 | governance-docs: canonical ARB rule file is cited but does not exist | qualified |  |
| 779 | fold guards: file-level allow-list grants hide live dead pointers | diff_only | GHI #779 has commits touching src/gzkit/ but no 'runtime' label |
| 780 | obpi-complete: tier-1 still passes without a receipt, so the class #765 named stays open | qualified |  |

## Operator Approval

Approved by gz patch release
