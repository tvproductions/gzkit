---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-22T08:25:25Z'
agent: claude-code
session_id: 8df533eb-eabc-4870-9395-bbcd72333795
continues_from: .gzkit/handoffs/20261022T005954Z-ro3-t1-landed-demotion-announced-certifi-lease-renewed.md
---

## Current State Summary

Resumed from the RO-3 tranche 1 handoff and worked the drydock in order. RO-3 tranches 2, 3 and 4 landed, which completes all four of RO-3's tranches; its witness reads true (gz validate --catalog exit 0, full unit tier 12510 OK, the scope in the default gz check with five negative controls), and closing RO-3 is left to the operator because the contract names no closing act. Tranche 2 (2fa677a76, d39752974, a43f0220e): outcome_transitioned and req_proof_recorded on all five registration surfaces with writers in gzkit.catalog_ledger and isolated producer probes. Tranche 3 (a627dbc2d, 021db4c62, 67227d524): the RO-2 resolver reads a catalog REQ-<n> from member_of, @covers and the tag scanner accept a held catalog REQ, data/catalog/externals.json, and the edge, coverage and BDD alignment checks. Tranche 4 (ed9ca3e74, b4f7c92b0): data/catalog/delivery_events.json and the advisory forward rule. Direct fixes found on the way: gz check announces a step the hangar demoted (d9771c382, 00ed4d541); the never-fired baseline drained beside probe-covered types (89a1f0e7a, ea9f5ba47); PRD section 8 reconciled with pyproject.toml (e79c48dde); 3239 absolute machine-path links in two docs made portable (8d5c1c7ce). The operator approved the three tranche 3 canaries (80c00112c). Last pushed commit 4ca5861ec; main level with origin.

## Important Context

Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md; most guards are advisory, and since d9771c382 gz check prints every demoted step's findings after the blocking results, so read that section rather than trusting a green tick. The per-change gz check selects only touched tests: run the full unit tier (uv run gz test) before push, as the RO-3 spec requires; it caught a registry-seam bypass the per-change gate missed this session. Every act is one commit with its Task: trailer, then gz arb red --commit on it; drive every survivor in a test commit and record equivalent mutants in the passage log. The catalog's coverage report reads 36 of 36 PRD needs uncovered and the forward rule announces nothing yet; both are advisory by ruling. Guard canaries are reviewed only through gz canary review with the operator's verbatim words. The lease and MX debt-aging warning stand as before (the orientation announces when the lease expires).

## Decisions Made

- [operator-ruled] Proceed on the handoff's RO-3 tranche 2 step (verbatim: "yes"), booked with gz handoff decide; the lease step set aside as not due.
- [operator-ruled] The outcome lifecycle grammar is Return-to-origin (selection: "Return-to-origin (Rec.)"): forward one step, blocked or deferred entered from queued through verified and left only to its origin, from_state read from the ledger, an attestor into validated.
- [operator-ruled] Fix the gz check silent demotion and the never-fired baseline as direct fixes (verbatim: "yes, fix both as direct fixes").
- [operator-ruled] The drain route fixes the writer (selection: "Fix the writer (Rec.)"): --write refuses only growth no verified isolated producer covers and writes the old baseline intersected with the current never-fired set.
- [operator-ruled] Tranche 3 began on "do next step" with four selections: "Leave to RO-5 (Rec.)" for the freeze lock, "Derive from heading (Rec.)" for NFR-<slug> ids, "Declared prefixes (Rec.)" for depends_on, "Widen both bindings (Rec.)" for @covers and the tag scanner.
- [operator-ruled] Address the PRD section 8 defect and the canary reviews (verbatim: "address these"); each of the three tranche 3 canaries approved (verbatim: "Approve").
- [operator-ruled] Fix the docs link, then take the next step (verbatim: "fix the docs link, then do next step"); tranche 4 by selection: "All nine (Rec.)", "Grammar over fields (Rec.)", "Timestamp in registry (Rec.)".
- [agent-chose] The legacy @covers and feature scanners pass a catalog REQ-<n> over silently and a separate scan_catalog_bindings reads it, so no reader of legacy REQ records changed.
- [agent-chose] One negative control per check family (edges, coverage, bdd, forward-rule), each planting every case of its family, rather than one claim per check.
- [agent-chose] RO-3 is recorded as witness read true with closure on the operator's word, not marked closed.
- [agent-chose] Absolute paths inside sealed records (terminal briefs, captured proof output, the three commands the eval audit recorded verbatim) were left as recorded; only links were rewritten.

## Immediate Next Steps

1. Ask the operator whether RO-3 is closed: all four tranches landed and its witness reads true; the contract names no closing act.
2. Present the requirements-catalog-forward-rule guard canary for operator review (mutant: names_req_or_outcome returns True; killed by TestReading.test_an_unnamed_listed_event_after_the_cutover_is_counted) and book the verdict with gz canary review.
3. Then GHI #1259 (gz interview obpi render fails on 13 unsupplied template variables).
4. Then RO-9 tranches 3 to 7 from docs/governance/harbor-ro9-astral-toolchain.md, in order.
5. When the operator chooses: GHI #1264 (the API reference; which modules count is the operator's call), GHI #1262 (debt reading), GHI #1263 (parked); renew the lease when the orientation announces it expired, on the operator's word.

## Pending Work / Open Loops

- The forward-rule canary awaits operator review; the other four catalog canaries are reviewed.
- RO-3 closure awaits the operator's word; RO-5 now owns the freeze lock and its baseline event (ruling 6).
- The forward rule and coverage report stay advisory until RO-5's verbs can supply outcome ids (rulings 4 and 10 to 12).
- Machine-local absolute paths remain inside sealed records under docs/design/adr (proof captures and terminal briefs); left as recorded, not links.
- .gzkit/ledger.jsonl carries one uncommitted line from the last commit; fold it into the next commit.

## Verification Checklist

- uv run gz handoff resume
- git rev-list --left-right --count origin/main...HEAD (expect 0 0 before new work)
- uv run gz validate --catalog (exit 0; the coverage advisory reads 36 of 36)
- uv run gz check (exit 0; read the Demoted section if one prints)
- uv run gz test (full unit tier; 12510 OK at 4ca5861ec)
- uv run python -c "from pathlib import Path; from gzkit.guard_canary import unreviewed; print(unreviewed(Path('.')))" (expect requirements-catalog-forward-rule until reviewed)

## Evidence / Artifacts

- `docs/governance/harbor-ro3-requirements-store.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `src/gzkit/catalog_ledger.py`
- `src/gzkit/governance/trust_audits/catalog_edges.py`
- `src/gzkit/governance/trust_audits/catalog_forward.py`
- `src/gzkit/core/id_resolver.py`
- `src/gzkit/traceability.py`
- `data/catalog/externals.json`
- `data/catalog/delivery_events.json`
- `data/guard_canaries.json`
- `data/ledger_vocabulary_grandfather.json`
- `docs/user/manpages/check.md`
- `docs/user/manpages/validate.md`
- `docs/design/prd/PRD-GZKIT-1.0.0.md`

## Settled Rulings

1653 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
