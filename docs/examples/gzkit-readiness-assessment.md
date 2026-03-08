# GZKit Readiness Assessment

## Student Greenfield Project Suitability

**Date:** 2026-03-08
**Evaluator:** Claude (Opus 4.6), commissioned by Jeff
**Target audience:** CIDM 6330/6395 graduate students
**Test candidate:** RHEA (Repository Harness for Entity Abstraction)

---

## Executive Summary

GZKit (v0.8.0) is a **production-quality governance CLI** that successfully
governs its own development through 9 completed ADRs, 305 passing tests, and
a comprehensive documentation suite. It is the real thing — not a toy.

**For student greenfield projects, it is not yet ready.** The tool works, but
the onboarding path assumes governance fluency that students won't have. The
gap is not in the tool's capabilities but in the **bridge between "install
this" and "now I understand what I'm doing."**

**Verdict: Ready for guided classroom use with instructor scaffolding. Not
ready for unguided student self-service.**

---

## Evaluation Criteria

| Criterion | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Installation and setup | High | B+ | `uv tool install gzkit && gz init` works cleanly |
| First-run experience | High | C | Quickstart exists but jumps past conceptual foundations |
| Conceptual clarity | High | B | Docs explain concepts but assume prior governance exposure |
| Workflow guidance | Medium | B- | Runbook and concept docs exist; no "first project" walkthrough |
| Error messages and help | Medium | B | CLI has help text; errors could be more instructive |
| Template quality | Medium | A- | Templates are well-structured; possibly too detailed for beginners |
| Documentation depth | Low | A | Comprehensive — 32 command pages, 6 concept docs, philosophy |
| Test coverage | Low | A | 305 tests, 11s runtime, high confidence in correctness |
| Extensibility | Low | A | Skill system, ledger, manifest — all extensible |

---

## Strengths for Student Use

### 1. It Actually Works

GZKit governs itself (dogfooding). The 9 completed ADRs, audit trails, and
ledger entries are real evidence that the workflow produces results. Students
would be using a tool that practices what it preaches.

### 2. Sound Conceptual Model

The workflow is pedagogically valuable:

```text
PRD (why build it?) → ADR (what design choices?) → OBPI (what tasks?) → Gates (is it done?)
```

This maps cleanly to software engineering fundamentals that grad students
should learn: requirements analysis, architectural reasoning, work
decomposition, and verification.

### 3. The Philosophy Document

`docs/user/why.md` is excellent teaching material. The "degradation pattern"
table (Week 1: careful review → Week 4: rubber stamp) resonates with anyone
who has used AI coding tools. This gives students a *reason* to care about
governance, not just a process to follow.

### 4. Lane Doctrine Supports Scaffolding

The Lite/Heavy lane system naturally supports progressive learning:

- **Week 1-4:** Lite lane (Gates 1-2 only: ADR + tests)
- **Week 5-8:** Heavy lane (add docs, BDD, attestation)

Students start with minimal ceremony and graduate to full governance as their
comfort grows.

### 5. CLI Is Well-Designed

The `gz` command namespace is intuitive: `gz init`, `gz prd`, `gz plan`,
`gz status`, `gz attest`. Students can discover commands through `gz --help`
without reading docs first.

---

## Gaps for Student Greenfield Projects

### Gap 1: No "First Project" Tutorial (Critical)

The quickstart goes from `gz init` straight to `gz prd GZKIT-1.0.0` and
`gz plan 0.1.0`. There is no worked example showing:

- What a student project PRD looks like (not gzkit's own PRD)
- What a student's first ADR contains
- What the output of each command looks like
- What decisions to make and why

**Impact:** Students will run the commands but won't understand what they're
producing or why.

**Recommendation:** Create a "First Project" guide using a simple domain
(e.g., a reading list app, a grade tracker) that walks through the full
cycle with verbatim command output.

### Gap 2: OBPI Complexity (High)

The OBPI brief template has 12+ sections including lanes, gates, allowed/
denied paths, discovery checklists, and evidence blocks. This is appropriate
for professional teams but overwhelming for students encountering governance
for the first time.

**Impact:** Students will either fill in boilerplate without understanding it,
or give up because the ceremony feels disproportionate to their small project.

**Recommendation:** Offer a "student task" mode that generates simplified
briefs (objective, requirements, acceptance criteria, verification — 5
sections instead of 12+). This is what the `docs/examples/templates/
task-template.md` companion guide provides.

### Gap 3: No Glossary (Medium)

Terms like "attestation", "ledger", "lane", "gate", "OBPI", "constitution",
and "closeout ceremony" are used throughout the docs without a central
glossary. Grad students in CIDM 6330/6395 will know some of these from
coursework, but the governance-specific meanings need definition.

**Impact:** Conceptual confusion slows adoption.

**Recommendation:** Add `docs/user/glossary.md` with 20-30 term definitions.

### Gap 4: Self-Referential Examples Only (Medium)

Every ADR example in gzkit is about gzkit itself (governance CLI features,
ledger schemas, skill mirroring). There are no examples from application
domains that students would recognize: web apps, APIs, data pipelines,
libraries.

**Impact:** Students struggle to map abstract governance concepts to their
own projects.

**Recommendation:** Add 2-3 example ADRs in a recognizable domain. The
student guide in `docs/examples/` begins this work.

### Gap 5: No Interview Transcript Examples (Low)

The PRD and ADR templates include a `## Q&A Transcript` section, and the
ADR creation workflow involves a mandatory defense/interview. But no example
transcript is published showing what this conversation looks like.

**Impact:** Students don't know what questions to expect or how to defend
their design decisions.

**Recommendation:** Publish 1-2 sanitized interview transcripts showing the
back-and-forth between human and AI agent during ADR creation.

---

## RHEA as a Test Case

RHEA is positioned as gzkit's first end-to-end development target. Its
current state (empty scaffold with a well-written README) makes it an ideal
test case for evaluating whether gzkit can bootstrap a greenfield project.

### What RHEA Tests

| Question | How RHEA Answers It |
|----------|---------------------|
| Can `gz init` set up governance from scratch? | RHEA has no `.gzkit/`, `AGENTS.md`, or config — pure greenfield |
| Can a PRD be written for a library (not a CLI)? | RHEA is a library with adapters, not a user-facing app |
| Do OBPI briefs work for small, focused deliverables? | RHEA's features (predicate DSL, adapters) are small and well-scoped |
| Can the gate chain verify library code? | Gate 2 (TDD) is the primary gate for libraries; heavy gates may be overkill |

### Recommended RHEA Bootstrap Sequence

1. `gz init` in the RHEA repo
2. `gz prd RHEA-1.0.0` — write a PRD from the existing README vision
3. `gz plan 0.1.0 --title "Core ReadRepo interface"` — first ADR
4. Create 3-4 OBPI briefs (ReadRepo interface, predicate DSL, in-memory
   adapter, SQLite adapter)
5. Implement in Lite lane (Gates 1-2 only)
6. `gz attest ADR-0.1.0 --status completed`

This sequence would reveal any friction points in the greenfield onboarding
path and produce a real worked example for student documentation.

---

## Readiness Verdict

| Dimension | Ready? | Notes |
|-----------|--------|-------|
| **Core CLI functionality** | Yes | Commands work; ledger, validation, gates functional |
| **Documentation quality** | Yes | Comprehensive but assumes governance fluency |
| **Professional team use** | Yes | Designed for this; proven by self-governance |
| **Instructor-guided classroom use** | Mostly | Instructor fills the onboarding gaps verbally |
| **Unguided student self-service** | No | Missing first-project tutorial, glossary, simplified templates |
| **Greenfield bootstrap (via RHEA)** | Untested | RHEA is the right test; should be attempted next |

---

## Recommended Next Steps

### Short-term (before next semester)

1. **Bootstrap RHEA with gzkit** — Prove the greenfield path works end-to-end
2. **Add glossary** — 20-30 governance terms defined for newcomers
3. **Publish a worked example** — One complete ADR cycle with command output
   in a recognizable domain (not gzkit self-governance)

### Medium-term (semester project)

4. **Student task mode** — Simplified brief generation (5 sections, not 12+)
5. **Interview transcript examples** — Show what PRD/ADR Q&A looks like
6. **"Learning mode" output** — Optional verbose output explaining gate
   concepts as students encounter them

### Long-term (if classroom adoption succeeds)

7. **Curriculum integration guide** — How to map gzkit ceremonies to course
   milestones (Sprint 1 = PRD + first ADR, Sprint 2 = implementation +
   gates, etc.)
8. **Student project gallery** — Curated examples of student work governed
   by gzkit
