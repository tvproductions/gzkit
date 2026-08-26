# Plan — OBPI-0.35.0-03-retire-duplicate-invariant-entries

**Parent ADR:** ADR-0.35.0-canon-entry-corpus-landing (heavy, feature)
**Brief:** docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md

## Context

All eight retirements this brief owns have LANDED. Measured 2026-08-26 against
`.gzkit/corpus/AGENTS.md.jsonl` (79 raw rows, 54 live invariant): all sixteen
enumerated ids resolve exactly as REQUIREMENTS 3-10 specify — eight retired
(present in raw, absent from live), eight retained live, ZERO byte-identical
live invariant texts. REQUIREMENT 2's set-comparison passes with no BLOCKERS.

What has NOT landed is the ledger witness. Two acceptance criteria assert
ledger events that do not exist:

- REQ-01 body requires a `corpus_entry_retired` event per enumerated id.
  Measured 1/8 — only the divergent pair (2026-07-22, GHI #635). The seven
  GHI #862 groups were retired by hand-appending tombstone rows in commit
  `8ed48271`, which touched `.gzkit/ledger.jsonl` not at all.
- REQ-01 AND REQ-03 both close with "Witnessed by eight `corpus_entry_appended`
  ledger events". Measured 0/8 — no retraction row has ever carried an append
  event, including the one the verb produced on 2026-07-22 (that run predates
  the dual emission, which landed in OBPI-0.35.0-02; current `retire.py:404-426`
  emits both).

Neither is reachable by any in-scope action: `gz content retire` fails closed on
an already-retired id, and backfilling events today would stamp a current
timestamp on a procedure that never ran — a fabricated receipt under
AGENTS.md § Attestation.

Operator ruling 2026-08-26, verbatim: "Amend REQ-01 to cite the corpus
tombstones as its proof channel and record the ledger gap against #885. -03 then
completes on what's provable. Cost: a SUPPORT REQ loses the ledger as its proof
channel." Extended to REQ-03 under the same rationale — the identical false
clause sits in both, and re-eliciting a settled ruling is the drift vector
AGENTS.md § Operator Doctrine #7 forbids.

This OBPI writes NO code. Its Denied Paths exclude `src/**` and `tests/**`; the
mechanism shipped in OBPI-0.35.0-01 and -02.

## Files

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md` (allowlisted) — the only file this plan touches.
- `.gzkit/corpus/AGENTS.md.jsonl` (allowlisted) — NO change required; all eight retirements already landed. Listed to record that it was considered and deliberately untouched.

## Steps

1. **Amend REQ-0.35.0-03-01** — replace the `corpus_entry_retired`-per-id
   predicate and the `corpus_entry_appended` witness clause with the corpus
   tombstone as proof channel (each enumerated id named by a live retraction row
   whose `retires` field cites it, verifiable per id against the store), keeping
   `gz validate --rendition-floor-coherence` as the structural validator arm so
   the REQ remains a well-formed SUPPORT REQ under ADR-0.0.59. Record the
   measured ledger gap (1/8 retired, 0/8 appended) and cite GHI #885. Record the
   operator ruling verbatim with its date.
2. **Amend REQ-0.35.0-03-03** — same treatment for its `corpus_entry_appended`
   witness clause; its append-only predicate (all eight originals present
   verbatim, named by a retraction row) is TRUE as measured and is retained
   unchanged.
3. **Correct the AMENDED 2026-08-22 block's false row** — it records
   `corpus_entry_retired` events for this brief's groups as "8 total, across
   three sessions". Measured 1. Correct in place with the measurement and its
   date, per .claude/rules/governance-core.md (a value in prose is a dated
   record, never authority).
4. **Add an AMENDED 2026-08-26 block** — records the ledger-witness finding, the
   operator ruling, its extension to REQ-03, and GHI #885 as the open route.
   This discharges REQ-02's subject for the third ruling.
5. **Discharge REQUIREMENT 2** — record the 2026-08-26 re-measurement (16/16 ids
   resolve; sets do not differ; no BLOCKERS) in the brief's Evidence.
6. **Add GHI #885 to § Tracked Defects.**
7. **Fill the brief's Evidence sections** — Gate 1, Gate 2 (no tests: this OBPI
   writes no code and `tests/**` is a Denied Path), Code Quality, Gate 3, Gate 4,
   Gate 5, Value Narrative, Key Proof, Implementation Summary.
8. **Present OBPI Acceptance Ceremony** (universal human gate, ADR-0.0.36).

## Verification

```bash
uv run gz validate --rendition-floor-coherence
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz test
```

Plus the brief's § Demo liveness/duplicate-count probes, re-run as Key Proof.

## Notes

### Step 6a — Plan-Before-Exploration Ordering (disclosure)

**Destination-in-mind.** Before writing this plan I had already formed the
conclusion that `-03` has no code work left and that the only obstacle is a REQ
asserting an unreachable ledger state. That conclusion came from a Stage-1
measurement pass in a prior turn, which halted the pipeline with BLOCKERS and
produced a FAIL plan-audit receipt. So this plan IS written to a destination
already chosen — the honest disclosure is that the exploration preceded it, and
the operator ruled between the two.

**Rejected alternatives.**
1. *Backfill the seven `corpus_entry_retired` events now.* Rejected: they would
   carry a 2026-08-26 timestamp and an attestor, retroactively witnessing a
   procedure that never ran — the fabricated-receipt failure in
   AGENTS.md § Attestation.
2. *Re-run `gz content retire` for the seven.* Rejected as impossible: the verb
   fails closed on an already-retired id (`retire.py` refuses unknown or
   already-retired ids, nothing written).
3. *Delete the hand-written tombstones and redo them through the verb.* Rejected:
   the corpus is append-only; deletion is alternative E the parent ADR rejects,
   and REQUIREMENT 15 forbids it outright.
4. *Hold `-03` until GHI #885 arm 2 settles a repair-event shape.* Viable and
   presented to the operator; they chose the amendment route so `-03` completes
   on what is provable while #885 keeps the ledger gap alive as its own work.
5. *Amend REQ-01 only, leaving REQ-03's identical false clause standing.*
   Rejected: it would leave a known-false witness clause in an attested brief,
   which is the defect this pass exists to remove.
