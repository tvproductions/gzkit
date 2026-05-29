# Plan — OBPI-0.0.63-01-step-advance-gate-5-enforcement

Parent ADR: ADR-0.0.63-closeout-ceremony-runtime-engine-parity (heavy, foundation)
Anchors: BI-3 (Gate-5 cannot be self-advanced); Decision item 1.

## Destination-in-mind (disclosure)

Before writing this plan I had already concluded — via two advisor passes against the
ADR/BI text and the code — that the fix is **B1-hybrid**: route both `--next` and
`--attest` through one shared ledger-gated advance helper, with `--attest` emitting the
`attested` receipt then crossing (pass-path) and `--next` at Step 6 fail-closing (fail-path).

## Rejected alternatives (disclosure)

- **Approach A (state-only block):** block `--next` at Step 6 by checking ceremony state, no
  ledger read. Rejected: produces no ledger-gated edge → fails BI-3, the very fence this OBPI anchors.
- **B2 (`--attest` emits but does not advance; `--next` advances):** true two-command edge.
  Rejected: makes `--attest` two operator commands where one sufficed (violates Operator Economy
  of Effort), and drags in `render_step_6`/SKILL.md/Gate-3 docs for no invariant gain.
- **New parallel ceremony event type:** rejected — BI-2 forbids `--attest` becoming a parallel
  emitter; reuse the existing `attested_event` surface.

## Context

`closeout_ceremony.py` emits zero ledger events today. Leaving Step 6 (ATTESTATION) has two
paths: `--attest` (records `state.attestation`, advances) and `--next` (blind step-counter
advance — the F1 bypass). The real `attested_event` fires only later in Step-7's `gz closeout`
(`closeout.py:504`), which already consumes the ceremony verdict (GHI #351).

## Files

- `src/gzkit/commands/closeout_ceremony.py` — add `attested_event` + `get_git_user` to imports
  (lines 34-47); add `_has_fresh_attestation_receipt(project_root, state) -> bool` and a shared
  `_advance_or_gate`/helper; route `_advance_ceremony` and `_record_attestation` through it.
- `tests/test_closeout_ceremony_cmd.py` — new `TestCeremonyGate5Enforcement` (`@covers` REQ-01/02/03);
  keep `test_advance_through_all_steps` green (it already crosses via `--attest`).

## Steps (RED → GREEN per increment)

1. **RED REQ-01:** test — walk to Step 6, call `--next`, assert exit 3 + state stays Step 6.
   Fails today (current `--next` advances to Step 7).
2. **RED REQ-03:** test — at Step 6, append a *stale* `attested` event (ts < run `started_at`),
   call `--next`, assert exit 3. Guards both the staleness hole and the string-compare bug.
3. **GREEN:** add `_has_fresh_attestation_receipt` (parse `started_at` + event `ts` with
   `datetime.fromisoformat`, compare as datetimes; True iff any `attested` event ts ≥ run start).
   Add a shared advance helper that fail-closes the ATTESTATION→CLOSEOUT edge when the receipt is
   absent; both `_advance_ceremony` and `_record_attestation` delegate to it (removes the
   458-476 duplication). `_record_attestation` emits `attested_event(adr_id, status, get_git_user(),
   reason)` (minimal inline verdict classify; cross-ref comment to closeout.py's
   `_parse_ceremony_attestation_text`) BEFORE delegating, so its crossing finds a fresh receipt.
4. **REQ-02 test:** at Step 6, `--attest "Completed"`, assert an `attested` ledger event exists
   AND state == CLOSEOUT.
5. Refactor for clarity; keep functions ≤50 lines.

## Verification

- `uv run -m unittest tests.test_closeout_ceremony_cmd`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run gz validate --documents`

## Notes

- Double-emit with `closeout.py:504` is the intended transitional state (Non-Goal; collapse = OBPI-05/BI-2).
- Scope stays inside `closeout_ceremony.py` + its test; no `events.py`/`closeout.py` edits.
