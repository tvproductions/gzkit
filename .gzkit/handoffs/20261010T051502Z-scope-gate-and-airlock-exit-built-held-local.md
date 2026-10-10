---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-10T05:15:02Z'
agent: claude-code
session_id: 6c08c9d9-650e-4774-a4ac-a63952913ba1
continues_from: .gzkit/handoffs/20261009T094116Z-renewing-vows-command-joined-lapses-addressed.md
---

## Current State Summary

The R&D run `renewing-vows` is still open in diamond 1 and was not advanced this traversal. The operator instead directed two direct fixes, both built, tested and committed locally, neither pushed.

GHI #1181: `gz obpi complete` now refuses, exit 3, when an uncommitted file lies outside the brief's Allowed Paths; `gz obpi precomplete` reports the same finding before attestation; the completion receipt carries the scope report again. gzkit's own record files never count. GHI #1185: the airlock exit now holds a transit's changed files against Allowed Paths and reports each one outside them as a finding; it reports and never refuses.

Five commits are ahead of origin: dbce808be, 19342f7c2, 81435469d, 8babe4d2a, eed290d09. Staged and uncommitted: the insights log, four red-commit receipt lines in the ledger, and the run record. Last observed on the final tree: `uv run gz check` exit 0, `uv run gz test` 11528 tests passing, behave 464 scenarios passing.

The commits are held local on purpose: the campaign's 2026-10-03 amendment requires the operator's ruling on a completion-path addition before it lands, and that ruling has not been given.

## Important Context

- The campaign plan's amendment of 2026-10-03 item 1 binds any fix that adds a check to the completion path: it states the obligation protected, the defect answered and the expected false-refusal cost, and the operator rules. The three statements are posted on GHI #1181. Measured cost: of the last 11 completed packages 10 would have passed; the one refused, `OBPI-0.35.0-09`, had nine of its own source and schema files outside its brief's Allowed Paths.
- The amendment of 2026-10-04 (3) makes `ADR-0.37.0` unavailable as a home for this repair: ascending order has no exception. The agent recommended pulling it forward without having read the amendments and the operator rejected that. Read the campaign's work-order amendments before recommending any change to what is worked next.
- The scope refusal predates the airlock. It lived in the brief validator from 2026-03-11 and was lost at the command level when `gz obpi complete` replaced `gz obpi emit-receipt` on 2026-04-05. The agent twice told the operator otherwise and was corrected.
- Only the uncommitted working tree is compared. A change committed before completion is not held against Allowed Paths, because commits cannot be attributed to a package soundly: the commit hook stamps active TASK trailers on untrailered commits.
- The airlock exit is reached only by `gz airlock out` and by the runtime's final stage. The skill-driven Stage 5 the operator uses does not call it, so GHI #1185's comparison does not yet run on a real package completion.
- The record-file exemption list `GZKIT_RECORD_PATHS` in `src/gzkit/hooks/obpi.py` is the agent's draft. It was put to the operator twice and not ruled.
- A verifier (`ruff`, `gz validate`, `gz check`) must be the last statement of a shell command, or be followed only by reading its exit status; a hook blocks anything else.
- `gz arb red --commit` returned undriven on both fix commits and inconclusive on the part-one commit; follow-up commits added the driving tests. The receipts are in the ledger lines still staged.

## Decisions Made

- [operator-ruled] The scope report is restored to the completion receipt under GHI #1181 (verbatim: "fix the first part under 1181").
- [operator-ruled] Completion refuses a change outside Allowed Paths, as a direct fix (verbatim: "refuse, direct fix under 1181").
- [operator-ruled] The scope check predates the airlock, and its restoration is filed as a GHI against the airlock (verbatim: "no, this predated the airlock, is the airlock even active? ghi the restoration to enhance/strengthen the airlock, if able"). Filed as GHI #1185.
- [operator-ruled] Pulling `ADR-0.37.0` forward in the campaign to carry GHI #1185 is not available (verbatim: "this is NOT currently possible").
- [operator-ruled] Both repairs are built as direct fixes (verbatim: "direct fix - this is a perfect storm of bad decisions and outcomes: 0.33.0 impotence plus a misguide regression in gz obpi complete. bad form.").
- [agent-chose] Held the five commits local instead of syncing, because the 2026-10-03 amendment puts the ruling on a completion-path addition before the landing. Rejected: syncing on the strength of the "direct fix" direction alone.
- [agent-chose] Drafted the record-file exemption as a fixed list plus the brief itself and its package's `logs/`, shared by every receipt producer and the validator. Rejected: exempting all of `.gzkit/`, which would hide edits to skills, rules and corpus.
- [agent-chose] The airlock exit reports out-of-scope files as findings and does not refuse, following the operator doctrine that the airlock is not a verification gate.
- [agent-chose] No backfill of old receipts and no comparison of committed changes.

## Immediate Next Steps

1. Put to the operator, one at a time, the rulings the scope gate waits on: the three statements on GHI #1181 under the campaign's 2026-10-03 amendment, then the draft record-file list in `GZKIT_RECORD_PATHS`.
2. On the operator's word "sync", run `uv run gz git-sync` as a dry run and then with `--apply`, after committing the staged insights, ledger and run record.
3. Take the operator's words for the two proposed canaries and record them with `gz canary review --claim completion-scope-outside-allowed-paths` and `--claim completion-scope-records-admitted`.
4. Once the commits are on origin and the rulings are given, close GHI #1181 through the ghi-close skill citing the commits. GHI #1185 stays open until the exit runs on a real package completion.
5. Resume the R&D run only on the operator's invocation of the gz-rnd skill on `docs/rnd/renewing-vows.md`, starting from the unanswered statements in the record's frontier.

## Pending Work / Open Loops

- GHI #1181: built, unpushed, awaiting the operator's ruling on the three statements and the record-file list.
- GHI #1185: built, unpushed. Open question for the operator: whether the pipeline skill's Stage 5 gains a `gz airlock out` step now or waits for campaign Movement B.
- Two guard canaries in `data/guard_canaries.json` are proposed and unreviewed.
- R&D run `renewing-vows`: open. Unanswered statements, frontier items 22, 14, 15, 13 and 12, the rewrite of `docs/rnd/renewing-vows/review.md` and the re-base of `docs/rnd/renewing-vows/doctrine-merge.md` are all still owed. The Article 3 title amendment is ruled and not made.
- Agent-owed reads: campaign amendments older than 2026-09-27 and `docs/governance/chore-class-system.md`.
- Defects recorded as insights only, with no operator go: the coherence audit never run; two Draft `ADR-0.39.0` briefs failing `gz validate --sensitivity`; staleness in the GovZero directory; a stale pointer in the gz-obpi-pipeline skill; 283 Completed briefs drawing "no modified paths" from the brief validator.
- The session-exit bookmark `.gzkit/handoffs/20261009T201247Z-session-exit-bookmark.md` belongs to another session and has not been read against what that session did.
- Chores wait until the run closes; the operator plans a patch release after them.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` shows 0 behind and 5 ahead until the sync, then 0 and 0.
- `git status --short` shows only the insights log, the ledger and the run record staged.
- `uv run gz check` exits 0.
- `uv run gz obpi lock list` shows no lock held; no pipeline marker is active.
- `gh issue view 1181` and `gh issue view 1185` both report OPEN.
- `uv run gz canary review --help` to confirm the review flags before recording the operator's words.

## Evidence / Artifacts

- `src/gzkit/hooks/obpi.py`
- `src/gzkit/hooks/core.py`
- `src/gzkit/commands/obpi_complete.py`
- `src/gzkit/commands/obpi_precomplete.py`
- `src/gzkit/commands/obpi_scope_gate_claims.py`
- `src/gzkit/airlock/exit.py`
- `src/gzkit/commands/airlock.py`
- `src/gzkit/pipeline_runtime.py`
- `data/guard_canaries.json`
- `tests/hooks/test_scope_audit_records.py`
- `tests/commands/test_obpi_scope_gate_claims.py`
- `tests/test_airlock_exit.py`
- `docs/user/manpages/obpi-complete.md`
- `docs/user/manpages/airlock-out.md`
- `docs/governance/GovZero/obpi-transaction-contract.md`
- `docs/rnd/renewing-vows.md`
- `.gzkit/handoffs/20261009T094116Z-renewing-vows-command-joined-lapses-addressed.md`

## Settled Rulings

1453 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
