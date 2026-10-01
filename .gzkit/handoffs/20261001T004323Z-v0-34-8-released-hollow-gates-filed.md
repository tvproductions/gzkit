---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-01T00:43:23Z'
agent: claude-code
session_id: c8cbbdf2-628e-4850-b40e-217d8a440e86
continues_from: .gzkit/handoffs/20260930T094259Z-ghi-1153-closed-ci-green-both-platforms.md
---

## Current State Summary

Released v0.34.8 (tag at 5f6df4b92; GitHub release published): 153 GHIs closed since v0.34.7. Before release, every one of the 160 changelog/notes entries was checked against its commits by an independent pass (96 held, 64 corrected), and the release carries a Known issues section on the attestation audit. Session work: tests for the three undriven guards from 73aaab093/92f64debc (57a94bd58; the third guard is the event-type filter, not the seen-dedupe the predecessor named). Reopened and fixed GHI #1017: the pre-push --reuse-verified skip never read commits made after the verifying run; it now consults the trailer validators and the task-envelope trailer channel (b22353885, c0aa6467b; both gz arb red --commit verdict=driven); closed. Filed GHI #1154 (gate tests feed absence as the only bad input and bless a stand-in as the good input; 12 measured instances) and GHI #1155 (9 of those 12 gates had no registered enforcement claim on the hollow function; find-and-register contract). Ran a four-group attestation audit of completions made while gates were open, and a mutation gate map of the 98 registered claims (92 load-bearing, 1 admit-pole, 5 unmeasured).

## Important Context

Confidence in a gate is measured per gate, not read from a green: a registered, load-bearing control is evidence; anything else is not yet (#1155). Subagent prose overclaimed often this session: 64 of 160 drafted release entries needed correction, and several audit claims were wrong when checked (#959 '13 of 13 no resolution' is false: all 13 refuted rows carry a resolution; '57a94bd58 drives 2 of 4 hunks' is false: all four mutants are killed). Verify any subagent figure before relaying it. The main session also stated two unmeasured claims as fact ('most of the release', 'almost nothing fed gates a bad input'); both were retracted and recorded as improvement insights. A Task: slug trailer must match [a-z][a-z0-9-]*; dots (v0.34.8) are refused, as the pre-push gate showed on the first release push. The attestation-audit reports, the 12-instance test-shape measurement, the gate map and the registered-at-parent script live only in the session scratchpad, not in the repo; their results are recorded in GHI #1154, #1155, #1017 and in RELEASE_NOTES.md Known issues.

## Decisions Made

- [operator-ruled] Add tests for the predecessor's undriven guards (verbatim: "add tests for the three untested guards the witness found in 73aaab093 and 92f64debc.").
- [operator-ruled] Patch-release Step 1a backfill runtime on #815, #832, #936, #963 (verbatim: "815, 832, 936, 963 (Recommended)").
- [operator-ruled] Step 1b: #611, #921, #978, #1028 stay open trackers (verbatim: "Leave all open (Recommended)").
- [operator-ruled] Step 1c adjudication accepted (verbatim: "Accept as proposed (Recommended)").
- [operator-ruled] After the highlights overclaimed, run both an attestation audit and a verified rewrite (verbatim: "Both").
- [operator-ruled] File a GHI for the hollow-gate class (verbatim: "file a GHI for the pervasive hollow-gate class").
- [operator-ruled] Audit-found defects: confirm each, then file (verbatim: "Confirm, then file (Recommended)").
- [operator-ruled] Release with a Known issues section (verbatim: "Release with Known issues (Recommended)").
- [operator-ruled] Exploited completions: confirm each, then present for repudiation rulings (verbatim: "Confirm each, then present (Recommended)").
- [operator-ruled] Fix defects rather than only file them (verbatim: "we need to fix defects").
- [operator-ruled] Measure the gate map first (verbatim: "Gate map first (Recommended)") and then whether the hollow gates were registered (verbatim: "yes, measure it").
- [operator-ruled] Close out the session (verbatim: "ghi that finds and fixes, attest the release, create handoff, git-sync").
- [agent-chose] Reopened #1017 instead of filing a new GHI: its own exit condition (a trailer-less code commit under a non-code commit is refused before origin) was falsified by 57a94bd58, and ghi-author reopens a GHI closed within 30 days.
- [agent-chose] Did not force-push to add trailers to the four trailer-less commits already on origin; recorded them in Known issues.

## Immediate Next Steps

1. Present the repudiation rulings to the operator: repudiate and re-complete OBPI-0.0.24-04 (failed unittest receipt e3b0f66d, not cited or disclosed), OBPI-0.35.0-09 and OBPI-0.34.0-02 (no valid falsifiability witness at completion); a ledger correction for OBPI-0.0.28-03 (transcript/receipt mismatch, tests passed). Only the operator repudiates.
2. Confirm, file (ghi-author) and fix each of the five audit defects: closeout Demos run in the live checkout; gz obpi verify-packet replays in the live checkout; validate_stage4_evidence has no production caller; the justify check never runs at ADR closeout; red-parity treats missing base provenance as working-tree.
3. Ask the operator to rule on docs/evals/test-suite-integrity-audit-2026-09-24.md sections 9 and 10, the destination GHI #1154 is blocked on.
4. Work GHI #1155: enumerate gates against the enforcement registry in gz check, and register load-bearing controls for the nine unregistered hollow gates.
5. Carried from the predecessor: ask whether to draw the next ADR-0.35.0 OBPI, and how to close the chore_decommission_processed emitter gap.

## Pending Work / Open Loops

GHI #1154 and #1155 open. #611, #921, #978 and #1028 are open trackers with partial landings in v0.34.8. Unfiled observations from this session, each still to be confirmed: gz patch release reports OPEN GHIs (#1022, #1091) in the diff_only bucket defined for closed GHIs; the ghi-author runtime predicate fires on rule/skill/template edits because they live under src/gzkit; the registry derives gate_targets for module-size and tautological-debt as the helper chores._resolve_chore_dir; red-parity keeps only the latest event per REQ and so overwrote 15 'none' rows (audit report, unconfirmed). Whether to commit the gate map and audit reports as dated records under docs/governance was asked and not ruled. Four trailer-less code commits on origin (57a94bd58, d85a36ca3, 4cb8cedbc, d98b520f3) stay as published history. Carried: GHI #799 waits on OBPI-0.35.0-10; tautological debt sits near its falling ceiling; AGENTS.md exceeds its advisory budget.

## Verification Checklist

gh release view v0.34.8 (expect published); git rev-parse v0.34.8^{commit} (expect 5f6df4b92...); gh issue view 1017 (expect CLOSED); gh issue view 1154 and 1155 (expect OPEN); uv run -m unittest tests.governance.test_commit_trailers_pushed_range tests.test_check_fingerprint tests.test_commit_witness (expect OK); uv run gz validate --changelog (expect exit 0); git rev-list --left-right --count origin/main...HEAD (expect 0 0 after sync); uv run gz check (expect exit 0).

## Evidence / Artifacts

Release: `RELEASE_NOTES.md`, `CHANGELOG.md`, `docs/releases/PATCH-v0.34.8.md`. #1017 fix: `src/gzkit/commands/quality.py`, `tests/governance/test_commit_trailers_pushed_range.py`, `docs/user/manpages/check.md`, `src/gzkit/check_fingerprint.py`; receipts `artifacts/receipts/arb-red-commit-b223538854d1-0b9e13b0636a4918954d9da63b83196e.json`, `artifacts/receipts/arb-red-commit-c0aa6467b09c-d98ef411963648e3b034fb0ebff63213.json`. Guard tests: `tests/test_commit_witness.py`, `tests/governance/test_justify_binding_gate.py`. Insights: `.gzkit/insights/agent-insights.jsonl`. Predecessor: `.gzkit/handoffs/20260930T094259Z-ghi-1153-closed-ci-green-both-platforms.md`.

## Settled Rulings

1235 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
