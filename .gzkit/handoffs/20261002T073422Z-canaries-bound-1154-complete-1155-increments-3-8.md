---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-02T07:34:22Z'
agent: claude-code
session_id: 8986dccc-70cd-440e-a8bb-9e8457d6757c
continues_from: .gzkit/handoffs/20261002T001654Z-gates-enrolled-1154-items-1-3-1155-increments-1-2.md
---

## Current State Summary

Worked the previous handoff's advised steps under the operator's rulings; everything is on origin/main except the last commit, which the git-sync after this document pushes. GHI #1155 (nine hollow gates carry no registered claim): increments 3 to 8 landed, one commit per gate, each with a refuse claim, an admit claim and a red witness with no survivors. #889 receipt gate (4f6a0ff01), #995 --json exit (3d8e02d69), #888 SUPPORT proof declaration (65bdff51d), #932 back-pointer match (47bfa4277), #933 reverse arm (3b3494cb4), #1124 gz tidy verdict (7393270a9). #996 needed no new claim: its fix commit eb91f20b6 already registered two claims naming validate_evaluation_justify_binding. GHI #1154 items 4 and 5 landed, so all five items are now in. Item 4 (06c2883ce): a shrink-ratchet surface is monotonic in identity, not only in count; 28 surfaces declare an identity, data/waiver_identity_baseline.json holds 1708 seeded identities. Item 5 (a267eed2b): data/guard_canaries.json binds a reviewed mutant to each of 8 registered refuse claims by a hash of guard source, claim id and designated failing test id; all 8 mutants are killed on an isolated copy of the tree in 14.5 s; 108 other claims are on the shrink-only roster data/guard_canary_grandfather.json. Both issues stay open: #1155 still owes enumeration of the other gate populations and #1154 still owes two parts of item 3.

## Important Context

Claim entrypoints must import the gate function themselves, because gate_targets are derived from the entrypoint's own imports. Production claim modules may not name a data directory path: the direct-reach check in config_derivation matches a quoted data path literal, so route locations through gzkit.registries (registry_path, load_registry). A claim that drives a handler with no seam binds its collaborators on the handler's module and restores them in a finally; the pre-commit enforcement-floor guard runs claims with Path.cwd patched, so a claim must not rely on the process cwd. The red witness flags a trailing return None as a survivor because reverting it is equivalent to falling through: express the decision as a conditional expression or an assignment, and drive every guard hunk with a test. The red witness for item 5 takes about 12 minutes because each reverted hunk re-runs the 18 s live canary tests; run it in the background. The verifier-pipe hook refuses a verifier followed by another statement, and it also reads heredoc text that mentions a verifier, so capture to a file, read the exit in the next statement, and write long bodies with the file tool. Each claim commit was verified by deleting its registration call in enforcement._ensure_production_claims_registered and watching its tests error. The declining tautological-test debt ceiling stepped to 230 on 2026-10-02 against 231 outstanding at HEAD, a pre-existing breach that surfaced when the date rolled; one test in tests/chores/test_eval_feedback_cluster.py was converted to assert through the chores loader to clear it, and the ceiling keeps stepping down 20 per month, so expect it to breach again. The 8 seeded canaries are recorded proposed by the agent with reviewed_by null; nothing marks them reviewed on the operator's behalf. The leftover modified .gzkit/ledger.jsonl is written by gz commands and carried by git-sync.

## Decisions Made

- [operator-ruled] Work step 1 (#889), then the remaining hollow gates in the listed order (verbatim: "proceed with step 1 (#889), then continue through step 2 in the order listed.").
- [operator-ruled] Take the next advised step, #1154 item 4 (verbatim: "do next"), then item 5 (verbatim: "#1154 item 5 next").
- [operator-ruled] Hold the handoff and git-sync while the red witness runs (verbatim: "hold"), then fix the red-witness survivors and re-run before syncing (verbatim: "1").
- [agent-chose] #996 gets no new claim: two claims already name its deciding function at HEAD, so the handoff's list of seven remaining gates was wrong on that one.
- [agent-chose] Identity monotonicity is opt-in at the registry level (identity_baseline), so the 0.0.73-09 fixtures are unchanged, and the baseline is a high-water set the audit never prunes: a removed entry may return, a new one may not, which keeps legitimate shrinks and the decommission chore from needing a second file edit.
- [agent-chose] Guard canaries are verified by a unit-tier fence (tests/governance/test_guard_canaries.py) plus a library, not a new validate scope, because a scope touches about 20 files and a CLI contract; the live kill runs on an isolated copy because a sweep rewrites the source file it mutates.
- [agent-chose] Canaries were seeded for the 8 refuse claims only, as proposed and unreviewed; the paired admit claims and the other claims sit on the shrink-only roster.
- [agent-chose] No progress comments were posted on #1154 or #1155 and neither was closed, because posting is outward-facing.

## Immediate Next Steps

1. Decision for you: review the 8 seeded canaries in data/guard_canaries.json. Each has reviewed_by null; say which mutants you accept, and I record your words as the reviewer. Rule on whether the admit claims need canaries too.
2. Decision for you: say whether to post progress comments on GHI #1154 and #1155 covering increments 3 to 8 and items 4 and 5, with the receipt ids, for your approval before they go out.
3. GHI #1155 remaining: enumerate the other gate populations (check steps that run a tool, precomplete checks, complete refusals, closeout steps), correct the two mis-derived gate_targets for module-size and tautological-debt, and decide on the precomplete verdict check and the lite-lane early return of the verdict gate, which are unclaimed.
4. GHI #1154 remaining under item 3: mismatched source and test identity (a graft that does not carry the test the REQ names) and a designated per-REQ discriminator. After that, decide whether to close #1154.
5. Bind canaries for the 108 roster claims over time, shrinking data/guard_canary_grandfather.json, and ask whether to start re-completion pipelines for the four repudiated OBPIs (OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02, OBPI-0.35.0-09); only the operator initiates them.

## Pending Work / Open Loops

Open: GHI #1154 (part of item 3) and GHI #1155 (enumeration, the two gate_targets, the unclaimed precomplete verdict check, 56 disclosed validate scopes and 108 claims without a canary). The seeded canaries await operator review. The tautological-test debt ceiling steps down monthly and will breach again without decommission work (chore decommission-tautological-tests). The red witness for a commit whose tests include live sweeps is slow; a faster way to drive it would help future gates. Carried from earlier handoffs: the chore_decommission_processed emitter gap, whether to draw the next ADR-0.35.0 OBPI, the unfiled patch-release diff_only listing, and trackers #611, #921, #978, #1028 and #799.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after git-sync; gh issue view 1154 1155: expect OPEN; waiver ratchet scope of gz validate: expect exit 0; gate enrollment scope of gz validate: expect exit 0 with 56 disclosed; the unit modules tests.governance.test_guard_canaries, tests.governance.test_waiver_identity_monotonic, tests.governance.test_pointer_integrity_claims, tests.commands.test_tidy_claims, tests.test_req_kind_support_claims, tests.commands.test_validate_json_exit_claims and tests.commands.test_obpi_precomplete_receipt_claims: expect OK; gz check: expect exit 0.

## Evidence / Artifacts

Claims: `src/gzkit/commands/obpi_precomplete_receipt_claims.py`, `src/gzkit/commands/validate_json_exit_claims.py`, `src/gzkit/req_kind_support_claims.py`, `src/gzkit/governance/trust_audits/pointer_integrity_claims.py`, `src/gzkit/commands/tidy_claims.py`. Item 4: `src/gzkit/governance/trust_audits/waiver_ratchet.py`, `src/gzkit/governance/trust_audits/waiver_identity_claims.py`, `data/waiver_identity_baseline.json`, `data/waiver_ratchet_registry.json`. Item 5: `src/gzkit/guard_canary.py`, `data/guard_canaries.json`, `data/guard_canary_grandfather.json`, `tests/governance/test_guard_canaries.py`. Tests: `tests/commands/test_obpi_precomplete_receipt_claims.py`, `tests/commands/test_validate_json_exit_claims.py`, `tests/test_req_kind_support_claims.py`, `tests/governance/test_pointer_integrity_claims.py`, `tests/commands/test_tidy_claims.py`, `tests/governance/test_waiver_identity_monotonic.py`. Red-witness receipts for the last two commits: arb-red-commit-a267eed2b9f8-317fc87a11e74b06b3c8d73501bd3225 (item 5) and arb-red-commit-06c2883ced16-8aec338953ac481394b888267ba5c3c1 (item 4). Predecessor: `.gzkit/handoffs/20261002T001654Z-gates-enrolled-1154-items-1-3-1155-increments-1-2.md`.

## Settled Rulings

1260 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
