---
id: OBPI-0.39.0-05-contradiction-detection
parent: ADR-0.39.0-instruction-plugin-registry
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.39.0-05: Contradiction Detection

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/ADR-0.39.0-instruction-plugin-registry.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.39.0-05 — "Contradiction detection — detect when local instructions contradict canonical rules"`

## OBJECTIVE

Design and implement contradiction detection between project-local instructions and gzkit's canonical instruction set. A contradiction occurs when a local instruction directs agents to do something that a canonical instruction explicitly prohibits, or vice versa. The detection must go beyond simple text diffing — it must understand instruction semantics at the rule level: required/prohibited patterns, toolchain choices, naming conventions, and error handling policies. The system must report contradictions with specific evidence (the conflicting rules from each instruction).

## SOURCE MATERIAL

- **Canonical set:** Output of OBPI-0.39.0-02 (canonical instruction catalog)
- **Extension mechanism:** Output of OBPI-0.39.0-03 (registration mechanism)
- **Conformance validation:** Output of OBPI-0.39.0-04 (validation infrastructure)

## ASSUMPTIONS

- Contradiction detection is harder than conformance checking — it requires understanding instruction semantics
- A practical first version can use structured rule extraction (tables, bullet lists with "DO"/"DO NOT" patterns)
- False positives are preferable to false negatives — it is better to flag a non-contradiction than miss a real one
- The detection algorithm must be deterministic and reproducible (no LLM-in-the-loop for validation)
- Contradictions should be categorized by severity: hard contradiction (direct conflict), soft contradiction (tension), informational (different emphasis)

## NON-GOALS

- Natural language understanding of arbitrary prose — focus on structured rule patterns
- Resolving contradictions automatically — the system reports, humans decide
- Checking instructions against code behavior — only instruction-vs-instruction comparison
- Building an LLM-powered semantic analysis engine

## REQUIREMENTS (FAIL-CLOSED)

1. Define contradiction types: hard (direct conflict), soft (tension), informational (different emphasis)
1. Implement structured rule extraction from instruction files (tables, DO/DO NOT patterns, convention statements)
1. Implement pairwise comparison between canonical and local rules within overlapping scopes
1. Report contradictions with evidence: the specific rules from each file that conflict
1. Integrate with `gz validate instructions` as an additional check (separate flag or default-on)
1. Write unit tests with known contradictions and known non-contradictions
1. Document the contradiction detection approach, limitations, and false positive handling

## ALLOWED PATHS

- `src/gzkit/instructions/` — contradiction detection implementation
- `tests/` — unit tests
- `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Detection approach documented with limitations
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
