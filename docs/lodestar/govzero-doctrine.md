# GovZero & gzkit

## Cooperative Design, Governance, and Correctness at the Edge of Computation

> **“My cost is the cost of learning, understanding, and striving for truth in correctness.”**

---

## Executive Summary

This report describes **GovZero** and **gzkit** as a single, inextricable system for **cooperative design between humans and non-deterministic, non-learning agents**. The system is not speed-first, YOLO, or agent-swarm oriented. Instead, it formalizes **habits, rituals, and ceremonies** that increase the odds a human can **assure correctness** despite the agent’s lack of memory, learning, and determinism.

The system’s organizing doctrine is **SPRINT / DRIFT**, adapted from anti-submarine warfare (ASW): rapid execution to regain contact (**SPRINT**), followed by deliberate slowing to sense, classify, and judge (**DRIFT**). In this context, agents sprint; humans drift. Artifacts, invariants, and ceremonies exist to make drift possible, repeatable, and meaningful.

---

## Canonical Source

**AirlineOps is the canonical reference implementation of GovZero.**

GovZero emerged inside AirlineOps under operational pressure, not as a designed framework. Its durability comes from enforcement machinery, not documentation. Treating AirlineOps as precedent rather than canon produces silent drift and false confidence.

### Location

AirlineOps lives at `../airlineops/` relative to gzkit (sibling directory under the same parent).

### Authoritative Artifacts

| Location | Contains |
|----------|----------|
| `../airlineops/.github/skills/gz-*` | GovZero agent skills (OBPI, ADR, sync, audit) |
| `../airlineops/docs/governance/GovZero/*` | Governance documentation |

### Divergence Rule

For any governance concept present in AirlineOps, gzkit MUST:

1. Treat AirlineOps as the source of truth
2. Preserve both structure *and* enforcement machinery
3. Reject divergent or weakened translations

**Divergence from AirlineOps requires explicit ADR authorization.** No silent reinterpretation.

Where AirlineOps has no corresponding concept, gzkit may introduce one only explicitly and additively (documented in an ADR).

---

## 1. GovZero's Purpose and Vision

**GovZero** is a governance framework **and** a cooperative design system. It exists to protect **human appraisal, appreciation, and judgment** when working daily with fast, unreliable collaborators.

### Core Intent

GovZero exists to:

- Formalize **habits and rituals** that surface design truths during **design, development, and execution**
- Encode **invariants and quality gates** that cannot be skipped
- Require **human involvement** at moments where judgment matters
- Increase the probability that a human can **assure correctness under uncertainty**

GovZero assumes:

- Agents do **not** learn
- Agents forget
- Agents are non-deterministic
- Agents may fail to obey

Accordingly, GovZero does not optimize velocity. It optimizes **truth-seeking under uncertainty**.

### SPRINT / DRIFT Doctrine

GovZero is organized around **SPRINT / DRIFT**, grounded in ASW operational doctrine:

- **SPRINT**
  The agent executes quickly—exploring solution space, decomposing work, producing code and plans.

- **DRIFT**
  The human deliberately slows—reviewing artifacts, interpreting signals, performing appreciation and judgment, and deciding whether contact with correctness is real or noise.

GovZero encodes the **DRIFT**: the pauses, gates, and ceremonies that make reflection mandatory before acceptance.

---

## 2. gzkit as the Material Enabler

**gzkit** is the **material enabler** that makes GovZero operable in daily work. GovZero without gzkit is aspirational; gzkit without GovZero is just tooling.

### What gzkit Is

gzkit provides:

- A **command surface (`gz`)** where cooperative work is conducted
- A **runtime substrate** for longitudinal agent–human collaboration
- A **memory system** (repository artifacts plus remote persistence)
- A **ritual boundary** where execution, sensing, and reflection occur

gzkit is not an accessory. It is where cooperative design becomes executable.

### Ritual, Not Convenience

`gz` commands are not wrappers for convenience. They are **ceremonial checkpoints**:

- how work is started
- how it is paused
- how it is verified
- how it is reflected upon
- how it is closed

Each invocation creates an opportunity for **inspection, evidence capture, and recalibration**, supporting the DRIFT phase without negating SPRINT.

---

## 3. Governance Mechanics

### Design → Acceptance → Validation

GovZero operationalizes cooperative design through a deliberate progression:

1. **Design / Plan** – articulate intent and constraints
2. **Specify / Plan** – make intent precise and reviewable
3. **Design Decomposition for Tasking** – break work into accountable units
4. **Task State & Plan State Tracking** – maintain visibility into progress and drift
5. **Acceptance Ceremonies** – pause for human appraisal
6. **Validation Procedures** – execute checks tied to invariants
7. **Human Attestation** – explicit human judgment that the outcome matches intent

These mechanics exist to **force moments of appreciation**—to slow down where correctness matters.

---

## 4. Agent Behavioral Telemetry (ABT)

> **Agents don’t learn. They review, calibrate, and (maybe, if you are lucky) obey.**

### What ABT Is

- **ABT is not a telemetry schema.**
- **ABT is a longitudinal behavioral evidence stream.**

ABT captures execution-time signals (e.g., verifier or linter outcomes) as **behavioral evidence** tied to concrete runs and commits. Its purpose is to support **agent review, calibration, and habit shaping over time**.

### What ABT Is Not

ABT is **not**:

- a bug tracker
- a quality gate
- a test framework
- a learning system

Quality repair is handled elsewhere. ABT is **process control**, not defect remediation.

### Governance Relationship

ABT is explicitly **non-normative** with respect to GovZero gates:

- Not Gate 2 evidence
- Not Gate 5 attestation
- Not blocking by default

Promotion follows a **hybrid model**:

- the **agent proposes** interpretations or constraints
- the **human ratifies** any promotion into control surfaces or enforcement

ABT is a **first-class feature of gzkit**, illustrating how the system handles obedience and calibration gaps over time—without confusing evidence with authority.

---

## 5. Categorical Context (Non-Competitive)

This system occupies a **distinct category**.

Different frameworks optimize for different axes:

- Specification clarity
- Role coverage
- Velocity

**GovZero + gzkit optimize human assurance of correctness under computational uncertainty.**

This is not a competitive claim; it is an axis distinction.

---

## 6. Strengthening GovZero for Agent-Paired Development

The system strengthens agent-paired development by:

- Treating **human judgment as sovereign**
- Encoding **SPRINT / DRIFT** as an operational rhythm
- Using **rituals and ceremonies** to surface truth
- Maintaining **memory and evidence** across runs
- Allowing agents to move fast without being trusted blindly

Speed is permitted. Reflection is enforced. Correctness remains the objective.

---

## Conclusion

GovZero and gzkit form a single cooperative design system. Together, they formalize habits, rituals, and ceremonies that allow humans to work productively with fast, unreliable agents—without surrendering judgment or truth.

> **“My cost is the cost of learning, understanding, and striving for truth in correctness.”**

That cost is intentional—and this system exists to make paying it worthwhile.
