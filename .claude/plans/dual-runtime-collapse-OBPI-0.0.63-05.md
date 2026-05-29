# Plan: OBPI-0.0.63-05 dual-runtime-collapse (BI-2)

## Context

Brief: `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-05-dual-runtime-collapse.md`
Parent ADR Decision item 6 + Boundary Invariant BI-2 (single-runtime-engine ledger parity).

A ceremony-driven closeout emits the `attested` ledger event **twice** for one
logical closeout: once by the ceremony at Step 6 (`closeout_ceremony.py:549`, the
BI-3 gate's fresh-receipt pass-path) and again by the Step-7 pipeline
(`closeout.py:504`), even though the pipeline already *consumed* the same operator
verdict via `_consume_ceremony_attestation`. The two events carry identical
`(status, reason, attester)` (mirror classifiers; both attesters `get_git_user()`),
so the second is pure redundancy.

Collapse direction is forced by BI-3 (attested-completed in OBPI-01): the ceremony's
emission is the BI-3 gate's expected receipt and cannot be removed. Therefore the
**pipeline** is the path that stops re-emitting — and only when it consumed a
ceremony attestation. The direct interactive path (no ceremony) keeps the pipeline
as sole emitter.

Design verified against code reads (closeout.py 192-231/474-559, closeout_ceremony.py
435-561, version_sync.py 200-207, ledger.py 589) and an advisor review pass.

## Files

- `src/gzkit/commands/closeout.py` — in `_complete_closeout_pipeline`, guard the
  `ledger.append(attested_event(...))` at line ~504 so it only fires when
  `consumed is None`. When `consumed is not None`, the ceremony's Step-6 emission
  is the single source; the pipeline keeps the consumed status/reason/text for the
  closeout form but does NOT append a duplicate ledger event.
- `tests/test_closeout_pipeline.py` — new `@covers`-decorated BI-2 parity tests.

## Steps

1. **Gate 1 (ADR):** Intent recorded in the authored brief (done).
2. **Gate 2 RED:** Author failing tests in `tests/test_closeout_pipeline.py`:
   - `REQ-0.0.63-05-01`: ceremony-driven closeout (ceremony attestation present /
     consumed) → exactly **one** `attested` event for the ADR after the pipeline runs.
   - `REQ-0.0.63-05-02`: the ordered `(event_type, status, attester)` tuple set the
     closeout appends is **equal** between the ceremony-driven path and the direct path.
   - `REQ-0.0.63-05-03`: direct closeout with no ceremony (`consumed is None`) → pipeline
     still appends exactly one `attested` event.
3. **Gate 2 GREEN:** Add the `consumed is None` guard around the `attested_event` append
   in `_complete_closeout_pipeline`. Keep the consumed `(attest_status, reason,
   ceremony_attestation_text)` flowing to the closeout form and version-sync read.
4. **Quality:** `uv run gz arb ruff`, `uv run gz arb typecheck`,
   `uv run gz arb step --name unittest -- uv run -m unittest tests.test_closeout_pipeline`.
5. **Parity gate:** `uv run gz covers OBPI-0.0.63-05-dual-runtime-collapse --json` →
   `uncovered_reqs == 0`.
6. **Gate 3 (docs):** `uv run mkdocs build --strict` (no doc surface change expected;
   confirm clean). REQ-04 is `[STRUCTURAL-FENCE]` → BI-2, audited at ADR closeout.
7. **Stage 4 ceremony → Stage 5 sync** per gz-obpi-pipeline.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.test_closeout_pipeline
uv run gz covers OBPI-0.0.63-05-dual-runtime-collapse --json
```

## Notes

- Denied: do NOT modify `closeout_ceremony.py:549` (BI-3 gate's emission / OBPI-01
  attested-completed) or the `attested_event` schema (`events.py`/`ledger.py`).
- Scope-collision advisory: `closeout.py` is touched by many historical OBPIs; the
  edit here is a single-guard suppression, not a structural change — advisory only.
- OBPI-0.0.63-05 references this plan; parent ADR-0.0.63.
