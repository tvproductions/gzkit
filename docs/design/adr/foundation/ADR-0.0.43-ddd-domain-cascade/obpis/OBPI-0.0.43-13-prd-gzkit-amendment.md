---
id: OBPI-0.0.43-13-prd-gzkit-amendment
parent: ADR-0.0.43
item: 13
lane: Heavy
status: Draft
---

# OBPI-0.0.43-13-prd-gzkit-amendment: PRD-GZKIT-1.0.0 amendment — first cascade authoring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #13 — "PRD-GZKIT-1.0.0 amendment with discovered BC list — First-cascade-authoring exercise; populates PRD § 2.1 / 2.2 / 2.3 from OBPI-07 classification ratification; PRD semver lifts to 0.4 (Draft - DDD Domain Cascade integrated); ledger events emitted for each BC introduced."

**Status:** Draft

## Objective

Amend `docs/design/prd/PRD-GZKIT-1.0.0.md` in-place with § 2.1 (Ubiquitous Language), § 2.2 (Bounded Contexts), § 2.3 (Context Map) populated from OBPI-07's ratified legacy mapping. This is the first cascade-authoring exercise — the BC list emerges from the existing corpus's evidence, not from a blank page. PRD semver lifts to 0.4 (Draft - DDD Domain Cascade integrated). One `bounded_context_created`, `glossary_term_added`, or `context_map_updated` event is emitted per addition.

## Lane

**Heavy** — modifies the canonical project-level PRD, which is parent intent for every downstream ADR / OBPI. Identity-shaping amendment.

## Allowed Paths

- `docs/design/prd/PRD-GZKIT-1.0.0.md` — EXTEND only (in-place edit; preserve existing 18 sections; insert § 2.1 / 2.2 / 2.3 after `## 2. Overview`)
- `tests/docs/test_prd_gzkit_cascade_sections.py` — NEW (structural test: sections present, count of BCs > 0, semver bumped)

## Denied Paths

- `src/gzkit/**` — source surface
- `src/gzkit/templates/prd.md` — OBPI-01 (template is the scaffolder source-of-truth; in-place PRD amendment is a one-shot authoring task here, not a template change)
- Other PRDs (none currently exist, but the rule applies — this OBPI only amends GZKIT 1.0.0)
- `docs/design/adr/**` — existing ADRs
- `docs/design/domain/**` — OBPI-02 / 07 territory
- `.gzkit/skills/**` — OBPI-08 / 09 / 10
- `docs/governance/**` and `docs/user/**` — OBPI-12
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (PRD semver lift).** Frontmatter `version` field updated from current (likely `0.3`) to `0.4` with subtitle `(Draft - DDD Domain Cascade integrated)`. Date field updated to amendment date.
2. **REQUIREMENT (`## 2.1 Ubiquitous Language` populated).** Section authored with all cross-cutting glossary terms surfaced from the corpus (terms used across multiple BCs) plus per-BC specializations. Each entry conforms to OBPI-01's `UbiquitousLanguageTerm` schema. Each addition emits one `glossary_term_added` event.
3. **REQUIREMENT (`## 2.2 Bounded Contexts` populated).** Section authored with the full BC list from OBPI-07's ratified legacy mapping. Each entry conforms to OBPI-01's `BoundedContextDeclaration` schema. Each addition emits one `bounded_context_created` event. The `governance` sentinel BC MUST be enumerated as a real BC.
4. **REQUIREMENT (`## 2.3 Context Map` populated).** Section authored with inter-BC relationships discovered during ratification. Each entry conforms to OBPI-01's `ContextMapEntry` schema, with Evans-7 + Vernon Partnership + Big-Ball-of-Mud type and ≥10-word description. Each addition emits one `context_map_updated` event with `action: "added"`.
5. **REQUIREMENT (preserve existing PRD content).** The existing 18 sections (Document Information, Overview, Context & Background, Scope, User Stories, Functional Requirements, Non-Functional Requirements, Dependencies, Risks & Assumptions, Acceptance Criteria, Success Metrics, Rollout, Open Questions, References, Invariants, Gate Mapping, Q&A Record, Attestation Block) MUST remain unchanged in content (renumbering allowed if § 2.1 / 2.2 / 2.3 insertion forces it).
6. **REQUIREMENT (validator pass).** Post-amendment, `gz validate --documents --domain-cascade --domain-views-fresh` MUST exit 0. The PRD's authored cascade content is the canonical input the cascade was designed to enforce.
7. **REQUIREMENT (Layer-3 regeneration).** Post-amendment, `gz domain regenerate` MUST be invoked to populate `docs/design/domain/{glossary,bounded-contexts,context-map}.md` from the new PRD content. The first regeneration is part of this OBPI's completion evidence.
8. **REQUIREMENT (Q&A Record append).** The PRD's `## 17. Q&A Record` section gains an entry documenting the cascade amendment decision: date, ratifier, summary of BCs introduced, link to ADR-0.0.43.
9. **REQUIREMENT (attestation block update).** The PRD's `## 18. Attestation Block` records the operator attestation for the cascade amendment.
10. **REQUIREMENT (operator-authored content discipline).** While agents may draft the BC list / glossary / context-map content from corpus evidence, every entry MUST be operator-ratified before this OBPI is marked complete. Agent-drafted-without-operator-review is a violation of OBPI-07's ratification invariant inherited here.

> STOP-on-BLOCKERS: if OBPI-07's ratified legacy mapping is not yet landed (or accuracy <70% triggered the override path), STOP — the BC list MUST come from ratified evidence, not from agent-drafted classifications.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #13 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § PRIME DIRECTIVE (operator owns the work), § OBPI Acceptance Protocol
- [ ] `docs/governance/state-doctrine.md` — PRD is Layer 1 canon
- [ ] `.gzkit/rules/governance-core.md`

**Context:**

- [ ] OBPI-07 ratified legacy mapping at `docs/design/domain/legacy-adr-bc-mapping.yaml`
- [ ] OBPI-01 strategic Pydantic models (used to validate PRD content)
- [ ] OBPI-06 cascade validator
- [ ] Existing `docs/design/prd/PRD-GZKIT-1.0.0.md`

**Prerequisites:**

- [ ] OBPI-07 ratified and `legacy-adr-bc-mapping.yaml` exists
- [ ] OBPI-01 / OBPI-02 / OBPI-03 / OBPI-04 / OBPI-05 / OBPI-06 landed (cascade machinery available)

**Existing Code:**

- [ ] Existing PRD file structure for section ordering / numbering conventions
- [ ] Existing Q&A Record format

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #13 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] PRD § 2.1 / 2.2 / 2.3 sections present and parseable against OBPI-01 schemas
- [ ] PRD semver bumped to 0.4 with correct subtitle
- [ ] Existing 18 sections present and content-preserved (byte-equal where renumbering doesn't apply)
- [ ] `gz validate --documents --domain-cascade --domain-views-fresh` exit 0
- [ ] Ledger contains one `bounded_context_created` per BC, one `glossary_term_added` per term, one `context_map_updated` per context-map entry
- [ ] `gz domain regenerate` produces the three Layer-3 view files
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Markdownlint clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] PRD renders correctly with new sections in navigation

### Gate 4: BDD (Heavy only)

- [ ] Scenario: cascade-aware ADR creation works against the amended PRD (a new test ADR authored via `gz plan create --bounded-context governance` succeeds)

### Gate 5: Human (Heavy + Foundation)

- [ ] **Operator attestation REQUIRED.** Operator reviews every § 2.1 / 2.2 / 2.3 entry and attests authorship. This is the canonical cascade authoring; operator-authority bar is highest here.
- [ ] Attestor: operator name only (per AGENTS.md PII rule)

## Verification

```bash
uv run gz validate --documents --domain-cascade --domain-views-fresh
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

grep -E '^## 2\.[123]' docs/design/prd/PRD-GZKIT-1.0.0.md
grep -E '^version:' docs/design/prd/PRD-GZKIT-1.0.0.md

# Regenerate Layer-3 views
uv run gz domain regenerate
ls docs/design/domain/{glossary,bounded-contexts,context-map}.md

# Verify ledger emissions
grep -E '(bounded_context_created|glossary_term_added|context_map_updated)' .gzkit/ledger.jsonl
```

## Demo

```bash
# Render PRD with new sections
uv run python -c "
import re
content = open('docs/design/prd/PRD-GZKIT-1.0.0.md').read()
print('§ 2.1:', '## 2.1 Ubiquitous Language' in content)
print('§ 2.2:', '## 2.2 Bounded Contexts' in content)
print('§ 2.3:', '## 2.3 Context Map' in content)
print('semver bumped:', re.search(r'version:\s*0\.4', content) is not None)
"

# Cascade-aware ADR creation now works against the amended PRD
uv run gz plan create demo-cascade-aware --kind feature --semver 0.99.0 --lane lite --bounded-context governance
rm -rf docs/design/adr/feature/ADR-0.99.0-demo-cascade-aware
```

## Acceptance Criteria

- [ ] REQ-0.0.43-13-01: Given PRD-GZKIT-1.0.0.md post-amendment, when frontmatter inspected, then `version: 0.4` with subtitle "(Draft - DDD Domain Cascade integrated)"
- [ ] REQ-0.0.43-13-02: Given PRD-GZKIT-1.0.0.md post-amendment, when § 2.1 inspected, then ≥1 ubiquitous language term entry present and parseable as `UbiquitousLanguageTerm`
- [ ] REQ-0.0.43-13-03: Given PRD-GZKIT-1.0.0.md post-amendment, when § 2.2 inspected, then ≥1 BC entry present and parseable as `BoundedContextDeclaration`; `governance` BC enumerated
- [ ] REQ-0.0.43-13-04: Given PRD-GZKIT-1.0.0.md post-amendment, when § 2.3 inspected, then ≥0 context-map entries present; if any cross-BC relationships exist from OBPI-07, then each parseable as `ContextMapEntry`
- [ ] REQ-0.0.43-13-05: Given PRD post-amendment, when the existing 18 sections compared to pre-amendment, then content byte-equal (or content-equal after renumbering, where only the section number changed)
- [ ] REQ-0.0.43-13-06: Given `gz validate --documents --domain-cascade --domain-views-fresh` post-amendment + `gz domain regenerate`, when invoked, then exit 0
- [ ] REQ-0.0.43-13-07: Given the ledger after this OBPI's amendment, when filtered for cascade events, then count of `bounded_context_created` matches the number of BCs in § 2.2
- [ ] REQ-0.0.43-13-08: Given `gz domain regenerate` invoked post-amendment, when invoked, then `docs/design/domain/{glossary,bounded-contexts,context-map}.md` populated and `--check` mode is byte-equal idempotent
- [ ] REQ-0.0.43-13-09: Given PRD post-amendment, when § 17 Q&A Record inspected, then entry documenting cascade amendment present (date, ratifier, BC summary, ADR-0.0.43 link)
- [ ] REQ-0.0.43-13-10: Given `gz plan create --bounded-context governance` invoked after amendment, when scaffold completes, then succeeds (governance BC resolves)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Structural tests pass
- [ ] **Code Quality:** Markdownlint clean
- [ ] **Gate 3 (Docs):** mkdocs clean
- [ ] **Gate 4 (BDD):** Cascade-aware ADR creation scenario passes
- [ ] **Gate 5 (Human):** **Operator attestation REQUIRED — every § 2.1 / 2.2 / 2.3 entry operator-authored or operator-ratified**
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste structural test output here
```

### Code Quality

```text
# Paste markdownlint output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs output here
```

### Gate 4 (BDD)

```text
# Paste cascade-aware ADR creation scenario output here
```

### Gate 5 (Human)

```text
# Record operator attestation here — MUST cover every § 2.1 / 2.2 / 2.3 entry
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:
- BCs ratified count:
- Glossary terms ratified count:
- Context-map entries ratified count:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`; MUST cover every § 2.1 / 2.2 / 2.3 entry as operator-authored or operator-ratified
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
