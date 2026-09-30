---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-30T03:17:36Z'
agent: claude-code
session_id: 62e1d102-4c74-4092-b850-1e307cc00196
continues_from: .gzkit/handoffs/20260930T005747Z-handoff-four-steps-droplet-live-1151-fixed.md
---

## Current State Summary

Continued after the four-steps handoff. The operator confirmed the droplet SSH key is set up (verified: key login to 209.97.149.89 returns myvps2), which retires that handoff's step 4. Fixed the gz arb red annotation false positive as a direct fix (73aaab093: commit_witness drops signature annotations no runtime reads). Reviewed arb red end to end, then filed GHI #1152 (commit mode left no receipt) and GHI #1153 (restructuring fixes read inconclusive). Fixed and closed #1152 (f8a2cb302): every commit-mode run writes an arb-red-commit receipt and a red_commit_receipt_emitted ledger event, and prints the receipt id. #1153 is open, waiting on an operator ruling. main is 0/0 with origin before this handoff's sync.

## Important Context

gz arb red has two modes. REQ mode (--req) writes arb-red-REQ receipts read by gz validate --red-parity. Commit mode (--commit) now writes arb-red-commit receipts (schema gzkit.arb.red_commit_receipt.v1) plus a red_commit_receipt_emitted ledger event. artifacts/ is gitignored, so every ARB receipt is local to the machine that ran it; the committed ledger row is the durable record. The commit witness grades a commit only against that commit's own test modules, so a fix and its test must land in one commit or the guard reads undriven. Survivors that are declaration-only (annotation-only imports, __all__, TYPE_CHECKING blocks) or guarded outside the commit (a gz validate scope, another test module) are expected and must be accounted for in the close, not waved through. The annotation filter in _behavior applies only under from __future__ import annotations and only to functions whose decorators are in _ANNOTATION_BLIND_DECORATORS; class-field annotations stay behavior.

## Decisions Made

- [operator-ruled] Take up the gz arb red annotation false-positive insight (verbatim: 'take up the gz arb red annotation false positive').
- [operator-ruled] File the no-receipt and inconclusive-rate findings as GHIs and fix the no-receipt one now (verbatim: 'yes').
- [agent-chose] Scoped the annotation filter to signature annotations under PEP 563 on functions with only annotation-blind decorators, because Pydantic reads class-field annotations and 153 of 524 src modules evaluate annotations eagerly.
- [agent-chose] Added red_commit_receipt_emitted as its own event type instead of reusing red_receipt_emitted, because the latter is REQ-keyed and read by --red-parity.
- [agent-chose] Squashed the #1152 fix and its printed-receipt-id test into one commit (f8a2cb302) before pushing, so the commit witness grades the fix with its own test.
- [agent-chose] Left #927 closed: both new findings were disclosed in its close under 'Not claimed', so they are new GHIs, not a reopen.

## Immediate Next Steps

1. Ask the operator to rule GHI #1153's mutation unit: revert dependent hunks together, mutate per statement, or neutralize a new helper's body instead of deleting it.
2. Ask the operator whether to draw the next ADR-0.35.0 OBPI; OBPI-0.35.0-10 also carries retention-scope REQs 08-10.
3. When OBPI-0.35.0-10 lands, add ADR-0.0.33's six anti-pattern rows to the scorecard as a direct fix under GHI #799.

## Pending Work / Open Loops

GHI #1153 open, awaiting the operator's mutation-unit ruling. GHI #799 open with an updated blocker comment. ADR-pool.handoff-resume-assessment awaits promotion when drawn. Commit mode does not mutate pure deletions (documented design, not tracked as a defect). Carried from earlier handoffs: #611 clause 4 and held item (a); #1149 and #1125 open; pool promotion-triage facility owed by ADR-pool.pool-management section 9; gz obpi precomplete has no manpage; GovZero docs cite AirlineOps-era ADR numbers.

## Verification Checklist

gh issue view 1152 (expect CLOSED); gh issue view 1153 (expect OPEN); uv run -m unittest tests.test_commit_witness tests.test_schemas (expect OK); uv run gz arb red --commit HEAD~1 (expect a printed receipt= id and a matching file under artifacts/receipts); grep -c red_commit_receipt_emitted .gzkit/ledger.jsonl (expect at least 2); uv run gz arb validate (expect exit 0); git rev-list --left-right --count origin/main...HEAD (expect 0 0); uv run gz check (expect exit 0).

## Evidence / Artifacts

Predecessor: `.gzkit/handoffs/20260930T005747Z-handoff-four-steps-droplet-live-1151-fixed.md`. Annotation fix: `src/gzkit/commit_witness.py`, `docs/user/manpages/arb-red.md`. GHI #1152: `src/gzkit/arb/red_reporter.py`, `src/gzkit/commands/arb.py`, `src/gzkit/arb/validator.py`, `data/schemas/arb_red_commit_receipt.schema.json`, `src/gzkit/events.py`, `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json`, `src/gzkit/governance/trust_audits/events.py`, `src/gzkit/ontology/corpus.py`, `.gzkit/skills/ghi-close/SKILL.md`, `tests/test_commit_witness.py`, `tests/test_schemas.py`.

## Settled Rulings

1221 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
