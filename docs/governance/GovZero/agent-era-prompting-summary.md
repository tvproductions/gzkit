# Agent-Era Prompting Summary (Nate B. Jones Transcript)

Source discussed by operator: "If You're Prompting Like It's Last Month, You're Already Late" (February 2026).

This summary captures the transcript's design-relevant claims for GovZero and `gzkit`.

---

## Core Thesis

Prompting has split into four different disciplines. Chat-era prompt craft alone is no longer sufficient for long-running autonomous agents.

Agents that run for hours or days require intent, context, and specification to be encoded before execution starts.

---

## Four Disciplines

1. Prompt Craft
- Clear instructions, examples/counterexamples, guardrails, output shape, ambiguity handling.
- Still required, but now table stakes.

2. Context Engineering
- Curate the token environment, not just one prompt.
- Control surfaces, retrieval, memory, and project conventions determine quality ceiling.

3. Intent Engineering
- Encode goals, values, trade-off rules, and escalation boundaries.
- Prevents "optimizing the wrong metric" failures.

4. Specification Engineering
- Write executable specs for work that spans long time horizons.
- Treat organizational documents as machine-operable specifications.

---

## Five Specification Primitives

1. Self-contained problem statements
- Task is solvable without implicit tribal context.

2. Acceptance criteria
- "Done" is independently verifiable.

3. Constraint architecture
- Musts, must-nots, preferences, escalation triggers.

4. Decomposition
- Work broken into independently executable/verifiable units.

5. Evaluation design
- Recurring test/eval cases with regression detection after updates.

---

## TDD and BDD Mapping

gzkit's existing gate model directly supports Nate's framework:

- Gate 2 (TDD) strengthens acceptance criteria and evaluation design through executable unit-test evidence.
- Gate 4 (BDD) strengthens self-contained problem statements and intent alignment through behavior-level contract checks.
- Together, TDD + BDD reduce "looks-right" outputs by enforcing measurable correctness at both implementation and behavior layers.

---

## Why This Matters For GovZero

GovZero already encodes several agent-era strengths:

- Gate model and lane doctrine
- Human authority boundary (attestation)
- Evidence-first closeout and audit flow
- Canonical control surfaces (`AGENTS.md`, `CLAUDE.md`, instructions, skills)

The transcript implies the next maturity step: readiness must be measured as a runtime contract, not only described in docs.

---

## gzkit Design Implications

1. Make readiness executable
- Add and maintain `gz readiness audit` with deterministic PASS/FAIL semantics.

2. Keep context surfaces synchronized
- Discovery index, control surfaces, runbooks, and command docs must stay coherent.

3. Elevate specification quality
- OBPI/ADR templates must preserve self-contained tasks, constraints, and acceptance criteria.

4. Institutionalize evaluation
- Include parity/readiness regression checks in routine quality gates.

5. Preserve human judgment boundary
- Automation can score readiness, but final authority remains with human attestation.

---

## Practical Operating Rule

For long-running agent tasks, do not rely on real-time correction. Encode context, intent, constraints, and verification criteria up front, then run deterministic checks before completion claims.
