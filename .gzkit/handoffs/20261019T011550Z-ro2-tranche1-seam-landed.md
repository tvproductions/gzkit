---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-19T01:15:50Z'
agent: claude-code
session_id: 0f093cd5-657a-4ef0-afd7-cbbb192b698a
continues_from: .gzkit/handoffs/20261018T233530Z-ci-green-full-tier-repaired.md
---

## Current State Summary

RO-2 tranche 1 landed and CI is green (run 39183253070 on c772375f2). Commits since the last handoff (64dced5c5): 7ef573c67 feat(id-seam), the seam and its witness; 3c813e005 test(id-seam), drives the hunks the red witness found undriven; 84d128c88 chore(drydock), passage log; a8bca1ef6 and c772375f2 gz git-sync; d09a11722 chore(canary), the operator's review of the two identity-seam canaries. The seam: one grammar body per kind in core/models.py (two-digit widths, measured to reject no live id), re-exported by triangle and tasks and byte-equal in obpi.json, obpi_brief_structure.json and adr.json; core/id_resolver.py with resolve (rename fold, separator-only prefix expansion, fail closed naming candidates) and parent_of (ledger, brief, then a marked spelling fallback). gz validate --id-seam runs in gz check as Identity seam: AST scan, a shrink-only baseline data/id_seam_baseline.json of 187 rows and 221 sites, and a resolution check over every @covers REQ, scenario REQ tag and brief frontmatter id. Red witness: 7ef573c67 undriven (41 survived); 3c813e005 no-production-hunks; regrading the act's hunks against both commits' tests gave 100 killed, 79 inconclusive, 6 survived, each a revert that changes nothing. gz check --full passed before each push. Tree clean, origin/main level.

## Important Context

Safe mode is still open as session e6800367 under docs/governance/harbor-pilotage-candidate-2026-10-15.md; its advisory debt is about 40 h and its lease ends near 2026-10-19T16:50Z. Plain gz check demotes validators to advisory in the hangar, so run uv run gz check --full before every push and read CI after it. The RO-2 spec (docs/governance/harbor-ro2-identity-seam.md) now records tranche 1's findings: the three uncertainties answered, the width settlement, the compose kind, and the seeded counts by kind (ADR 47, OBPI 40, REQ 20, TASK 7, parent 22, compose 85 sites). Tranches 2 to 5 each retire one kind's rows from the baseline; every removal must lower or delete its row and set baseline_count in data/waiver_ratchet_registry.json and the identities in data/waiver_identity_baseline.json in the same commit, or the scope fails. A change to check_seam_baseline rebinds the two canaries in data/guard_canaries.json, which then need the operator's review again. gz arb red --commit grades only the commit's own test modules; wiring hunks need assertions in the commit's own tests. The verifier-pipe-gate hook matches verifier names inside heredocs: write commit messages to a file and commit with -F.

## Decisions Made

- [operator-ruled] Resume ruling on the predecessor handoff, verbatim: "proceed — start RO-2 tranche 1 per the spec" (booked by gz handoff decide).
- [operator-ruled] The identity-seam and identity-seam-baselined guard canaries, verbatim: "approve those canaries (explain them first please)" (booked by gz canary review as guard_canary_reviewed).
- [operator-ruled] Once CI is green, write the handoff and propose tranches 2 to 5 as separate sessions, verbatim: "Yes — once CI is green, write the handoff and propose tranches 2 to 5 as separate sessions."
- [agent-chose] Widths settled at two digits for every numeric component; the resolver takes no width into its match so attested REQ-0.35.0-15-02 stays true.
- [agent-chose] Added the compose kind (id-shaped f-strings) to the scan and gave its rows to tranche 5, so an empty baseline can witness that no spelling-derived parent or child-prefix scan remains.
- [agent-chose] A REQ no brief lists resolves when its spelled OBPI is parked or withdrawn, recorded as such; only module- and class-level @covers decorations are bindings.
- [agent-chose] Removed the dangling @REQ-0.0.32-06-10 tag and its step-module citation as a direct defect fix; recorded as a defect-resolution insight (scope drydock-ro2).

## Immediate Next Steps

1. Start the RO-2 tranche 2 to 5 sessions from their cards (one per tranche: REQ and TASK readers; OBPI readers and brief finders; ADR readers and package finders; parent and compose sites through parent_of), each landing as one act with a TASK-ro2-<slug> trailer, a failing test first and gz check --full before push.
2. Specify RO-3 as re-scoped to requirements-model.md (data/catalog/ families, outcomes, REQs with statement and pass/fail criteria, proof, derives_from, applies_to; the freeze lock; the BDD alignment of user-facing outcomes).
3. Put the RO-2/RO-3 compatibility path (requirements-model.md § Step 5) to the operator now that tranche 1 exists and once the RO-3 spec does.
4. Decide with the operator when to close the hangar (gz mx exit through the gz-mx skill): the debt is about 40 h and the lease ends near 2026-10-19T16:50Z.

## Pending Work / Open Loops

Tranches 2 to 5 of RO-2 are open; their sessions are proposed as cards and none has started. The Windows CI investigation is proposed as a card (the unit tier takes 758 s on Windows against 444 s on Linux). Carried for the operator: correction_mining.DEFAULT_RECURRENCE_THRESHOLD duplicates the maxim-13 threshold but cannot read the registry under ADR-0.0.70's stdlib-only fence. Carried defect from the RO-2 spec: commands/task.py resolves a short OBPI id without project_root, ignoring the parked flag (the GHI #653 [settled] divergence); tranche 3 or a direct fix owns it. Carried: the first contract pin naming rewritten commit 640629757; gz mx and gz context have no tagged scenarios; the session orientation is over its 4000-byte budget; thirty chores are overdue; the handback amendment waits for the drydock's exit conditions.

## Verification Checklist

gh run list --limit 3 (expect 39183253070 success); git log --oneline -7 (expect d09a11722, 84d128c88, 3c813e005, 7ef573c67); git rev-list --left-right --count origin/main...HEAD reads 0 0; uv run gz validate --id-seam exits 0; uv run python -m unittest tests.test_id_seam_grammar tests.test_id_resolver tests.governance.test_id_seam_audit passes; uv run gz handoff rulings --search 'approve those canaries' returns the ruling.

## Evidence / Artifacts

- `docs/governance/harbor-ro2-identity-seam.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `src/gzkit/core/models.py`
- `src/gzkit/core/id_resolver.py`
- `src/gzkit/governance/trust_audits/id_seam.py`
- `data/id_seam_baseline.json`
- `data/guard_canaries.json`
- `data/waiver_ratchet_registry.json`
- `docs/user/manpages/validate.md`
- `tests/test_id_seam_grammar.py`
- `tests/test_id_resolver.py`
- `tests/governance/test_id_seam_audit.py`

## Settled Rulings

1620 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
