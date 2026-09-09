# Stage 4a — OBPI-0.35.0-05-corpus-candidate-generator

> **Current round: 2026-09-09.** Everything above the "Prior rounds (preserved)" divider is the
> CURRENT acceptance argument, bound to input digest `5338bac8637d754d02f84a48836ae1fbfff66aa7659fe24e57531ac792e28d6e`.
> Earlier rounds are preserved verbatim below as history, tied to their own reviewed state.

## 1. Value Narrative

Before this OBPI the corpus could not materialize a candidate: owned sections were not generated
from the effective corpus, unowned sections had no byte-verbatim carry-forward guarantee, no
per-consumer lineage recorded which was which, and `ByteEvidence` computed
`compressible_bytes_after = total_bytes - invariant_bytes` — a formula whose output tracks corpus
size, not compression, and a witness that could not fail.

Now the generator derives owned bytes from the effective corpus, carries unowned sections forward
byte-verbatim, persists a `<consumer>.lineage.json` covering every section, and reports byte
accounting that reconciles: invariant + compressible_after + structural_carried == total.

## 2. Key Proof

The accounting reconciles on the real corpus — the 6,540 bytes that were previously unaccounted
are now reported as structural/carried rather than silently absorbed:

```console
$ uv run python -c "from pathlib import Path; from gzkit.content.composer import generate_candidate; r=generate_candidate(Path('.'),'AGENTS.md','root'); e=r.rendition.byte_evidence if hasattr(r,'rendition') else r.byte_evidence; print(e.invariant_bytes, e.compressible_bytes_after, e.structural_carried_bytes, e.total_bytes); print(e.invariant_bytes+e.compressible_bytes_after+e.structural_carried_bytes == e.total_bytes)"
24350 354 6540 31244
True
```

Cited proof record: `proof-47b118cc9c03419eadfe1077ae7a2207` (REQ-06) and
`proof-b2a0ae3dbc2045f0b9be16b7d217dd5a` (REQ-07), each an executed kill-and-restore control.

## 3. Evidence

**Quality checks:**

| Check | Command | Result |
|-------|---------|--------|
| Tests | `arb:unittest` (below) | 10090 pass, 4 skipped — receipt `arb-step-unittest-8ae95c3264894fc98bfcbc7366fac921` |
| Lint | `arb:ruff` (below) | clean — receipt `arb-ruff-c68a7f05840c4e73962ed52431e04b76` |
| Typecheck | `arb:typecheck` (below) | clean — receipt `arb-step-typecheck-932f0d3fd4c249b2a6de6f1db120ad70` |
| Docs | `arb:mkdocs` (below) | clean — receipt `arb-step-mkdocs-33ada1532fb94d30ac900df6ca3b9373` |
| BDD | `arb:behave` (below) | 11 scenarios pass — receipt `arb-step-behave-9c2f1c698642434aa3fa8eb62e90e24e` |

```bash
# arb:unittest
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
# arb:ruff
uv run gz arb ruff
# arb:typecheck
uv run gz arb typecheck
# arb:mkdocs
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# arb:behave
uv run gz arb step --name behave -- uv run -m behave features/content_compose.feature
```

**Files modified this round:**
- `src/gzkit/content/rendition.py` (`structural_carried_bytes` field on `ByteEvidence`)
- `src/gzkit/content/composer.py` (remainder computation + `_refuse_negative_structural_remainder`)
- `src/gzkit/commands/content/compose.py` (surfaces `structural=` on the byte-evidence line)
- `tests/content/test_composer.py` (reconciliation + guard tests; F15/Q1 and Q2 oracle repairs)
- `tests/commands/test_content_compose.py` (CLI surfacing test)
- OBPI brief (F3: stale illustrative figure repaired to a dated record at both sites)

**REQ coverage:**

| REQ | Kind | Proof location | Proof | Result |
|-----|------|----------------|-------|--------|
| REQ-0.35.0-05-01 | BEHAVIOR | `TestOwnedSectionBodyFromCorpus.test_owned_section_body_is_derived_from_corpus_not_prior_text` | `proof-07f03909431042da…` kill+restore | Pass |
| REQ-0.35.0-05-02 | BEHAVIOR | `TestUnownedSectionByteVerbatim.test_unowned_section_bytes_are_byte_verbatim` | `proof-457ddddb3e784740…` kill+restore | Pass |
| REQ-0.35.0-05-03 | BEHAVIOR | `TestRetiredEntryExcludedButVerbatimSpanUnaffected.test_retired_entry_contributes_nothing_while_verbatim_span_is_unaffected` | `proof-3f5f06cfe01a4fbf…` kill+restore | Pass |
| REQ-0.35.0-05-04 | BEHAVIOR | `TestLineageCoversEverySectionId.test_lineage_carries_owned_entry_ids_and_byte_span_for_every_section` | `proof-3cbe8de31f684e14…` kill+restore | Pass |
| REQ-0.35.0-05-05 | BEHAVIOR | `TestPerConsumerOffsetsAndRouteRefusal.test_two_routed_consumers_get_different_offsets_and_off_route_is_refused` | `proof-cc5ba575d3a8459b…` kill+restore | Pass |
| REQ-0.35.0-05-06 | BEHAVIOR | `TestGeneratedEmissionAttributionCountsOnlyEmittedEntries.test_a_compressible_entry_in_an_unowned_section_is_never_attributed` | `proof-47b118cc9c03419e…` kill+restore | Pass |
| REQ-0.35.0-05-07 | BEHAVIOR | `TestByteEvidenceAccounting.test_byte_evidence_raises_when_attributed_exceeds_before` | `proof-b2a0ae3dbc2045f0…` kill+restore | Pass |
| REQ-0.35.0-05-08 | BEHAVIOR | `TestDeterministicGeneration.test_two_runs_produce_byte_identical_candidate_and_lineage` | `proof-f33e26fc5d2b4c12…` kill+restore | Pass |
| REQ-0.35.0-05-09 | BEHAVIOR | `TestDuplicateLiveInvariantRefusal.test_two_live_byte_identical_invariant_entries_are_refused` | `proof-2a277025381a4f17…` kill+restore | Pass |
| REQ-0.35.0-05-10 | STRUCTURAL-FENCE | `parent-ADR `## Boundary Invariants`` | `proof-f0269472156d4c41…` fence resolver | Pass |
## 4. Disclosed limitations — read these, do not read silence as clean

1. **The RED falsifiability witness did not run conclusively.** All nine BEHAVIOR REQs returned
   `failure_class=error` against a RECONSTRUCTED base, which the pipeline defines as INCONCLUSIVE —
   not a RED, and not an accusation about the tests. Zero REQs returned `none`, so no hollow test
   was detected. The falsifiability evidence in this packet rests on the `acceptance prove`
   kill-and-restore records, not on the historical RED witness.
2. **REQ-10 has no `@covers` test and must not acquire one.** It is STRUCTURAL-FENCE; its proof
   channel is the parent ADR's `## Boundary Invariants`, audited at closeout (ADR-0.0.59).
   `gz covers` reports `behavior_uncovered_reqs: 0`, which is the gate that binds.
3. **The ledger event does not yet reconcile.** `composition_candidate_emitted_event` still carries
   only the original four byte fields, so the CLI line reports `structural=` while the ledger does
   not. Extending it needs `src/gzkit/ledger_events.py`, outside this brief's allowlist. Tracked in
   `.gzkit/insights/agent-insights.jsonl` scope `content-compose-ledger-event`.
4. **`composer.py` is 637 lines** against pythonic.md's <=600 authoring guidance (unenforced; the
   gated limit is class size). Raised by the quality reviewer as an unmapped, non-blocking
   observation.
5. **Finding F11 was misfiled.** It was recorded against REQ-01 but the repair it describes lives in
   a test covering REQ-04. The spec reviewer verified REQ-01's current selectors are free of the
   defect F11 named and closed it on that basis. Tracked in insights, scope
   `obpi-acceptance-finding-scope`.

## Prior rounds (preserved)

Earlier rounds are retained verbatim in `.gzkit/evidence/OBPI-0.35.0-05-corpus-candidate-generator.stage4a-history.md`, tied to their own reviewed state.
They are history, not present-tense evidence, and their transcripts are not expected to reproduce
against today's tree — which is why they live outside this packet rather than inside its replay scope.
