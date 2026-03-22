# Student Guides and Templates

## CIDM 6330/6395 — Software Engineering Governance

---

This directory contains student-oriented guides, templates, and assessments
for learning software engineering governance practices. All materials use a
**template-first approach** — you create governance artifacts manually from
templates using a text editor and git. No special tooling required.

> **New here?** Start with the [video tutorial series](presentations/index.md),
> then work through the [First Project tutorial](tutorial-first-project.md).

## Presentations

| Resource | What You'll Learn |
|----------|-------------------|
| [Video Tutorial Series](presentations/index.md) | Six-part video series covering the full governance cycle with a worked example |

Individual parts cover: why governance matters, PRDs, ADRs, task decomposition,
implementation, and the full cycle in review. Slide decks included.

## Guides

| Guide | What You'll Learn | Video |
|-------|-------------------|-------|
| [PRD Guide](guide-prd.md) | What a Product Requirements Document is, why you write one, and how to write one well | [Part 2](presentations/part2-script.md) |
| [ADR Guide](guide-adr.md) | What an Architecture Decision Record is, why design decisions should be recorded, and how to write one | [Part 3](presentations/part3-script.md) |
| [Task Guide](guide-tasks.md) | How to decompose features into small, testable tasks with clear acceptance criteria | [Part 4](presentations/part4-script.md) |

**Recommended reading order:** PRD Guide → ADR Guide → Task Guide

## Tutorials

| Tutorial | What You'll Do |
|----------|---------------|
| [First Project](tutorial-first-project.md) | Build a reading list tracker from templates through the full governance cycle (setup → attest) with worked examples |
| [RHEA Bootstrap](tutorial-rhea-bootstrap.md) | Bootstrap a real greenfield library project with gzkit — the litmus test for student readiness |

**Start here:** The First Project tutorial walks through every step with
expected output. Do this before your own project.

## Reference

| Document | Contents |
|----------|----------|
| [Glossary](glossary.md) | 25+ governance terms defined with examples |

## Templates

Ready-to-use templates in this directory:

| Template | Use When |
|----------|----------|
| [PRD Template](templates/prd-template.md) | Starting a new project — define what you're building and why |
| [ADR Template](templates/adr-template.md) | Making a design decision — record the choice, alternatives, and tradeoffs |
| [REQ Template](templates/req-template.md) | Breaking an ADR into requirements — one REQ per requirements checklist item |
| [Task Template](templates/task-template.md) | Leaf work items under a REQ — one concrete thing to build, fix, or change |

## Distribution

| Document | Contents |
|----------|----------|
| [Releasing Guide](guide-releasing.md) | How to tag a release, build binaries, and publish to PyPI |

## Assessments

| Document | Contents |
|----------|----------|
| [GZKit Readiness Assessment](gzkit-readiness-assessment.md) | Evaluation of gzkit's suitability for student greenfield projects |
| [Go-Live Gap Analysis](go-live-gap-analysis.md) | What gzkit needs before students can use it independently |
| [Framework Comparison](comparison-gzkit-speckit-bmad.md) | How gzkit compares to OpenSpec, GitHub Spec Kit, and BMAD Method |

## The Workflow

```text
1. Write a PRD ──→ Define WHAT to build and WHY
2. Write ADRs  ──→ Record HOW you'll approach each major feature
3. Create Tasks ──→ Break each ADR into small, testable deliverables
4. Implement    ──→ Build one task at a time, verify each one
5. Review       ──→ Demonstrate that acceptance criteria are met
```

## Relationship to GZKit

These guides simplify gzkit's professional governance workflow for classroom
use. The mapping:

| Student Concept | GZKit Professional Equivalent |
|----------------|------------------------------|
| PRD | PRD (same concept, lighter template) |
| ADR | ADR with Requirements Checklist |
| REQ | OBPI Brief (One Brief Per Item) |
| Task | Leaf work item within an OBPI |
| "All tests pass" | Gate 2 (TDD) |
| Instructor review | Gate 5 (Human Attestation) |

Students who want to explore the full professional workflow can install gzkit
(`uv tool install gzkit`) and use `gz init` to bootstrap governance in their
project. See the [Readiness Assessment](gzkit-readiness-assessment.md) for
current status and recommendations.
