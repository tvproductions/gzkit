---
id: OBPI-0.35.0-06-validate-rendition-lineage
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 6
lane: Heavy
status: Draft
allowlist:
- src/gzkit/governance/trust_audits/rendition_lineage.py
- src/gzkit/governance/trust_audits/__init__.py
- src/gzkit/commands/validate_cmd.py
- tests/governance/test_rendition_lineage.py
- features/**
- docs/user/manpages/validate.md
- docs/governance/governance_runbook.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-06-validate-rendition-lineage.md
reqs:
- REQ-0.35.0-06-01
- REQ-0.35.0-06-02
- REQ-0.35.0-06-03
- REQ-0.35.0-06-04
- REQ-0.35.0-06-05
- REQ-0.35.0-06-06
- REQ-0.35.0-06-07
- REQ-0.35.0-06-08
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --rendition-lineage
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz cli audit
- uv run mkdocs build --strict
---

# OBPI-0.35.0-06-validate-rendition-lineage: Validate Rendition Lineage

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #6 - "gz validate --rendition-lineage -- fail-closed over owned sections, coverage % surfaced to Fidelity Assertions"

**Status:** Draft

## Objective

Ship gz validate --rendition-lineage: exit 0 when every owned section in a committed rendition is derivable from the effective corpus, exit 3 on hand-authored prose inside an owned section, unowned bytes reported as measured debt and never failed, and the coverage percentage surfaced so the gate's partial scope is declared rather than implied.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 06 depends on 04 (the ownership declaration that defines the gate's scope) and 05 (the lineage map and the generator whose output the gate compares against). Per § Scope Minimization, 04 and 06 are cut together or not at all — cutting 06 alone leaves ownership as a claim with no enforcement, which IS pre-mortem #2 and the worst possible combination.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/governance/trust_audits/rendition_lineage.py` — the new validator scope **CREATE**
- `src/gzkit/governance/trust_audits/__init__.py` — scope registration
- `src/gzkit/commands/validate_cmd.py` — `--rendition-lineage` flag wiring
- `tests/governance/test_rendition_lineage.py` — covering tests **CREATE**
- `features/**` — Gate 4 scenarios
- `docs/user/manpages/validate.md`, `docs/governance/governance_runbook.md` — the new scope
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-06-validate-rendition-lineage.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — the existing invariant-floor gate is a sibling scope and stays as-is; its substring-test defect is discharged by OBPI-0.35.0-03, not rewritten here
- `src/gzkit/content/composer.py`, `src/gzkit/content/lineage.py` — the generator and lineage writer are OBPI-0.35.0-05 and are consumed read-only
- `src/gzkit/content/ownership.py` — OBPI-0.35.0-04, consumed read-only
- `AGENTS.md` — the gate measures the surface; it never edits it
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS fail closed over OWNED SECTIONS ONLY. Unowned bytes are reported as measured debt and MUST NEVER contribute to a non-zero exit. A gate whose scope is partial and undeclared is the theater ADR-0.35.0 exists to remove.
2. ALWAYS surface the coverage figure in the scope's output — sections owned of total, bytes owned of total, and the percentage — so every run re-measures the 31.2% claim rather than reprinting it. The figure is asserted in the parent ADR's Fidelity Assertions and must be reproducible from this scope's output.
3. NEVER hardcode 31.2%, 8, 22, 9,966, or 22,378. Every figure is computed from the ownership declaration, the effective corpus, and the committed rendition at run time. A stored constant is a witness that cannot fail — the same defect class as the `ByteEvidence` inflation.
4. ALWAYS read the EFFECTIVE corpus (OBPI-0.35.0-01), never `load_corpus`'s raw return. A consumer left on the raw log is a one-line omission whose symptom is a GREEN gate over a rendition that omits canon — pre-mortem #3, the worst detection latency in this ADR.
5. ALWAYS emit three-part recovery prose on the exit-3 path per `.claude/rules/guardrail-feedback-prose.md`: which owned section drifted, that owned sections are corpus-derived by ADR-0.35.0 § Decision item 4, and the runnable next step.
6. NEVER present marking a section `unowned` as the recovery for a lineage failure. Pre-mortem #2 is that owned-section fail-closed becomes the thing agents route around, and the cheapest route is un-owning; the recovery prose must name the corpus round-trip, with the attested raise-path (OBPI-0.35.0-04) as a deliberate, attested move and never as the suggested escape.
7. ALWAYS resolve severity through the shared MX checkpoint the way `rendition_floor_coherence.py:47-51` does, so hangar behavior is consistent across the two content gates.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

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

- [ ] ADR § Decision item 4 — owned-sections-only fail-closed, and why the coverage percentage is in Fidelity Assertions.
- [ ] ADR § Consequences (Negative) #1, #2 and #4 — thin coverage, the ratchet's missing forcing function, and the route-around risk this gate's recovery prose must not feed.
- [ ] ADR § Fidelity Assertions — two rows resolve to this scope; both expect exit 0.
- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part bar every fail-closed surface must clear.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-04 landed: `.gzkit/ownership/AGENTS.md.json` declares every AGENTS.md section
- [ ] OBPI-0.35.0-05 landed: `<consumer>.lineage.json` is emitted and the generator is deterministic
- [ ] OBPI-0.35.0-01 landed: `effective_corpus()` is the corpus read path
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` exists — the sibling scope whose registration, MX-checkpoint, and `ValidationError` shape this scope mirrors
- [ ] `src/gzkit/commands/validate_cmd.py` exists and carries the scope-registration pattern

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:32-105` — the whole sibling scope: MX checkpoint resolution, per-surface iteration, `ValidationError` construction, and the drift ledger event
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:1-9` — the module docstring naming mtime comparison as the discredited fake witness this family of gates exists to replace
- [ ] `src/gzkit/commands/validate_cmd.py` — how a scope is registered and how `gz check` picks up its default scope set

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
uv run gz validate --rendition-lineage
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz validate --rendition-lineage
uv run gz validate --rendition-lineage --json
uv run gz adr fidelity ADR-0.35.0
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-06-01 [behavior]: Given a committed rendition whose every owned section matches the deterministic materialization of the effective corpus, when gz validate --rendition-lineage runs, then it exits 0.
- [ ] REQ-0.35.0-06-02 [behavior]: Given a committed rendition in which an OWNED section carries prose that is not derivable from the effective corpus, when the scope runs fail-closed, then it exits 3 and names the offending section id.
- [ ] REQ-0.35.0-06-03 [behavior]: Given a committed rendition in which an UNOWNED section carries arbitrary hand-authored prose, when the scope runs, then it exits 0 and reports those bytes as measured debt — unowned text never fails the gate.
- [ ] REQ-0.35.0-06-04 [behavior]: Given the day-one ownership declaration and corpus, when the scope runs, then its output carries the coverage figure computed at run time — owned sections of total, owned bytes of total, and the percentage — and changing the ownership declaration changes the reported figure.
- [ ] REQ-0.35.0-06-05 [behavior]: Given a corpus in which an invariant entry has been retired by a tombstone and a rendition that still carries its text inside an owned section, when the scope runs, then it exits 3 — the scope reads the effective corpus, so a retired entry left in an owned section is drift, not a pass.
- [ ] REQ-0.35.0-06-06 [behavior]: Given the exit-3 path, when stderr is read, then it carries all three recovery parts — the drifted owned section, the cited ADR-0.35.0 § Decision item 4, and a runnable corpus round-trip next step — and it does NOT name un-owning the section as the recovery.
- [ ] REQ-0.35.0-06-07 [support]: gz validate --rendition-lineage is registered in the validator scope registry and documented in `docs/user/manpages/validate.md` and `docs/governance/governance_runbook.md` — witnessed by an `artifact_edited` ledger event citing `docs/user/manpages/validate.md` — and `gz validate --cli-alignment` resolves every reference those docs prescribe.
- [ ] REQ-0.35.0-06-08 [structural-fence]: The fail-closed reach of `--rendition-lineage` is owned sections only, and no ADR-0.35.0 OBPI extends it over unowned bytes. The gate's partial scope is a declared property of the whole decomposition — OBPI-0.35.0-04 sets the scope, 05 supplies the comparison artifact, 07 consumes the result — so it is audited at ADR closeout, not per-OBPI.

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
