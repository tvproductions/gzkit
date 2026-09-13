---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-13T03:34:49Z'
agent: claude-code
session_id: 89fe194c-e710-4a42-a2c2-c4dd7c0bbc7d
continues_from: .gzkit/handoffs/20260913T024806Z-chore-class-schema-and-found-defects.md
---

## Current State Summary

Continuation of session 89fe194c after `20260913T024806Z-chore-class-schema-and-found-defects.md`. The operator ruled on the two open GHIs and both were repaired and closed. GHI #1001 (exit code 2): after the first framing omitted attested REQ-0.0.4-02-03, the question was re-put and the operator ruled to keep 2 and fix the labels; commit `fa45e2504` relabels code 2 as Usage or System/IO in cli.md 0.7.0, the shared help epilog, the exception map and the CLI spec, scores scorecard rows 91 and 92, and registers the negative control NC:cli-usage-error-exit-two with a public `extend_known_claims` so no private cross-package import was needed. GHI #1000 (rulings lag): the operator ruled booking at authoring; commit `2909096e8` books a handoff's own operator rulings when it is written, and `6d7aeca62` adds the linked-handoff test that a mutation sweep showed was missing. gz check passed with real exit 0 before each commit set; heavy-lane ARB receipts were emitted and cited in both close comments.

## Important Context

- The background-task notification reported exit 0 on two gz check runs whose real exit was 1; the verifier's own exit (captured with echo REAL EXIT) is the only trustworthy signal, per `.gzkit/rules/tests.md` and GHI #969.
- A Mechanical scorecard row now requires a registered property-level negative control cited as NC:<claim-id>; a unit test alone is not accepted by `gz validate --advisory-scorecard`, and the row's rule text must appear verbatim in the per-turn surface (`gz validate --surface-fidelity`).
- The private-import ratchet (`tests` test_no_new_private_cross_package_import) is shrink-only; claim sources should use `gzkit.enforcement.extend_known_claims` rather than importing `_KNOWN_QC_CLAIM_IDS`.
- This handoff is the first written with booking at authoring live, so its own operator rulings reach `.gzkit/handoffs/rulings.jsonl` immediately.

## Decisions Made

- [operator-ruled] GHI #1001 re-put with REQ-0.0.4-02-03 disclosed: "Keep 2; fix the labels (Recommended)" — parse errors keep exiting 2; code 2 is labelled Usage or System/IO; the earlier "Usage error → 1" selection is withdrawn as made on an incomplete framing.
- [operator-ruled] GHI #1000: "Book at authoring (Recommended)" — gz handoff create books the document's own operator rulings when it writes the handoff, accepting that a later linked handoff in another lineage inherits them.
- [operator-ruled] Session correction, verbatim "this seems very sloppy": defects found in flight are fixed or routed to a work order in-session, never listed back to the operator as notes.
- [agent-chose] Built a registered negative control for scorecard row 91 rather than scoring it Promotable, because the campaign's Movement C box drives Promotable rows to zero and the row carried observed drift evidence.

## Immediate Next Steps

1. GHI #999 step 3: class-conformance validator — a CHORE.md whose workflow contradicts its declared rung fails — sharing the criteria/version authority GHI #1002 settles.
2. GHI #1002: reconcile CHORE.md acceptance tables and versions with acceptance.json and registry.json under one declared authority, with a witness.
3. GHI #936: `gz chores status` rendering current / due / overdue / paused from the staleness declaration, announced in `scripts/session_orientation.py`.

## Pending Work / Open Loops

- GHI #999 steps 4-6 (README class and rung semantics, per-chore declarations with the absence-to-refusal flip, suppression rule with witness).
- Resumed-handoff step 3 (rule-chore Pass D alignment) and step 4 (R&D skill design, fresh session) remain unworked.
- GHI #936 and GHI #1002 open.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz handoff rulings --search "Keep 2"
gh issue view 1000 --json state
gh issue view 1001 --json state
uv run -m unittest tests.cli.test_exit_code_claims tests.governance.test_handoff_ruling_store
```

Expected: 0 0 after sync; the Keep 2 search returns this handoff's ruling (booked at authoring); #1000 and #1001 CLOSED; tests green.

## Evidence / Artifacts

- `src/gzkit/cli/helpers/exit_code_claims.py` — NC:cli-usage-error-exit-two.
- `tests/cli/test_exit_code_claims.py` — control PASS and FACADE-under-mutation tests.
- `src/gzkit/handoff_api.py` — own rulings booked at authoring.
- `tests/governance/test_handoff_ruling_store.py` — OwnRulingsBookedAtAuthoringTests.
- `docs/governance/advisory-rules-audit.md` — rows 91 and 92, cli.md ledger at 0.7.0.
- `.gzkit/rules/cli.md` — rule 0.7.0.
- Commits `fa45e2504`, `2909096e8`, `6d7aeca62`; ARB receipts `arb-ruff-4ad63df49a1443caaeef2bd1b41f0c14`, `arb-step-typecheck-80e979e5eb7b4a6a8ead42f1ce06a44c`, `arb-step-unittest-0967bf57f9d745e7b378da2b53d0e2d8`.

## Settled Rulings

827 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
