---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T20:49:22Z'
agent: claude-code
session_id: e6800367-eb28-4b68-9624-65d94f7cdf17
continues_from: .gzkit/handoffs/20261018T164201Z-ro2-ro3-compat-token-block-route.md
---

## Current State Summary

Since the last handoff (542e8c87b) this session: cycled the drydock (session 696ca9a4 closed through the hard gate after four red guards were repaired in 4b356eadf; safe mode reopened as e6800367 under the same contract); reviewed the operator's Bodies of Knowledge note one decision at a time and wrote the rulings into requirements-model.md § 11 and the PRD (11c1d8f25); built two of them: insight_recorded ledger pointers for every insight (d7e332190) and the safe-mode contract pin at entry plus mx_contract_amended per committed edit (e621a4d2c, live and chaining); folded the analysis into the repair-order register, RO-3 re-scoped to the model (481fa9e6c); landed the token-block expiry rule as an RO-5 act, expired work locks booked and kept, never evicted, eight attested REQs amended in place (f29a96a4f, tests 78f079250, passage log 8071d7146). Tree clean, origin/main level at dc9717a26.

## Important Context

Safe mode is open as session e6800367 under docs/governance/harbor-pilotage-candidate-2026-10-15.md; the contract is now pinned in the ledger and each committed edit books mx_contract_amended through the post-commit recorder, so do not amend a commit after that recorder has booked against it (recorded defect: the first pin names rewritten commit 640629757). gz arb red --commit only runs the graded commit's own test modules; when a follow-up commit must carry the tests, prove the survivors with gzkit.mutation_witness.run_mutation_sweep, as 78f079250 did. Every gz insights remember now takes --source operator|agent; pass operator only for the operator's own words (an agent reading stays agent). An expired OBPI lock is now held: claims by another agent are refused; free it only by the holder's completion or release --force --abandon on the operator's word. Present design questions one at a time with their context; the operator corrected a wall of text this session.

## Decisions Made

- [operator-ruled] The close-and-reopen was a lease renewal inside one drydock, verbatim: 'you told me the lock was closed, asked that we close the old and open new.'
- [operator-ruled] The Bodies of Knowledge note is general design input, verbatim: 'the copy and paste is a general design discussion, not a comment on the dry dock mechanics'; reviewed in full: 'review ALL of that doc with me, so we can see how it can help gzkit while it is in drydock'.
- [operator-ruled] Rulings reach the ledger as a pointer, verbatim: 'what is the harm that the ledger notes that an insight was recorded and references it?', then 'Pointer + 3 fields (Rec.)'.
- [operator-ruled] Note review selections, verbatim: 'Baseline + forward rule (Rec.)', 'Hash at entry + amend event (Rec.)', 'Criterion + forward rule (Rec.)', 'Initiate per WP + measure (Rec.)', 'Statement + criteria fields (Rec.)', 'Reopen with your words (Rec.)', 'Inspector at freeze (Rec.)', 'Short note + residual (Rec.)', 'One act, four outcomes (Rec.)', 'derives_from on REQ (Rec.)', 'FR = need, REQ = req (Rec.)', 'Map in the model + note text (Rec.)'.
- [operator-ruled] The analysis enters the register, verbatim: 'are we done with that analysis? we are supposed to be in safe mode now', then 'Fold into existing ROs (Rec.)'.
- [operator-ruled] Token-block expiry, verbatim: 'Drydock act under RO-5 (Rec.)', 'Holder or your word (Rec.)', and for the attested REQs that assert reaping 'Amend in place (Rec.)'.
- [agent-chose] Landed the 78f079250 tests as a follow-up commit and proved the fifteen survivors by mutation sweep rather than amending f29a96a4f, whose SHA the contract pin had already booked.

## Immediate Next Steps

1. Put the open debt-aging question to the operator with context: advisory debt is measured per session, so a lease renewal resets it (recorded defect, scope mx-hardening); the recommendation is to age debt from the first safe-mode entry under the same contract.
2. Put the recurrence threshold for the common-versus-special-cause test (RO-1 and RO-7) to the operator; it goes in JSON.
3. Start the RO-2 specification (card task_9c394f63 awaits the operator): one resolver for every reader of version-shaped ids, the reused-prefix constraint (OBPI-0.28.0-01), and the baselines already in the passage log.
4. Specify RO-3 as re-scoped to requirements-model.md (data/catalog/ families, outcomes, REQs with statement and pass/fail criteria, proof, derives_from, applies_to; the freeze lock; the BDD alignment of user-facing outcomes).

## Pending Work / Open Loops

Open defects recorded as insights: per-session debt aging (mx-hardening); the first contract pin naming rewritten commit 640629757 (mx-contract-pin); gz mx and gz context have no tagged scenarios, and ADR-0.28.0 took the lite lane for a human-facing CLI verb (bdd-coverage); the reused 0.28.0 slot (identifier-migration). The session orientation is over its 4000-byte budget. Thirty chores are overdue. The semver-order work ruling still binds legacy ADR work until explicitly retired. The handback amendment comes only when the drydock's exit conditions are met.

## Verification Checklist

git log --oneline -12 (expect dc9717a26 down to 11c1d8f25); uv run gz handoff rulings --search 'Amend in place'; python3 -c to list mx_contract_amended rows in .gzkit/ledger.jsonl (expect a chain whose previous_sha256 links each row to the one before); uv run gz obpi lock list --json (an expired lock would show expired: true); read docs/governance/ieee/requirements-model.md § 11 and the harbor contract § Repair orders RO-0, RO-1, RO-2, RO-3, RO-5, RO-7, RO-8; git rev-list --left-right --count origin/main...HEAD reads 0 0.

## Evidence / Artifacts

- `docs/governance/ieee/requirements-model.md`
- `docs/design/prd/PRD-GZKIT-1.0.0.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `src/gzkit/insights/ledger_ref.py`
- `src/gzkit/mx/contract.py`
- `src/gzkit/lock_manager.py`
- `tests/mx/test_contract_pin.py`
- `tests/commands/test_token_block_never_evict_surfaces.py`
- `docs/governance/attested-req-subject-retirement.md`
- `.gzkit/rules/token-block-discipline.md`

## Settled Rulings

1606 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
