---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-03T06:17:11Z'
agent: claude-code
session_id: 5c006e53-399c-462a-97d8-a5d9da85b716
continues_from: .gzkit/handoffs/20261003T043915Z-resolver-and-canary-witness-fixed-amendment-r2.md
---

## Current State Summary

Resumed the predecessor and worked its advised steps 1 and 2 under the operator's rulings; steps 3, 4 and 5 are untouched and carried. Step 1: the operator ratified all six proposals of the campaign amendment (P2, P3 and P4 with a change made at ratification); it is landed as § Amendments 2026-10-03 of the campaign plan in 2c56b309a, with the Topmost line, § 5's backlog gate, the ghi-author skill (1.10.0, Introduced-by line) and the evidence README updated. No batch of OBPIs is initiated. Step 2: GHI #1163 was filed, repaired direct and closed: the uncalled Step-4b verdict gate, the precomplete check that was no longer yielded, and five ignored flags of gz obpi complete are removed (0ccde2c97, survivors dispositioned in 9f7624726); the manpage, the gz-obpi-pipeline skill (6.64.0) and Draft briefs OBPI-0.36.0-03 and OBPI-0.36.0-07 name the acceptance reducer. The tautological-debt step of gz check went red on the date (230 against a ceiling of 229); two ops were drained in 0045c1434 and the gate is green at 228. All four commits are pushed; this handoff is carried by the git-sync after it.

## Important Context

Session orientation transcribes only the campaign plan's Topmost line, so a sequence change written in a separate banner block never reaches a session; the 2026-09-27 ADR-work-first ruling had been missing from orientation for that reason, and the 2026-10-03 draw order is now written into that line. The Step-4b refusal lives in acceptance_store.completion_review and acceptance.assess_readiness and reads no lane: gz obpi complete refuses on every lane, and takes no verdict, reviewer, tier or receipt from its caller. The "we will NOT alter the OBPI process" freeze is ruled narrow in the rulings store and does not bar defect repair of the Step-4b surface. gz obpi brief-drift --apply repairs the allowlist dimension only, so the two Draft briefs were corrected by hand under the operator's route ruling and each records it under Tracked Defects. The single-op tautological tests are not disposable: the ones read carry @covers for attested REQs and must be converted in place, never deleted. data/tautological_test_baseline.json still lists drained ops (280 entries against 228 live); it was not regenerated. The verifier-pipe hook refuses a verifier that is piped or followed by another statement: redirect to a log and echo the exit, or use set -e. git-sync is an operator-only skill. Workflow fronts (source: the campaign plan § Workflow fronts): handoff system and adr/obpi campaign were worked this session; ghi triage was not run; new R&D was not touched.

## Decisions Made

- [operator-ruled] Work the predecessor's advised steps 1 and 2 in that order, the campaign amendment and then the dead Step-4b code (verbatim: "1, then 2").
- [operator-ruled] Amendment P1, completion-path additions come to the operator, advisory (verbatim: "Adopt as written (Recommended)").
- [operator-ruled] Amendment P2, the post-June completion-path review runs as one bounded pass only on the operator's word (verbatim: "Adopt, run when you call it (Recommended)").
- [operator-ruled] Amendment P3, batch initiation recorded in the campaign plan with the OBPI ids, and sessions draw a GHI on their own only when it blocks feature work, a gate or a release (verbatim: "Adopt, batch recorded in plan (Recommended)").
- [operator-ruled] Amendment P4, ghi-author adds an Introduced-by line whose named origin cites a commit, GHI or ADR id (verbatim: "Adopt, origin cites an id (Recommended)").
- [operator-ruled] Amendment P5, the § 5 backlog gate is a bounded check at 1.0 closeout (verbatim: "Adopt as written (Recommended)").
- [operator-ruled] Amendment P6, a read-only Codex sanity pass at each campaign amendment and monthly on the operator's go-ahead (verbatim: "Adopt as written (Recommended)").
- [operator-ruled] Route the dead Step-4b helpers and five ignored flags through one GHI and remove them outright (verbatim: "GHI, remove outright (Recommended)").
- [operator-ruled] Drain two tautological-debt ops before syncing (verbatim: "Drain two ops, then sync (Recommended)").
- [operator-ruled] Write the handoff and sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] The amendment entry carries the measurement as a pointer to the evidence directory, not its tables; the draft file is left unedited as the record of what was put to the operator.
- [agent-chose] The Topmost line was prefixed with the 2026-10-03 draw order and the 2026-09-27 resequencing, and the 2026-09-15 drawn-work block was marked superseded.
- [agent-chose] ADVERSARY_VERDICTS and the three provenance flags (--adversary-job-id, --refuted-claim, --adversary-resolution) were kept; REFUTATION_VERDICTS was removed with its last reader.
- [agent-chose] Two paragraphs of the gz-obpi-pipeline skill describing the removed name scan were dropped and nothing was lifted to a rationale doc.
- [agent-chose] ADR-0.36.0 Boundary Invariant #1 and REQ-0.36.0-07-05 were left naming obpi_complete_adversarial.py; only the briefs' Objective and Discovery Checklist were corrected.
- [agent-chose] The two drained ops were test_justify_command_doc_and_index_exist and test_chore_registered_as_heavy_lane_in_production_config, converted to assert through check_surfaces_report and _load_chores_registry.

## Immediate Next Steps

1. Decision for you: batch-initiate OBPIs of ADR-0.35.0 under the 2026-10-03 amendment. Six are unlanded (OBPI-0.35.0-08 and OBPI-0.35.0-10 through OBPI-0.35.0-13 lack ledger proof of completion; OBPI-0.35.0-09 is repudiated). The batch is recorded in the campaign plan § Amendments with your verbatim words and the OBPI ids.
2. Drain tautological-test debt again before 2026-10-06: debt is 228 and by the schedule in data/tautological_test_debt_target.json the ceiling reaches 227 that day, which turns gz check red for every change. Run uv run python .gzkit/chores/decommission-tautological-tests/check_debt_target.py to measure. The chore is operator-paced.
3. Decision for you: the 2026-10-03 draw order does not say what a session draws when no OBPI is initiated and no GHI blocks feature work, a gate or a release.
4. Decision for you: ADR-0.36.0 Boundary Invariant #1 and REQ-0.36.0-07-05 name obpi_complete_adversarial.py as the Step-4b surface, while the gate lives in acceptance_store.py and acceptance.py.
5. Carried decisions for you: GHI #1154 (one discriminator test per BEHAVIOR REQ, how canaries scale, whether the mutation text joins the canary binding), and whether to start re-completion pipelines for OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02 and OBPI-0.35.0-09.

## Pending Work / Open Loops

Open: GHI #1154 and GHI #1155 (measure the mechanism at the nine fix parents; decide whether a mechanism should detect a claimed gate no production path calls). The amendment's standing items await the operator's word: the P2 completion-path review, the monthly reading of Introduced-by lines, and the next Codex sanity pass. Whether the three remaining provenance flags of gz obpi complete should stay was left outside GHI #1163 [settled]. data/tautological_test_baseline.json was not regenerated after the drain. Not run this session: ghi-triage, and the 19 ancestor handoffs were not read. Carried: the chore_decommission_processed emitter gap; the typecheck control runs uv run ty check . while the gz check step excludes features; the QC rendition-lineage advisory (NCSurface.md/root owned-section) prints on every gz check; a drafted Claude Code feedback item is queued locally for the operator's /feedback; the unfiled patch-release diff_only listing; trackers #611, #921, #978, #1028 and #799; 35 chores overdue on the board.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after git-sync; gh issue view 1163: expect CLOSED; uv run gz check: expect exit 0 until 2026-10-06, then the Tautological debt step unless more ops are drained; uv run python .gzkit/chores/decommission-tautological-tests/check_debt_target.py: expect 228 outstanding; uv run gz cli audit: expect 151/151 fully covered; uv run gz obpi complete --help: expect no --adversary-verdict, --adversary, --adversary-receipt, --adversary-fallback-reason or --adversary-tier; uv run python -m unittest tests.test_adversarial_validation_gate tests.test_adversarial_validation_audit tests.test_acceptance_store tests.policy.test_import_boundaries: expect OK; session orientation's Topmost line: expect it to open with AMENDED 2026-10-03; uv run gz obpi lock list: expect no active locks.

## Evidence / Artifacts

Commits 2c56b309a (amendment), 0ccde2c97 and 9f7624726 (GHI #1163), 0045c1434 (debt drain). Receipt: arb-red-commit-0ccde2c979f2-c5c42fd2906a46e394c5a0f41cfdadd1. Files: `docs/governance/build-to-1.0-campaign-2026-09-20.md`, `docs/governance/completion-cost-2026-10-02-evidence/README.md`, `.gzkit/skills/ghi-author/SKILL.md`, `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, `src/gzkit/commands/obpi_complete_adversarial.py`, `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/obpi_precomplete.py`, `src/gzkit/cli/parser_obpi.py`, `src/gzkit/quality.py`, `src/gzkit/governance/trust_audits/adversarial_validation.py`, `docs/user/manpages/obpi-complete.md`, `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/obpis/OBPI-0.36.0-07-verdict-resolution-transition.md`, `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/obpis/OBPI-0.36.0-03-operator-door.md`, `tests/test_adversarial_validation_gate.py`, `tests/test_adversarial_validation_audit.py`, `tests/test_acceptance_store.py`, `tests/policy/test_import_boundaries.py`, `tests/commands/test_justify_cmd.py`, `tests/commands/test_frontmatter_reconcile.py`. Predecessor: `.gzkit/handoffs/20261003T043915Z-resolver-and-canary-witness-fixed-amendment-r2.md`.

## Settled Rulings

1284 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
