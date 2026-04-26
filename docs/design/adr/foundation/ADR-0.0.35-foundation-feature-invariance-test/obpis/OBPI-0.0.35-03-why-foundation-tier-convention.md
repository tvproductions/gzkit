---
id: OBPI-0.0.35-03-why-foundation-tier-convention
parent: ADR-0.0.35-foundation-feature-invariance-test
item: 3
lane: Lite
status: Draft
---

# OBPI-0.0.35-03-why-foundation-tier-convention: Why-Foundation-Tier Section Convention + Scaffolding Template Update

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.35-foundation-feature-invariance-test/ADR-0.0.35-foundation-feature-invariance-test.md`
- **Checklist Item:** #3 — "Why-foundation-tier section convention — define the `## Why foundation tier?` section every foundation ADR carries (one-line answer to the invariance test plus port-vs-plug framing); update the foundation ADR template in `gz plan create --kind foundation` scaffolding so new ADRs scaffold the section pre-populated; document the convention in the concepts page authored under OBPI-01. Depends on OBPI-01."

**Status:** Draft

## Objective

Define and codify the `## Why foundation tier?` section convention for every foundation-kind ADR — operator answers the invariance test affirmatively in plain language under that exact heading. Update `src/gzkit/templates/adr.md` (the scaffolding template `gz plan create --kind foundation` renders) so new foundation ADRs land the section pre-populated with author-prompts that walk the operator through the test answer and the port-vs-plug framing. Document the convention in the OBPI-01 concept page so it appears alongside the test itself, and cross-reference the convention from the runbook section that discusses `gz plan create --kind`.

## Lane

**Lite** — Template surface and concept-page documentation. The template change is internal to `gz plan create` scaffolding (a string template; no CLI surface or runtime contract changes). Foundation-kind brief-level attestation still applies (parent ADR-0.0.35 is foundation-kind).

## Allowed Paths

- `src/gzkit/templates/adr.md` — foundation-ADR scaffolding template (add `## Why foundation tier?` section)
- `src/gzkit/commands/plan.py` — renderer wiring for the new section (only if the section needs conditional rendering for foundation vs feature/pool; minimal logic)
- `docs/user/concepts/foundation-feature-invariance-test.md` — concept-page section documenting the convention (this OBPI extends the OBPI-01 page; non-conflicting addition under a `## Why foundation tier? (the convention)` subsection)
- `docs/user/runbook.md` — cross-reference at the `gz plan create --kind foundation` section
- `docs/user/manpages/gz-plan.md` — manpage update reflecting the new section in scaffolding output (if manpage discusses scaffolded structure)

## Denied Paths

- `.claude/skills/**`, `.github/skills/**` — generated mirrors; OBPI-02's scope
- `.gzkit/skills/**` — skill prompts; OBPI-02's scope
- `src/gzkit/governance/trust_audits.py` — `gz validate --kind-invariance` validator is OBPI-04's scope
- `tests/**` — no test surface here; renderer determinism is the gate (an integration test would belong with the validator in OBPI-04, not this OBPI)
- All ADR/OBPI files except this brief and OBPI-01's deliverable
- `src/gzkit/templates/adr_pool.md` — pool template; pool ADRs have no `kind:` frontmatter and no foundation-tier framing
- `src/gzkit/templates/obpi.md` — OBPI brief template; the convention applies to ADR bodies, not OBPI briefs

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT — section heading is exact.** The new section heading MUST be `## Why foundation tier?` (sentence case, trailing question mark). Any drift in casing or punctuation is a defect — the heading is the validator's match anchor under OBPI-04 and must be byte-identical across every foundation ADR.
2. **REQUIREMENT — section appears only on foundation kind.** Feature-kind ADRs MUST NOT scaffold this section; pool ADRs (no `kind:` frontmatter) MUST NOT scaffold this section. The section is foundation-specific by contract.
3. **REQUIREMENT — section pre-populates two prompts.** The scaffolded section body MUST include two operator-facing prompts: one for the invariance-test answer (*"Without this ADR, would the project still be the project?"* with author-fillable answer space) and one for the port-vs-plug framing (*"Is this ADR a port (an abstract contract every implementation must honor) or a plug (one implementation behind an existing port)?"* with answer space).
4. **REQUIREMENT — concept-page convention section.** `docs/user/concepts/foundation-feature-invariance-test.md` (OBPI-01 deliverable) MUST gain a `## Why foundation tier? (the convention)` subsection (or equivalent named home) explaining the convention, naming the exact heading, and showing one filled-in example.
5. **REQUIREMENT — runbook cross-reference.** `docs/user/runbook.md` § `gz plan create --kind foundation` (or wherever foundation scaffolding is discussed) MUST cross-reference the convention.
6. **REQUIREMENT — existing foundation ADRs not mutated.** This OBPI introduces the convention forward-only; OBPI-04's validator will report drift on the existing-foundation-ADR population for a follow-up backfill sweep. No backfill happens here.
7. **REQUIREMENT — `gz plan create --kind foundation` scaffolds the section.** A fresh invocation of `gz plan create test-slug --kind foundation --semver 0.0.99` MUST produce an ADR file containing the `## Why foundation tier?` heading. Verified via dry-run inspection or integration touch-test.
8. **REQUIREMENT — `gz plan create --kind feature` does NOT scaffold the section.** Verified via dry-run inspection of a feature-kind scaffold.
9. **REQUIREMENT — section position is between Persona and Intent.** The section sits as the second H2 in the rendered ADR body (after `## Persona`, before `## Intent`). This positioning makes the test answer the first substantive content an adopter encounters — the framing for everything below.
10. **NEVER — encode the section as conditional rendering using a third-party template engine.** Per Stdlib-First doctrine, the renderer uses string `.format()` substitution. If conditional rendering is needed, implement it via two template variants (`adr.md` for foundation; existing logic untouched for feature) or a renderer-level branch in `plan.py` — not a Jinja2 / Mako / Handlebars dependency.
11. **NEVER — paraphrase the convention name.** The section heading is `## Why foundation tier?` exactly — not *"## Foundation Justification"*, not *"## Why is this foundation?"*, not *"## Why Foundation?"*. The byte-identical match is what OBPI-04's validator pins.

> STOP-on-BLOCKERS: if `docs/user/concepts/foundation-feature-invariance-test.md` does not exist, OBPI-01 has not landed — print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned per GHI #321):**

- [ ] Quote ADR-0.0.35 § Decision item #6 (Why-foundation-tier section becomes load-bearing) verbatim into Implementation Summary.
- [ ] Read ADR-0.0.35 § Intent and § Decision § "Why-foundation-tier section becomes load-bearing" subsection.

> **STOP:** If you cannot quote ADR-0.0.35 § Decision item #6 verbatim, STOP and re-read.

**Sibling rule reference:**

- [ ] Read `AGENTS.md` § STDLIB-FIRST DOCTRINE — confirm the renderer constraint (no template-engine dependency).
- [ ] Read OBPI-04 brief — confirm the validator's section-heading match anchor matches the heading authored here. Drift between the two breaks the convention.

**OBPI-01 dependency check:**

- [ ] `docs/user/concepts/foundation-feature-invariance-test.md` exists (OBPI-01 landed). If absent, this OBPI cannot proceed.

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/templates/adr.md` exists
- [ ] `src/gzkit/commands/plan.py` exists and contains the scaffolding renderer
- [ ] OBPI-01 deliverable exists: `docs/user/concepts/foundation-feature-invariance-test.md`
- [ ] `gz plan create --kind foundation --dry-run` resolves cleanly against an arbitrary test slug

**Existing Code (understand current state):**

- [ ] `src/gzkit/templates/adr.md` — read end-to-end; identify the second-H2 insertion point (between `## Persona` and `## Intent`).
- [ ] `src/gzkit/commands/plan.py` — read the rendering path that produces the ADR file; identify where `kind:` is read and how the template is filled. Determine whether conditional section rendering needs renderer logic or can be handled at template-level via two template files.
- [ ] `src/gzkit/templates/adr_pool.md` — confirm pool ADRs do not scaffold a `## Why foundation tier?` section (they should not, by REQ-02).
- [ ] `docs/user/manpages/gz-plan.md` — confirm whether scaffolding output structure is described; if so, the manpage needs updating.
- [ ] `docs/user/runbook.md` — locate the `gz plan create --kind foundation` discussion section; confirm the cross-reference insertion point.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR § Decision item #6 quoted

### Gate 2: TDD (Red-Green-Refactor)

The convention has a code path (renderer logic in `plan.py`). RGR applies:

- [ ] **Red:** Author a unit test asserting `gz plan create --kind foundation` produces an ADR file containing `## Why foundation tier?` and that `--kind feature` does NOT. Run; observe RED for the right reason (section missing in foundation case).
- [ ] **Green:** Update template + renderer so the test passes. The simplest implementation that makes the test pass.
- [ ] **Refactor:** Tighten the implementation if duplication accrued.
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs

- [ ] `uv run mkdocs build --strict` exits 0 (concept-page convention section + runbook cross-reference + manpage update)

### Gate 5: Human (Foundation-kind brief-level attestation)

- [ ] Foundation-kind parent → brief-level attestation required.
- [ ] Operator confirms section heading exact-match wording, position (between Persona and Intent), and pre-populated prompts.

## Verification

```bash
# Template contains the new section heading exactly
grep -F "## Why foundation tier?" src/gzkit/templates/adr.md

# Pool template does NOT contain the section
grep -F "## Why foundation tier?" src/gzkit/templates/adr_pool.md && echo "DEFECT: pool template should not have the section" || echo "OK: pool template clean"

# Foundation scaffolding produces the section
uv run gz plan create test-foundation-scaffold-$(date +%s) --kind foundation --semver 0.0.99 --lane lite --score-data-state 0 --score-logic-engine 0 --score-interface 0 --score-observability 0 --score-lineage 1 --dry-run

# Feature scaffolding does NOT produce the section
uv run gz plan create test-feature-scaffold-$(date +%s) --kind feature --semver 0.99.0 --lane lite --score-data-state 0 --score-logic-engine 0 --score-interface 0 --score-observability 0 --score-lineage 1 --dry-run

# Concept page documents the convention
grep -F "Why foundation tier?" docs/user/concepts/foundation-feature-invariance-test.md

# Runbook cross-references it
grep -F "Why foundation tier?" docs/user/runbook.md

# Tests pass
uv run gz test

# ARB receipts
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Acceptance Criteria

- [ ] **REQ-0.0.35-03-01:** Given `src/gzkit/templates/adr.md`, when read, then a heading exactly matching `## Why foundation tier?` is present (byte-identical, trailing question mark, sentence case).
- [ ] **REQ-0.0.35-03-02:** Given a fresh invocation of `gz plan create <slug> --kind foundation --semver 0.0.99 ...`, when the rendered ADR file is read, then it contains the `## Why foundation tier?` heading positioned between `## Persona` and `## Intent`.
- [ ] **REQ-0.0.35-03-03:** Given a fresh invocation of `gz plan create <slug> --kind feature --semver 0.99.0 ...`, when the rendered ADR file is read, then it does NOT contain the `## Why foundation tier?` heading.
- [ ] **REQ-0.0.35-03-04:** Given the scaffolded foundation ADR, when an operator reads the `## Why foundation tier?` section, then two prompts are present: one for the invariance-test answer and one for the port-vs-plug framing.
- [ ] **REQ-0.0.35-03-05:** Given `docs/user/concepts/foundation-feature-invariance-test.md`, when read, then a section documenting the `## Why foundation tier?` convention is present, naming the exact heading and showing one filled example.
- [ ] **REQ-0.0.35-03-06:** Given `docs/user/runbook.md`, when read at the `gz plan create --kind foundation` section, then a cross-reference to the convention concept-page section is present.
- [ ] **REQ-0.0.35-03-07:** Given the unit test asserting foundation-vs-feature scaffolding behavior, when run, then it passed RED before implementation and GREEN after; both states are recorded in evidence.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent § Decision quoted
- [ ] **Gate 2 (TDD):** RED-GREEN-REFACTOR cycle followed; tests passing
- [ ] **Code Quality:** Lint, format, typecheck clean
- [ ] **Gate 3 (Docs):** mkdocs strict clean
- [ ] **Gate 5 (Human):** Foundation-kind brief-level attestation recorded
- [ ] **Value Narrative:** Recorded below
- [ ] **Key Proof:** A scaffolded foundation ADR (excerpt) shown alongside a scaffolded feature ADR (excerpt) demonstrating the section's presence and absence
- [ ] **OBPI Acceptance:** Evidence section populated

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste RED test output (section missing) and GREEN test output (section present) here
```

### Code Quality

```text
# Paste lint, format, typecheck output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output here
```

### Gate 5 (Human)

```text
# Record foundation-kind brief-level attestation text here
```

### Value Narrative

Before this OBPI: foundation-kind ADRs have no canonical home for the invariance test answer; some authors fold it into Intent prose, others into Decision, many leave it implicit. Adopters reading a foundation ADR cannot find a single load-bearing place that says *why this is foundation*. After this OBPI: every newly-scaffolded foundation ADR carries a `## Why foundation tier?` section between Persona and Intent, with operator prompts walking the author through the invariance-test answer and port-vs-plug framing. The convention becomes the validator's match anchor under OBPI-04 — once OBPI-04 ships, an empty or missing section fails closed; before OBPI-04 ships, the convention is honor-system but the scaffolding makes the floor easy to clear.

### Key Proof

Excerpts side-by-side: `gz plan create test-x --kind foundation` produces an ADR with `## Why foundation tier?` heading visible at the second-H2 position; `gz plan create test-y --kind feature` produces an ADR with no such heading. RED test output and GREEN test output pasted in evidence demonstrate the same.

### Implementation Summary

- Files modified: `src/gzkit/templates/adr.md`, `src/gzkit/commands/plan.py` (renderer logic if needed), `docs/user/concepts/foundation-feature-invariance-test.md`, `docs/user/runbook.md`, `docs/user/manpages/gz-plan.md` (if applicable)
- Tests added: `tests/commands/test_plan.py` (foundation scaffolds with section; feature does not) — exact test name TBD by implementer
- Date completed: -
- Attestation status: -
- Defects noted: -

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` — required (foundation-kind parent)
- Attestation: -
- Date: -

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
