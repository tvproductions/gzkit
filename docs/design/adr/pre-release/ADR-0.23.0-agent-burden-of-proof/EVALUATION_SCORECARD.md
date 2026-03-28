<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

## Metadata

**ADR:** ADR-0.23.0 — Agent Burden of Proof at ADR Closeout
**Evaluator:** Claude Opus 4.6 (independent evaluation)
**Date:** 2026-03-28

---

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 |
| 2 | Decision Justification | 15% | 4 | 0.60 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 4 | 0.40 |
| 7 | Evidence Requirements | 10% | 4 | 0.40 |
| 8 | Architectural Alignment | 10% | 4 | 0.40 |

**WEIGHTED TOTAL: 3.75/4.0**
**THRESHOLD: 3.0 (GO)**

---

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|:-----------:|:-----------:|:-----:|:----:|:-------:|:---:|
| 01 — Closing Argument | 4 | 4 | 4 | 3 | 4 | 3.80 |
| 02 — Product Proof Gate | 4 | 4 | 4 | 4 | 4 | 4.00 |
| 03 — Reviewer Agent | 4 | 3 | 4 | 3 | 3 | 3.40 |
| 04 — Ceremony Enforcement | 3 | 3 | 4 | 4 | 4 | 3.60 |

**OBPI Average: 3.70** (threshold: 3.0)
**No dimension scores 1 on any OBPI.**

---

## Dimension Rationale

### Problem Clarity (4/4)

The problem is quantified with a specific cautionary exemplar (ADR-0.15.0: all gates passed, Summary Deltas still read "TBD", completion table full of placeholder links) and a counter-exemplar (ADR-0.12.0: concrete post-attestation ceremony, operator-facing value narratives, specific CLI verification). Before state is concrete — agents satisfy closeout superficially. After state is testable — closing arguments, product proof gate, reviewer assessment. The "so what?" is immediate: governance becomes theater when agents can declare completion without substantive proof.

### Decision Justification (4/4)

Three alternatives are explicitly named and dismissed with specific reasoning: more checklist items (the anti-pattern this ADR targets, with ADR-0.15.0 as evidence), human-only review (doesn't scale), automated prose quality scoring (over-engineered). Each decision has an independent "why." Counterarguments are addressed through the anti-pattern warning and scope creep guardrails. ADR-0.12.0 is cited as the exemplar precedent being formalized.

### Feature Checklist Completeness (3/4)

All items are justified and coverage appears complete. The 1:1 OBPI mapping is clean. The checklist could be more explicit about the mechanics of "new validation steps" in the CLI — the reader must go to OBPI-02 to understand what "product proof" concretely means at the checklist level. The migration strategy in Consequences is strong (four-tier path for existing briefs). Not 4 because the checklist items are at slightly uneven abstraction levels — "CLI `gz closeout` gains new product-proof validation steps" packs more complexity than "No config/calendar changes."

### OBPI Decomposition Quality (4/4)

Excellent decomposition. Three independent OBPIs (01-03) feeding one integrator (04), with an ASCII dependency diagram. Critical path = max(01,02,03) + 04, reducing effective depth from 4 to 2. Each OBPI follows domain boundaries (template / quality check / agent role / ceremony skill). The integrator pattern is architecturally sound — 04 can't start until 01-03 deliver, but 01-03 don't block each other.

### Lane Assignment Correctness (3/4)

Heavy assignments for OBPIs 02-04 are clearly correct — each touches an external contract (CLI, pipeline, ceremony). OBPI-01's Lite assignment is debatable: the brief itself acknowledges "External contract changes detected: OBPI brief template is an agent-facing contract" but then argues it's internal governance tooling. This is defensible but creates a tension the ADR doesn't fully resolve. The parent-lane attestation floor is correctly captured via the attestation reminder checkbox. Not 4 because of the self-acknowledged tension in OBPI-01's lane.

### Scope Discipline (4/4)

Five explicit non-goals with justification: retroactive migration, automated prose scoring, replacing human attestation, non-closeout scope expansion, attestation vocabulary changes. Guardrails reference ADR-0.19.0 specifically. Lite-Lane Applicability section addresses proportional rigor (closing arguments + docstrings required for Lite, reviewer advisory not blocking, no Gate 5). The scope boundaries are tightly drawn.

### Evidence Requirements (4/4)

Every OBPI has concrete verification commands with expected output. OBPI-01: four grep/unittest commands. OBPI-02: gates 1-4 listed plus dry-run CLI. OBPI-03: four verification commands for reviewer role, assessment artifacts, structured fields, and separate-agent dispatch. OBPI-04: ceremony skill content checks plus end-to-end dry-run. Heavy OBPIs explicitly list Gate 5 human attestation.

### Architectural Alignment (4/4)

Two concrete repository exemplars: ADR-0.15.0 (cautionary — every gate passed, operator got nothing usable) and ADR-0.12.0 (gold standard — concrete evidence, operator-facing narratives, verification commands). Integration points listed with file paths and line numbers (cli.py lines ~2286-2505, quality.py, commands/common.py lines ~448-593, pipeline.py). Anti-pattern is named and exemplified ("more checkboxes = more rigor" with ADR-0.15.0 as proof this fails). References ADR-0.18.0 (multi-agent) and ADR-0.19.0 (closeout-audit) for architectural continuity.

---

## OBPI Rationale

### OBPI-01 — Closing Argument (Avg: 3.80)

- **Independence (4):** Fully independent — no dependencies on other OBPIs.
- **Testability (4):** Four concrete grep/unittest commands with expected output values.
- **Value (4):** Without it, closing arguments remain planning echoes — the entire burden-of-proof thesis collapses at the template level.
- **Size (3):** Template rename + guidance text + one test file. Under 1 day of work — slightly small but not trivially so, given the template requires careful framing to avoid the "renamed but same structure" anti-pattern.
- **Clarity (4):** Four requirements with specific three-element structure (artifact paths, operator capability, proof command/link). Anti-pattern explicitly named.

### OBPI-02 — Product Proof Gate (Avg: 4.00)

- **Independence (4):** Fully independent.
- **Testability (4):** Unit tests + BDD scenarios + dry-run CLI command. `gz closeout --dry-run` is the single-command proof.
- **Value (4):** Without it, closeout has no automated documentation check — the core gate of the ADR's thesis.
- **Size (4):** New quality check function + CLI integration + BDD + docs. Solid 2-3 day work unit.
- **Clarity (4):** Five requirements, three proof types defined (runbook keyword match, manpage file + synopsis, docstrings), clear output format (per-OBPI table).

### OBPI-03 — Reviewer Agent (Avg: 3.40)

- **Independence (4):** Fully independent. References ADR-0.18.0 infrastructure but doesn't depend on OBPIs 01, 02, or 04.
- **Testability (3):** Four verification commands, but `ls REVIEW-*.md` assumes an assessment artifact naming convention that isn't defined in the brief. The verification is aspirational rather than concrete on this point.
- **Value (4):** Without it, there's no independent check — the implementing agent self-certifies quality. This is the ADR's strongest anti-rubber-stamp mechanism.
- **Size (3):** New agent role + dispatch logic + structured assessment format + ceremony integration point. Could push to 3-4 days given the multi-agent dispatch complexity.
- **Clarity (3):** The structured assessment format (promises-met, docs-quality, closing-argument-quality) is named but the exact schema is unspecified. A different agent might produce a different assessment shape, file format, or storage location.

### OBPI-04 — Ceremony Enforcement (Avg: 3.60)

- **Independence (3):** Explicitly depends on 01-03. Dependency is declared, justified, and diagrammed. The integrator role is architecturally correct — this is inherent dependency, not a decomposition flaw.
- **Testability (3):** Four verification commands check presence, but the real proof is the end-to-end dry-run, which depends on all prior OBPIs being integrated. Hard to test in isolation.
- **Value (4):** Without it, the ceremony remains a rubber-stamp form — all other OBPIs' outputs have no enforcement point. This is the convergence OBPI.
- **Size (4):** Ceremony skill update + closeout form update + BDD + docs. Solid 2-3 day work unit.
- **Clarity (4):** Six requirements with clear blocking conditions. Edge cases for Lite-lane ADRs and partial product proof are explicitly addressed.

---

## Overall Verdict

**[x] GO — Ready for proposal/defense review**

**Weighted total: 3.75/4.0** exceeds 3.0 threshold.
**OBPI average: 3.70** exceeds 3.0 threshold.
**No dimension scores 1. No dimension scores 2.**

### Strengths

1. **Problem grounded in repository evidence** — ADR-0.15.0 is a real exemplar of the failure mode, not a hypothetical
2. **Anti-pattern is named and exemplified** — "more checkboxes" trap is backed by concrete evidence
3. **Gold standard cited and codified** — ADR-0.12.0's closeout discipline becomes the formal requirement
4. **Parallelizable decomposition** — OBPIs 01-03 independent, critical path depth of 2
5. **Every OBPI has verification commands** — concrete bash commands that prove completion
6. **Lite-lane handling is explicit** — proportional rigor without exemption
7. **Migration path is concrete** — four tiers covering every brief lifecycle state

### Weaknesses

1. **OBPI-01 lane tension** — brief acknowledges agent-facing contract change but assigns Lite; defensible but not airtight
2. **OBPI-03 assessment schema underspecified** — the reviewer agent's output format is named but not defined; risks implementation divergence
3. **OBPI-04 testability in isolation** — the integrator role makes standalone verification commands weaker; real proof requires all prior OBPIs

### Action Items

1. Consider specifying OBPI-03's assessment schema more concretely — even a 3-field example would reduce implementation ambiguity
2. Acknowledge the OBPI-01 lane tension explicitly in the ADR (the brief does, but the ADR's WBS table does not)
3. No blocking items — proceed to proposal/defense
