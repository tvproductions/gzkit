---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-02T00:16:54Z'
agent: claude-code
session_id: bb8d4458-d180-48b9-8a37-422b7c435b36
continues_from: .gzkit/handoffs/20261001T085000Z-repudiations-four-defects-fixed-s9-s10-ruled.md
---

## Current State Summary

Worked the advised steps of the predecessor handoff, all pushed, origin/main in sync. GHI #1160 fixed and closed (8026fc0dc): a path:symbol discovery citation now resolves on its file. GHI #1154 (gate tests feed absence and stand-ins): items 1 to 3 of 5 landed, the issue stays open. Item 1 (572314835): a zero-exit unit run that tested nothing is refused (unittest-parallel exits 0 for an empty or all-skipped suite). Item 2 (86465500b): covering runs must execute in gz obpi complete, and ADR closeout honors REQ kind. Item 3 (21ca3f404): a RED base run that executed no test is not-applicable, not a weak RED or a hollow accusation. GHI #1155 (gates with no registered claim): two increments landed, the issue stays open. Increment 1 (30084eb10): gz validate --gate-enrollment inventories validate scopes no enforcement claim names (101 scopes, 44 named, 57 disclosed shrink-only). Increment 2 (0913f339d): a paired claim for the Step-4b verdict gate covering #959 and #960; 7 of the 9 hollow gates remain.

## Important Context

Each fix commit carries an arb red --commit receipt that resolves under artifacts/receipts; cite those, not verdict text. arb red --commit only re-runs the commit's own test modules, so pure wiring hunks (check-step registration, qc classification) show survived there; I verified by reverting each that a pre-existing coherence suite fails, and that lint witnesses the __all__ entry. A claim's gate_targets come from the entrypoint's OWN imports, so the entrypoint must import the gate function itself, not a helper. Controls must read get_enforcement_registry(), because the floor test requires one discovery per run. Reads of data/ files go through gzkit.registries (a fenced seam), and json.dumps reformats data/config_registry.json, so insert entries as text. The verifier-pipe hook refuses a verifier chained with a later statement; capture to a file and read the exit code immediately. The unit-tier floor in data/unit_collection_floor.json is 11000, my own choice against a measured 11229 run. Operator ruling on #1154: lite-lane REQ-coverage gaps stay warn-only per AGENTS.md (ADR-0.0.25). The leftover modified .gzkit/ledger.jsonl is unstaged and not mine to hand-edit; git-sync carries it.

## Decisions Made

- [operator-ruled] Work the advised steps 2, 3 and 4 (verbatim: "proceed with 2 then 3 and 4").
- [operator-ruled] Take item 1 of GHI #1154 first, then 2 and 3 (verbatim: "A"; then "do item 2, then 3").
- [operator-ruled] Keep lite-lane REQ gaps warn-only, take the stated defaults for #1154 items 4 and 5, and do #1155 next (verbatim: "approve all three").
- [operator-ruled] Start enrolling the nine hollow gates, beginning with the verdict gate (verbatim: "a").
- [agent-chose] The unit-tier collection floor is 11000, below the measured 11229 so ordinary test deletion does not trip it.
- [agent-chose] The enrollment find mechanism covers validate scopes only and discloses the 57 unnamed ones, rather than writing controls for all of them.
- [agent-chose] The precomplete verdict check was not claimed: it is the bypassable preflight and complete is the chokepoint.

## Immediate Next Steps

1. Decision for you: I'd go on one gate per commit, each with its own control and arb red check, as with the verdict gate. Next would be #889 [settled], the receipt gate, where a bare {} file passed as a receipt while 577 of 3718 live receipts recorded failed runs. Say if you want a different order, or want me to pause here.
2. After that ruling, continue the remaining hollow gates one per commit: #996 [settled], #995 [settled], #888 [settled], #932 [settled], #933 [settled] and #1124 [settled].
3. GHI #1154 item 4 (waiver and baseline monotonicity): default ruled is that a renamed or moved operation is new and fails unless a reviewed authorization record names it; read the existing waiver ratchet first to confirm it can host that record.
4. GHI #1154 item 5 (reviewed guard mutation canaries): default ruled is binding each canary by a hash of the guard source, the REQ id and the designated failing test id, built on mutation_witness.
5. Ask whether to start re-completion pipelines for the four repudiated OBPIs (OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02, OBPI-0.35.0-09); only the operator initiates them.

## Pending Work / Open Loops

Open: GHI #1154 (items 4 and 5 owed, plus the not-covered parts of item 3: mismatched source and test identity, and a designated per-REQ discriminator). GHI #1155 owes: claims for 7 hollow gates (#889 [settled], #996 [settled], #995 [settled], #888 [settled], #932 [settled], #933 [settled], #1124 [settled]), enumeration of the other gate populations (check steps that run a tool, precomplete checks, complete refusals, closeout steps), and correcting the two mis-derived gate_targets for module-size and tautological-debt. The 57 disclosed validate scopes include foundational ones (manifest, surfaces, taxonomy, commit_trailers); six have a runner that resolves no gzkit callable. The precomplete verdict check and the lite-lane early return of the verdict gate are unclaimed. Carried from the predecessor: the chore_decommission_processed emitter gap, whether to draw the next ADR-0.35.0 OBPI, and the unfiled patch-release diff_only listing. Trackers #611, #921, #978, #1028 and #799 remain open.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0; gh issue view 1154 1155: expect OPEN; gh issue view 1160: expect CLOSED; uv run gz validate --gate-enrollment: expect exit 0 with 101 scopes, 44 named, 57 disclosed; uv run -m unittest tests.test_unit_run_provenance tests.test_red_witness tests.governance.test_gate_enrollment tests.commands.test_obpi_complete_adversarial_claims tests.commands.test_adr_closeout_coverage_kind_aware: expect OK; uv run gz check: expect exit 0.

## Evidence / Artifacts

Fixes: `src/gzkit/unit_run_provenance.py`, `src/gzkit/quality.py`, `src/gzkit/red_witness.py`, `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/adr_audit.py`, `src/gzkit/governance/brief_reconcile.py`. Enrollment: `src/gzkit/governance/trust_audits/gate_enrollment.py`, `data/gate_enrollment_grandfather.json`, `src/gzkit/commands/obpi_complete_adversarial_claims.py`, `data/unit_collection_floor.json`. Tests: `tests/test_unit_run_provenance.py`, `tests/test_red_witness.py`, `tests/governance/test_gate_enrollment.py`, `tests/cli/test_validate_gate_enrollment_cli.py`, `tests/commands/test_obpi_complete_adversarial_claims.py`, `tests/commands/test_adr_closeout_coverage_kind_aware.py`. Predecessor: `.gzkit/handoffs/20261001T085000Z-repudiations-four-defects-fixed-s9-s10-ruled.md`.

## Settled Rulings

1257 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
