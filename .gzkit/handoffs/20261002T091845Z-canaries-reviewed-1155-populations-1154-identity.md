---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-02T09:18:45Z'
agent: claude-code
session_id: 2a7c15bc-66bf-4b19-bcfb-abf7bf6698d0
continues_from: .gzkit/handoffs/20261002T073422Z-canaries-bound-1154-complete-1155-increments-3-8.md
---

## Current State Summary

Worked all five advised steps of the predecessor under the operator's rulings. Step 1: the 8 refuse canaries were reviewed by the operator (7f1ace88f); 8 admit canaries (always-refuse mutants) were bound (67faf51ca); session orientation now names unreviewed canaries (4803dd028, 4ceccf9c2). Step 3, GHI #1155: found that increment 2's claims named obpi_complete_adversarial._enforce_adversarial_validation, which no production path calls since 8436bfd8f (GHI #985); the claims now drive acceptance.assess_readiness (1f35158d8, 310d3ef36, 37014cc66). Acceptance (d): enforces() takes delegates_to and 17 qc controls declare the command they drive (597c500ba). Acceptance (a): gate_population inventories the precomplete, complete, closeout and check-step populations, 56 members, 7 named, 49 disclosed on data/gate_population_grandfather.json, with its own claim pair and canaries (a8b8862fd, 5f37c06f8). Step 4, GHI #1154 item 3: run_red_witness now requires a green current-tree baseline, every named test executed in the graft, and a RED attributed to a named test (55e5b47af, 0ac557f4d); class-level @covers names its class (a425a4c65). Step 5: gate-enrollment canary pair bound (02abbd95b), roster 108 to 98. Step 2: progress comments posted on #1154 and #1155. All pushed except this handoff, which the git-sync after it carries.

## Important Context

The canary live kill runs in the unit tier one designated test at a time, so a canary whose only designated test is the full enforcement floor (8.8 s) costs that much on every gz check; most of the 98 roster claims have no focused test, which is why only cheap ones were bound. A canary's isolated copy carries src, tests and data only, so a designated test needing other files is inconclusive there (airlock-in-unaccounted-seam was tried and withdrawn). Claim entrypoints import only their gate; registry readers go in a helper so gate_targets stays the gate, and a control passes the floor's populated registry rather than re-running discovery (test_default_run_registers_production_claims fails otherwise). The arb red --commit verdict counts only the commit's own test modules: moved code and call sites driven by other suites show as survived, and docstring or signature hunks show as survived or inconclusive; each commit message names which. The verifier-pipe hook refuses a verifier followed by any other statement, including inside an && chain, so read the exit in the very next statement. A subagent's worktree is removed and its local branch deleted after its diff is applied to main.

## Decisions Made

- [operator-ruled] Accept the 8 seeded refuse canaries (verbatim: "accept all 8").
- [operator-ruled] Work every advised step of the predecessor (verbatim: "do all 5 steps").
- [operator-ruled] Run the governed insights command when canon requires it rather than deferring on a harness denial (verbatim: "NO! you run that insights command - that is ridiculous").
- [agent-chose] The two adversarial canaries were rebound to the live reducer and returned to reviewed_by null, because the operator's review covered the old mutants on the dead function.
- [agent-chose] The dead verdict gate, the five ignored --adversary-* flags and the stale prose were recorded as an insight and not filed or fixed: removal crosses the OBPI-process fence quoted in Draft brief OBPI-0.36.0-07, whose premise rests on that module, so routing is the operator's.
- [agent-chose] Gate members resolve one level down; deeper claims are disclosed with a reason rather than counted, the conservative direction increment 1 chose.
- [agent-chose] Canaries were bound only where a focused designated test keeps the unit-tier kill cheap.

## Immediate Next Steps

1. Decision for you: review the 13 unreviewed canaries in data/guard_canaries.json (8 admit partners, the 2 rebound adversarial ones, the 2 gate-population and 2 gate-enrollment ones); session orientation lists them.
2. Decision for you: route the dead Step-4b verdict gate (insight recorded 2026-10-02): delete obpi_complete_adversarial._enforce_adversarial_validation and obpi_precomplete._check_adversarial_validation, retire or wire the five --adversary-* flags, correct the prose, and amend OBPI-0.36.0-07's premise; this crosses the OBPI-process fence, so it waits for your ruling.
3. Decision for you on GHI #1154: should every BEHAVIOR REQ designate one discriminator test (the audit row calls this a broadening that needs a doctrine decision), and how should canaries scale: a per-claim designated test, a scheduled rather than per-change live kill, or kill runs only for canaries whose binding changed.
4. Decision for you: whether to start re-completion pipelines for the four repudiated OBPIs (OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02, OBPI-0.35.0-09); only the operator initiates them.
5. GHI #1155 remaining: measure the mechanism at the nine fix parents, and decide whether a mechanism should detect a claimed or documented gate that no production path calls (GHI #1158 [settled] was the same class).

## Pending Work / Open Loops

Open: GHI #1154 (designated discriminator ruling, canary scale) and GHI #1155 (nine-parent replay, 56 plus 49 disclosed members, the uncalled-gate class). 13 canaries await review. The dead Step-4b verdict gate awaits routing. The gz handoff resume citation resolver reported OBPI-0.34.0-02 and OBPI-0.35.0-09 as unknown while gz obpi status shows both REPUDIATED; the ledger names them with slugged ids, unverified as the cause. The typecheck control runs uv run ty check . while the gz check step runs ty check . --exclude features, a divergence the delegates_to declaration now makes visible. Carried: the tautological-test debt ceiling steps down monthly; the chore_decommission_processed emitter gap; the unfiled patch-release diff_only listing; trackers #611, #921, #978, #1028 and #799.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after git-sync; uv run gz validate --gate-enrollment: expect exit 0 with 101 scopes and 56 other gates inventoried; uv run python -m unittest tests.governance.test_guard_canaries tests.test_acceptance_claims tests.governance.test_gate_population tests.governance.test_gate_population_claims tests.test_red_witness tests.governance.test_enforces_registry: expect OK; uv run gz check: expect exit 0; gh issue view 1154 1155: expect OPEN.

## Evidence / Artifacts

Claims and audits: `src/gzkit/acceptance_claims.py`, `src/gzkit/governance/trust_audits/gate_population.py`, `src/gzkit/governance/trust_audits/gate_population_claims.py`, `src/gzkit/governance/trust_audits/_qc_claim_delegations.py`, `src/gzkit/red_witness.py`, `src/gzkit/unit_run_provenance.py`, `src/gzkit/traceability.py`, `scripts/session_orientation.py`. Data: `data/guard_canaries.json`, `data/guard_canary_grandfather.json`, `data/gate_population_grandfather.json`. Tests: `tests/test_acceptance_claims.py`, `tests/governance/test_gate_population.py`, `tests/governance/test_gate_population_claims.py`, `tests/test_red_witness.py`, `tests/governance/test_enforces_registry.py`, `tests/scripts/test_session_orientation.py`. Docs: `docs/user/manpages/validate.md`, `docs/user/manpages/arb-red.md`. Red-witness receipts: arb-red-commit-597c500ba9c6-ec0be9836c2746c69c9e8ff8f9e3af09 (driven), arb-red-commit-55e5b47afe52-3e4c31fe319747f3b6279cfb8f5ae725, arb-red-commit-a8b8862fd865-22e17b3e1fc944b69ed357ec1938ad92, arb-red-commit-37014cc668bc-88bf8e0c5d37472bb9064fbb691393db, arb-red-commit-5f37c06f8bd2-aa7d8523c9dd49fbbafa68310dc22819, arb-red-commit-a425a4c65abe-1af1268b308b45509ad81ffb451c5022. Comments: issues/1154#issuecomment-5949013782, issues/1155#issuecomment-5948866325. Predecessor: `.gzkit/handoffs/20261002T073422Z-canaries-bound-1154-complete-1155-increments-3-8.md`.

## Settled Rulings

1263 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
