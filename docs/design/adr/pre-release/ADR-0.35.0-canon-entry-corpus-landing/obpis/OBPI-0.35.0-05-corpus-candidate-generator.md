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
- src/gzkit/commands/content/compose.py
- tests/content/test_composer.py
- tests/content/test_lineage.py
- tests/commands/test_content_compose.py
- features/**
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

**Dependency order (ADR-0.35.0 § Scope Minimization):** 05 depends on 01 (effective corpus) and 04 (ownership declaration). Shipping 05 before 01-03 ships a REGRESSION BY CONSTRUCTION: the seven byte-identical duplicate groups are invisible today only because `rendition_floor_coherence.py:72` is a substring test, and they become literal double-emissions the instant a generator materializes (ADR § Alternatives H). 07 depends on 05.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/content/composer.py` — the corpus->candidate generator and the `ByteEvidence` correction
- `src/gzkit/content/rendition.py` — `ByteEvidence` field semantics, if the correction requires it
- `src/gzkit/content/lineage.py` — the `<consumer>.lineage.json` model and writer **CREATE**
- `src/gzkit/commands/content/compose.py` — route compose through the generator
- `tests/content/test_composer.py`, `tests/content/test_lineage.py`, `tests/commands/test_content_compose.py` — covering tests **CREATE**
- `features/**` — Gate 4 scenarios
- `docs/user/manpages/content.md` — updated `compose` contract and the lineage artifact
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-05-corpus-candidate-generator.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/content/rendition_store.py` — `RenditionProvenance` is frozen/`extra="forbid"` and written at COMMIT time; bolting the lineage map onto it is ADR § Alternatives O, rejected
- `src/gzkit/content/ownership.py` — the declaration and ratchet are OBPI-0.35.0-04 and are consumed read-only here
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
5. ALWAYS make `byte_span` PER-CONSUMER. The corpus is per-surface but renditions are per-(surface, consumer) at different setpoints; an owned section rendered at `lite` and at `heavy` is not the same bytes (`DESIGN_FORCING_FUNCTIONS.md` § 4).
6. NEVER store the lineage map inside `RenditionProvenance`. It is frozen/`extra="forbid"` and written at commit time; the lineage map is produced at generate time and is per-section, not per-artifact (ADR § Alternatives O).
7. ALWAYS correct the `ByteEvidence` accounting. `composer.py:63-65` computes `compressible_bytes_after = total_bytes - invariant_bytes`, which on today's corpus reports 354 B -> 22,378 B: a 63x INFLATION labelled compression, and a witness that cannot fail. `compressible_bytes_after` MUST count only compressible-tier bytes actually present in the candidate.
8. NEVER emit a byte accounting in which `compressible_bytes_after` exceeds `compressible_bytes_before`. Compression cannot add compressible bytes; if the computed value would exceed the input, that is a defect to fail on, not a number to print.
9. ALWAYS keep the generator deterministic — no LLM, no network, no clock. Determinism is load-bearing for OBPI-0.35.0-07's single-attestation-over-N-consumers ruling (ADR § Alternatives L).
10. NEVER emit two copies of a byte-identical invariant entry into one candidate, even if the corpus were to contain a live duplicate pair. This is the standing regression fence that OBPI-0.35.0-03 discharges for today's corpus.
11. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

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
- [ ] OBPI-0.35.0-03 landed: the eight duplicates retired, so materialization does not double-emit
- [ ] OBPI-0.35.0-04 landed: `.gzkit/ownership/AGENTS.md.json` declares every AGENTS.md section
- [ ] `src/gzkit/content/composer.py` and `src/gzkit/content/rendition.py` exist
- [ ] `.gzkit/renditions/AGENTS.md/root.md` (31,990 B) and `codex.md` (13,606 B) exist as the carry-forward and setpoint-delta reference artifacts

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/composer.py:24-31` and its docstring line 6 — the `candidate_text` parameter and the conceded agent judgment
- [ ] `src/gzkit/content/composer.py:59-65` — the raw-corpus read and the `total - invariant` arithmetic, both corrected here
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

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content compose AGENTS.md --consumer claude
uv run gz content compose AGENTS.md --consumer codex
uv run python -c "import json, pathlib; d = json.loads(pathlib.Path('.gzkit/renditions/AGENTS.md/root.lineage.json').read_text(encoding='utf-8')); print('sections', len(d), '| owned', sum(1 for v in d.values() if v['owned']))"
uv run python -c "import json, pathlib; a = json.loads(pathlib.Path('.gzkit/renditions/AGENTS.md/root.lineage.json').read_text(encoding='utf-8')); b = json.loads(pathlib.Path('.gzkit/renditions/AGENTS.md/codex.lineage.json').read_text(encoding='utf-8')); s = next(k for k, v in a.items() if v['owned']); print(s, 'claude span', a[s]['byte_span'], '| codex span', b[s]['byte_span'])"
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
- [ ] REQ-0.35.0-05-03 [behavior]: Given a corpus containing a live entry that a tombstone retired, when the generator runs, then the retired entry's text is ABSENT from the candidate — the generator reads the effective view, not the raw log.
- [ ] REQ-0.35.0-05-04 [behavior]: Given a generator run for consumer C, when it completes, then `<consumer>.lineage.json` exists carrying, for every AGENTS.md section id, an `owned` flag, the contributing `entry_ids` (empty for unowned), and a `byte_span`.
- [ ] REQ-0.35.0-05-05 [behavior]: Given the same owned section generated for consumer `claude` (setpoint heavy) and consumer `codex` (setpoint lite), when both lineage maps are read, then the section's `byte_span` DIFFERS between them — the map is per-consumer, not surface-wide.
- [ ] REQ-0.35.0-05-06 [behavior]: Given a candidate produced by the generator, when `ByteEvidence` is computed, then `compressible_bytes_after` counts only compressible-tier bytes present in the candidate and is less than or equal to `compressible_bytes_before` — never `total_bytes - invariant_bytes`, which on today's corpus yields 22,378 against an input of 354.
- [ ] REQ-0.35.0-05-07 [behavior]: Given a computed accounting in which `compressible_bytes_after` would exceed `compressible_bytes_before`, when the generator runs, then it FAILS with recovery prose rather than emitting the inflated figure — the witness must be able to fail.
- [ ] REQ-0.35.0-05-08 [behavior]: Given identical corpus, ownership declaration, and prior rendition, when the generator is run twice, then it produces byte-identical candidates and byte-identical lineage maps — determinism is load-bearing for the OBPI-0.35.0-07 single-attestation ruling.
- [ ] REQ-0.35.0-05-09 [behavior]: Given a corpus containing two LIVE byte-identical `invariant` entries, when the generator runs, then the text appears exactly ONCE in the candidate — the standing double-emission fence.
- [ ] REQ-0.35.0-05-10 [structural-fence]: The rendered-section-to-contributing-entry-ids map lives in `<consumer>.lineage.json` and NOWHERE inside `RenditionProvenance`, which remains frozen with `extra="forbid"` and unextended across every ADR-0.35.0 OBPI. Generate-time and commit-time lifecycles stay separated (ADR § Alternatives O); the property is a cross-OBPI boundary because OBPI-0.35.0-06 and OBPI-0.35.0-07 both read these artifacts and either could bolt the map on.

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
