---
id: OBPI-0.35.0-04-section-ownership-and-ratchet
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 4
lane: Heavy
status: Draft
allowlist:
- src/gzkit/content/ownership.py
- src/gzkit/commands/content/unown.py
- src/gzkit/commands/content/__init__.py
- src/gzkit/cli/**
- src/gzkit/schemas/section_ownership.json
- .gzkit/ownership/AGENTS.md.json
- src/gzkit/governance/events.py
- tests/content/test_ownership.py
- tests/commands/test_content_unown.py
- features/**
- docs/user/manpages/content.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md
reqs:
- REQ-0.35.0-04-01
- REQ-0.35.0-04-02
- REQ-0.35.0-04-03
- REQ-0.35.0-04-04
- REQ-0.35.0-04-05
- REQ-0.35.0-04-06
- REQ-0.35.0-04-07
- REQ-0.35.0-04-08
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz cli audit
- uv run mkdocs build --strict
---

# OBPI-0.35.0-04-section-ownership-and-ratchet: Section Ownership And Ratchet

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #4 - "Section ownership declaration + decrease-only unowned-byte ratchet + attested ratchet-raise path for un-owning"

**Status:** Draft

## Objective

Declare every AGENTS.md H1/H2 section either `corpus-owned` or `unowned`, record the unowned byte total in a decrease-only ratchet, and gate the only move that raises it — un-owning a section — behind an attested raise-path with the same Gate 5 shape as gz content withdraw.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 04 has no prerequisite inside ADR-0.35.0 and may land in parallel with 01-03. 05 depends on 01 + 04; 06 depends on 04 + 05. Per § Scope Minimization, 04 and 06 are cut together or not at all — cutting 06 alone leaves ownership as a claim with no enforcement, which IS pre-mortem #2.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/content/ownership.py` — ownership declaration model, store, and ratchet **CREATE**
- `src/gzkit/commands/content/unown.py` — the attested ratchet-raise command **CREATE**
- `src/gzkit/commands/content/__init__.py`, `src/gzkit/cli/**` — parser registration for the raise-path verb only
- `src/gzkit/schemas/section_ownership.json` — declaration schema **CREATE**
- `.gzkit/ownership/AGENTS.md.json` — the day-one declaration and ratchet floor **CREATE**
- `src/gzkit/governance/events.py` — ownership and ratchet ledger events
- `tests/content/test_ownership.py`, `tests/commands/test_content_unown.py` — covering tests **CREATE**
- `features/**` — Gate 4 scenarios for the attested raise-path
- `docs/user/manpages/content.md` — the raise-path section
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md` — this brief's evidence sections

## Denied Paths

- `AGENTS.md` — this OBPI declares ownership OVER sections; it never edits them
- `src/gzkit/content/composer.py` — materialization is OBPI-0.35.0-05
- `src/gzkit/governance/trust_audits/**` — `--rendition-lineage` is OBPI-0.35.0-06; this OBPI ships the declaration and the ratchet, not the gate
- `src/gzkit/content/models/corpus.py` — the corpus model is OBPI-0.35.0-01
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS declare a closed enum. A section's ownership is exactly one of `corpus-owned` or `unowned`. Any third value, or a section present in AGENTS.md with no declaration, is fail-closed — an undeclared section is the silent third state this OBPI exists to remove.
2. DAY-ONE BASELINE (re-measured before this brief was written, and to be re-measured at implementation time): AGENTS.md is 31,990 B across 22 H1/H2 sections. Eight sections are corpus-addressed — `attestation`, `behavior-rules`, `defect-fix-routing`, `do-it-right-craftsmanship-maxim`, `governance-doctrine-surfaces`, `obpi-acceptance-protocol`, `operator-doctrine-verbatim-canon`, `prime-directive-ownership` — carrying 9,612 B invariant + 354 B compressible = 9,966 B. The remaining 22,378 B across 14 sections is the day-one unowned ratchet floor.
3. NEVER let the ratchet increase without attestation. Recording an unowned-byte total GREATER than the stored floor MUST be refused. Decrease or equality updates the floor; an increase is only reachable through the attested raise-path.
4. ALWAYS gate the raise-path at Gate 5, fail-closed, with the SAME shape as gz content withdraw: empty or whitespace-only `--attestor` or `--reason` exits non-zero and writes nothing. Un-owning a section is the same act on the same kind of canon, so it takes the same ceremony (ADR § Reversibility).
5. ALWAYS emit a ledger event on both moves — an ownership transition and a ratchet-floor change — carrying the section id, the prior and new byte totals, and, on a raise, the attestor and reason.
6. NEVER couple ownership to a section TITLE. Declarations key on the stable kebab-case section id used by the corpus `section` field, so renaming an H2 heading does not silently orphan a declaration (`DESIGN_FORCING_FUNCTIONS.md` § 2 assumption a1).
7. ALWAYS record the coverage figure alongside the ratchet so it can be read without recomputation: 9,966 of 31,990 B = 31.2%, 8 of 22 sections.
8. NAMED HONESTLY IN THE BRIEF, NOT MARKETED: three of the eight owned sections (`governance-doctrine-surfaces`, `obpi-acceptance-protocol`, `defect-fix-routing`) carry exactly ONE corpus entry each, and `governance-doctrine-surfaces`'s single entry is `compressible` tier, so it is not on the invariant floor at all. "8 of 22 sections" is functionally four sections plus three tokens (ADR § Consequences Negative #1). The implementation MUST NOT round, average, or otherwise present the figure as stronger than this.
9. ALWAYS emit three-part recovery prose on every fail-closed exit per `.claude/rules/guardrail-feedback-prose.md`.
10. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

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

- [ ] ADR § Decision item 3 — ownership plus decrease-only ratchet, and the attested raise-path.
- [ ] ADR § Consequences (Negative) #1, #2 and #4 — thin coverage, the ratchet's missing forcing function, and owned-section fail-closed becoming the thing agents route around.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 1 pre-mortem #1 and #2, and § 6 Reversibility — the raise-path exists because the undefined reversal path is the one agents invent.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 4 — ownership is declared surface-wide but materialization is per-consumer; that looseness is deliberate and is resolved in the OBPI-0.35.0-05 lineage map.

**Prerequisites (check existence, STOP if missing):**

- [ ] `AGENTS.md` present; 22 H1/H2 headings and 31,990 B re-measured at implementation time
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` present; the eight corpus-addressed section ids re-derived at implementation time
- [ ] `src/gzkit/governance/events.py` exists and carries the emit-helper pattern
- [ ] `src/gzkit/commands/content/commit.py` exists (the Gate-5 fail-closed pattern the raise-path mirrors)
- [ ] `docs/user/manpages/content.md` exists

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/models/corpus.py:43` — `section: str` is flat and `anchor: str | None` is largely unused; ownership is declared at a granularity the model supports only weakly
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:87-91` — the staged-warn precedent, and `_checkpoint.resolve`'s hangar downgrade; the in-repo evidence for pre-mortem #2
- [ ] `src/gzkit/commands/content/commit.py:47-54` — the Gate-5 shape to mirror

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
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content unown --help
uv run gz content unown AGENTS.md --section attestation --attestor "" --reason "probe"
uv run python -c "import json, pathlib; d = json.loads(pathlib.Path('.gzkit/ownership/AGENTS.md.json').read_text(encoding='utf-8')); print('owned', sum(1 for v in d['sections'].values() if v == 'corpus-owned'), '| unowned floor', d['unowned_byte_floor'], '| coverage', d['coverage_pct'])"
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-04-01 [behavior]: Given a section declaration whose value is neither `corpus-owned` nor `unowned`, or an AGENTS.md section with no declaration at all, when the ownership store is loaded, then it fails closed naming the offending section id — there is no undeclared third state.
- [ ] REQ-0.35.0-04-02 [behavior]: Given a stored unowned-byte floor of N, when a recorded total greater than N is submitted through the ordinary (unattested) path, then the update is REFUSED and the stored floor is unchanged — the ratchet is decrease-only.
- [ ] REQ-0.35.0-04-03 [behavior]: Given a stored floor of N, when a recorded total less than or equal to N is submitted, then the floor is updated to the new total and a ratchet ledger event is emitted carrying the prior and new values.
- [ ] REQ-0.35.0-04-04 [behavior]: Given the attested raise-path invoked with an empty or whitespace-only `--attestor` or `--reason`, when it runs, then it exits non-zero, the ownership declaration and ratchet floor are byte-unchanged, and no ledger event is written.
- [ ] REQ-0.35.0-04-05 [behavior]: Given the attested raise-path invoked with a non-empty attestor and reason against a `corpus-owned` section, when it runs, then the section becomes `unowned`, the ratchet floor RISES by that section's byte count, and a ledger event records the section id, both floor values, the attestor, and the reason.
- [ ] REQ-0.35.0-04-06 [behavior]: Given an AGENTS.md whose H2 heading TEXT changed while its kebab-case section id is unchanged, when the ownership store is loaded, then the declaration still resolves — ownership keys on the id, never on the title.
- [ ] REQ-0.35.0-04-07 [behavior]: Given the day-one AGENTS.md and corpus, when the baseline is computed, then it reports 8 owned sections, 22,378 unowned bytes across 14 sections, and 31.2% coverage of 31,990 B — derived by measurement, never by a stored constant.
- [ ] REQ-0.35.0-04-08 [support]: The day-one declaration at `.gzkit/ownership/AGENTS.md.json` is present and validates against `src/gzkit/schemas/section_ownership.json` — witnessed by an `artifact_edited` ledger event citing `.gzkit/ownership/AGENTS.md.json` — and `gz validate --documents` admits the shape.

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
