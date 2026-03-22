<!-- markdownlint-disable-file MD013 MD022 MD032 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

ADR: ADR-0.24.0: Skill Documentation Contract
Evaluator: Codex (`gz-adr-eval --red-team`)
Date: 2026-03-22

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 4 | 0.60 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

**WEIGHTED TOTAL: 3.15/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

## ADR Dimension Rationale

1. **Problem Clarity - 3/4**
   The problem remains concrete in
   [ADR-0.24.0-skill-documentation-contract.md](./ADR-0.24.0-skill-documentation-contract.md):
   gzkit has 52 `SKILL.md` files but no operator-facing skill documentation
   surface, and the repository lacks doctrine for when manpages, runbooks, and
   docstrings are required. The before/after state is specific. It stops at 3
   because the tidy-first audits are still proposed rather than summarized as a
   measured baseline.

2. **Decision Justification - 3/4**
   The ADR now has a real alternatives section in
   [ADR-0.24.0-skill-documentation-contract.md](./ADR-0.24.0-skill-documentation-contract.md),
   and each rejected option attacks a plausible shortcut: `SKILL.md`-only
   documentation, runbook-only documentation, mechanical generation, and
   docstrings-only coverage. The rationale is defensible and internally
   consistent. It remains a 3 because it is strong without yet being a
   repository-gold-standard argument anchored to multiple historical ADR
   exemplars.

3. **Feature Checklist - 4/4**
   The structural defect is fixed. The ADR now presents five numbered
   capabilities that map 1:1 to the five briefs, and the necessity table
   explains the concrete loss if any item disappears. The items are at
   consistent granularity, independently valuable, and logically ordered.

4. **OBPI Decomposition - 3/4**
   The package is now explicit about sequencing and parallelization in
   [ADR-0.24.0-skill-documentation-contract.md](./ADR-0.24.0-skill-documentation-contract.md):
   taxonomy feeds template and surface work; pilot pages depend on those; the
   runbook entries close the loop once the manpages exist. The boundaries are
   clear and the graph is acyclic. It remains solid rather than exemplary
   because OBPI-05 is still the broadest work unit in the package.

5. **Lane Assignment - 3/4**
   Lite lane is now explicitly defended: the ADR changes documentation doctrine
   and operator docs surfaces, but not CLI, API, schema, or runtime behavior.
   That matches local lane rules in [AGENTS.md](../../../../../AGENTS.md). The
   reasoning is correct and concrete, even if brief.

6. **Scope Discipline - 3/4**
   The ADR now includes `Non-Goals` and `Scope Creep Guardrails`, and the
   boundaries line up with the briefs. It clearly excludes command redesign,
   repository-wide automation, and `SKILL.md` semantic changes. That resolves
   the prior ambiguity.

7. **Evidence Requirements - 3/4**
   The package now includes an ADR-level verification spine plus
   brief-specific `VERIFICATION COMMANDS` sections in
   [OBPI-0.24.0-01-documentation-taxonomy.md](./briefs/OBPI-0.24.0-01-documentation-taxonomy.md),
   [OBPI-0.24.0-02-skill-manpage-template.md](./briefs/OBPI-0.24.0-02-skill-manpage-template.md),
   [OBPI-0.24.0-03-skills-surface-and-index.md](./briefs/OBPI-0.24.0-03-skills-surface-and-index.md),
   [OBPI-0.24.0-04-runbook-skill-entries.md](./briefs/OBPI-0.24.0-04-runbook-skill-entries.md),
   and
   [OBPI-0.24.0-05-pilot-skill-manpages.md](./briefs/OBPI-0.24.0-05-pilot-skill-manpages.md).
   An evaluator can now write the proof script directly from the package. It
   remains a 3 because several checks are still grep/path-based rather than
   runtime contract tests.

8. **Architectural Alignment - 3/4**
   The ADR now names local documentation exemplars explicitly:
   `docs/user/commands/`, `docs/user/commands/index.md`,
   `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, and
   `.claude/skills/*/SKILL.md`. The operator/agent/developer audience split is
   now structurally aligned with existing repository surfaces rather than
   asserted abstractly.

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 4 | 3 | 4 | 4 | 4 | 3.8 |
| 02 | 4 | 3 | 4 | 4 | 4 | 3.8 |
| 03 | 3 | 3 | 4 | 4 | 4 | 3.6 |
| 04 | 3 | 3 | 4 | 4 | 3 | 3.4 |
| 05 | 3 | 3 | 4 | 3 | 4 | 3.4 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.**

## OBPI Notes

- **OBPI-01** is strong: it owns the doctrine layer cleanly and has direct
  path-level proof commands for the taxonomy artifact and ADR linkage.
- **OBPI-02** remains a well-bounded template unit with clear operator-facing
  requirements and targeted section checks.
- **OBPI-03** depends naturally on the taxonomy/template decisions, but its
  value and proof story are now concrete.
- **OBPI-04** improved materially: the proof commands now assert actual
  runbook links into the skill surface instead of a vague reference to docs in
  general.
- **OBPI-05** is broader than the others, but fixing the pilot set as six named
  skills makes the deliverable much clearer and more reproducible.

## Red-Team Challenges

| # | Challenge | Result (Pass/Fail) | Notes |
|---|-----------|-------------------|-------|
| 1 | So What? | Pass | The ADR now includes a checklist necessity table that states the concrete repository/operator loss for removing any of the five items. |
| 2 | Scope | Pass | `Non-Goals` and `Scope Creep Guardrails` now bound the ADR to doctrine, docs surface, and workflow insertion points without spilling into command redesign or skill-semantics changes. |
| 3 | Alternative | Pass | Five OBPIs remains a defensible split: doctrine, template, discovery surface, workflow integration, and real-surface validation each own a distinct capability. |
| 4 | Dependency | Pass | The dependency graph is now explicit, and the only downstream bottleneck is the expected one: pilot manpages must exist before runbooks can link them. |
| 5 | Gold Standard | Pass | Compared with [ADR-0.21.0-tests-for-spec.md](../ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md), ADR-0.24.0 now matches the local standard for alternatives, checklist necessity, dependency framing, and verification spine. |
| 6 | Timeline | Pass | The critical path is explicit: `OBPI-01 -> OBPI-02 -> OBPI-05 -> OBPI-04`, while `OBPI-03` can progress in parallel after the taxonomy settles. |
| 7 | Evidence | Pass | Every OBPI now has exact proof commands, and the ADR carries a verification spine instead of forcing evaluators to invent the proof contract. |
| 8 | Consumer | Pass | An operator can now answer the key readiness questions: where the docs will live, how skills will be discovered, how runbooks will point to them, and which pilot pages prove the template works. |
| 9 | Regression | Pass | `Long-Term Validity Guards` now define what doctrinal drift looks like: adding operator-invocable skills without the required taxonomy, skill-surface, or runbook updates. |
| 10 | Parity | Pass | The weakest alignment claim is that the skill docs surface should parallel command docs; the ADR now narrows that to discovery and operator-reference shape rather than claiming skills and commands are semantically identical. |

**RED-TEAM THRESHOLD: <=2 failures = GO, 3-4 = CONDITIONAL GO, >=5 = NO GO**
**RED-TEAM RESULT: 0 failures -> GO**

## Overall Verdict

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

## Action Items

1. No blocking structural actions.
2. Optional improvement: summarize the tidy-first audit results in the ADR once
   gathered to lift Problem Clarity from solid to exemplary.
3. Optional improvement: add one concrete local command-manpage file citation
   if you want Architectural Alignment to move from 3 to 4.
