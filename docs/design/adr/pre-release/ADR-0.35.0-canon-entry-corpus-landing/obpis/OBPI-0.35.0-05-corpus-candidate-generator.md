---
id: OBPI-0.35.0-05-corpus-candidate-generator
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 5
lane: Heavy
status: Active
allowlist:
- src/gzkit/content/composer.py
- src/gzkit/content/rendition.py
- src/gzkit/content/lineage.py
- src/gzkit/content/ownership.py
- src/gzkit/content/corpus_store.py
- tests/content/test_ownership.py
- src/gzkit/commands/content/__init__.py
- src/gzkit/commands/content/compose.py
- tests/content/test_composer.py
- tests/content/test_lineage.py
- tests/commands/test_content_compose.py
- features/content_compose.feature
- features/steps/content_compose_steps.py
- docs/user/manpages/content.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-05-corpus-candidate-generator.md
reqs:
- REQ-0.35.0-05-01
- REQ-0.35.0-05-02
- REQ-0.35.0-05-03
- REQ-0.35.0-05-04
- REQ-0.35.0-05-05
- REQ-0.35.0-05-06
- REQ-0.35.0-05-07
- REQ-0.35.0-05-08
- REQ-0.35.0-05-09
- REQ-0.35.0-05-10
verification:
- uv run -m unittest tests.content.test_composer tests.content.test_lineage tests.commands.test_content_compose
- uv run -m behave features/content_compose.feature
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz validate --invariant-coherence
- uv run gz validate --rendition-floor-coherence
- uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-05-01-01
  - TASK-0.35.0-05-02-01
  - TASK-0.35.0-05-03-01
  - TASK-0.35.0-05-04-01
  - TASK-0.35.0-05-05-01
  - TASK-0.35.0-05-06-01
  - TASK-0.35.0-05-07-01
  - TASK-0.35.0-05-08-01
  - TASK-0.35.0-05-09-01
  - TASK-0.35.0-05-10-01
  - TASK-0.35.0-05-01-02
  - TASK-0.35.0-05-02-02
  - TASK-0.35.0-05-04-02
---

# OBPI-0.35.0-05-corpus-candidate-generator: Corpus Candidate Generator

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #5 - "corpus->candidate generator (owned materialize / unowned carry-forward) + `<consumer>.lineage.json` emission + `ByteEvidence` accounting correction"

**Status:** Draft

## Objective

Make the corpus actually materialize a candidate: owned sections are generated from the effective corpus, unowned sections are carried forward verbatim, a per-consumer `<consumer>.lineage.json` records which is which, and `ByteEvidence` stops reporting a 63x inflation as a compression accounting.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 05 depends on 01/03 (effective corpus and completed retirement), 04 (ownership declaration), and 09 (the delivered root-only AgentContract route). Shipping 05 before 01-03 ships a REGRESSION BY CONSTRUCTION: the seven byte-identical duplicate groups are invisible today only because `rendition_floor_coherence.py:72` is a substring test, and they become literal double-emissions the instant a generator materializes (ADR § Alternatives H). 07 depends on 05.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/content/composer.py` — the corpus->candidate generator and the `ByteEvidence` correction
- `src/gzkit/content/rendition.py` — `ByteEvidence` field semantics, if the correction requires it
- `src/gzkit/content/lineage.py` — the `<consumer>.lineage.json` model and writer **CREATE**
- `src/gzkit/content/ownership.py` — shared byte-boundary iterator only; preserve declaration and ratchet policy
- `src/gzkit/content/corpus_store.py` — **READ-ONLY dependency, never modified.** Declared because this OBPI's REQ-covering tests import `append_entry`/`load_corpus` to seed fixture corpora, and `_compute_missing_in_brief` reports an undeclared same-neighborhood src import as allowlist drift (amended in flight 2026-09-07; the file's own diff stays empty)
- `tests/content/test_ownership.py` — shared-boundary and existing ownership regression proof
- `src/gzkit/commands/content/__init__.py` — compose help/examples for generated versus explicit-candidate mode
- `src/gzkit/commands/content/compose.py` — route compose through the generator
- `tests/content/test_composer.py`, `tests/content/test_lineage.py`, `tests/commands/test_content_compose.py` — covering tests **CREATE**
- `features/content_compose.feature`, `features/steps/content_compose_steps.py` — Gate 4 scenarios
- `docs/user/manpages/content.md` — updated `compose` contract and the lineage artifact
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-05-corpus-candidate-generator.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/content/rendition_store.py` — `RenditionProvenance` is frozen/`extra="forbid"` and written at COMMIT time; bolting the lineage map onto it is ADR § Alternatives O, rejected
- `src/gzkit/content/models/corpus.py`, `src/gzkit/content/tier_policy.py` — OBPI-0.35.0-01
- `src/gzkit/governance/trust_audits/**` — `--rendition-lineage` is OBPI-0.35.0-06
- `src/gzkit/sync_surfaces.py`, `src/gzkit/governance/compose.py` — playback wiring is OBPI-0.35.0-09
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS derive owned sections from the EFFECTIVE corpus (OBPI-0.35.0-01), never the raw log. A generator on the raw log resurrects retired canon and emits the retired duplicates twice — the exact regression alternative H names.
2. ALWAYS carry unowned sections forward BYTE-VERBATIM. `gz validate --invariant-coherence` byte-compares a re-render against committed AGENTS.md, so a generator that reflows 22,378 B of carried-forward text fails a gate it was never meant to touch (`DESIGN_FORCING_FUNCTIONS.md` § 2 assumption a3).
3. NEVER take the candidate text as a parameter on the generated path. `composer.py:24-31` accepts `candidate_text` from the agent and its own docstring line 6 concedes "the drop/combine/rewrite judgment is the agent's." That is the gap this OBPI closes; the generator produces the owned bytes itself.
4. ALWAYS emit `<consumer>.lineage.json` alongside the candidate, shaped `{section_id: {owned: bool, entry_ids: list[str], byte_span: [start, end]}}`.
5. ALWAYS make `byte_span` PER-CONSUMER. The corpus is per-surface but renditions are per-(surface, consumer) at different setpoints; each span must be computed against its own candidate; equal candidates legitimately have equal spans, including different setpoints because the projection filter was retired (`DESIGN_FORCING_FUNCTIONS.md` § 4).
6. NEVER store the lineage map inside `RenditionProvenance`. It is frozen/`extra="forbid"` and written at commit time; the lineage map is produced at generate time and is per-section, not per-artifact (ADR § Alternatives O).
7. ALWAYS correct the `ByteEvidence` accounting. `composer.py:63-65` computes `compressible_bytes_after = total_bytes - invariant_bytes`, whose output tracks corpus size rather than compression: it reported 354 B -> 22,378 B at authoring and 354 B -> 6,894 B on 2026-09-08 (dated records of the defect, not live figures). Either way it is an INFLATION labelled compression, and a witness that cannot fail. `compressible_bytes_after` MUST count only compressible-tier bytes actually present in the candidate.
8. NEVER emit a byte accounting in which `compressible_bytes_after` exceeds `compressible_bytes_before`. Compression cannot add compressible bytes; if the computed value would exceed the input, that is a defect to fail on, not a number to print.
9. ALWAYS keep the generator deterministic — no LLM, no network, no clock. Determinism is load-bearing for OBPI-0.35.0-07's single-attestation-over-N-consumers ruling (ADR § Alternatives L).
10. NEVER emit two copies of a byte-identical invariant entry into one candidate. A live duplicate pair is a pre-publication error naming both identities, never an automatic text-keyed winner. This is the standing regression fence that OBPI-0.35.0-03 discharges for today's corpus.
11. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Generation and Accounting Contract

The generated path is selected when compose receives neither --candidate nor caller-supplied
text; it must not block reading stdin. Explicit candidate validation remains available for
existing callers, with its current invariant check. Generation resolves active routes and
ownership, then emits owned entries in effective log order with deterministic heading and
separator bytes. Invariant and compressible entry text is preserved verbatim; no new
compression policy or setpoint-dependent rewrite is invented. Empty owned sections retain
their heading. Unknown section ids, duplicate section ids and duplicate live invariant text
fail before writing. Unowned sections, including their delimiters, use the prior rendition's
raw UTF-8 spans. Missing prior text for any unowned section is a named refusal.

Lineage spans are half-open UTF-8 offsets covering a disjoint, complete section partition,
using OBPI-04's H1/H2 identity vocabulary. The current ownership scanner does not track
fences: this item owns extracting one shared fence-aware byte-boundary iterator and making
ownership measurement and generation consume it. Preserve unfenced-input results, preamble
accounting, collision refusals and declaration/ratchet policy. Test fenced H1/H2 examples
and multibyte offsets through both consumers. Existing declarations that disagree with the
corrected actual section roster fail with the governed reconciliation path; never silently
re-anchor or reset a ratchet. 13 consumes this iterator rather than inventing another scanner. Entry ids appear once in effective
order and only in their addressed owned section. Candidate lineage is staged with the candidate;
it must never overwrite the committed lineage for the prior rendition before landing.
05 exposes a pure candidate-plus-lineage result; 07 owns final publication.

ByteEvidence uses effective entry text bytes by tier. Owned emitted compressible text
contributes to compressible_bytes_after; unowned carry-forward, headings and delimiters do
not. Report these structural/carried bytes separately so total output reconciles without
calling all non-invariant bytes compression. Ownership coverage and ratchet are section-span
metrics from 04; the per-section entry histogram and entry-text totals remain separately
labeled population statistics, never a claim of unique rendered-byte coverage.

REQ-01/02 cover fenced headings, empty owned sections, missing carry-forward and unknown ids.
REQ-04 covers missing/extra ids, partition gaps, overlapping/out-of-bounds spans and Unicode.
REQ-06/07 cover retired compressible entries and unowned text that happens to equal an entry;
accounting must use emission attribution, never substring subtraction.
REQ-08 includes explicit-candidate compatibility and the no-stdin generated CLI path.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — pre-mortem, WWHTBT, constraint archaeology, 2am-operator, reversibility, scope minimization.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against

**Context:**

- [ ] ADR § Decision items 3 and 5 — materialize/carry-forward and the separate lineage artifact.
- [ ] ADR § Intent gap 1 and the `ByteEvidence` paragraph — the two defects this OBPI closes.
- [ ] ADR § Alternatives C, H, L, O — delta-patch-only, generator-first, LLM-in-the-render-path, and provenance-bolting; all rejected.
- [ ] ADR § Consequences (Positive) #8 — the lineage map is the provenance artifact the 2026-06-03 Re-Alignment specified and `RenditionProvenance` never carried.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-01 landed: `effective_corpus()` available and `invariant_entries()` reads it
- [ ] OBPI-0.35.0-03 is attested in the ledger: remeasure the effective invariant population and prove no live duplicate groups remain; historical counts are not input constants
- [ ] OBPI-0.35.0-04 landed: `.gzkit/ownership/AGENTS.md.json` declares every AGENTS.md section
- [ ] `src/gzkit/content/composer.py` and `src/gzkit/content/rendition.py` exist
- [ ] OBPI-09 and data/vendor-manifest.json route AgentContract only to root; `.gzkit/renditions/AGENTS.md/root.md` is the carry-forward source. Retained codex.md is off-route history, never a generation target.

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/composer.py:24-31` and its docstring line 6 — the `candidate_text` parameter and the conceded agent judgment
- [ ] Read the whole composer and its callers: effective folding applies to both tiers, and the current `total - invariant` arithmetic wrongly includes unowned and structural bytes
- [ ] `src/gzkit/content/rendition.py:19-33` — `ByteEvidence` field semantics
- [ ] `src/gzkit/content/rendition_store.py:31-53` — `RenditionProvenance`, frozen and commit-time; read to understand why lineage is a separate artifact

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run -m unittest tests.content.test_composer tests.content.test_lineage tests.commands.test_content_compose
uv run -m behave features/content_compose.feature
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --invariant-coherence
uv run gz validate --rendition-floor-coherence
uv run mkdocs build --strict
```

## Demo

Commands below demonstrate the delivered generated path after implementation.

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content compose AGENTS.md --consumer root
uv run -m unittest tests.content.test_composer tests.content.test_lineage tests.commands.test_content_compose
uv run -m behave features/content_compose.feature
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-05-01 [behavior]: Given an ownership declaration marking section S `corpus-owned` and a corpus carrying entries addressed to S, when the generator runs, then S's bytes in the candidate are derived from the EFFECTIVE corpus entries for S, with no `candidate_text` supplied by the caller for that section.
- [ ] REQ-0.35.0-05-02 [behavior]: Given a section marked `unowned`, when the generator runs against the prior committed rendition, then that section's bytes appear in the candidate BYTE-VERBATIM — carry-forward reflows nothing.
- [ ] REQ-0.35.0-05-03 [behavior]: Given a corpus containing a live entry that a tombstone retired, when the generator runs, then that retired entry contributes no bytes or lineage id to owned materialization. Coincidentally identical text in an unowned carried-forward span remains byte-verbatim; text absence from the entire document is not the liveness witness.
- [ ] REQ-0.35.0-05-04 [behavior]: Given a generator run for consumer C, when it completes, then `<consumer>.lineage.json` exists carrying, for every AGENTS.md section id, an `owned` flag, the contributing `entry_ids` (empty for unowned), and a `byte_span`.
- [ ] REQ-0.35.0-05-05 [behavior]: Given a fixture with two manifest-routed consumers, each lineage span indexes its own candidate's exact UTF-8 section bytes; identical candidates permit equal spans and deliberately different prefix lengths produce different offsets. On this repository AgentContract generates root only and refuses off-route claude/codex targets.
- [ ] REQ-0.35.0-05-06 [behavior]: Given a candidate produced by the generator, when `ByteEvidence` is computed, then `compressible_bytes_after` counts only compressible-tier bytes present in the candidate and is less than or equal to `compressible_bytes_before` — never `total_bytes - invariant_bytes`, a formula whose output tracks corpus size rather than compression (it yielded 22,378 against an input of 354 at authoring, and 6,894 against 354 on 2026-09-08 -- dated records, not live figures).
- [ ] REQ-0.35.0-05-07 [behavior]: Given a computed accounting in which `compressible_bytes_after` would exceed `compressible_bytes_before`, when the generator runs, then it FAILS with recovery prose rather than emitting the inflated figure — the witness must be able to fail.
- [ ] REQ-0.35.0-05-08 [behavior]: Given identical corpus, ownership declaration, and prior rendition, when the generator is run twice, then it produces byte-identical candidates and byte-identical lineage maps — determinism is load-bearing for the OBPI-0.35.0-07 single-attestation ruling.
- [ ] REQ-0.35.0-05-09 [behavior]: Given a corpus containing two LIVE byte-identical `invariant` entries, when the generator runs, then generation fails before emitting a candidate and identifies both entry ids and sections for governed retirement; it never silently elects a winning section or deduplicates by text (parent Alternatives D).
- [ ] REQ-0.35.0-05-10 [structural-fence]: The rendered-section-to-contributing-entry-ids map lives in `<consumer>.lineage.json` and NOWHERE inside `RenditionProvenance`, which remains frozen with `extra="forbid"` with no embedded lineage fields across every ADR-0.35.0 OBPI; the optional commit-time landing_id explicitly required by parent Decision 6 is permitted. Generate-time and commit-time lifecycles stay separated (ADR § Alternatives O); the property is a cross-OBPI boundary because OBPI-0.35.0-06 and OBPI-0.35.0-07 both read these artifacts and either could bolt the map on.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

Scoped suite (`uv run -m unittest tests.content.test_composer tests.content.test_lineage
tests.commands.test_content_compose`): **53 tests, OK**. Full suite: 9952 tests, receipt
`arb-step-unittest-5a440760fc5542ab9d08a48c18d4de08` (`exit_status: 0`).

> **Both figures are superseded and are kept as the record of what was observed when.**
> Re-measured 2026-09-08: the full suite is **9,966 tests, OK (skipped=4)**, receipt
> `arb-step-unittest-ebee8240d52d4445a4b66b141116b14a`. The scoped run was widened to include
> `tests.content.test_ownership` — the fourth module this OBPI edits — giving **191 tests, OK
> (skipped=4)**; 53 was the three-module figure, not a discrepancy. Full observed output:
> `.gzkit/evidence/OBPI-0.35.0-05-corpus-candidate-generator.stage4a.md` § 6.1.

#### Native Windows execution — observed, not asserted

Round 1 finding 3 (the CLI persisting the candidate through `Path.write_text`, whose
`newline=None` performs LF→CRLF translation on Windows and would slide every lineage
offset) left a residual: *"native Windows persistence was not executed here."* A prior
revision discharged it with *"the repository runs `windows-latest` in CI"* — which is a
**presence check**, answering *"is a Windows job armed"* and never *"did it run against
this revision"*. Round 5 then caught this section citing a run it did not contain. Both are
closed by the runs below, which were obtained and inspected rather than cited.

`.github/workflows/ci.yml` is a **Denied Path** for this OBPI and operator canon forbids
feature branches, so the only native-Windows surface available is CI on push to `main`.
The implementation was therefore pushed ahead of Gate 5 deliberately; the brief stays
`Active`, no completion receipt exists, and Stage 5 is not entered.

| Revision | Run | Windows job | Result |
|---|---|---|---|
| `edb52f10` | `34173295241` | `101897663925` | success |
| `c4055edf` (round-4 reviewed; last production change) | `34175266902` | — | success |
| `04f18f0e` (round-5 reviewed) | `34175949868` | `101905245705` | success |
| **`53b6b0f6`** (contract-derived oracle) | **`34177044358`** | **`101908408526`** | **success** |

Job `101908408526`, `2026-09-08T01:33:25Z → 01:46:17Z`:

- Runner OS read from the job log: **`Microsoft Windows Server 2025`** — a native runner,
  not a claim about workflow configuration.
- Step 7 `uv run gz check` — the full gate — passed, with **60 named checks** green,
  including `Test` (the whole unittest suite, so every test in this OBPI's scope executed
  natively), `Behave`, `Format`, `Line endings`, `Invariant coherence`,
  `Rendition floor coherence`, `RED parity` and `Surface fidelity`.

This discharges the tier-1 adversary's own recorded next step — *"Run the focused
disk-fixture tests, including the persisted-byte test on Windows, in writable CI"* — and
the sandbox `No usable temporary directory found` coverage limit, which is an environment
limitation of the read-only reviewer rather than a defect. The persisted-byte and
contract-oracle tests both ran under that suite on Windows.

#### Falsifiability — per-REQ behavioural negative controls

The `gz arb red` witness returned `failure_class: error` for all nine BEHAVIOR REQs: the
covering tests import `generate_candidate` / `_byte_evidence` at module level, so
withholding the production hunks breaks the import before any assertion runs. Per
`.gzkit/rules/tests.md` that is a WEAK red — it proves the symbols are absent, never that
the assertions bite. It is recorded here for completeness and is **superseded as the
falsifiability evidence** by the controls below.

Each row below is a **behavioural** negative control: a one-edit mutation of production
code that VIOLATES the named requirement, leaves the module importable (`imports=True`,
so the failure is never an import error), and is run against **only that REQ's own
`@covers` test** — so the observed `failure_class` is that test's own verdict and never
collateral from a neighbour. Every row therefore carries both halves the operator asked
for: a **green baseline** on the unmutated tree, and a **failure caused by violating the
requirement**, reaching the assertion.

Run via the repository's sanctioned `gzkit.mutation_witness.run_mutation_sweep`, one sweep
per REQ (its own baseline, its own scope).

| REQ | Mutation (the requirement violated) | Baseline | Outcome | `failure_class` | Assertion reached in |
|-----|-------------------------------------|----------|---------|-----------------|----------------------|
| 05-01 | owned section body taken from PRIOR TEXT (`chunk = heading_bytes + body` → `chunk = prior_bytes[boundary.start : boundary.end]`) | green | killed | `assertion` | `test_owned_section_body_is_derived_from_corpus_not_prior_text` |
| 05-02 | unowned carry-forward REFLOWED LF→CRLF instead of byte-verbatim | green | killed | `assertion` | `test_unowned_section_bytes_are_byte_verbatim` |
| 05-03 | owned sections derived from the RAW log (`effective = effective_corpus(corpus)` → `effective = corpus`), resurrecting retired entries | green | killed | `assertion` | `test_retired_entry_contributes_nothing_while_verbatim_span_is_unaffected` |
| 05-04 | lineage emits no contributing `entry_ids` (`tuple(e.id for e in section_entries)` → `()`) | green | killed | `assertion` | `test_lineage_carries_owned_entry_ids_and_byte_span_for_every_section` |
| 05-05 | off-route consumer not refused (`if consumer not in declared_routes:` → `if not declared_routes:`) | green | killed | `assertion` | `test_two_routed_consumers_get_different_offsets_and_off_route_is_refused` |
| 05-06 | GENERATED emission attribution counts entries the generator never emitted (`section_entries` → `effective.entries`) | green | killed | `assertion` | `test_a_compressible_entry_in_an_unowned_section_is_never_attributed` |
| 05-07 | inflation guard defeated (`if compressible_bytes_after > compressible_bytes_before:` → `if False:`) — the inflated figure is emitted, not refused | green | killed | `assertion` | `test_byte_evidence_raises_when_attributed_exceeds_before` |
| 05-08 | generation made call-history dependent — same inputs, different bytes | green | killed | `assertion` | `test_two_runs_produce_byte_identical_candidate_and_lineage` |
| 05-09 | duplicate-live-invariant refusal defeated (`len(group) <= 1` → `len(group) <= 2`) | green | killed | `assertion` | `test_two_live_byte_identical_invariant_entries_are_refused` |
| 05-04/05 *(round-3 high)* | lineage validated by section-id ROSTER instead of actual boundary offsets (`if actual == claimed:` → `if set(actual) == set(claimed):`) | green | killed | `assertion` | `test_same_roster_heading_injection_that_moves_boundaries_is_refused` |
| 05-02 *(round-3 medium)* | fence scanner enters fence state on a 4-space-indented code block | green | killed | `assertion` | `test_four_space_indented_backtick_run_is_an_indented_code_block_not_a_fence` |
| 05-02 *(round-3 medium)* | fence scanner treats an inline code span as a backtick fence opener | green | killed | `assertion` | `test_inline_code_span_is_not_a_backtick_fence_opener` |
| 05-04/05 *(round-4 weakest point)* | persisted candidate newline-translated, sliding every lineage offset — the Windows `write_text` defect simulated platform-independently | green | killed | `assertion` | `test_generated_lineage_spans_index_the_PERSISTED_candidate_bytes` |
| 05-04/05 *(round-5 isolation)* | persisted boundary MOVED AT CONSTANT LENGTH — 95 B → 95 B (`_GEN_PRIOR_TEXT` measured at 95 B, 2026-09-08), so the length assertion structurally cannot fire. OBSERVED: this test's three earlier assertions — the owned-body slice assertion, the contiguity resume assertion, and the final persisted-length assertion — passed, and the persisted identity/offset mapping assertion fired. Whether any assertion OUTSIDE this test detects the mutation was NOT measured; this row is scoped to the test, never an exclusivity claim | green | killed | `assertion` | `test_generated_lineage_spans_index_the_PERSISTED_candidate_bytes` |
| 05-02 *(oracle, parser side)* | SHARED-parser defect — fence tracking disabled. Fires on the literals | green | killed | `assertion` | `test_parser_reproduces_the_contract_derived_identities_and_offsets` |
| 05-04/05 *(oracle, persisted side)* | SHARED-parser defect — fence tracking disabled. **Kills at that test's CLI exit-code assertion (`assertEqual(result.exit_code, 0, ...)`), NOT at its contract-literal span assertion** — `load_declaration` refuses the undeclared `fake` section first. Retained as a real kill, but it does NOT evidence the persisted oracle's incremental strength | green | killed | `assertion` | `test_persisted_lineage_matches_contract_derived_offsets_not_just_the_parser` |
| 05-02 *(oracle literals, parser side)* | byte offsets computed as CODEPOINTS; roster unchanged. Fires on the literals in BOTH oracle tests — `test_parser_reproduces_the_contract_derived_identities_and_offsets` at its section-id->span mapping assertion, with `{'a': (0, 25), 'b': (25, 32)} != {'a': (0, 26), 'b': (26, 33)}`, and `test_measured_spans_match_the_contract_derived_widths` at its `measure_section_spans` assertion, with `{'a': 25, 'b': 7} != {'a': 26, 'b': 7}`. **Not exclusive** — production refuses this candidate too, and the pre-existing `TestIterSectionBoundaries` test fails at its byte-offset assertion | green | killed | `assertion` | `test_parser_reproduces_...` (mapping assertion) / `test_measured_spans_...` (widths assertion) |
| 05-04 *(oracle literals, persisted side)* | PERSISTED lineage diverges from the validated in-memory lineage — every span shifted +1; roster unchanged, spans contiguous, widths constant; declaration validation and persistence both succeed. Fires on that test's contract-literal span assertion: `{'a': [1, 27], 'b': [27, 34]} != {'a': [0, 26], 'b': [26, 33]}`. **Not exclusive** — the sibling test's contiguity assertion also catches it (`span (1, 47) does not resume at byte 0`). Demonstrates the literal assertion's SENSITIVITY to post-validation serialization corruption, nothing more | green | killed | `assertion` | `test_persisted_lineage_matches_contract_derived_offsets_not_just_the_parser` |

Observed transcript (`baseline_green` is the unmutated scoped run; `failing` is the test
the mutation broke):

```text
REQ-0.35.0-05-01  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_owned_section_body_is_derived_from_corpus_not_prior_text']
REQ-0.35.0-05-02  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_unowned_section_bytes_are_byte_verbatim']
REQ-0.35.0-05-03  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_retired_entry_contributes_nothing_while_verbatim_span_is_unaffected']
REQ-0.35.0-05-04  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_lineage_carries_owned_entry_ids_and_byte_span_for_every_section']
REQ-0.35.0-05-05  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_two_routed_consumers_get_different_offsets_and_off_route_is_refused']
REQ-0.35.0-05-06  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_a_compressible_entry_in_an_unowned_section_is_never_attributed']
REQ-0.35.0-05-07  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_byte_evidence_raises_when_attributed_exceeds_before']
REQ-0.35.0-05-08  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_two_runs_produce_byte_identical_candidate_and_lineage']
REQ-0.35.0-05-09  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_two_live_byte_identical_invariant_entries_are_refused']
REQ-0.35.0-05-04/05 (round-3 high)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_same_roster_heading_injection_that_moves_boundaries_is_refused']
REQ-0.35.0-05-02 (round-3 medium)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_four_space_indented_backtick_run_is_an_indented_code_block_not_a_fence']
REQ-0.35.0-05-02 (round-3 medium)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_inline_code_span_is_not_a_backtick_fence_opener']
REQ-0.35.0-05-04/05 (round-4 weakest point)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_generated_lineage_spans_index_the_PERSISTED_candidate_bytes']
REQ-0.35.0-05-04/05 (round-5 isolation)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_generated_lineage_spans_index_the_PERSISTED_candidate_bytes']
REQ-0.35.0-05-02 (oracle, parser side)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_measured_spans_match_the_contract_derived_widths', 'test_parser_reproduces_the_contract_derived_identities_and_offsets']
REQ-0.35.0-05-04/05 (oracle, persisted side)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_persisted_lineage_matches_contract_derived_offsets_not_just_the_parser']
REQ-0.35.0-05-02 (oracle literals, parser side)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_measured_spans_match_the_contract_derived_widths', 'test_parser_reproduces_the_contract_derived_identities_and_offsets']
REQ-0.35.0-05-04 (oracle literals, persisted side)  baseline_green=True  outcome=killed       failure_class=assertion imports=True  failing=['test_persisted_lineage_matches_contract_derived_offsets_not_just_the_parser']

CONCLUSIVE: 18/18 assertion-class kills; all baselines green=True
```

**Reproducibility of these rows from this record — measured 2026-09-08.** Eight rows carry
an exact find→replace string and can be re-run by any reader: **1, 3, 4, 5, 6, 7, 9, 10**.
Ten rows carry a prose description only and CANNOT be reproduced from this record without
reconstructing a mutation the record does not specify: **2, 8, 11, 12, 13, 14, 15, 16, 17,
18**. Every row bearing an isolation or exclusivity claim (13, 14, 16, 17, 18) is in the
non-reproducible set. This is stated as a limit of the record, not repaired by inventing
strings that were never run: the outcomes were observed when the sweeps ran, and this
session did not re-run them.

**Which assertion killed a mutation is OBSERVED, never inferred** (operator ruling
2026-09-08: *"constant byte length alone does not prove which assertion killed the
mutation"*). Both persisted-candidate rows were re-run with the mutation applied and the
failure read:

- Row 14 (constant-length boundary move) fails at **`test_content_compose.py:478`**, the
  added identity/offset mapping assertion, with its own message:
  `AssertionError: {'owned-section': (0, 95)} != {'owned-section': (0, 46), 'unowned-section': (46, 95)}`.
  The fixture is **95 B → 95 B** under the mutation, so the length assertion structurally
  cannot fire; the mapping assertion is what caught it. (An earlier revision wrote 58 B
  here — that measured a hand-typed snippet, not `_GEN_PRIOR_TEXT`. Round 6 caught it;
  the constant-length property holds, the number did not.) Its incremental strength is
  therefore demonstrated, not assumed.
- Row 13 (LF→CRLF) fails at **`test_content_compose.py:446`**, the owned-body slice
  assertion — `AssertionError: b'Owned body from the corpus.' not found in
  b'## Owned Section\r\n\r\nOwned body from the corpus'`. **This corrects round 5's
  account**, which attributed the pre-emption to the final-length assertion; the
  conclusion it drew (row 13 does not isolate the mapping assertion) was right, its
  mechanism was not.

**A disclosed bound on REQ-02's covering assertion (measured 2026-09-08).**
`test_unowned_section_bytes_are_byte_verbatim` (`test_composer.py:516`) locates BOTH sides
with production code: `expected` is sliced from the prior rendition using
`iter_section_boundaries`, and `actual` is sliced from the candidate using the production
lineage span. It therefore proves the carried bytes are byte-identical — which is what row
05-02's LF→CRLF kill witnesses — and it does NOT independently verify boundary LOCATION: a
boundary shift correlated across both slices would pass. Contiguity-from-zero at
`test_content_compose.py:457` is the parser-independent structural check; this assertion is
not one.

**Two rows of the first 9-row sweep were faulted by round 3's mutation audit and are
corrected above, not defended.** Row 05's off-route vendor also lacked a declared
temperature, so defeating the route guard still refused — via `temperature_for` — and the
covering assertion could only fail on diagnostic wording; the fixture now gives that vendor
a temperature AND a prior rendition, so the refusal is attributable to the route gate
alone. Row 06 dropped the EXPLICIT path's presence filter, which leaves GENERATED emission
attribution untouched, so it never witnessed the generator-specific REQ-06 it claimed; it
is rebound to emission attribution with a new covering test. The earlier
"9/9 assertion-class kills" therefore **overstated** what was established — 7 of 9 rows
were sound. The corrected sweep was 12/12 AT THAT POINT — the nine rebound original rows plus round 3's three. The table has since grown to 18 rows; the transcript's `CONCLUSIVE: 18/18` is the current all-rows figure, and 12/12 is a historical waypoint, not a competing total.

The source file is restored by the sweep and after the run
`src/gzkit/content/composer.py` carries none of the nine mutation strings and all six
canonical guards at their original lines (verified by grep; the 53-test scoped suite is
green again).

### Code Quality

```text
uv run gz arb ruff        -> clean, receipt arb-ruff-77cc404ebe724bb6bfe0388427961906        (exit_status: 0)
uv run gz arb typecheck   -> clean, receipt arb-step-typecheck-8438242770414aa8b1dc4e3d07ddf786 (exit_status: 0)
```

### Gate 3 (Docs)

```text
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
-> clean, receipt arb-step-mkdocs-dd58dc103a2d45cb89bec1322bba805a (exit_status: 0)
```

`docs/user/manpages/content.md` carries both compose modes (explicit candidate and
generated) and the `<consumer>.candidate.lineage.json` artifact.

### Gate 4 (BDD)

```text
uv run gz arb step --name behave -- uv run -m behave \
  --tags=@REQ-0.35.0-05-01,@REQ-0.35.0-05-02,@REQ-0.35.0-05-04,@REQ-0.35.0-05-05,@REQ-0.35.0-05-08 features/
-> 5/5 scoped scenarios pass, receipt arb-step-behave-b0eb5da37ce642699734e2de4707cdd6 (exit_status: 0)
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Step 4b — Independent Adversarial Validation

**Standing verdict:** refuted

> Declared per GHI #964 — exactly one declaration line; round 3's refutation token below
> stays written where it happened and is not relabelled. The word is round 5's ACTUAL
> verdict and is not adjusted by this agent's confidence in its own subsequent repairs.
>
> **ATTESTATION MUST NOT BE SOLICITED ON THIS LINE ALONE.** Round 5 raised two findings
> against the EVIDENCE and both were repaired after it reviewed, so no independent round
> has yet seen the corrected evidence or the contract-derived oracle. Round 6 is dispatched
> for exactly that. Closure is demonstrated, never round-counted.


**SCOPE RULING 2026-09-08 — what the standing declaration above is ABOUT.** The
operator ruled that the assertion classifier's role be resolved before another review
dispatch. It was traced to the governing acceptance requirements and found **AUXILIARY, not
required proof**: no REQ in `## Acceptance Criteria` asks for assertion classification; a
classifier's output is not one of the three proof channels `.gzkit/rules/tests.md` § REQ
Scope Discipline admits; `.gzkit/evidence/**` is not in this brief's Allowed Paths; and the
classifier postdates the work by five rounds. The measured consequence: the last commit
touching `src/**`, `tests/**` or `features/**` is `1cef5d80` (round 9's repair), so
**rounds 10 through 14 produced zero production change and zero test change** — verifiable
as `git diff --stat -- src tests features` returning empty.

The declaration above therefore records a refutation whose SUBJECT is the evidence record's
commentary about that diagnostic, never the generator: no round from 10 to 14 reports a defect
in `src/gzkit/content/**`, and none changed a line there. **A false attribution written into an
earlier draft of this block is corrected rather than quietly dropped** — it claimed *"every
round from 8 through 14 wrote the same sentence: 'No production defect has been demonstrated.'"*
Measured: that sentence occurs at `:1051`, `:1119` and `:1179` — rounds 11, 12 and 13 only.
Round 10 words it differently and **round 14 carries no such sentence at all**; it is also this
agent's own cumulative summary line, never a reviewer verdict. Writing a quotation as though
seven rounds had recorded it, without grepping for it, is the defect class this sequence is
about. The rounds are preserved
below unaltered as history — no finding is withdrawn, no round is relabelled, and the two
open classifier misclassification families (2 inline `str(ctx.exception)`, 6 loop-binding,
root-caused to the `ast.Assign`-only taint walk at `assertion-audit.py:97`) stay recorded.
Per the operator: *"Stop making the accuracy of optional diagnostic commentary a
prerequisite for accepting the generator."*

The acceptance argument is rebuilt on direct, requirement-specific evidence in
`.gzkit/evidence/OBPI-0.35.0-05-corpus-candidate-generator.stage4a.md` §§ 5-7 — the covering
tests re-run, the live generator's persisted lineage partition, the accounting, the observed
refusals, determinism, and the structural fence — with all unresolved findings carried in
§ 7. Classifications and totals are withdrawn from that argument and preserved as history in
its § 8. No regression test discovered through any review round is removed.

Tier 1 (cross-vendor, Codex via the `codex-companion.mjs` plugin), two rounds. The
round-1 refutation token below is the historical record of what was found and
discharged; the standing verdict above is the state after closure.

**Round 1 — `NOT-CORROBORATED | refuted`** (receipt
`arb-step-codexadversary-eee752c4e22645739c0e20a0451aa563`, `exit_status: 0`). It
confirmed the live feature (deterministic candidate+lineage, exact owned ids, unowned
byte equality, partition, invariant floor, emission attribution, off-route refusal) and
then reproduced five defects — three high:

1. `[high]` `e.text.strip()` mutilated entry text: a valid indented compressible entry
   emitted without its indentation while accounting still reported the original bytes,
   trailing Markdown hard-breaks removed, and a valid indented **invariant** entry was
   FALSELY REFUSED by the floor (the floor searches the unstripped text).
2. `[high]` An entry whose *text* carried a heading injected a rendered section with no
   lineage record (`extra rendered ids=['unexpected-new-section']`) while
   `assert_complete_partition` still passed, because it validated the generator's own
   numeric assignments rather than the rendered output; and an entry addressed to an
   unknown section id was silently dropped instead of refused.
3. `[high]` The CLI persisted the candidate with `Path.write_text`, so Windows LF→CRLF
   translation would invalidate every lineage offset (`generated= 31244 persisted= 31520`).
4. `[medium]` The explicit path overwrote the candidate but left the stale generated
   lineage beside it.
5. `[medium]` Fence tracking toggled on any three-backtick prefix, so a four-backtick
   fence containing a three-backtick example closed early (roster `['a','fake','b']`);
   tilde fences were unrecognized.

**Round 2 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-43e450a13deb4649a432b7e3356d5d66`, `exit_status: 0`), a focused
closure review over the unchanged scope. All five findings **CLOSED** with pasted
evidence, no material findings, LIVE PASS retained
(`deterministic=True exact_owned_ids=True unowned_byte_equality=True actual_spans=True
partition=True invariant_floor=True emission_attribution=True`), and no regression across
REQ-01/02/04/05. Each closure was checked in both directions — the guard refuses the
defect AND still accepts the legitimate positive case.

**Caveats, and their disposition.** Round 2's caveats were sandbox coverage limits (its
filesystem is read-only), not defects. Two were closed locally in a writable environment
after the review, which is what its own "next steps" asked for:

- Closure 3 real write: persisted candidate `31244 B` == lineage max span end `31244`.
- Closure 4 real generated→explicit round-trip: `after generated: lineage=present
  candidate=31244B` → `after explicit (exit 0): lineage=absent candidate=47851B`.
- The seven disk-fixture tests it could not run are green in the full suite
  (`arb-step-unittest-5a440760fc5542ab9d08a48c18d4de08`, 9952 tests, `exit_status: 0`).

**Residual, disclosed:** native Windows persistence was not executed here. The fix is a
`write_bytes` call whose correctness follows from removing text-mode translation, and the
repository runs `windows-latest` in CI, but this session did not observe it.

**Round 3 — `NOT-CORROBORATED | refuted`** (receipt
`arb-step-codexadversary-6d6d992d16e2466cb6a8af7d18073620`, `exit_status: 0`), tier 1,
cross-vendor Codex via the `codex-companion.mjs` plugin, scoped
`--scope branch --base c9e62790` against revision `edb52f10`. Dispatched under the
operator's 2026-09-07 instruction to re-review the final implementation with the round-1
findings supplied, their closure verified, and freedom to discover new defects.

It CONFIRMED the live feature positively — `LIVE deterministic=True actual_spans=True
unowned_verbatim=True exact_owned_ids=True partition=True invariant_floor=True
emission_attribution=True`, all five round-1 closures verified in BOTH directions, every
refusal guard exercised against a legitimate control, `REQ10 frozen=True extra=forbid
lineage_fields=[]` — and then reproduced **two new defects**:

1. `[high]` **Roster-only lineage validation** (`composer.py`). Round 1's fix re-walked the
   candidate but compared only section-id SETS. An entry whose text carries a heading
   DUPLICATING an existing later heading, plus an unbalanced fence hiding the original,
   leaves the roster byte-identical while the real boundary MOVES — so the lineage names
   spans belonging to a different section. Both the roster check and
   `assert_complete_partition` passed, because the generator's own numbers stayed
   internally consistent. **Independently reproduced here against the live corpus** before
   acting: `governance-doctrine-surfaces` lineage `(30261, 30682)` vs actual
   `(30261, 30650)`; `architectural-boundaries` lineage `(30682, 31277)` vs actual
   `(30650, 31277)` — 32 bytes of false provenance, roster 22 = 22, partition "complete".
2. `[medium]` **Fence scanner over-acceptance** (`ownership.py`). `_fence_run` `lstrip()`ed
   arbitrary indentation and read any leading three-backtick run as a fence. Under
   CommonMark a 4-space-indented run is an indented CODE BLOCK, and a backtick fence's info
   string may not contain a backtick — so ` ```inline code``` ` is not a fence opener.
   Both entered fence state and swallowed the next heading. The failure direction is a
   **FALSE REFUSAL**: legitimate invariant entry text is rejected because a real section
   appears to have gone missing. Independently reproduced: `# a` + the line + `## b`
   returned roster `['a']` against a true `['a', 'b']` for both inputs.

It also **audited the recorded mutation table** and faulted two rows as not witnessing the
REQ they claimed (05 and 06) — corrected in § Falsifiability above rather than defended.

**Same-root escalation, surfaced not resolved.** Round 1's finding 2 and round 3's high
finding share one root: *the lineage is validated against a weaker proxy than the rendered
bytes* (first the generator's own numeric assignments, then the section-id roster). The
`gz-obpi-pipeline` skill directs that a repeated root be escalated to the operator rather
than patched again. The fix applied compares each reparsed section's identity AND exact
half-open offsets — which IS the rendered output, leaving nothing weaker to regress to — so
it is judged terminal for this root rather than a third layer. **That judgment is the
operator's to overturn.**

**Disposition:** both findings fixed, each with a paired covering test proving the guard
fires on the defect AND still accepts the legitimate case, and each with a behavioural
negative control (rows 10-12 above). Round 4 re-review pending; the standing verdict stays
`refuted` until an independent round returns otherwise.

**Round 4 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-e82f72ebb97543668d9a86790ee4d0a2`, `exit_status: 0`), tier 1,
same cross-vendor Codex plugin, scoped `--scope branch --base edb52f10` against revision
`c4055edf` — a FOCUSED closure re-review over the unchanged scope and threat model, not a
fresh unrestricted search.

Both round-3 findings **CLOSED**, each checked in both directions with pasted output:

- Finding 1 CLOSED — `ATTACK refused=True` with the moved spans named
  (`governance-doctrine-surfaces lineage=(30261, 30682), actual=(30261, 30650)`), three-part
  recovery prose present, and the legitimate direction still succeeding:
  `LIVE accepted=True deterministic=True actual_spans=True unowned_verbatim=True
  exact_owned_ids=True partition=True invariant_floor=True emission_attribution=True
  explicit_compatible=True bytes=31244 sections=22`. Its own partition probes:
  `exact: accepted / missing: refused / extra: refused / moved: refused`.
- Finding 2 CLOSED — `Ran 10 tests ... OK`, and eight scanner+live-generation probes
  (`indented`, `inline`, `plain`, `long`, `python`, `tilde`, `long-tilde`, `tilde-info`)
  each returning `roster=['a', 'b'] live_generation=accepted`.
- Mutation correction ACCEPTED as semantic, not wording-only: *"Row 05 supplies vendorC's
  temperature and prior rendition, so disabling route refusal permits forbidden generation
  rather than merely changing diagnostics... These are semantic failures, not wording-only
  kills."* It also noted the brief *"explicitly retracts 9/9 as overstated and records 7/9
  sound rows."*

**No material findings.**

**Its caveats were coverage limits of a read-only sandbox, and their disposition:**

- Could not execute disk-fixture tests, the persisted-byte CLI test, Windows behaviour, or
  the mutation sweep (`FileNotFoundError: No usable temporary directory found`). Its own
  next step was *"Run the focused disk-fixture tests, including the persisted-byte test on
  Windows, in writable CI."* — discharged by the native `windows-latest` run recorded in
  § Gate 2 below, which executes the whole suite on Windows Server 2025.
- Weakest point: *"Persisted-file coherence remains source-inspected rather than
  independently executed here."* The test-strength half is CLOSED — the persisted-byte test
  now re-parses the bytes that reached disk and holds every section's identity and exact
  offsets to the same bar `_refuse_generated_lineage_drift` applies in memory, with control
  row 13 proving it fails under simulated newline translation. **Production code is
  BYTE-IDENTICAL to the round-4 reviewed revision** (`git diff c4055edf -- src/` is empty),
  so round 4's verdict covers the entire production surface presented.
- IRREDUCIBLE, disclosed: the mutation sweep *"remains recorded evidence, not an
  independently executed sweep."* No read-only reviewer can execute a sweep that edits and
  restores a guard. The record is reproducible by the operator from the table above.

**Round 5 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-27a74d68972e47d4b26f7e6bcad878d5`, `exit_status: 0`), tier 1,
scoped `--scope branch --base c4055edf` against revision `04f18f0e` — a narrow
confirmation over a test-only delta. It verified `git diff c4055edf -- src/` itself (exit
0, empty), confirmed the strengthened assertion matches `_refuse_generated_lineage_drift`'s
bar, and confirmed exactly one standing-verdict declaration with round 3's refutation
preserved as history.

**This round is NOT recorded as clean.** It returned no material findings about the
implementation, but it raised **two findings against the EVIDENCE**, and both were
repaired AFTER it had reviewed — so its verdict describes the pre-repair evidence and
cannot certify the repair (operator ruling 2026-09-08: *"Do not describe round 5 as clean
while its evidence findings remain awaiting verification."*). Their closure is what round 6
exists to verify.

1. **Dangling Windows citation — the OBPI's own defect, not the reviewer's.** *"The cited
   Gate 2 section does not identify the claimed native Windows run."* The round-4 record
   asserted the sandbox coverage limit was discharged by a `windows-latest` run *"recorded
   in § Gate 2 below"*, and no such record existed. A citation naming an artifact that is
   not there is the presence-check family AGENTS.md names. Closed by § Gate 2 —
   § Native Windows execution below, which now carries run and job ids, the runner OS, and
   the executed gate list.
2. **Row 13 did not isolate the added assertion.** Closed by row 14 above, with the
   killing assertion observed rather than inferred.

**Withdrawn claim — independent verification never required a second parser.** A prior
revision of this brief asserted that closing round 5's shared-parser weakest point *"would
need a second, independent parser, which is beyond this brief."* **That does not follow and
is withdrawn** (operator ruling 2026-09-08: *"Independent expected results do not require
another parser."*). Using one parser on both sides proves the two AGREE; it cannot prove the
boundaries are CORRECT. An oracle only needs expectations derived from the CONTRACT — so
`TestBoundariesAgainstContractDerivedExpectations` and
`test_persisted_lineage_matches_contract_derived_offsets_not_just_the_parser` state the
section identities and exact half-open byte offsets as hand-derived literals (segment
lengths spelled out in the fixture: `# A\n`=4, `café\n`=6, ` ```\n `=4, `## fake\n`=8
FENCED, ` ```\n `=4, `## B\n`=5, `x\n`=2 ⇒ `a`=[0,26), `b`=[26,33), total 33).

**The blindness claim is WITHDRAWN — it was overstated twice, and neither correction
rescued it.** Round 6 showed the first version was an ARTEFACT: it ran the fence-disabling
defect against `_GEN_PRIOR_TEXT`, which carries no fence and no multibyte character (95 B,
verified), so the agreement tests survived because nothing touched them. Round 7 then
showed the *re-measurement* was still overstated: comparing two walks of the same
deterministic parser establishes only that a deterministic function is deterministic. It
says nothing about `_refuse_generated_lineage_drift`, which compares **two different
computations** — a lineage accumulated from emitted byte-chunk lengths
(`composer.py:449-479`) against a parse of the resulting candidate.

**Measured, and it settles the question in production's favour:** under the codepoint
defect the two parser walks agree, and the real generator REFUSES anyway —
`moved spans={'b': {'lineage': (25, 32), 'actual': (25, 31)}}`. The production agreement
check is **not** blind to parser defects, precisely because its two sides are not the same
computation. Round 7's own probe reproduced this.

So the contract oracle's value is NOT *"it catches what the agreement check misses"* —
production already catches those. Round 8 then withdrew the replacement framing too: the
claims *"only witness for persisted-artifact divergence"* and *"invisible to every
agreement check"* are **also false**, and are withdrawn. Measured: row 18's serialization
shift is caught at `test_content_compose.py:457` by the sibling test's contiguity assertion
(`span (1, 47) does not resume at byte 0`), so `:552` is not the exclusive detector; and a
pre-existing test, `TestIterSectionBoundaries.test_finds_ordinary_unfenced_boundaries_with_correct_byte_offsets`,
already derives its expected offsets independently and fails at `:241` under the codepoint
defect (expected first-section `end=33`, actual `26`) — so independent expectations were
not absent before this OBPI either.

**What the oracle demonstrably adds, and nothing beyond it:**

1. **An ABSOLUTE expectation** where the neighbouring assertions state relative ones. An
   agreement or contiguity check says two computations match, or that spans tile without a
   gap; neither says the offsets are the CONTRACT'S offsets. Rows 15 and 17 fire on
   literals for that reason.
2. **Fixture coverage the pre-existing independent test does not reach** — a fenced heading
   that must contribute no section, combined with a multibyte character in the same
   document. **Coverage only; no added comparison strength.** Round 9 established that
   `TestIterSectionBoundaries` already compares BOTH sections' complete `SectionBoundary`
   values (identity, level, and both offsets) — observed expectations
   `[('caf-n-c-d', 0, 33), ('second', 33, 52)]` — so the earlier claim that this class
   upgrades *"one boundary pair"* to a complete identity→offset mapping was FALSE and is
   withdrawn. A dictionary representation of the same comparison adds no semantic coverage.
3. **Sensitivity to post-validation serialization corruption** (row 18), stated as
   sensitivity and NOT as exclusive detection.

No claim of uniqueness or of competing-check blindness survives anywhere in this section;
round 8 audited all 18 rows, the Gate 2 record, Value Narrative, Key Proof, rounds 1-7 and
Tracked Defects and found no further instance of the class.

Control rows 15-18 pin this, with the scope above and no wider claim. The claim is refuted by this OBPI's own evidence, not merely
retracted in prose.

**Disposition of the remaining limitations — environment, not defect, and each justified
under the governing skill:**

- **The mutation sweep is not executed by the adversary.** This is an ENVIRONMENT limitation
  of the tier-1 reviewer *and a sanctioned division of labour*, not an impossibility. The
  governing skill states it directly (`.claude/skills/gz-obpi-pipeline/SKILL.md`): *"the
  mutation sweep (which must edit a guard and restore it) and any negative control that
  mutates the tree are Step 4a's burden; Step 4b audits that record rather than reproducing
  it."* Rounds 4 and 5 each performed that audit, round 4 finding the record semantically
  sound and round 5 correctly faulting row 13. A prior revision of this brief called this
  *"irreducible"*, which overstated: it is reproducible by the operator from the table
  above, and the skill assigns the audit — not the re-execution — as the correct Step 4b
  treatment.
- **Disk-fixture tests error in the sandbox** (`No usable temporary directory found`).
  Environment limitation; the skill instructs the adversary to *"report it as a coverage
  limit, never as a defect."* Discharged by execution in writable CI — § Gate 2 below.

**Round 6 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-da4ad857527848f09d88932990096780`, `exit_status: 0`), tier 1,
scoped `--scope branch --base 04f18f0e` against revision `3738d606`. Dispatched to verify
closure of round 5's two EVIDENCE findings and to adversarially assess the
contract-derived oracle.

- **Finding A (dangling Windows citation) — CLOSED.** *"Gate 2 now identifies concrete
  Windows executions, including revision 53b6b0f6, run 34177044358, job 101908408526,
  Windows Server 2025, the job window, and named checks. The generic windows-latest wording
  survives only as explicitly rejected history."*
- **Finding B (row 13 did not isolate) — CLOSED.** It confirmed by reading that for the
  row-14 mutation *"the owned-body slice, contiguity, and final-length assertions pass;
  line 478 is the first failing assertion"*, and that row 13 instead fails at line 446 —
  *"so the correction to round 5 is right."*
- It independently answered the oracle questions: the literals are **arithmetically
  correct** (`4+6+4+8+4+5+2` ⇒ `a=[0,26)`, `b=[26,33)`, total 33); the oracle is genuinely
  independent (*"Fixture setup uses production measurement for the ownership floor, but
  does not derive the expected mapping from it"*); no false-positive risk on this fixed
  fixture; and *"The withdrawn second-parser claim is correctly withdrawn."* It also
  confirmed the Step-4a/4b sweep division *"is justified; it does not excuse misattributing
  a mutation kill."*

**It found one new `[medium]` and one factual error, both in THIS OBPI's evidence:**

1. `[medium]` **Row 16's kill was misattributed.** The table credited the persisted contract
   oracle; the fence-disabled defect actually fails at `:541`, because `load_declaration`
   refuses the undeclared `fake` section before generation or persistence. *"Thus the
   reported FAIL is credible, but its attribution does not establish the incremental
   persisted-oracle strength… This is missing proof, not a demonstrated implementation
   defect."* Correctly classified as MISSING PROOF, not a defect. Closed by recording row
   16's actual first failing assertion and by adding row 18 to its recommendation — a
   same-roster, contiguous, constant-width shift that permits declaration validation and
   persistence and fires at `:552` on the literals.
2. **Row 14's fixture is 95 B, not the 58 B recorded.** The 58 B figure measured a
   hand-typed snippet rather than `_GEN_PRIOR_TEXT`. The constant-length property holds
   (95 → 95, which round 6 verified); the number was wrong. Corrected above.
3. It further observed that the original blindness demonstration proved less than claimed —
   *"The two older agreement fixtures contain no fences, explaining their predicted survival
   without demonstrating two incorrect parses agreeing."* Verified: that fixture carries no
   fence and no multibyte character, so the defect could not act on it. The demonstration is
   re-measured on the oracle fixture above, where two walks of the defective parser agree on
   the wrong roster `['a','b','fake']` while the literals expect `['a','b']`.

**Round 6 is therefore NOT recorded as clean either.** Its `[medium]` and its factual
correction were repaired after it reviewed, so no independent round has yet seen rows 17-18,
the corrected attribution table, or the re-measured demonstration. Round 7 exists for that.

**Round 7 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-ad3c9965e26243a0a1f8e232dab5fa1c`, `exit_status: 0`), tier 1,
scoped `--scope branch --base 3738d606` against revision `fc3b51b8`.

- **Item 1 (row 16 misattribution) — CLOSED.** It traced the assertion order and confirmed
  row 18 satisfies the shape it had itself recommended: *"Row 18 changes serialized lineage
  after in-memory validation: roster unchanged, adjacent spans contiguous, summed widths 33
  … assertions :509, :541, :550 and :551 pass; :552 is the first failing assertion."*
- **Item 2 (95 B vs 58 B) — CLOSED.** *"Measured `_GEN_PRIOR_TEXT` and generated candidate
  are both 95 B… The remaining '58 B' mentions explicitly describe the withdrawn error, not
  current measurements."*
- **Item 3 (blindness demonstration) — NOT CLOSED, and now WITHDRAWN rather than repaired
  a third time.** *"Two defective walks do agree incorrectly, but that weaker comparison
  does not establish that chunk-accumulated lineage agrees with a parser re-walk."* Its
  probe settled it: *"two parser walks agreed, but the actual generator refused b's claimed
  (25,32) versus reparsed (25,31)."* The production agreement check is **not** blind to
  parser defects. The claim is withdrawn; § Falsifiability now states the oracle's two
  demonstrated values instead, neither of which needs it.
- It also caught a third mis-pairing: *"row 17 quotes the width-test failure while naming
  the identity/offset test."* Verified. **The correction was recorded as complete before it
  was** — round 8 found the prose fixed but the control-table cell still carrying the wrong
  message and an exclusivity claim. Both are now corrected; the premature claim is left
  standing here as the record of it.
- *"No implementation DEFECT was demonstrated within the unchanged boundary."*

**The repeating root is in this agent's evidence discipline, and is named here rather than
patched a fourth time.** Rounds 5, 6 and 7 each found the same class: a claim of the form
*"defect X was caught by mechanism Y"* written without observing Y — row 13's killer
(round 5), row 16's killer and the 58 B figure and the artefact demonstration (round 6),
row 17's quoted message and the parser-self-agreement substitution (round 7). None was an
implementation defect; every one was an unobserved mechanism attribution in the prose. The
sweep's own `failing=[…]` list and `failure_class` are observed output and were never
wrong — the gap was between what the tool measured and what the prose asserted about it.
**Standing discipline for this brief: any sentence naming the mechanism that produced an
observed result must quote the captured line number and assertion message, or must not name
a mechanism at all.**

**Round 8 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-9668c407b8b346c283f31cdf90fbe112`, `exit_status: 0`), tier 1,
scoped `--scope branch --base fc3b51b8` against revision `1b66a328`. Dispatched to verify
round 7's open item AND to sweep the whole evidence surface for the defect CLASS named
above, rather than accept this agent's assurance that the instances were all found.

**Item 3 — still NOT CLOSED, with three `[medium]` MISSING PROOF findings.** All three are
verified here and repaired; none is an implementation defect
(*"No implementation DEFECT demonstrated within the unchanged GHI #983 boundary"*).

1. **The replacement framing overclaimed too.** *"only witness for persisted-artifact
   divergence"* and *"invisible to every agreement check"* are false. Verified: row 18's
   serialization shift is caught at `test_content_compose.py:457` by the sibling test's
   contiguity assertion — `AssertionError: 1 != 0 : span (1, 47) does not resume at byte 0`.
   Row 18 shows the literal assertion's SENSITIVITY, not exclusive detection. Withdrawn to
   round 8's own recommendation.
2. **Row 17's table cell still quoted the wrong assertion**, and still claimed *"only the
   contract literals can catch it"*. The round-7 record had already called this corrected —
   the prose was, the cell was not. Both fixed; the premature claim is left standing in the
   round-7 entry as the record of it.
3. **The test docstrings retained the withdrawn blanket claim.** Verified that the
   pre-existing `TestIterSectionBoundaries.test_finds_ordinary_unfenced_boundaries_with_correct_byte_offsets`
   already derives expectations independently and fails at `:241` under the codepoint defect
   (`end=26` against an expected `33`) — so *"every other boundary/lineage assertion
   compares one parser run against another"* was false. Both oracle docstrings now state
   scope accurately: what they add is fixture coverage and an absolute expectation, never
   uniqueness.

**Class audit result, which is the substance of this round.** Round 8 audited *"all 18
control rows against the recorded sweep and relevant assertions; Gate 2 Windows records and
captured logs; Value Narrative and Key Proof in the Stage 4a packet; rounds 1-7 receipts;
and Tracked Defects"* and reported **no additional surviving class instance beyond those
three**. It independently reproduced the live figures (31,244 B vs 47,851 B, deterministic,
exact carried bytes, 354→354 accounting), GHI #983's 10/12 incomplete sections, and the
60 successful checks in the captured Windows log; and confirmed exactly one standing-verdict
declaration retaining the attestation prohibition, with rounds 5, 6 and 7 nowhere described
as clean.

Its Weakest point — *"a scoped assertion kill is still being promoted into an unmeasured
claim that competing checks cannot detect the defect"* — is the exact residue these three
repairs remove.

**Round 9 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-8552aa57cf4b470a9c7b4cb0e99b3619`, `exit_status: 0`), tier 1,
scoped `--scope branch --base 1b66a328` against revision `ba997aae`, with the audit
re-run from scratch rather than inheriting round 8's sweep.

- **Finding 1 (exclusivity claims) — CLOSED.**
- **Finding 2 (row 17 cell + premature correction disclosure) — CLOSED**, *"including both
  message pairings and the premature-correction disclosure."*
- **Finding 3 — NOT CLOSED.** The blanket claim was withdrawn, but *"its replacement
  overstates incremental coverage."*

`[medium]` **The replacement coverage claim understated the pre-existing test.** This brief
said the oracle asserts *"a complete identity→offset mapping rather than one boundary
pair."* Verified false: `TestIterSectionBoundaries` compares the entire list of two
`SectionBoundary` objects — identity, level and BOTH offsets — observed expectations
`[('caf-n-c-d', 0, 33), ('second', 33, 52)]`. *"A dictionary representation adds no
corresponding semantic coverage."* Corrected: the combined fenced-heading/multibyte fixture
is demonstrated added COVERAGE; the comparison-strength claim is withdrawn.

**Two further items it surfaced, both repaired:**

- **A tautological assertion of this agent's own authorship.** `assertEqual(broken_ids,
  broken_ids)` — a value compared to itself, which cannot fail. Round 9: *":401 remains a
  tautological self-comparison."* Removed; the two assertions that CAN fail remain. That
  this brief argued for falsifiable negative controls while carrying an unfalsifiable
  assertion is the sharpest instance of the class named above.
- **Line numbers drifted under this brief's own edits.** Round 9 measured row 17's messages
  at `:372`/`:378` and row 18's literal failure at `:563`, where the brief recorded
  `:367`/`:373` and `:552`. The figures were correct when captured and went stale as the
  files grew. **The remedy recorded here at round 9 — "citations are now anchored to the
  revision they were measured at" — was applied to the PROSE and never to the TABLE CELLS,
  which kept bare numbers. Round 15 found the same drift again, and by then the numbers had
  moved a second time: round 9's `:372`/`:378` measure `:376`/`:382` on 2026-09-08. Repaired
  at the class this time, not the instance — the affected cells now cite the ASSERTION's
  identity ("the CLI exit-code assertion", "the contract-literal span assertion", "the
  `measure_section_spans` assertion"), which does not drift when a file grows. Bare line
  numbers are not reintroduced into the cells. Historical round narratives below keep their
  numbers as recorded; they are the record of what was measured then, not current claims.**

**Its fresh audit** covered *"all 18 control rows and recorded sweep results, relevant
assertions, both changed docstrings, renamed test, three oracle-value claims, round records,
Gate 2 captured Windows evidence, Stage 4a Value Narrative/Key Proof, and Tracked
Defects"*, reporting *"no additional material class instance found beyond the two locations
reported."* It reproduced row 13's failure at `:446`, row 14's at `:478` with 95→95 bytes,
row 18's sibling failure at `:457` and literal failure at `:563`, confirmed
*"the round-8 account accurately records its three findings"*, one standing-verdict
declaration retaining the prohibition, and no round described as clean. Claims 1 and 3 of
the oracle's value are *"supported"*.

**Round 10 — `NOT-CORROBORATED | refuted`** (receipt
`arb-step-codexadversary-91a708dd68f046c6aadc6b29ded41d84`, `exit_status: 0`, 320,534 ms),
tier 1, scoped `--scope branch --base ba997aae` against `1cef5d80` plus this session's
uncommitted evidence repairs. **This is the first round 10 that ever ran.** A prior session
recorded at 2026-09-08T02:51:42Z that it had *"asked round 10 to re-audit from scratch"* and
exited 50 seconds later; a round takes ~305 s, and no receipt, output or process existed.

Dispatched to verify four evidence repairs (A: row 14's exclusivity scoping; B: the
18/18-versus-12/12 reconciliation; C: the reproducible-versus-prose-only row partition;
D: the `:516` shared-parser bound) AND to re-derive the assertion population independently.

**Repairs A–D: SUPPORTED.** Its pasted output confirms `TABLE rows= 18 TRANSCRIPT rows= 18`,
`exact_find_replace_rows= [1, 3, 4, 5, 6, 7, 9, 10]`,
`prose_only_rows= [2, 8, 11, 12, 13, 14, 15, 16, 17, 18]`, `_GEN_PRIOR_TEXT bytes= 95`, and
assertion lines `[433, 446, 457, 461, 478]` — adding that an exit-code assertion at `:433`
also precedes `:478`, which the row-14 cell had not named. It records that *"the revised
wording makes no outside-test exclusivity claim"* and that D *"is accurate."*

**`[medium]` REFUTATION — the repair pass introduced a new incorrect claim, which is the
defect this round existed to catch.** The Stage 4a packet claimed **144** added assertions
and attributed the literal `len(b"Emitted body.")` comparison to `:940`. Two independent AST
counts returned **145** (composer 64, lineage 13, ownership 33, command 35; and 489−344=145),
and the literal comparison is at **`:939`** — `:940` compares two production values.
Verified locally and accepted in full: the miscount was a name whitelist that silently
omitted `self.assertIsInstance` at `test_composer.py:621`, and the prior class counts
(84+29+17=130) did not sum to their own stated total because census and classifier used
different name sets. The packet's audit section was regenerated from one definition with a
line-level inventory. Its further note that `:1055` *"checks containment inside a
parser-derived expected slice"* is also accepted; the "independently validates its fixture"
wording is withdrawn.

**Positive demonstration, which this round did supply:**
`LIVE bytes= 31244 prior_bytes= 47851 sections= 22 owned= 12`,
`deterministic=True independent_live_spans=True unowned_verbatim=True exact_owned_ids=True
invariant_floor=True explicit_compatible=True`, `accounting= 354 354`, and both off-route
consumers refused. `Ran 27 tests ... OK` on the ownership and lineage classes. No new
production defect was demonstrated.

**Its Weakest point, recorded unmodified:** it could not execute the mutation sweep, confirm
the historical assertion kills, exercise persisted-file or native-Windows behavior, or
corroborate the full-suite and classifier totals; *"Ten mutation rows lack exact replacement
strings. A–D repair the record's wording; they do not supply those missing execution
witnesses."* The 50 `FileNotFoundError: No usable temporary directory found` errors are the
documented read-only sandbox limit, not defects.

**Consequence: the standing verdict above is `refuted` until a further round clears it.**
Round 11 is dispatched against the corrected packet.

**Round 11 — `NOT-CORROBORATED | refuted`** (receipt
`arb-step-codexadversary-9fba791f7d384a489cb998e2a965d7ef`, `exit_status: 0`, 260,678 ms),
tier 1, focused closure review of round 10's finding, scoped `--scope branch --base 1cef5d80`
against the working tree.

**Round 10's principal corrections VERIFIED CLOSED.** Its pasted output confirms the census
(`TOTAL 145`, per-file `64/13/33/35`, cross-check `489 - 344 = 145`), that the stated
definition is *"clear and reproducible"*, and `CHECK 621 added=True self.assertIsInstance`,
`CHECK 939 ... len(b'Emitted body.')`, `CHECK 940 ... assertGreater`. Brief check:
`STANDING COUNT 1` (the one declaration line, reading `refuted`), `ROUND10 RECEIPT PRESENT True`.

**`[medium]` REFUTED AGAIN, on the same root: classifier output published as verified fact.**
Three instances, all accepted and verified locally:

1. The packet said *"All 17 CODE-VS-CODE assertions"* and **enumerated 16** — `:883` was
   dropped from the prose while present in the inventory.
2. `:1055` was described as a containment check; **containment is at `:1051`**. This is the
   same misattribution class as `:939`/`:940`, committed one paragraph after correcting it.
3. `test_ownership.py:241` was filed under the shared-parser bound; its **offsets are
   independently fixture-derived** and only its expected identity uses `section_id()`. This
   agent had stated that correctly earlier in the same session and then wrote it wrongly.

It further established that the `103/17/25` totals rest on an unspecified heuristic and do
not reproduce (its own tracing gives `ANCHORED=121 CODE_OR_MIXED=20 FIXTURE_ONLY=4`), that
the 25 rows labelled LITERAL-ONLY are in fact production-derived refusal messages, and that
`:457`'s contiguity check is anchored only on its first iteration.

**Structural response — a method change, NOT a claim that the class is eliminated.**
Operator ruling 2026-09-08, verbatim: *"tool-generated evidence does not make false claims
structurally impossible. A command can faithfully reproduce a tautology or measure the wrong
thing. Interpretation still needs independent review."* An earlier revision of this record
claimed the defect class had been removed; **that claim is WITHDRAWN as untested.** What
changed is that the measuring method is now disclosed and the raw inventory published, so
Step 4b can fault the method itself. The packet
classifier totals ONLY alongside the executable classifier and per-row class assignments that support them (the intermediate revision that removed totals entirely was an over-correction, reversed under the operator ruling of 2026-09-08: *"Do not prohibit numbers or classifications merely because they appear in analysis"*). The complete 145-row inventory is published as a reviewable artifact
(`.gzkit/evidence/OBPI-0.35.0-05-assertion-inventory.txt`), which since round 12 carries a
per-row class assignment produced by the published classifier
`.gzkit/evidence/OBPI-0.35.0-05-assertion-audit.py`. The census is the single count claim,
and every per-assertion statement is one read individually, with
`:241`, `:1051`/`:1055` and `:457` corrected per this round.

**Regression check clean:** `LIVE bytes=31244 prior_bytes=47851 sections=22 owned=12`,
`deterministic=True ... invariant_floor=True`, `accounting=354 354`, both off-route consumers
refused, `Ran 27 tests in 0.000s — OK`. **No production defect has been demonstrated in any
round from 8 through 11.**

**Its Weakest point, recorded unmodified:** *"This confirms the live read-only path and
focused tests, not persisted-file/native-Windows behavior, historical mutation kills or the
full suite. The original classifier and complete generated inventory were unavailable."*

**DISPATCHING STOPS HERE.** Rounds 10 and 11 name the SAME root at different surfaces — an
agent publishing its own unverified analysis as evidence. Per `gz-obpi-pipeline` § *"When a
round repeats the prior round's ROOT, stop dispatching and escalate the DESIGN"* (operator
ruling 2026-09-03), the next move is an operator ruling, not round 12. The standing verdict
remains `refuted`.

**Round 12 — `NOT-CORROBORATED | refuted`** (receipt
`arb-step-codexadversary-3e166363a03243adb5fc29f6d71bd7db`, `exit_status: 0`, 341,798 ms),
tier 1, dispatched under the operator ruling of 2026-09-08 that Step 4b must judge *"whether
the measuring method itself is sound"* — with `docs/governance/evidence-record-contract.md`
as its PRIMARY target, because claims about a remedy are the category this agent had already
got wrong twice.

**Finding 1 `[medium]` — the remedy-effectiveness overclaim recurred inside the document
written to stop it.** Having withdrawn *"structurally impossible"*, the contract then
asserted it *"reduces the rate of unverified claims reaching attestation"* with no rate
measured. Round 12 also established that the prevention table conflated **automatic
enforcement** with **compliant authoring**: *"'Prevents none' is defensible only as
'automatically prevents none'."* Both accepted. The table is now a three-way split
(auto-enforced / excluded by compliant authoring / retrospectively detectable) — auto-enforced
is **No** for all five, three are excluded by compliant authoring, one partially, one not at
all — and effectiveness is recorded as an UNTESTED HYPOTHESIS.

**Finding 2 `[medium]` — classifications were published without their measuring artifacts.**
The inventory carried no per-row classes, no executable classifier existed, and the census
and tautology scan had no published programs. Round 12 further found **six inventory rows
silently truncated at 150 characters** (`test_composer.py:878`, `test_ownership.py:241`,
`test_content_compose.py:446/:461/:478/:563`). All accepted and repaired:
`.gzkit/evidence/OBPI-0.35.0-05-assertion-audit.py` is now published as the executable
measurer, its captured output carries per-row class assignments and complete untruncated
source, and the packet cites both. Round 12 also correctly faulted the contract's claim that
R2 was *"unsatisfiable"* without a new template column — the existing `Proof` fields can
carry it; the amendment is to prompt it structurally. That claim is softened.

**Verification note on this agent's own checking.** The truncation check this agent ran used
`awk`, which counts BYTES; `test_ownership.py:241` is 150 characters but 164 bytes, so the
agent's own verification found five of the six. Round 12's count was right. Recorded because
it is the same class as the findings themselves — an unsound measuring method producing a
confident number.

**Post-round-12 defect in the published measurer itself, caught by the turn-end lint gate.**
`.gzkit/evidence/OBPI-0.35.0-05-assertion-audit.py` shipped with `BLE001` (blind
`except Exception`) and **`B023` — a closure over the loop-rebound `prod`/`tainted` symbol
tables**. B023 is a latent correctness hazard in the very tool whose soundness the packet
asks a reviewer to judge: had classification been deferred rather than evaluated in-iteration,
rows would have been classified against another file's symbol table. Both fixed; `prod` and
`tainted` are now bound as explicit defaults. `uv run ruff check` on the file exits 0, and the
regenerated inventory is **byte-identical** (sha256 `1ac10ea0254272fe9134ddb92a3b8a3814044e93eedf9a3a3b33a70b39afabfb`
unchanged AS AT ROUND 12; the inventory has been regenerated twice since — see rounds 13
and 14 for the current hash), so the fix is semantics-preserving on this input and round 12's and 13's readings
of the artifact stand. Recorded rather than silently repaired, because "the measuring tool had
a latent defect" is the finding class this OBPI is being held on.

**Confirmed by round 12:** both prior withdrawals landed (`PACKET 129`, `BRIEF 1012`); census
`TOTAL 145` with `489 - 344 = 145`; `INVENTORY_ROWS 145 unique_locations 145;
missing_locations []; extra_locations []; metadata_or_source_mismatches []`; sha256 match;
`syntactic_self_comparisons []`; and it judged the semantic-falsifiability disclaimer
*"adequately limits this narrow claim."*

**Regression clean:** `LIVE bytes=31244 prior_bytes=47851 sections=22 owned=12`,
`deterministic=True ... invariant_floor=True`, `accounting= 354 354`, both off-route consumers
refused, `Ran 27 tests in 0.000s — OK`. **No production defect has been demonstrated in any
round from 8 through 12.**

**Its Weakest point, recorded unmodified:** *"The remedy still relies on prose to connect a
measurement method to its claimed benefit. Publishing a reproducible count establishes the
count under that method; neither a caveat nor earlier successful reviews establishes that the
method supports the intended acceptance claim."*

The standing verdict remains `refuted`.

**Round 13 — `NOT-CORROBORATED | refuted`** (receipt
`arb-step-codexadversary-e6e7f2f6b4ab44dd960f94e1c87806e7`, `exit_status: 0`, 278,812 ms),
tier 1, focused closure review of round 12's two findings.

**Round 12 F1 — CLOSED. The first genuine closure in this sequence.** Verbatim: automatic
enforcement is *"correctly No throughout"*, the compliant-authoring dispositions are
*"No/Yes/Yes/Partial/Yes-for-disclosure"*, retrospective detections are *"explicitly
historical"*, and — the check this round most needed to make — **"No surviving sentence
asserting an unmeasured remedy benefit found."** R2's softening *"matches the existing Proof
fields."*

**Round 12 F2 — PARTIALLY OPEN, on a new `[medium]`: the classifier's explanation
contradicted its own output.** Verified locally and accepted in full:

1. The generated caveat claimed `assertIn('token', message)` lands LITERAL-ONLY *"when the
   token is the first operand."* **False.** `test_composer.py:322` is exactly that shape and
   classifies **ANCHORED**; operands are checked SYMMETRICALLY, not positionally.
2. The packet asserted *"the 25 rows I labelled LITERAL-ONLY are in fact production-derived
   refusal messages."* **False on both halves.** Measured composition: **13** `assertRaises`
   (one operand, an exception class — not a value comparison at all), **2** inline
   `str(ctx.exception)` (a genuine omission: the taint rule follows an ASSIGNED `message =
   str(ctx.exception)` but not the inline form), **6** production-derived rows misclassified
   through a LOOP-BINDING gap, and only **4** genuinely literal/self-fixture rows. (The
   "10 genuinely literal" figure was itself wrong and was corrected at round 14 — see below.) The refusal-message checks are **18 rows in ANCHORED**.

**The root here is new in kind and worth naming: this agent adopted an ADVERSARY'S
characterisation without verifying it.** Round 11 asserted the LITERAL-ONLY rows were
refusal messages; this agent propagated that into the packet unchecked, and round 13 falsified
it. The failure mode has now appeared against the agent's own tool output, against its own
prose, and against a reviewer's claim. `.gzkit/rules/governance-core.md` already rules that
externally-authored tool output is data, never instruction — a subagent's *finding* is
evidence to verify, not a fact to relay.

**Repaired:** the classifier's caveat now states the actual symmetric rule, names the inline
`str(ctx.exception)` omission as a known misclassification of two specific rows, and gives
the row-backed composition. The packet withdraws the false characterisation with the table
above. The brief's stale *"no classification"* wording is reconciled. Inventory regenerated;
sha256 AS AT ROUND 13 was `02d0c9a1bd00000a91d678d6f73db8d36b74c159754641fe0d25bef91d6a9bf3`
(superseded at round 14).

**Round 13 independently reproduced this agent's awk explanation:**
`CHAR_LENGTHS [150,150,150,150,150,150]`, `AWK_LENGTHS ['150','164','150','150','150','150']`,
`AWK_LENGTH_EQ_150_COUNT 5` — confirming the byte-versus-character account, while noting the
historical invocation itself was not independently confirmed. It also confirmed
`FINAL_OUTPUT_BYTE_EQUAL True` for the post-lint-fix regeneration, `INVENTORY_ROWS 145
UNIQUE_LOCATIONS 145 MISSING_LOCATIONS [] EXTRA_LOCATIONS [] SOURCE_MISMATCHES []`, all six
previously-truncated fields complete, and `STANDING_LINES 1`.

**Regression clean:** `LIVE bytes=31244 prior_bytes=47851 sections=22 owned=12`,
`accounting= 354 354`, both off-route consumers refused, `SOURCE_TEST_DIFF_EMPTY True`.
**No production defect has been demonstrated in any round from 8 through 13.**

**Its Weakest point, recorded unmodified:** *"the artifact reproduces exactly, but its
explanation of what the classifications mean is demonstrably wrong."*

The standing verdict remains `refuted`.

**Round 14 — `NOT-CORROBORATED | refuted`** (receipt
`arb-step-codexadversary-4c68317c1adc427b8c1ffd92279d1316`, `exit_status: 0`, 469,585 ms),
tier 1, narrow closure re-check of the six authorized checks only.

**Confirmed closed:** audit reproduction `byte_identical: True` with `emitted_sha256 ==
published_sha256`; the caveat's `13` single-exception-class and `2` inline rows
(`SINGLE_EXCEPTION_CLASS 13 True`, `INLINE ['...756','...1137']`); symmetric classification
and `:322`; `ANCHORED_REFUSAL 18`; no stale sha in the packet; `STANDING_LINES
['**Standing verdict:** refuted']`, round 13's receipt and Weakest point preserved, stale
wording reconciled; and — the check that most needed making — *"No new unmeasured-benefit
claim found."* Regression clean (`Ran 33 tests ... OK`).

**`[medium]` STILL OPEN: the corrected composition was itself wrong.** The repair for round
13 asserted *"10 genuinely literal or self-fixture comparisons."* Verified false: **only 4
qualify** (`test_ownership.py:369/:408/:409`, `test_content_compose.py:520`). **Six inspect
production-derived values** — `test_composer.py:621/:622` iterate
`result.lineage.sections.values()`; `test_content_compose.py:289/:290/:291` iterate the
generated lineage JSON; `:457` compares spans drawn from it.

**Root cause located in the classifier and confirmed by reading it:** the taint rule walks
`ast.Assign` only (`assertion-audit.py:97`) and never `ast.For`, so a for-target bound from
production output is not tainted. **8 of the 25 LITERAL-ONLY rows are therefore known
misclassifications** (2 inline exception + 6 loop-binding).

**Repaired in all three surfaces round 14 named** — the emitted caveat, the packet table, and
this brief — with the 6 and the 4 enumerated by file and line, and the loop-binding gap named
as the cause. The totals are published WITH their known errors stated rather than silently
adjusted; round 14 confirmed *"No classifier redesign is required for this explanation-only
closure."* Inventory regenerated; sha256
`0e9e04a087db7d5316262a7a7bd075b2ea175de6fc8e0f5f7a7d69cb28cf4ed4`.

**Verification discipline note.** Round 13 had just faulted this agent for relaying a
reviewer's characterisation unchecked. Round 14's *"only four qualify"* was therefore
verified against source before adoption — `broken_ids` at `:408`/`:409` is a TEST-LOCAL
fence-blind re-derivation (the site of round 9's removed tautology), not production output,
so those rows do qualify. The claim held.

**Its Weakest point, recorded unmodified:** *"exact reproduction still reproduces a false
interpretation. Persisted-file/native-Windows behavior, historical mutation kills, and the
full suite were not re-confirmed in this narrow read-only review."*

The standing verdict remains `refuted`.

#### Round 15 repair pass — the ten findings of the § 9 independent review

The two read-only reviewers dispatched against the corrected argument returned ten open
findings, carried as items 7-16 of
`.gzkit/evidence/OBPI-0.35.0-05-corpus-candidate-generator.stage4a.md` § 7 and recorded
there **unrepaired**, because repairing a test or a production writer is OBPI
implementation work that only the operator initiates. The operator initiated it on
2026-09-08. Every finding below was re-established from source before it was acted on —
none was adopted on the reviewer's characterisation, per round 13's lesson.

Dispatch: implementer + spec-reviewer + quality-reviewer, recorded via `gz obpi dispatch`.

| # | Finding | Disposition |
|---|---|---|
| 7 | REQ-02's carried-forward bytes and boundaries have no check independent of the lineage | **Repaired.** Confirmed: the contiguity loop anchors only its first iteration and its final length; every internal boundary is lineage-vs-lineage, and the literal-anchored sibling marks BOTH sections `unowned`, so the mixed shape the generator actually produces had no contract-derived check. Added `test_mixed_owned_unowned_candidate_matches_contract_derived_literals` holding the PERSISTED candidate's bytes, the carried-forward slice and both spans to hand-derived literals (95 B; `[0, 46)` / `[46, 95)`), deriving nothing from `iter_section_boundaries` or from `prior_bytes` |
| 8 | REQ-05-07's guard cannot fire through the generator | **Confirmed, NOT repaired — escalated.** `section_entries` is a filtered subset of `effective.entries` deduplicated by `id`, while `compressible_bytes_before` sums every effective compressible entry, so `after <= before` is a structural invariant of the generated path. The covering test reaches the guard only by passing a `foreign_entry` absent from the corpus straight to the private `_byte_evidence`. REQ-05-06's mandated emission attribution is WHAT MAKES REQ-05-07's "when the generator runs" antecedent vacuous — two acceptance criteria in tension, which is the operator's to rule on, not this agent's |
| 9 | The falsifiability table's line citations are stale | **Repaired at the class.** Confirmed exactly: `:541` is a fixture literal, `:552` is the exit-code assertion, the literals are at `:563`; `:367` is a `def` line and `:373` an assignment, with the assertions at `:376`/`:382`. Round 9 had already reported this drift and recorded a remedy that was applied to the prose and never to the cells — and the numbers had drifted AGAIN since (round 9's `:372`/`:378` measure `:376`/`:382` today). The cells now cite the ASSERTION's identity instead of a bare number |
| 10 | `test_contract_literals_reject_a_roster_a_fence_blind_parser_would_produce` exercises zero production code | **Repaired.** Confirmed: it derived `broken_ids` from a class constant and compared it against another class constant, calling nothing from `gzkit.content`. It now calls `iter_section_boundaries` and asserts the production roster differs from the fence-blind one and excludes the fenced heading. Proven by mutation: fence tracking disabled in `ownership.py` is now KILLED by this test, which the previous version could not have caught under any production change |
| 11 | Two assertions dominated by a production guard | **Repaired.** Confirmed: `generate_candidate` cannot return without passing `_refuse_generated_lineage_drift`, which computes the identical section-id->span mapping and raises, nor without `assert_complete_partition`. Replaced with hand-derived literal assertions (owned chunk 50 B, candidate 99 B) that fail on a change the guards accept |
| 12 | `assertIsInstance(byte_span, tuple)` / `len(byte_span) == 2` on a Pydantic `tuple[int, int]` field | **Repaired.** Confirmed unconstructible otherwise (`frozen=True`, `extra="forbid"`, field validator). Both assertions deleted; the surrounding `owned` / `entry_ids` assertions stand. Not replaced with a reworded restatement of the type system |
| 13 | `expected` computed by the production expression | **Repaired.** Confirmed identical to `composer.py`'s own unowned-branch slice, with the boundary located by the same production parser. `expected` is now the contract literal `b"## Unowned Section\ncarried forward text verbatim\n"` (49 B), with the arithmetic spelled out |
| 14 | `lineage.py` persists via `write_text` where its sibling uses `write_bytes` | **Repaired.** Confirmed; `save_candidate_lineage` has exactly one production caller (`compose.py`), and `load_candidate_lineage` reads with `read_text`, whose universal-newline translation would MASK the difference on a round-trip — so the witness had to assert persisted bytes. Now `write_bytes`, guarded by a test that patches `Path.write_text` to raise (byte equality alone witnesses nothing on macOS, where the two are identical). **Scoped honestly:** no current consumer reads this file's bytes, so this is coupled-surface coherence (AGENTS.md § DO IT RIGHT 1a) plus REQ-05-08's "byte-identical lineage maps" wording, NOT a demonstrated live break. It carries weight because `.gzkit/renditions/**` IS byte-read (`invariant_coherence.py:28` `read_bytes()`; `rendition_freshness.py:99` fingerprints raw bytes) and OBPI-0.35.0-07 publishes this artifact |
| 15 | Stated-rationale contradiction in the generator | **Confirmed, NOT repaired — escalated.** `_refuse_unknown_section_addressing` refuses an undeclared-section entry because *"silently omitting the entry would drop it from both the candidate text and its lineage with no trace"*, yet a **compressible** entry addressed to a DECLARED-but-`unowned` section is dropped from both with no trace, is accepted, and counts toward `compressible_bytes_before` only — so a drop is reported as compression. Only the invariant tier is caught, by `assert_invariant_verbatim`. Whether that is a defect is a design question for the operator |
| 16 | Size guidance | **Re-grounded, NOT repaired — escalated.** The finding cited line counts from `.claude/rules/pythonic.md`; a value in a Markdown doc is illustrative, never authoritative (`governance-core.md`). Measured against the authoritative surface instead: `uv run gz complexity advise src/gzkit/content/composer.py` **exits 3**, with `generate_candidate` and `_byte_evidence` both `radon_cc 14.0` against a `block` band of 11.0 (`.gzkit/rules/complexity-thresholds.json`), archetype `arrowhead`. The signal discriminates — `rendition.py`, `corpus_store.py` and `commands/content/compose.py` each exit 0. It is UNGATED in practice: `gz complexity advise` is in neither `gz check` nor this brief's Verification list. Refactoring the deliverable versus recording an intrinsic-complexity attestation is the operator's routing call |

**Falsifiability, observed rather than asserted.** Each repaired test was run against a
mutation that VIOLATES the requirement it names, via `gzkit.mutation_witness.run_mutation_sweep`
(never a hand-rolled loop — `.gzkit/rules/tests.md` § Mutation-sweep integrity). The
four-way verdict is reported, never a two-way one. `src/**` verified restored afterwards
(`git status --short -- src/gzkit/content/` shows only `lineage.py`, the intended change).

**Every mutation is given as an exact find/replace so any reader can re-run it** — the
defect standing finding 2 records against ten of the eighteen older rows (prose-only,
non-reproducible) is not repeated here.

```text
F7  test_mixed_owned_unowned_candidate_matches_contract_derived_literals
    src/gzkit/content/composer.py
    find:    "            chunk = prior_bytes[boundary.start : boundary.end]"
    replace: same line + '.replace(b"\n", b"\r\n")'
    killed=1 survived=0 invalid=0 inconclusive=0 conclusive=True

F13 test_unowned_section_bytes_are_byte_verbatim
    same file, same find/replace as F7, run against tests.content.test_composer alone
    killed=1 survived=0 invalid=0 inconclusive=0 conclusive=True

F10 test_contract_literals_reject_a_roster_a_fence_blind_parser_would_produce
    src/gzkit/content/ownership.py
    find:    "        elif (run := _fence_run(stripped)) is not None:"
    replace: same line + " and False:"  (keeps `run` bound; never opens a fence)
    killed=1 survived=0 invalid=0 inconclusive=0 conclusive=True

F11 test_ordinary_generation_is_still_accepted
    src/gzkit/content/composer.py
    find:    '            body = b"\n" + _join_section_body(section_entries) + b"\n" if section_entries else b""'
    replace: same line with the leading b"\n" widened to b"\n\n"
    killed=1 survived=0 invalid=0 inconclusive=0 conclusive=True
```

F7 and F13 share one mutation but were run as **separate sweeps against separate
selectors**, because a single sweep naming two expected tests reports one `killed` and does
not establish that both selectors fired — round 16 raised exactly that, and it was measured
rather than argued.

**Stage 3, re-run on the repaired tree (2026-09-08).** Full sweep `Ran 9971 tests ... OK
(skipped=4)`, receipt `arb-step-unittest-5907f04900b44224a0495004af5ff20b`; lint clean,
`arb-ruff-6610f5cf95494b2d886152a59d3b05da`; typecheck `All checks passed!`,
`arb-step-typecheck-cf0310a4f9e141e78c7715b273029064`; scoped behave 5 scenarios passed,
`arb-step-behave-3777c46bd5aa4b60b92872353c0af28d`; `mkdocs build --strict` clean,
`arb-step-mkdocs-40efd6c992e445f5bf871285caf44e3a`. `gz covers` reports
`behavior_uncovered_reqs: 0` (the one uncovered REQ is `REQ-0.35.0-05-10`,
STRUCTURAL-FENCE, which correctly carries no `@covers`). `gz validate --documents`,
`--req-kind-discipline`, `--invariant-coherence` and `--rendition-floor-coherence` each
exit 0.

**A finding raised in review and REJECTED on verification, recorded because rejecting it
silently is the same defect as adopting it silently.** The quality review raised a
`medium` that `advisor_qc.record_verdict` shares finding 14's `write_text` hazard and
carries "its own byte-identical-receipt REQ". Verified and **it does not hold**: the
canonical ARB receipt writer it mirrors (`src/gzkit/arb/step_reporter.py:46`) also uses
`write_text`; every ARB receipt reader is `json.loads(read_text(...))` with no byte
comparison and no hash of the file; and REQ-0.0.37-24-03 requires a deterministic receipt
**payload**, not byte-identical files. No GHI was filed. The sibling
`rendition_store.save_fingerprint` is a separate question owned by the LIVE brief
OBPI-0.35.0-07 (`Draft`), whose Discovery Checklist names `save_fingerprint` as the write
path being made atomic — routed to the operator, not resolved here.

**The standing verdict above is unchanged by this pass.** These repairs have not been seen
by any independent round; closure is demonstrated, never round-counted, and no agent's
confidence in its own repairs moves a verdict word.

**Round 16 — `CORROBORATED-WITH-CAVEATS | not-refuted`** (receipt
`arb-step-codexadversary-a4c38d459f084cd4a650129ce4a84ca2`, `exit_status: 0`), tier 1
(cross-vendor, Codex via the `codex-companion.mjs` plugin), dispatched as a FOCUSED CLOSURE
RE-CHECK of the ten findings only, with that boundary stated in the prompt and out-of-scope
findings forbidden.

**All ten dispositions corroborated**, verbatim highlights: finding 7 *"persisted candidate,
carried-forward slice, and both spans have independent literals: 95 bytes, [0,46), [46,95).
Reflow or corrupted persisted spans can fail these checks"*; finding 10 *"production
iter_section_boundaries is called. A fence-blind parser exposes fake and fails assertNotIn"*
— and it sharpened the claim: *"The preceding roster inequality alone is insufficient because
the test-local roster omits H1 headings"*; finding 11 *"Coherent changes to generated body
bytes can pass production consistency guards and fail this test"*; finding 14 *"Restoring the
old writer would trigger the patched exception."* The three deliberate non-repairs (8, 15, 16)
were each corroborated as justified. Round 16 recorded **"No material findings"** and
**"No additional production repair is requested by this review."**

**It also upheld the rejected finding, and corrected this agent's reasoning for it.** On
`advisor_qc`: *"The sibling writer alone would not justify rejection; the payload contract and
consumer behavior do."* Recorded because the conclusion was right for a partly wrong reason.

**Two caveats were actionable and were fixed, not disclosed.** (a) The record cited a sweep
script at a path that does not exist in the repository — *"scratchpad/sweep.py is absent"*.
The citation is removed and every mutation is now given inline as an exact find/replace.
(b) *"The combined F7+F13 count does not independently establish both selectors ran."*
Correct: one sweep naming two expected tests reports one `killed`. Re-run as two separate
sweeps against two separate selectors; both `killed=1 ... conclusive=True`, recorded above.

**Its remaining caveats are coverage limits of a read-only sandbox, recorded unrepaired
because they are honest bounds rather than defects:** fresh filesystem persistence and the
CLI fixture tests could not run (*"No usable temporary directory found"* — 115 errors of that
signature, which is the barrier and not a regression; the same suite runs
`Ran 9971 tests ... OK` on the host, receipt
`arb-step-unittest-5907f04900b44224a0495004af5ff20b`); native Windows execution of the
repaired writer was not exercised, its serializer check being mocked I/O; and the dirty-tree
diff cannot be pinned to the receipts beyond commit + `dirty: true`.

**Its Weakest point, recorded unmodified:** *"The implementation and test failure mechanisms
withstand this bounded review, and live generation works. Historical mutation provenance
remains weaker than the source-level closure argument. This verdict does not certify fresh
disk-writing execution or resolve the deliberately retained operator dispositions."*

**The standing declaration above is deliberately NOT changed by this round, and that is a
decision for the operator, not this agent.** Round 16's scope boundary excluded the subject
the standing `refuted` is about — the evidence record's commentary on the auxiliary assertion
classifier (see the SCOPE RULING above). A round that did not examine that thread cannot
discharge a refutation of it, and flipping the word on the strength of a differently-scoped
round is the verdict substitution this gate exists to catch. Discharging it needs either a
round scoped to include that thread, or the operator's ruling that the thread does not bear
on the verdict.


### Value Narrative

Before this OBPI the corpus materialized nothing. `composer.py` accepted `candidate_text`
from the agent and only validated it — its own docstring conceded *"the drop/combine/rewrite
judgment is the agent's"* (ADR-0.35.0 § Intent gap 1). Nothing derived AGENTS.md from the
corpus, and `ByteEvidence` reported `total_bytes - invariant_bytes` as "compression".

Now `gz content compose <surface> --consumer <vendor>` with no candidate materializes one:
owned sections generated from the EFFECTIVE corpus, unowned sections carried forward
byte-verbatim from the prior committed rendition, a per-consumer
`<consumer>.candidate.lineage.json` recording which is which as half-open UTF-8 spans forming
a disjoint complete partition, and byte accounting that attributes only entries actually
emitted and refuses rather than prints an inflated figure.

### Key Proof

```text
$ uv run gz content compose AGENTS.md --consumer root < /dev/null
Candidate: <project-root>/.gzkit/renditions/AGENTS.md/root.candidate.md
Lineage: <project-root>/.gzkit/renditions/AGENTS.md/root.candidate.lineage.json
Byte evidence (population): invariant=24350B compressible=354B→354B total=31244B setpoint=lite
Rendered bytes (assembled): emitted=24704B structural=535B carried=6005B total=31244B
                                                                        REAL EXIT: 0

$ uv run gz content compose AGENTS.md --consumer claude                 REAL EXIT: 1
Error: Surface 'AGENTS.md' (content type 'AgentContract') declares no route to consumer
'claude'; declared routes are ['root']. ...
```

Measured against the two persisted files, 2026-09-08: 22 sections, 12 owned / 10 unowned;
the lineage partition is contiguous from 0 with no gap or overlap and ends at exactly 31,244
bytes; all 10 unowned slices occur byte-verbatim in the committed prior rendition; all 71
live corpus entries are cited and **none of the 24 retired entries is cited anywhere**; two
consecutive runs produce byte-identical candidate and lineage. Full observed output:
`.gzkit/evidence/OBPI-0.35.0-05-corpus-candidate-generator.stage4a.md` § 6.

### Implementation Summary

- Files created/modified: `src/gzkit/content/composer.py` (generator + `ByteEvidence`
  correction), `src/gzkit/content/lineage.py` **created**, `src/gzkit/content/ownership.py`
  (shared fence-aware byte-boundary iterator), `src/gzkit/commands/content/compose.py` and
  `__init__.py` (generated-path routing), `docs/user/manpages/content.md`,
  `features/content_compose.feature` + steps.
- Tests added: `tests/content/test_composer.py`, `tests/content/test_lineage.py`,
  `tests/commands/test_content_compose.py` **created**; `tests/content/test_ownership.py`
  extended. Scoped suite observed 2026-09-08: `Ran 191 tests — OK (skipped=4)`, exit 0.
  Nine BEHAVIOR REQs carry `@covers`; `REQ-0.35.0-05-10` is STRUCTURAL-FENCE and correctly
  carries none. `gz validate --req-kind-discipline` exits 0.
- Date completed: **not completed** — Stage 5 not entered.
- Attestation status: **none solicited.** No completion receipt exists; the brief stays
  `Draft`/Active.
- Defects noted: GHI #983 (below) plus four items carried in the Stage 4a packet § 7 —
  10 of 18 mutation rows non-reproducible from the record; a stale illustrative figure in
  REQ-05-06 / Requirement 7 (22,378 cited, 6,894 measured today — binding clause unaffected);
  `.gitignore` asymmetry on the staged lineage sidecar; and two open classifier
  misclassification families that affect no requirement.

### Change Log

Substantive corrections and decisions taken inside this operator-initiated OBPI.
Finding identities are reused, never re-minted; the ledger records remain the
authority for proof, review, closure and readiness.

#### 2026-09-09 — rendered-byte accounting separated from corpus population totals

**Findings closed:** `ADV-OVERLAPPING-BYTE-ACCOUNTING` (REQ-0.35.0-05-06,
counterexample, high) and `ADV-INFLATION-CONTROL-MASKED` (REQ-0.35.0-05-07,
missing-proof, medium). Both were raised by the tier-1 cross-vendor adversary in
receipt **`arb-step-codexadversary-a4e87abb4af74cb0a38de4106239a684`**
(`exit_status: 0`, verdict `NOT-CORROBORATED` / `refuted`, 2026-09-09T05:01:11Z).

**The receipt's review record could not be imported, and the findings stand
anyway.** `gz obpi acceptance ... review --receipt arb-step-codexadversary-a4e87abb…`
returned, verbatim:

> Acceptance blocked: Review describes stale file contents; re-review the current proof.

The adversary copied `input_digest` `5338bac8637d…` out of the status payload it
was handed, and `input_digest` hashes the executing environment alongside the
file roster (`acceptance_execution.input_digest`), so a review produced in the
Codex sandbox can never carry the orchestrator session's digest. The rejection is
about the RECORD's freshness, not the finding's truth: both counterexamples were
reproduced locally against contract-derived fixtures before any repair was made.
This is why the repair below was executed, and its proof regenerated, by a single
owner in one environment.

**What changed.** `ByteEvidence.structural_carried_bytes` was a rendered-byte
remainder, `total_bytes - invariant_bytes - compressible_bytes_after`, computed
from `invariant_bytes` — a POPULATION statistic summing every effective invariant
entry's text. Two distinct live invariant entries whose texts overlap in the
rendition are each counted in full there, so their sum legitimately exceeds the
span carrying both; the remainder went negative and
`_refuse_negative_structural_remainder` refused a valid candidate. The brief's
§ Generation and Accounting Contract had already ruled this out — entry-text
totals "remain separately labeled population statistics, never a claim of unique
rendered-byte coverage" — so this is a repair toward the approved contract, not
an amendment of it.

- `src/gzkit/content/rendition.py` — `structural_carried_bytes` removed;
  `emitted_entry_bytes`, `generated_structural_bytes` and `carried_forward_bytes`
  added (`int | None`, `None` on the explicit path, which assembles nothing);
  `rendered_bytes_total` property; `invariant_bytes` / `compressible_bytes_before`
  relabelled POPULATION on the model itself.
- `src/gzkit/content/composer.py` — `_refuse_negative_structural_remainder`
  deleted; `RenderedBytes` added; `_assemble_section` measures each section's
  three contributions as it builds the chunk; `generate_candidate` accumulates
  them and passes them to `_byte_evidence`. The reporting obligation is kept and
  widened, never dropped: structural and carried are now two measured figures
  where one derived figure stood.
- `src/gzkit/commands/content/compose.py` — two labelled lines,
  `Byte evidence (population):` and `Rendered bytes (assembled):`, the second
  printed only on the generated path.
- `docs/user/manpages/content.md` — § "Byte evidence: two measurements, never one".
- `tests/content/test_composer.py`, `tests/commands/test_content_compose.py` —
  contract-derived fixtures with hand-counted literals (below).

**Demonstrations (contract-derived, hand-counted — never re-derived from
production arithmetic):**

| Demonstration | Test | Observed |
|---|---|---|
| Overlapping invariant texts in valid carried-forward content are accepted | `TestOverlappingInvariantsInCarriedForwardAreAccepted` | population `invariant_bytes` 79 against `total_bytes` 64, accepted; rendered 0 + 9 + 55 = 64 |
| Structural/carried counts match independently calculated byte lengths | `TestRenderedByteContributionsAreMeasuredDuringAssembly` | emitted 9, structural 13, carried 24, total 46 |
| Explicit-candidate overlap is accepted | `TestByteEvidenceAccounting.test_overlapping_invariant_and_compressible_text_is_accepted` | invariant 22 + compressible-after 15 > total 22, accepted |
| Persisted candidate bytes and lineage boundaries remain correct | `test_generated_candidate_persists_the_bytes_its_lineage_indexes` | file 95 B; spans `[0, 46]` / `[46, 95]` slice to the persisted section bytes |
| Inflation control fails through its intended guard | `test_byte_evidence_raises_when_attributed_exceeds_before` | mutation `if False and bytes_after > bytes_before:` → `AssertionError: ValueError not raised` at the `assertRaises` line |

The last row is `ADV-INFLATION-CONTROL-MASKED`'s closure. The prior mutation
record killed on `assertIn('compressible_bytes_before', message)` because the
structural guard fired first and supplied a different diagnostic; removing that
guard removes the confound, and the control now fails through `assertRaises`
itself.

**Live-corpus effect.** The previously reported `structural=6540B` was the SUM of
two distinct quantities and reconciled only because gzkit's current corpus happens
to carry no overlapping invariant texts. Measured 2026-09-09, the two are now
reported apart: `structural=535B` (headings and separators) and `carried=6005B`
(unowned carry-forward), 535 + 6005 = 6540, with `emitted=24704B` completing a
partition that sums to `total=31244B`.

**Disclosure retained.** `composition_candidate_emitted_event` still carries the
original four byte fields, so the ledger event does not surface the rendered
partition; `src/gzkit/ledger_events.py` is outside this brief's Allowed Paths.
Tracked in `.gzkit/insights/agent-insights.jsonl`, scope
`content-compose-ledger-event`.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **GHI #983** — `section ownership: 10 of 12 corpus-owned sections carry no covering corpus content`. Surfaced by this OBPI's generator: materializing from the live corpus yields 31,244 B against the 47,851 B committed rendition, a −16,607 B delta (113 uncovered content lines, 16 H3+ structural lines) because 10 of 12 sections the declaration marks `corpus-owned` fail OBPI-04's own `section_coverage` completeness predicate — three of them at zero coverage. The 0-Kelvin invariant floor still passes on the generated candidate. Operator ruled 2026-09-07 that this OBPI's generator stays faithful to its brief (emits what the corpus carries; no new refusal surface) and that the finding routes to a GHI rather than widening this OBPI's scope. Not a defect of this OBPI's deliverable — a pre-existing declaration state this OBPI made measurable for the first time.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
