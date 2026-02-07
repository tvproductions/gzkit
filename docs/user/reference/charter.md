# The gzkit Charter

Status: Active
Version: 1.2
Authority: Canon (sole authority for covenant definitions)

This document defines the **Development Covenant**—the binding agreement between human and agent for how work gets done.

---

## The Zero Doctrine

The "Zero" in gzkit is not absence. It is primacy.

**Index zero.** The human. First in the value chain, final in authority.

| Evolution | Meaning |
|-----------|---------|
| **Originally** | Resistance to ceremony bloat in agent-assisted development |
| **Now** | Resistance to any source of truth that is not human-centric |

The Zero Doctrine holds that:

1. **The human is index zero** — First in priority, last in override
2. **Agents serve, not decide** — They generate evidence; humans render judgment
3. **Ceremony is debt** — Every gate must earn its place or be killed
4. **Silence is abdication** — Passive approval is not approval

gzkit exists to prevent the human from drifting to rubber-stamp. When the agent becomes the de facto authority, the Zero erodes. This tool actively resists that drift.

---

## The Human Discipline

The covenant has two sides. Gates and lanes constrain agents. But the Zero Doctrine only holds if the human practices two disciplines.

### The Tradeoff

Let's be honest: **this is slower than agent orchestration.**

Multi-agent autopilot exists. Some people YOLO their way through agentic workflows and ship fast. If that works for you, gzkit is not your tool.

But here's the bet: **more people need the sanity of this pace than can handle the chaos of full autonomy.**

The speed of agent orchestration comes at a cost: architectural agency drifts from human to machine. You stop understanding your own codebase. You approve PRs you didn't read. You attest to work you didn't verify. The agent becomes the architect, and you become the rubber stamp.

gzkit is slower because it keeps architectural agency with the human. That's not a bug. That's the entire point.

### 1. Read Everything

Agents produce volume. They are eager, thorough, and fast. The temptation is to skim, to trust, to let the green checkmarks speak for themselves.

**This is the failure mode.**

Reading everything means:
- Every line of generated code, not just the diff summary
- Every test, not just the pass/fail count
- Every explanation, not just the conclusion
- Every warning, not just the errors

Yes, this is a pain in the ass. **That's the feature.**

The friction is intentional. It forces you to stay engaged. It prevents you from becoming a passive observer of your own project. The agent cannot trick you if you read what it wrote. The agent cannot drift from intent if you notice the drift.

Skimming is how the Zero abdicates without realizing it. Reading everything is how you keep the chair.

### 2. Insist on Q&A

At every critical juncture—design decisions, implementation choices, evaluation moments—stop and question.

Not optional. Not "when it feels necessary." **Insist.**

| Juncture | Questions to ask |
|----------|------------------|
| **Design** | "What problem are we actually solving? What are we not solving?" |
| **Implementation** | "Why this approach? What's the tradeoff? What could break?" |
| **Evaluation** | "Does this actually work? Did I verify it myself? What did I miss?" |

Q&A is not the agent's job. The agent will answer questions, but it will not ask them unprompted. The human must demand the conversation.

### Why These Two

These disciplines compound:
- Reading everything surfaces the questions worth asking
- Asking questions reveals what you missed in reading
- Together, they keep the human engaged and authoritative

Without them, the covenant is theater. The gates pass, the attestations record, but the human never actually verified anything. The Zero becomes a rubber stamp with extra steps.

**The gates are scaffolding. These two practices are the discipline.**

---

## The Covenant

A development covenant is an explicit, binding agreement that:

1. **Preserves intent** across context boundaries
2. **Provides constraints** agents can reason against
3. **Creates verification loops** both parties trust
4. **Reserves judgment** for humans

This is not governance in the compliance sense. It is cognitive infrastructure that actively resists your replacement.

---

## Authority Boundary

| Role | Authority |
|------|-----------|
| **Human** | Originates intent; defines constraints; attests completion |
| **Agent** | Interprets intent; operates within constraints; generates evidence |
| **Verification** | Mutual—tests, checks, and audits that both parties trust |

Human attestation is the closeout gate. Agents cannot attest on behalf of humans.

---

## Q&A Imperative

**Q&A is mandatory at every design phase.** Not optional. Not "when helpful." Mandatory.

Q&A is the forcing function that keeps index zero engaged. Without it, humans drift to passive approval. The agent becomes the de facto decision-maker. The covenant fails silently.

### The Four Modes

| Mode | Purpose | Example |
|------|---------|---------|
| **Exploratory** | Surface unstated assumptions | "What are we actually trying to do here?" |
| **Expansive** | Widen the solution space | "What else could go wrong? What haven't we considered?" |
| **Critical** | Challenge necessity | "Is this needed or are we adding ceremony?" |
| **Adversarial** | Stress-test completeness | "You think this is done? Prove it." |

### When Q&A Applies

- **Gate 1 (ADR):** Before an ADR is accepted, Q&A must challenge the problem statement and decision rationale
- **Gate 5 (Attestation):** Before attestation, Q&A must verify the human actually observed the artifacts
- **Any design decision:** If the agent proposes, the human must engage critically

### Q&A is Not

- A checklist to complete
- A formality to satisfy
- Something the agent can do on the human's behalf

Q&A exists because humans are lazy and agents are eager. Left unchecked, the agent will happily do all the thinking. That is the failure mode gzkit exists to prevent.

---

## Five Gates

All work flows through gates. Gates are verification checkpoints, not bureaucratic hurdles.

### Gate 1: ADR (Intent)

**Purpose:** Record intent and tradeoffs before implementation.

**Artifact:** ADR document with problem statement, decision, and consequences.

**Applies to:** All work (Lite and Heavy lanes).

---

### Gate 2: TDD (Tests)

**Purpose:** Verify implementation correctness through automated tests.

**Artifact:** Passing tests with reasonable coverage.

**Applies to:** All work (Lite and Heavy lanes).

---

### Gate 3: Docs (Documentation)

**Purpose:** Ensure documentation accurately describes behavior.

**Artifact:** User documentation, command manpages, and an operator runbook that build cleanly, resolve links, and match code behavior.

**Applies to:** Heavy lane only.

---

### Gate 4: BDD (Behavior)

**Purpose:** Verify external contract behavior through acceptance tests.

**Artifact:** Passing acceptance scenarios for CLI/API/schema contracts.

**Applies to:** Heavy lane only.

---

### Gate 5: Human (Attestation)

**Purpose:** Human directly observes artifacts and attests to completion.

**Artifact:** Explicit human attestation with timestamp.

**Applies to:** Heavy lane only.

**Authority:** Human attestation is the sole authority for completion. Agents present artifacts; humans observe and attest.

---

## Lane Doctrine

| Lane | Gates | Trigger |
|------|-------|---------|
| **Lite** | 1, 2 | Internal changes (no external contract changes) |
| **Heavy** | 1, 2, 3, 4, 5 | External contract changes (CLI, API, schema) |

Default lane is Lite. Escalate to Heavy when external contracts change.

---

## Attestation Terms

Human attestation uses one of these exact forms:

| Term | Meaning |
|------|---------|
| **Completed** | Work finished; all claims verified |
| **Completed — Partial: [reason]** | Subset accepted; remainder deferred |
| **Dropped — [reason]** | Work rejected; rationale provided |

These terms are canonical. Other terms are not valid for closeout.

---

## The Three Concerns

The covenant spans three concerns:

### Specification (Agent-Native)

What invariants must hold. Explicit constraints, declarative intent, acceptance criteria.

Agents ground against specification. It should be:
- Constraint-forward (NEVER/ALWAYS rules)
- Testable (verifiable claims)
- Immutable once accepted (canon)

### Methodology (Shared)

How work flows through phases. Gates, checkpoints, verification loops.

Methodology provides structure. It should be:
- Sequential where dependencies exist
- Parallel where independent
- Observable (status is always knowable)

### Governance (Human-Native)

Who has authority to decide. Attestation, audit, closeout.

Governance reserves judgment. It should be:
- Explicit (written down)
- Human-final (Gate 5)
- Auditable (evidence trail)

---

## Principles

gzkit is opinionated. These are not suggestions.

1. **The human is index zero** — First in priority, final in authority, non-negotiable
2. **Q&A is mandatory** — No silent approvals; engagement is required
3. **Governance is verification, not celebration** — Gates produce evidence, not theater
4. **Silence is abdication** — Unstated assumptions are invalid; passive approval is failure
5. **Ceremony is debt** — If a gate doesn't change behavior, kill it
6. **Artifacts survive sessions** — Intent must persist across context boundaries
7. **Constraints are first-class** — Agents need explicit boundaries to reason against
8. **Human attestation is final** — No automation bypasses Gate 5
9. **Sarcasm is valid** — Critical engagement beats polite compliance

---

## Opinions

Like Django, Rails, and other opinionated tools, gzkit makes choices so you don't have to argue about them.

| Opinion | Rationale |
|---------|-----------|
| **Lite lane is default** | Most work doesn't need five gates. Escalate when contracts change. |
| **ADRs before code** | Intent recorded before implementation prevents drift. |
| **Tests are non-negotiable** | Gate 2 applies to all lanes. No exceptions. |
| **Docs are proof** | Gate 3 proof comes from user docs, manpages, and runbook fidelity to real behavior. |
| **Humans must observe** | Gate 5 cannot be automated. That's the point. |
| **Q&A must be adversarial** | Polite questions get polite non-answers. Push back. |

These opinions exist because decision fatigue is real and bike-shedding is expensive. Disagree? Fork it.

---

## References

- [Lineage](lineage.md) — Heritage from spec-kit and GovZero
- [Gates](../concepts/gates.md) — The five verification gates
- [Lanes](../concepts/lanes.md) — Lite and Heavy lanes
