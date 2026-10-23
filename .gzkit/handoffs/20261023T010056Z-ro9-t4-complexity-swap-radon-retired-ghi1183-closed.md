---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-23T01:00:56Z'
agent: claude-code
session_id: 57b56ee8-15f4-4b71-bfa0-b1aa6c3a8352
continues_from: .gzkit/handoffs/20261022T094237Z-ro3-closed-ghi1259-ro9-t3-landed.md
---

## Current State Summary

RO-9 tranche 4 (lint and type to the maximum) is underway: its complexity half and the interrogate retirement are landed and pushed, and GHI #1183 is closed with evidence. Landed, all pushed, origin level: 25287b8e0 the Lizard C/C/C ceiling (gz validate --complexity-ceiling, default gz check) with Ruff C901 at 20, complexipy at 15 on its own shrink-only snapshot, xenon retired; 872fb99c8 its survivor tests; e1470956d Radon retired, the corpus re-distilled (distilled-characteristics-2026-10-22.md, six metrics), the advisor, guide and hook on lizard_ccn naming unmeasured functions; c9140b1a1 GHI #1233 closed (the Lint step's combined verdict witnessed); bdf268628 survivor tests; 6732155fe interrogate retired for Ruff's D-series; fb6be116f the dependency-currency chore scans every declared dependency and the complexity analyzers; d132d8af5 Radon-against-Lizard per-function comparison (99.3% identical, no verdict change at 20); 522f23790 passage-log row for the first two acts. GHI #1265 filed (cohesion_lcom4 measures cohesion %, not LCOM4). The astral baseline is at 8 rows.

## Important Context

Safe mode (drydock) is open: OBPI initiation and brief ceremony are suspended; guards outside gate5_invariants run advisory, so read gz check and validator output for [MX advisory] lines rather than trusting exit codes. A complexity distillation pass normally is OBPI work; it ran as an RO-9 act on the operator's ruling. gz arb red --commit grades a commit with its OWN tests, so a later test commit cannot change its verdict; survivors are driven in a follow-up commit and each new test is checked by reverting its hunk by hand. complexipy rewrites complexipy-snapshot.json when a function improves, so a commit can fail once on that hook; restage and recommit (the end-of-file fixer excludes that file). The fidelity self-check (tests.governance.test_qc_binding_self_check) replays the previous HEAD in a worktree with the live venv, so a dependency removal fails it until committed. The pythonic size-limits note and the complexity thresholds are now Lizard metrics; cohesion_lcom4 is the one bootstrap metric.

## Decisions Made

- [operator-ruled] Tranche 4 exceptions: "PT + COM812 + CPY001 (Rec.)"; scope "Package-strict, tests curated (Rec.)"; cognitive "15 with shrink-ratchet (Rec.)"; Radon metrics "Map or retire each (Rec.)".
- [operator-ruled] REQ-0.0.29-05-01/02/03, REQ-0.0.28-01-10 and REQ-0.0.27-03-05 "Amend in place (Rec.)"; REQ-0.0.27-03-07 and REQ-0.0.28-01-03 "Amend both in place (Rec.)"; the ceiling gate is a "gz validate scope (Rec.)".
- [operator-ruled] Module size "Lizard file NLOC, re-distilled (Rec.)"; the pass runs as "RO-9 act, you observe (Rec.)"; lizard_file_nloc "Same mapping (Rec.)"; lizard_nesting_depth "Corpus bands (Rec.)"; cohesion_lcom4 "Keep bootstrap, file GHI (Rec.)"; diff narration "Use the draft".
- [operator-ruled] Practitioner-eye observations "Carry forward"; lizard_ccn "Move radon_cc words"; cohesion "Keep with a note".
- [operator-ruled] A function Lizard skips is "Name it, don't guess (Rec.)": named on stderr by the advisor, guide and hook, never scored.
- [agent-chose] A body of `...` alone is exempt from the ceiling's discovery refusal; the population is the Python the uv_build wheel ships; the ceiling is read from [tool.ruff.lint.mccabe] max-complexity and an undeclared one is refused.
- [agent-chose] complexipy's own snapshot is the cognitive ratchet; the chore slugs complexity-reduction-xenon and module-sloc-cap-radon keep their historical names as stable identifiers.

## Immediate Next Steps

1. Ask the operator to review the complexity-ceiling canary: `uv run gz canary review --claim complexity-ceiling --attestor g0 --operator-text "<their words>"` (break: `if score.cyclomatic > ceiling` becomes `if False`; test test_function_over_the_ceiling_fails_with_its_score; killed).
2. Ask the operator to rule on the Ruff ALL package findings (about 13k in src/gzkit, the largest DOC201 at 3,564): fix all, or a keyed shrink-ratchet baseline like complexipy's. Then land Ruff ALL with the ruled exceptions (PT family, COM812, CPY001) and the tests/features/scripts curation list.
3. Land [tool.ty] with the warn rules raised, ruling the 2026-08-08 features/ exclusion afresh; then TID251 and `ruff analyze graph` behind the import-boundary checks.
4. Add the tranche 4 passage-log row for the remaining acts, then check the tranche's done condition ("No lint or type row remains; GHI #1183 [settled] closes"): #1183 [settled] is closed; the astral baseline's remaining lint rows decide the rest.

## Pending Work / Open Loops

- GHI #1265: cohesion_lcom4 rename and lower-is-worse bands; the bands need ADR-pool.polarity-aware-threshold-model.
- The site-by-site Ruff security findings named in the spec: S506 (quality.py YAML loader), S608 (trust_audits/cli.py), two S701, about 260 S603/S607/S404.
- RO-9 tranches 5 to 7 after tranche 4; Ruff 0.17.2, ty 0.0.91 and Lizard 1.24.2 are out (the dependency-currency chore surfaces them).
- The release-workflow first live run (release.yml) still wants watching at the next release.
- The MX hangar's advisory debt keeps aging; renew or exit the lease on the operator's word.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads 0 0.
- `uv run gz validate --complexity-ceiling` passes; `uv run complexipy -q` passes.
- `uv run gz validate --astral-discipline` shows no [MX advisory] lines; the baseline holds 8 rows.
- `gh issue view 1183 --json state` and `gh issue view 1233 --json state` read CLOSED; #1265 OPEN.
- `uv run gz test` for the full unit tier (12,574 tests at e1470956d).

## Evidence / Artifacts

- `docs/governance/harbor-ro9-astral-toolchain.md` (§ Ruled for tranche 4, the per-function comparison)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (passage-log row, tranche 4 first two acts)
- `docs/governance/complexity/distilled-characteristics-2026-10-22.md`
- `docs/governance/complexity/complexity-thresholds-rationale.md` (amendment record, Radon retired)
- `src/gzkit/governance/trust_audits/complexity_ceiling.py`
- `src/gzkit/complexity/functions.py`
- `src/gzkit/complexity/lizard_adapter.py`
- `complexipy-snapshot.json`
- `artifacts/receipts/arb-red-commit-25287b8e0068-caf10c11f34c45e3a1223d89b2b82fcd.json`
- `artifacts/receipts/arb-red-commit-e1470956d587-bde41586336347c7a094ce935cd77f8f.json`

## Settled Rulings

1664 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
