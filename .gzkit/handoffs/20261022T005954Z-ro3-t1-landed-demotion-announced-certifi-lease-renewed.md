---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-22T00:59:54Z'
agent: claude-code
session_id: ac786a88-b3a3-487c-8b23-f1f7a1a58a08
continues_from:
- .gzkit/handoffs/20261021T083404Z-ro9-t2-landed-ro3-specified.md
- .gzkit/handoffs/20261021T202419Z-session-exit-bookmark.md
---

## Current State Summary

Since `.gzkit/handoffs/20261021T083404Z-ro9-t2-landed-ro3-specified.md` (and folding in the exit bookmark `.gzkit/handoffs/20261021T202419Z-session-exit-bookmark.md`, which recorded only where session ac786a88 stopped): RO-3 tranche 1 landed in 96e7ed62f and cd1afd70f, with its passage-log row in 61ed180d7. The registry read seam admits `catalog/`; `data/catalog/` holds families.json (decision 8.3's eleven families seeded), outcomes.json and reqs.json (empty), with frozen models in gzkit.models.catalog, committed schemas, and `gz validate --catalog` in gz check as Requirements catalog. gz validate now announces a demoted scope's findings on stderr instead of dropping them (c00f1ee82, a4174be2b; row 55c230ce7). certifi bumped to 2026.10.19 (bba2ebb75); Dependabot alert 29 reads fixed. The drydock lease was renewed at 2026-10-22T00:37Z (3160f9a4c) and the requirements-catalog canary was reviewed (39d107504). CI green on bba2ebb75; origin/main 0 0.

## Important Context

- The drydock lease (MX session 57346836, renewed 2026-10-22T00:37Z, 24h) expires about 2026-10-23T00:37Z. Renew with `gz mx renew --attestor g0` through the gz-mx skill on the operator's word. The mx-session lock is now held by this Claude session's agent id (claude-code-ac786a88).
- The per-change gz check misses tests that scan a registry or the tree. Run `uv run gz test` before pushing any change that adds a validate scope, a CLI flag, a check step or an id grammar: on RO-3 tranche 1 it caught the id-seam ratchet and the QC binding's step-slug claim key, both invisible to gz check (insight scope gz-check-changed-tests).
- A new validate scope in gz check touches about fifteen surfaces: the flag and dispatch, the scope registry and policy-breach set, the quality runner, the check step and its guard meta (the guard name is the step name slugged, and the negative-control claim id must equal it), qc_binding, scope membership and step concurrency, the registry parity list, the negative control with entrypoint, exemption and population, a guard canary, and the manpage. 94ee376e4 (brief size) and 96e7ed62f are the worked examples.
- An id grammar (for example `REQ-<n>`) must live in gzkit.core.models; spelling it elsewhere fails `gz validate --id-seam`.
- Under safe mode a demoted scope's findings now print on stderr, but the stdout line still says All validations passed (insight scope gz-validate-demotion).
- The GHI #1263 CI switch stays parked in git stash@{0}.

## Decisions Made

- [operator-ruled] Proceed on the handoff's RO-3 step (verbatim: "proceed: RO-3 tranche 1 from harbor-ro3-requirements-store.md § Tranches"), booked with gz handoff decide; the lease step was set aside as not yet due.
- [operator-ruled] Fix the silent demotion directly (verbatim: "Fix the silent demotion in gz validate here as a direct fix, then push.").
- [operator-ruled] Bump certifi directly (verbatim: "Bump certifi in uv.lock to 2026.10.19 as a direct fix, verify, commit and push.").
- [operator-ruled] Renew the drydock lease (verbatim: "renew lease").
- [operator-ruled] Approve the requirements-catalog canary (verbatim: "Approve the requirements-catalog canary.").
- [agent-chose] The REQ entry's criteria take the ghi-close closure-contract fields: state_or_input, required_outcome, evidence.
- [agent-chose] The tranche-1 structure checks read 'a code's band matching its family' as the band enum on each family plus an outcome's family letter existing in the legend; no band is hard-coded outside families.json.
- [agent-chose] The seam's return line stays the original `/` join; `gz arb red --commit cd1afd70f` reads undriven there as an equivalent mutant, recorded in the passage log rather than churned.

## Immediate Next Steps

1. RO-3 tranche 2 from `docs/governance/harbor-ro3-requirements-store.md` § Tranches: outcome_transitioned and req_proof_recorded on all five registration surfaces, their library writer functions and isolated producer probes in gzkit.ledger_producer_probe; done when the inertness check reads both verified and a disallowed transition and a fourth verdict are refused.
2. Then RO-3 tranches 3 and 4; tranche 3 opens with the operator's choice on the freeze lock (land it against RO-5's declared baseline event, vacuous until it fires, or leave it to RO-5).
3. Then GHI #1259; RO-9 tranches 3 to 7 follow in order.
4. When the operator chooses: GHI #1264 (the API reference; which modules count is the operator's call), GHI #1262 (debt reading), GHI #1263 (parked).
5. Renew the lease when the orientation announces it expired, on the operator's word.

## Pending Work / Open Loops

- RO-3 tranches 2 to 4 and the known uncertainties the specification names (the freeze lock's event, depends_on non-outcome targets, section 7 attribute ids, the delivery-event list).
- RO-9 tranches 3 to 7; the Read the Docs asdf step, unverified until the next tag build.
- GHI #1264, GHI #1262, GHI #1263 (parked in git stash@{0}).
- Insight gz-validate-demotion: the stdout pass line under safe mode does not count demoted scopes.
- Insight gz-check-changed-tests: the per-change test-selection gap, a neighbour of GHI #1240.
- Unverified ordering question: gz status shows ADR-0.34.0 at 4 of 5 OBPIs while the campaign's topmost item sits in ADR-0.35.0; check whether 0.34.0's fifth OBPI is withdrawn or held before reading it as a semver-order conflict.
- 30 overdue chores, carried.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads `0 0`; `gh run list --limit 1 --workflow CI` shows success on bba2ebb75 or later.
- `uv run gz validate --catalog` exits 0; `uv run python -m unittest tests.governance.test_catalog tests.test_registries` passes.
- `uv run gz obpi lock list` shows the mx-session lock active with a lease from 2026-10-22T00:37Z.
- `gh api repos/tvproductions/gzkit/dependabot/alerts/29 --jq .state` prints fixed.
- The orientation lists no canary awaiting review.

## Evidence / Artifacts

- `docs/governance/harbor-ro3-requirements-store.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `src/gzkit/models/catalog.py`
- `src/gzkit/governance/trust_audits/catalog.py`
- `src/gzkit/registries.py`
- `src/gzkit/commands/validate_cmd.py`
- `data/catalog/families.json`
- `data/guard_canaries.json`
- `tests/governance/test_catalog.py`
- `tests/mx/test_checkpoint.py`
- `uv.lock`

## Settled Rulings

1646 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
