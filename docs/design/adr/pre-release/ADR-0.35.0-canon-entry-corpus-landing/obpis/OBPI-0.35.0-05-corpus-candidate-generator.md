---
id: OBPI-0.35.0-05-corpus-candidate-generator
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 5
lane: Heavy
status: Draft
allowlist:
- src/gzkit/content/composer.py
- src/gzkit/content/rendition.py
- src/gzkit/content/lineage.py
- src/gzkit/content/ownership.py
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
7. ALWAYS correct the `ByteEvidence` accounting. `composer.py:63-65` computes `compressible_bytes_after = total_bytes - invariant_bytes`, which on today's corpus reports 354 B -> 22,378 B: a 63x INFLATION labelled compression, and a witness that cannot fail. `compressible_bytes_after` MUST count only compressible-tier bytes actually present in the candidate.
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
- [ ] REQ-0.35.0-05-06 [behavior]: Given a candidate produced by the generator, when `ByteEvidence` is computed, then `compressible_bytes_after` counts only compressible-tier bytes present in the candidate and is less than or equal to `compressible_bytes_before` — never `total_bytes - invariant_bytes`, which on today's corpus yields 22,378 against an input of 354.
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

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
