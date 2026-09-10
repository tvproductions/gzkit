# Stage 4a — OBPI-0.35.0-05-corpus-candidate-generator

Composed 2026-09-10 against input_digest `e7e57882b737c92c0956ee7e270ae2e44b6707aafce81335c7e6d057958e1bef`.
Prior rounds are retained in `OBPI-0.35.0-05-corpus-candidate-generator.stage4a-history.md`; they are tied
to their own reviewed state and are not expected to reproduce against today's tree.

## 1. Value Narrative

Before this OBPI, `compose()` took the candidate's text as a parameter and its own docstring conceded that
"the drop/combine/rewrite judgment is the agent's" — the tool validated bytes an LLM had already chosen, and
its `compressible_bytes_after = total_bytes - invariant_bytes` arithmetic reported a 63x INFLATION labelled as
compression, a witness that could not fail. There was no provenance artifact tying candidate bytes back to the
corpus entries that produced them.

Now the generator materializes owned sections from the EFFECTIVE corpus itself (no `candidate_text` on the
generated path), carries unowned sections forward byte-verbatim out of the prior rendition, emits a per-consumer
`<consumer>.lineage.json` mapping every section to `{owned, entry_ids, byte_span}` over a complete disjoint
partition, and accounts bytes by emission attribution with a fail-closed inflation refusal. POPULATION totals
(corpus entry text by tier) and RENDERED totals (measured per section during assembly) are separately labelled
and never blended.

## 2. Key Proof

The independent tier-1 adversary ran the generator against the real AGENTS.md corpus — un-mocked, reading the
live corpus, prior rendition and ownership declaration — and observed the feature doing its job:

```text
LIVE GENERATION ACCEPTED
{"invariant_bytes":24350,"compressible_bytes_before":354,"compressible_bytes_after":354,"emitted_entry_bytes":24704,"generated_structural_bytes":535,"carried_forward_bytes":6005,"total_bytes":31244,"setpoint":"lite"}
sections 22 owned 12 unowned_verbatim 10 emitted_ids 71 retired_ids_emitted 0
candidate_sha256 08fb1752b7945f373af0f30686ab4f9d53ed841ba273da6fa31277a99537bb49
two_runs_equal True partition_total 31244
```

The rendered partition reconciles exactly (24704 + 535 + 6005 = 31244 = `total_bytes`), zero retired entries were
emitted, and two runs were byte-identical. Recorded in receipt `arb-step-codexadversary-bfdaa9930e3840248b845b13ceaf926e`.

The same round exercised the refusal direction, so the guards are witnessed firing as well as staying silent:

```text
OVERLAP ACCEPTED {"invariant_bytes":79,...,"generated_structural_bytes":9,"carried_forward_bytes":55,"total_bytes":64,"setpoint":"lite"}
INFLATION REFUSED compressible_bytes_after (6) exceeds compressible_bytes_before (3).
OFF_ROUTE claude Surface 'AGENTS.md' (content type 'AgentContract') declares no route to consumer 'claude'; declared routes are ['root'].
```

The overlapping-invariant case is the ADV-OVERLAPPING-BYTE-ACCOUNTING regression (a 79-byte population against a
64-byte candidate): it is ACCEPTED rather than refused, which is the repair landed in `2c32d6de8`.

## 3. Evidence

**Quality checks:**

| Check | Command | Result |
|-------|---------|--------|
| Tests | `arb:unittest` (see below) | 10117/10117 pass (skipped=4) — receipt `arb-step-unittest-66a9f379412c430988897cadfd632961` |
| Lint | `arb:ruff` (see below) | clean — receipt `arb-ruff-98aaaecdab42457a85cdf860ec553f81` |
| Typecheck | `arb:typecheck` (see below) | clean — receipt `arb-step-typecheck-7c0f7eedea944469a79c50e3ef392d7d` |
| Docs (Heavy) | `arb:mkdocs` (see below) | strict build clean — receipt `arb-step-mkdocs-6cbdaa6724ec46c5a35a894a821160c8` |
| BDD (Heavy) | `arb:behave` (see below) | 5/5 scoped scenarios, 47 steps — receipt `arb-step-behave-4485a9c0d6774009b14eb024610449dc` |
| Step 4b adversary | `arb:codexadversary` (see below) | CORROBORATED-WITH-CAVEATS, tier 1 — receipt `arb-step-codexadversary-bfdaa9930e3840248b845b13ceaf926e` |

```bash
# arb:unittest — full unittest sweep
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer

# arb:ruff — lint
uv run gz arb ruff

# arb:typecheck — static type check
uv run gz arb typecheck

# arb:mkdocs — Heavy-lane docs build
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# arb:behave — Heavy-lane scoped BDD
uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.35.0-05-01,@REQ-0.35.0-05-02,@REQ-0.35.0-05-04,@REQ-0.35.0-05-05,@REQ-0.35.0-05-08 features/

# arb:codexadversary — Step 4b tier-1 cross-vendor adversarial review
uv run gz arb step --name codexadversary --max-output-chars -1 -- node .../codex-companion.mjs adversarial-review --wait --scope working-tree '<focus text>'
```

Governance validators, re-run here:

```text
$ uv run gz validate --req-kind-discipline
Validated: req_kind_discipline

✓ All validations passed (1 scopes).
```

```text
$ uv run gz validate --rendition-floor-coherence
Validated: rendition_floor_coherence

✓ All validations passed (1 scopes).
```

REQ→covers parity — the gate that binds is `behavior_uncovered_reqs`, and REQ-10 is the one
uncovered REQ because it is STRUCTURAL-FENCE and must never acquire a `@covers` test (ADR-0.0.59):

```text
$ uv run gz covers OBPI-0.35.0-05-corpus-candidate-generator --json
      "behavior_uncovered_reqs": 0,
```

**Files created/modified** — the implementation is already committed; the working tree carries no `src/`
or `tests/` diff at this packet's composition:

```text
$ git diff --numstat -- src tests; echo "exit $?"
exit 0
```

Implementation landed across `edb52f104` (generator, lineage map, ByteEvidence correction), `c4055edf0`
(lineage validated against actual boundaries; CommonMark fences), `53b6b0f6a` / `04f18f0e6` (contract-derived
oracles), `1cef5d802` (tautological assertion removed) and `2c32d6de8` (measured rendered partition —
the ADV-OVERLAPPING-BYTE-ACCOUNTING repair), touching `src/gzkit/content/composer.py`,
`src/gzkit/content/rendition.py`, `src/gzkit/content/lineage.py`, `src/gzkit/commands/content/compose.py`,
`docs/user/manpages/content.md`, and the four test modules.

**REQ coverage** — every row's Proof is the CURRENT proof id at input_digest `e7e5788…`, each an executed
kill-and-restore against live production source, all ten independently approved by the tier-1 adversary:

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|-----|------|-----------|----------------|-------|--------|
| REQ-0.35.0-05-01 | BEHAVIOR | owned body from effective corpus | `req-01:covers` | `proof-20cfad5cc9fb…` kill+restore | Pass |
| REQ-0.35.0-05-02 | BEHAVIOR | unowned carry-forward byte-verbatim | `req-02:covers` | `proof-d66ae3cdd5cb…` kill+restore | Pass |
| REQ-0.35.0-05-03 | BEHAVIOR | effective-corpus liveness fold | `req-03:covers` | `proof-863de2c94aa2…` kill+restore | Pass |
| REQ-0.35.0-05-04 | BEHAVIOR | lineage entry_ids + byte_span partition | `req-04:covers` | `proof-475a8dd6d3da…` kill+restore | Pass |
| REQ-0.35.0-05-05 | BEHAVIOR | per-consumer spans; off-route refusal | `req-05:covers` | `proof-2369b5596543…` kill+restore | Pass |
| REQ-0.35.0-05-06 | BEHAVIOR | emission attribution, not subtraction | `req-06:covers` | `proof-f216cde38c56…` kill+restore (3 mutations) | Pass |
| REQ-0.35.0-05-07 | BEHAVIOR | inflation refusal fails closed | `req-07:covers` | `proof-b473618a391b…` kill+restore | Pass |
| REQ-0.35.0-05-08 | BEHAVIOR | deterministic generation | `req-08:covers` | `proof-7ea0fb505dbc…` kill+restore | Pass |
| REQ-0.35.0-05-09 | BEHAVIOR | duplicate live invariant refused | `req-09:covers` | `proof-84d5214f1ea5…` kill+restore | Pass |
| REQ-0.35.0-05-10 | STRUCTURAL-FENCE | lineage never inside RenditionProvenance | parent-ADR `## Boundary Invariants` BI-03 | `proof-c38b859d9c6a…` fence resolver | Pass |

```text
# req-01:covers — tests.content.test_composer.TestOwnedSectionBodyFromCorpus.test_owned_section_body_is_derived_from_corpus_not_prior_text
#                 + TestEmptyOwnedSectionRetainsHeading.test_empty_owned_section_retains_its_heading
# req-02:covers — TestUnownedSectionByteVerbatim.test_unowned_section_bytes_are_byte_verbatim
#                 + TestOverlappingInvariantsInCarriedForwardAreAccepted.test_overlapping_invariant_texts_in_an_unowned_section_are_accepted
#                 + tests.commands.test_content_compose.TestContentComposeCmd.test_mixed_owned_unowned_candidate_matches_contract_derived_literals
# req-03:covers — TestRetiredEntryExcludedButVerbatimSpanUnaffected.test_retired_entry_contributes_nothing_while_verbatim_span_is_unaffected
# req-04:covers — TestLineageCoversEverySectionId.test_lineage_carries_owned_entry_ids_and_byte_span_for_every_section
#                 + TestContentComposeCmd.test_generated_candidate_persists_the_bytes_its_lineage_indexes
# req-05:covers — TestPerConsumerOffsetsAndRouteRefusal.test_two_routed_consumers_get_different_offsets_and_off_route_is_refused
# req-06:covers — TestGeneratedEmissionAttributionCountsOnlyEmittedEntries + TestRenderedByteContributionsAreMeasuredDuringAssembly
#                 + TestOverlappingInvariantsInCarriedForwardAreAccepted (2) + TestByteEvidenceAccounting + TestContentComposeCmd (6 selectors)
# req-07:covers — TestByteEvidenceAccounting.test_byte_evidence_raises_when_attributed_exceeds_before
# req-08:covers — TestDeterministicGeneration.test_two_runs_produce_byte_identical_candidate_and_lineage
# req-09:covers — TestDuplicateLiveInvariantRefusal.test_two_live_byte_identical_invariant_entries_are_refused
```

**Step 4b — independent tier-1 adversarial validation.** Verdict CORROBORATED-WITH-CAVEATS
(receipt `arb-step-codexadversary-bfdaa9930e3840248b845b13ceaf926e`, tier derived from the execution
transport as 1). The adversary re-derived the claim from the REQs and the repository, audited all eleven
production substitutions against live source (each found exactly once; live SHA-256 matched both recorded
original and restored hashes), read every failure and restore transcript, and independently closed all ten
outstanding findings — F3, F7, F10, F11, F12, F13, F14, Q1, Q2, F15 — with its own reasoning rather than
restating the supplied descriptions. It recorded zero findings. Acceptance readiness after import:

```text
$ uv run gz obpi acceptance OBPI-0.35.0-05-corpus-candidate-generator status --stage stage4 --json
  "ready": true,
```

## 4. Disclosed limitations — read these, do not read silence as clean

1. **The adversary could not replay the mutation sweeps.** `codex-companion.mjs` pins the adversarial-review
   path to a read-only sandbox, so the kill-and-restore controls (which must edit and restore a source file)
   could not be re-executed independently. The adversary audited the RECORDED evidence against live source
   instead — verifying each `find` string exists exactly once, that live SHA-256 matches the recorded original
   and restored hashes, and that each failure is a requirement-relevant `AssertionError` rather than an
   import error. Tracked at GHI #961. Its own stated Weakest point.
2. **Filesystem-backed persistence was not freshly observed by the adversary.** CLI persistence, staging
   cleanup and native Windows serialization could not run under the read-only barrier. 127 of the 205 tests in
   the four scoped modules errored there with one signature — `FileNotFoundError: No usable temporary directory
   found` — a sandbox coverage limit, not a suite defect. Those same modules pass in the unrestricted full
   sweep (10,117 tests, receipt `arb-step-unittest-66a9f379…`).
3. **One REQ-06 mutation label overstates its own replacement.** The label reads
   `restore-the-population-derived-structural-remainder` but the substitution merely zeros
   `emitted_entry_bytes`. The adversary credited the observed attribution kill, not the broader label. The
   repaired overlap behaviour is established by the fresh live overlap execution, not by that label.
4. **The RED falsifiability witness is not part of this packet's evidence.** On the `--from=verify` path it
   reconstructs a base predating both test and implementation, where an `error` class is inconclusive by the
   pipeline's own definition. The falsifiability evidence here rests on the `acceptance prove`
   kill-and-restore records, which are current-tree executions.
5. **The ledger event still does not carry the rendered partition.** `composition_candidate_emitted_event`
   carries only the original four byte fields, so the CLI prints `structural=` while the ledger does not.
   Extending it needs `src/gzkit/ledger_events.py`, outside this brief's allowlist. Tracked in
   `.gzkit/insights/agent-insights.jsonl`, scope `content-compose-ledger-event`.
6. **GHI #983 remains open and is not a defect of this deliverable.** Materializing from the live corpus
   yields 31,244 B against the 47,851 B committed rendition because 10 of 12 corpus-owned sections carry no
   covering corpus content. The operator ruled 2026-09-07 that this generator stays faithful to its brief and
   the finding routes to a GHI. This OBPI made that pre-existing declaration state measurable for the first time.
