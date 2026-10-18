---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T23:35:30Z'
agent: claude-code
session_id: c0d62a11-d764-4f30-9f34-95f27eba758e
continues_from: .gzkit/handoffs/20261018T225102Z-ro2-specified-recurrence-and-debt-landed.md
---

## Current State Summary

Since the last handoff (ff8fa7dd1, landed with the RO-2 specification): CI had failed on every push since dc9717a26 with 21 full-tier unit tests the per-change gz check never ran. All 21 are fixed in 965b28524 across twelve causes: three preflight tests still asserting reaping after never-evict (re-seated onto the orphan mx-session lock); six complexity-rule tests pinning rule-version literals that RO-1 act (d) bumped (now read the canonical marker); `gz mx log` named in safe-mode-doctrine.md (the log is rendered by `gz mx exit`); the live OBPI-0.9.0-02 brief citing the hook RO-1 act (b) deleted (dated note, on the operator's ruling); recurrence_threshold.json given its authority and the module default removed (a missing registry now exits 1); the private cross-package import promoted to lock_manager.adr_id_from_obpi; a guard canary bound for mx-hardening, killed live and reviewed by the operator (7e58603d7); two ledger-schema fields made nullable to match their models; gz-justify's last_reviewed quoted again; the --mx-hardening help cut to 71 chars; validate.md's debt-aging row corrected. gz check --full passed locally; CI on 9388120da (the repair) passed, the first green since dc9717a26; the run on 7e58603d7 was in progress at writing. Tree clean, origin/main level.

## Important Context

Safe mode is open as session e6800367 under docs/governance/harbor-pilotage-candidate-2026-10-15.md (lease to about 2026-10-19T16:50Z). While it is open, plain `gz check` demotes every validator outside the floor to advisory and runs only the tests a change touches, so a drydock act can pass locally and break CI: run `uv run gz check --full` before pushing an act, and read the CI run after each push (`gh run list --limit 3`). The RO-2 specification (docs/governance/harbor-ro2-identity-seam.md) is the brief for tranche 1. `gz arb red --commit` grades only the commit's own test modules: when a hunk is exercised only by an untouched module, add the assertion to the commit's tests; restructure an equivalent hunk away rather than chase it; `inconclusive` (a revert that raises) is disclosed, not repaired. Amend only a commit that is unpushed and that the contract pin has not booked (it books commits that edit the harbor contract). The verifier-pipe-gate hook matches verifier names inside heredoc commit messages: write the message to a file and commit -F in its own call.

## Decisions Made

- [operator-ruled] The live OBPI-0.9.0-02 brief's stale Discovery row, verbatim selection: 'Dated note on the row (Rec.)' — line 92 keeps its observation and gains '(instruction-router.py not present since 2026-10-17: removed by drydock RO-1 act b)'.
- [operator-ruled] The mx-hardening guard canary, verbatim: 'approve the mx-hardening canary' (booked by gz canary review as guard_canary_reviewed).
- [agent-chose] Re-seated the six complexity-rule tests to read the canonical rule-version marker instead of pinning a literal, as a doctrine-neutral surface repair of attested REQ-0.0.27/0.0.28 coverage (their REQs require agreement, not a number).
- [agent-chose] Removed DEFAULT_MIN_OCCURRENCES rather than roster it: the threshold lives only in data/recurrence_threshold.json and a missing registry is reported, never defaulted past.
- [agent-chose] Left correction_mining.DEFAULT_RECURRENCE_THRESHOLD as is and recorded it: ADR-0.0.70's stdlib-only fence forbids that module importing the registry seam.

## Immediate Next Steps

1. Confirm CI on 7e58603d7 finished green (`gh run list --limit 3`); if not, read `gh run view <id> --log-failed` before anything else.
2. Start RO-2 tranche 1 per docs/governance/harbor-ro2-identity-seam.md: resolve its three known uncertainties first, then the seam, the JSON schemas tied to it, the id-seam validator scope with its seeded baseline and registry entry, and the resolution check; one act, failing test first, `gz check --full` before the push.
3. Once tranche 1 lands, propose tranches 2 to 5 as cheaper sessions, one per tranche, each brief citing the spec's tranche row.
4. Specify RO-3 as re-scoped to requirements-model.md (data/catalog/ families, outcomes, REQs with statement and pass/fail criteria, proof, derives_from, applies_to; the freeze lock; the BDD alignment of user-facing outcomes).
5. Put the RO-2/RO-3 compatibility path (requirements-model.md § Step 5, half reached) to the operator once tranche 1 and the RO-3 spec exist.

## Pending Work / Open Loops

For the operator to rule: correction_mining.DEFAULT_RECURRENCE_THRESHOLD duplicates the maxim-13 threshold but cannot read the registry under ADR-0.0.70's fence (pass it in from the chore runner, or record the two as deliberately separate). Recorded process defect: safe-mode demotion plus a CI-only full tier let six pushes land red; the next act should run `gz check --full` first. Carried open defects: the first contract pin naming rewritten commit 640629757; gz mx and gz context have no tagged scenarios and ADR-0.28.0 took the lite lane for a human-facing verb; the reused 0.28.0 slot, now bounded by RO-2's fail-closed resolver. RO-2 tranche 3 owns the separator-less first-match brief finders. The session orientation is over its 4000-byte budget; thirty chores are overdue. The handback amendment waits for the drydock's exit conditions.

## Verification Checklist

gh run list --limit 3 (expect 9388120da success and 7e58603d7 finished); git log --oneline -6 (expect 7e58603d7 and 965b28524); git rev-list --left-right --count origin/main...HEAD reads 0 0; uv run gz check --full exits 0; uv run gz handoff rulings --search 'Dated note on the row' returns the ruling; read the harbor contract's RO-2 row and docs/governance/harbor-ro2-identity-seam.md.

## Evidence / Artifacts

- `docs/governance/harbor-ro2-identity-seam.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/safe-mode-doctrine.md`
- `data/recurrence_threshold.json`
- `data/guard_canaries.json`
- `src/gzkit/insights/recurrence.py`
- `src/gzkit/commands/insights.py`
- `src/gzkit/lock_manager.py`
- `src/gzkit/schemas/ledger.json`
- `tests/commands/test_preflight.py`
- `tests/governance/test_complexity_thresholds_rule.py`
- `tests/commands/test_insights_recurrence.py`
- `docs/user/manpages/insights-recurrence.md`

## Settled Rulings

1617 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
