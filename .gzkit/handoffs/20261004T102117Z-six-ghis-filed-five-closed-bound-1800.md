---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-04T10:21:17Z'
agent: claude-code
session_id: 9bc22653-d764-4d49-97e0-ecedc08e1eab
continues_from: .gzkit/handoffs/20261004T084203Z-windows-ci-test-fixed-1165-bound-open.md
---

## Current State Summary

This session resumed the predecessor handoff, verified its claims against live state, and worked its advised steps 1 and 2 on the operator's ruling. Step 1: five GHIs were filed through ghi-author (#1166 to #1170), each repaired as a direct fix, pushed and closed with evidence. Step 2: the operator ruled on GHI #1165 and the hang bound in src/gzkit/quality_command_timeout.json was raised from 900 to 1800 seconds; #1165 is left open for its exit evidence. Eight commits landed on main, 00c6977ea through 22bb2b304, and gz check passed on the final tree (exit 0, unit tier 11450-odd tests in about 100 seconds locally). CI run 37193855012 on 22bb2b304 finished green on both platforms: ubuntu-latest Test 372.57s, windows-latest Test 1117.23s. That Windows run would have been killed under the old bound, and it is slower than every run the new value was sized from (696 to 895 seconds). One further GHI was filed and not worked: #1171, an investigation into why windows-latest takes two to three times as long as ubuntu-latest. No OBPI was initiated, no lock was claimed or released, and OBPI-0.35.0-10 is unchanged apart from what its status and orientation surfaces now report.

## Important Context

Three of the five repairs changed what an agent reads, so the next session will see different surfaces. gz obpi status now prints Attestation State missing for every uncompleted or repudiated OBPI (391 of 950 in this ledger changed, in the two attestation fields only). The session orientation's pipeline section now names OBPI-0.35.0-10 at stage implement with its resume command, read from the marker. The pipeline skill (now 6.64.3) has an Abort surrender section prescribing gz obpi lock release with --abandon, and the --no-subagents flag is gone from gz obpi pipeline: a single-session run is the declaration gz obpi dispatch with --single-driver and --reason. Two repairs ran into attested REQs under Validated ADRs that literally asserted the retired command: four REQs under ADR-0.18.0 named --no-subagents, and REQ-0.0.14-03-07 named lock release --force. Both were escalated and the operator ruled amend in place; the record is docs/governance/attested-req-subject-retirement.md, Worked example 4. The agent first offered the #1166 choice before reading ADR-0.18.0 and had to ask again; that miss is recorded as an insight. A gap is left open on purpose: no abandon category names an abort after failed verification, so the skill now says to leave the lock held, name it in the handoff and report it. OBPI-0.35.0-10's lock is still held by claude-code-a0f543a5 and expires at 2026-10-04T12:35Z. Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section): handoff system was worked (resume, ruling booked, this handoff, the 09:21Z exit bookmark landed in 22bb2b304); ghi triage was not run, though six GHIs were filed and five closed; adr/obpi campaign is unchanged, with ADR-0.35.0's landed count read from gz adr status; new R&D was not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] Work advised steps 1 and 2 of the resumed handoff and then stop (verbatim: "do 1 and 2, then stop and report").
- [operator-ruled] GHI #1165: one hang bound of 1800 seconds for every host (verbatim: "Raise to 1800 s (Recommended)"). Rejected alternatives offered: a per-platform bound, and keeping 900 seconds while reducing the Windows runtime.
- [operator-ruled] GHI #1166: remove the --no-subagents flag from gz obpi pipeline instead of wiring it (verbatim: "Remove the flag (Recommended)").
- [operator-ruled] GHI #1166, once ADR-0.18.0 had been read: the four attested REQs naming the flag keep their text and gain a dated amendment (verbatim: "Remove, amend REQs in place (Recommended)").
- [operator-ruled] GHI #1167: REQ-0.0.14-03-07 keeps its attested text and gains a dated amendment, and its covering test keeps its binding (verbatim: "Amend in place (Recommended)"). Rejected alternatives offered: keeping --force beside --abandon, and reverting the fix.
- [operator-ruled] Write this handoff once CI finished and sync it (verbatim: "write the handoff when CI finishes" and "git-sync the handoff when it's written").
- [agent-chose] GHI #1170: ledger_semantics states the universal attestation rule itself and a test holds it equal to the completion gate's predicate, because the import-boundary ratchet refuses a private cross-package import.
- [agent-chose] GHI #1167: added no abandon category; where none describes an abort the skill says to leave the lock held and report it.
- [agent-chose] Left GHI #1165 open after the bound was raised, because its exit condition asks for several consecutive healthy Windows runs and one is in hand.
- [agent-chose] Filed GHI #1171 for the unexplained Windows runtime and did not work it.

## Immediate Next Steps

1. Read the Test duration of the next several windows-latest CI runs against GHI #1165. If they return to the 700 to 900 second range, close #1165 as fixed citing 0d632cb80 and those runs. If they stay near 1100 seconds, the operator re-rules the bound with that measurement: 1800 seconds is 1.6 times the 1117.23 second run, not the twice it was sized as.
2. The operator opens the gz-design dialogue for the tune-up: phased OBPI runs with runtime-written save points, a marker that advances within a run, lock continuity across a phase boundary, proof staleness scoped to what a proof names, the pipeline skill split by stage, and refusal records for hooks and validators. Two questions from this session belong in it: what an abort after failed verification does with its lock, since no abandon category names it, and whether one unit of work per session ended by a handoff becomes canon. Ask where the tune-up sits relative to ADR-0.35.0.
3. After 2026-10-04T12:35Z, the operator invokes gz-obpi-pipeline for OBPI-0.35.0-10 to repair findings E1 to E5 from docs/governance/obpi-run-cost-2026-10-03-evidence/trial-evaluation.md and complete it. The human-review judgment and the attestation are the operator's words; never author them.
4. The operator invokes gz-obpi-pipeline for each repudiated OBPI in turn: OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02 and OBPI-0.35.0-09.
5. The operator rules on the handoff-retention observation recorded as an insight at 2026-10-04T09:18Z (903 documents under .gzkit/handoffs, archive verb run by nothing); it has no GHI and no work order.

## Pending Work / Open Loops

The predecessor chain's open loops that this session did not touch are unchanged and are not restated here. Open from this session: GHI #1165 awaits its Windows run evidence. GHI #1171 is an unselected investigation. Three findings were stated in close comments and have no work order: no check compares the options a subparser declares with what its handler receives, so another inert CLI option would not be caught; the orientation's blockers key is still a constant; and docs/user/manpages/obpi-lock-release.md still carries a --force example that would exit 3 on a held lock, kept as flag syntax. The abandon-category gap for a failed-verification abort is reserved for the tune-up design. The operator's question from the prior session, compaction versus handoff per unit of work, still has a recommendation and no ruling. The verify-packet masked-command replay question from the prior session is unchanged.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0. gh run list --workflow CI --limit 3: expect run 37193855012 on 22bb2b304 completed with success, and read the windows-latest Test duration of any later run. gh issue view for 1166, 1167, 1168, 1169 and 1170 with --json state: expect CLOSED for each. gh issue view 1165 --json state and gh issue view 1171 --json state: expect OPEN. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS, Attestation State missing and Completion PENDING. uv run gz obpi pipeline --help: expect no --no-subagents option. uv run gz obpi lock list: expect no OBPI-0.35.0-10 lock after 2026-10-04T12:35Z. uv run -m unittest tests.scripts.test_session_orientation tests.test_ledger tests.test_cli_parser tests.test_obpi_skill_migration: expect OK. uv run gz handoff rulings --search "Amend in place": expect this handoff's rulings.

## Evidence / Artifacts

Changed: `scripts/session_orientation.py`, `src/gzkit/ledger_semantics.py`, `src/gzkit/cli/parser_obpi.py`, `src/gzkit/commands/obpi_precomplete.py`, `src/gzkit/quality_command_timeout.json`, `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, `.gzkit/skills/gz-obpi-lock/SKILL.md`, `docs/user/manpages/obpi-pipeline.md`, `docs/user/manpages/obpi-lock-release.md`, `docs/user/manpages/obpi-lock-list.md`, `docs/user/manpages/obpi-complete.md`, `docs/user/manpages/obpi-status.md`, `docs/user/manpages/obpi-sync.md`, `docs/user/runbook.md`, `docs/user/concepts/subagent-pipeline.md`, `docs/governance/attested-req-subject-retirement.md`, `docs/governance/hexagonal-architecture.md`. Amended REQ lines: `docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands/obpis/OBPI-0.0.14-03-pipeline-skill-migration.md` and the four briefs 05 to 08 under `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/obpis`. Tests: `tests/scripts/test_session_orientation.py`, `tests/test_ledger.py`, `tests/commands/test_status.py`, `tests/commands/test_status_obpi.py`, `tests/test_cli_parser.py`, `tests/test_pipeline_dispatch.py`, `tests/test_obpi_skill_migration.py`. Predecessor: `.gzkit/handoffs/20261004T084203Z-windows-ci-test-fixed-1165-bound-open.md`, whose resume decision is booked proceed under session 9bc22653-d764-4d49-97e0-ecedc08e1eab; the exit bookmark `.gzkit/handoffs/20261004T092120Z-session-exit-bookmark.md` is superseded by this document. Commits: 00c6977ea (#1169), e2ce63afb (#1168), 35a483418 (#1170), a1726901b and f64f279af (#1167), 0d632cb80 (#1165), 325bff69e (#1166), 22bb2b304 (sync). Receipts: `artifacts/receipts/arb-red-commit-e2ce63afb3b1-0343269b2cb148ce96c2d2da3cebe069.json`, `artifacts/receipts/arb-red-commit-35a483418aa4-124112ef25764a6398c8309565f2338b.json`, `artifacts/receipts/arb-red-commit-325bff69eb42-a423ff65fbb8411aac781411c1b5302b.json`. CI run: 37193855012 (passed, 22bb2b304).

## Settled Rulings

1329 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
