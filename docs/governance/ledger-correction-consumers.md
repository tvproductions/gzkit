# Ledger correction consumers — which question each reader asks

> **Status:** inventory + classification, GHI #611. Authored 2026-09-06 after the
> review of `47214176` found that flipping `Ledger.read_all()` to the corrected
> stream moved *every* consumer to the **state** reading, including consumers
> asking an **evidence** question.

`gzkit.ledger_corrections` derives two readings from the same append-only file,
and they answer different questions. Choosing between them is a per-consumer
judgment; the mistake this document exists to prevent is making it *by default*.

| Reading | Drops | Answers |
|---|---|---|
| `live_events` — `Ledger.read_all()`, `Ledger.query()` | `void` + `discharged` | **State** — what is in force *now* |
| `evidence_events` — `Ledger.read_evidence()`, `query(stream="evidence")` | `void` only | **Evidence** — what was ever *true* |
| *(none)* — `Ledger.read_history()`, `query(stream="history")` | nothing | **History** — every row is the subject |

`void` says a row records something that was **never the case**. `discharged`
says it was **true when written** and its condition later ended. A consumer that
cannot tell those apart forces one to be filed as the other — the collapse
GHI #823 names.

`gzkit.ledger.read_corrected_rows` is the **tolerant** counterpart for readers
that must not raise (pipeline gates, commit hooks): it parses the JSONL itself,
skips an undecodable line, and applies the same two readings.

## The default is deliberately the narrowest

`read_all()` nets by default and that is correct: netting per call site is the
per-consumer hand-patching GHI #611 exists to end, and it fails **open** — a
consumer written next year is correction-blind unless its author remembers.
Defaulting to `live` makes forgetting safe.

But `live` is the *narrowest* reading, so the flip could only ever mis-serve
consumers in one direction: an evidence consumer silently loses discharged rows.
That is exactly what happened, and it is why `evidence` and `history` are named
opt-ins on the same call rather than separate methods a reader must know exist.

## Classification

### Evidence consumers — corrected on the `evidence` stream

| Consumer | Question it asks | Why `live` was wrong |
|---|---|---|
| `handoff_archive._locked_paths` | *Did any token surrender ever cite this file?* | A discharged `obpi_lock_released` vanished, so the exchange record a **real** surrender cited became archivable. Fixed: `query(..., stream="evidence")`. |
| `governance.trust_audits.lock_exchange_coupling` | *Does this past release own a valid exchange record?* | Same event, same question, one call site away. A discharged release still happened and still owes its coupling. Fixed: `read_evidence()`. |
| `pipeline_runtime.check_reconcile_receipt_gate` | *Was this brief reconciled, and when?* | Never reached the flip at all (raw JSONL reader) — a **voided** receipt still opened Stage 2. Fixed: `read_corrected_rows(..., stream="evidence")`. |
| `commands.obpi_complete._latest_reconcile_receipt` | Same, at Stage 5. | Same defect, same cause; a voided receipt still satisfied completion. Fixed identically, so the two ends of the pipeline agree about which receipts exist. |

### State consumers — correct on the default

Everything reaching the ledger through `Ledger.read_all()` / `query()` and
asking *what is in force now*: `gz state`'s artifact graph, gate readiness,
lifecycle status, OBPI park/block state, TASK liveness
(`tasks.active_task_trailers`, which applies `live_events` explicitly because it
runs in a commit hook where an exception blocks all work). These are served by
the default and need no change.

### History consumers — `read_history()`

`commands.ledger_correct` (both the corrections census and subject resolution)
and replay-fidelity audits. Their subject genuinely is every row, corrections
included; netting would hide the thing they exist to read.

## Unresolved semantic choice — surfaced, not decided

**What `discharged` means on a `brief_reconciled` receipt is not settled, and
the repair takes the conservative reading rather than ruling on it.**

The vocabulary was designed for rows recording a *condition* (a block, a lock, a
launch). A receipt is not a condition — it records that a run happened at a
time. `void` is unambiguous there (the run never happened). `discharged` has no
established meaning: read literally it says "the reconciliation was true and
stopped being true", which sounds like *stale*.

**Implemented: the `evidence` reading** — a discharged receipt still counts.
**Recommended: leave it there**, for three reasons.

1. It is strictly the more conservative choice. It removes only what the ledger
   says never happened, and never silently weakens a gate.
2. Reconciliation staleness already has a dedicated mechanism —
   `is_receipt_fresh` against the allowlist domain's mtimes. Letting `discharged`
   also mean "stale" would build a second, weaker staleness channel beside it,
   and the two would disagree.
3. If the operator later rules that discharging a receipt *should* force
   re-reconciliation, that is a **widening** of the gate. Widening a gate later
   is safe; discovering that a gate was silently narrowed is not.

An operator ruling on this would be recorded here and in
`gzkit.ledger.read_corrected_rows`.

## What the repair preserves

* **Raw history is untouched.** Corrections are append-only forward rows; every
  subject row and every correction stays on disk, and `read_history()` returns
  all of them.
* **Legitimate intervening work survives a correction.** The reconciliation
  readers take the *newest* matching receipt, so voiding the latest one falls
  back to the real receipt beneath it rather than reporting "no receipt" — a
  correction must never cause a larger outage than the error it repairs.
  Asserted by
  `tests/test_ledger_correction_consumers.py::VoidedReconcileReceiptsStopCountingAsReceipts::test_an_earlier_receipt_resurfaces_when_the_later_one_is_voided`.

## Which corrections apply at all — one contract, both paths

Choosing a reading is the *second* question. The first is whether a correction
counts, and every reader answers it identically because they share one
predicate: `is_well_formed` plus the append-order rule in `correction_state`
(`gzkit.ledger_corrections`), which `gz validate --ledger` imports rather than
restates. A correction applies only when **all** of the following hold.

| Requirement | Refused when | Checked by |
|---|---|---|
| **Envelope** — this ledger's `schema` tag, a non-empty `id`, a parseable ISO8601 `ts` | a foreign tag, a blank id, `ts: "not-a-date"` | `_has_valid_envelope` |
| **Payload** — seven `str` fields; `disposition` and `cause` in their closed vocabularies | a wrong type, whitespace-only content, an unknown term | `is_well_formed` |
| **Subject resolution** — the named `(event, id, ts)` triple exists | nothing carries that identity | `gz validate --ledger` (it holds the whole file) |
| **Append order** — the subject appears *earlier in the sequence* | the correction stands ahead of the row it names | `correction_state`, and the validator by line number |

Two of these used to live only in the validator, so a correction it **reported**
still voided its subject at replay — the operator saw the gate fire and the row
was corrected anyway. That split is the defect; sharing the predicate is the fix.

**Order is position, never the timestamp.** The file *is* the append order. Two
rows may legitimately share a `ts` — the committed ledger already holds such a
pair — so a rule comparing timestamps reads an inversion between same-instant
rows as fine, and says nothing at all when either `ts` fails to parse.

**A malformed row is a finding, never an exception.** Values of the wrong
*container* type are ordinary malformed input: `cause: []` cannot be tested
against a frozenset and `id: []` cannot be hashed into a subject index. Both
raised `TypeError` and took down the reader that existed to report them —
including the tolerant reader, whose whole contract is that a pipeline gate or
commit hook must not raise. `identity_key` returns `None` for a row that has no
identity under the ledger's rule, and such a row is *uncorrectable* rather than
corrected: no well-formed correction can name it.

Subject resolution is the one requirement replay does **not** enforce, and
deliberately: a caller holding only a window of the ledger would otherwise drop
a correction whose subject sits outside it. Requiring the subject to have been
*seen* covers the harmful half without needing global knowledge — a correction
whose subject is outside the window nets nothing anyway, because nothing in the
window carries its key.

## Known limit

This inventory is a **reading**, not a mechanically enforced partition. Nothing
stops a new consumer from taking the default when it wanted evidence — the
default is chosen to make that mistake the safe one, not to make it impossible.
The behavior of the four consumers above is pinned by
`tests/test_ledger_correction_consumers.py`; the classification of a *fifth* is
not. Reclassify on an observed instance of a new consumer taking the wrong
stream.
