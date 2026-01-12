# gzkit

**A Development Covenant for Human-AI Collaboration**

---

## The Zero Doctrine

The "Zero" in gzkit is not absence. It is primacy.

**Index zero.** The human. First in the value chain, final in authority.

gzkit is cognitive infrastructure that actively resists your replacement. It preserves human intent across agent context boundaries, gives agents constraints to reason against, creates verification loops both parties trust, and reserves final judgment for humans.

---

## The Honest Tradeoff

This is slower than multi-agent orchestration. **That's the point.**

Some people can YOLO through agentic workflows—let agents spawn agents, approve PRs in batches, ship at machine speed. If that works for you, gzkit is not your tool.

But here's the bet: **more people need the sanity of this pace than can handle the chaos of full autonomy.**

The friction is intentional. Reading everything is a pain in the ass. Q&A at every juncture slows you down. That friction is the feature. It keeps you in the chair.

---

## The Human Discipline

The covenant has two sides. Gates and lanes constrain agents. But the Zero Doctrine only holds if the human practices two disciplines:

### 1. Read Everything

Agents produce volume. The temptation is to skim, to trust, to let the green checkmarks speak for themselves.

**This is the failure mode.**

The agent cannot drift from intent if you notice the drift. Skimming is how the Zero abdicates without realizing it.

### 2. Insist on Q&A

At every critical juncture—design decisions, implementation choices, evaluation moments—stop and question.

Not optional. Not "when it feels necessary." **Insist.**

Q&A is not the agent's job. The agent will answer questions, but it will not ask them unprompted. The human must demand the conversation.

---

## Five Gates

| Gate | Name | Purpose |
|------|------|---------|
| 1 | **ADR** | Record intent and tradeoffs before implementation |
| 2 | **TDD** | Verify correctness through automated tests |
| 3 | **Docs** | Ensure documentation describes actual behavior |
| 4 | **BDD** | Verify external contracts through acceptance tests |
| 5 | **Human** | Human observes artifacts and attests completion |

**Lite lane** (internal changes): Gates 1, 2

**Heavy lane** (external contracts): Gates 1, 2, 3, 4, 5

Gate 5 cannot be automated. That's the whole point.

---

## Quick Start

```bash
# Install with uv
uv tool install gzkit

# Initialize in your project
gz init

# Create a new ADR
gz plan new "Feature description"

# Check status
gz status

# Verify gates
gz verify
```

---

## Opinionated

Like Django, Rails, and other opinionated tools, gzkit makes choices so you don't have to argue about them.

| Opinion | Rationale |
|---------|-----------|
| **Lite lane is default** | Most work doesn't need five gates |
| **ADRs before code** | Intent recorded before implementation |
| **Tests are non-negotiable** | Gate 2 applies to all lanes |
| **Docs are proof** | Documentation IS the verification |
| **Humans must observe** | Gate 5 cannot be automated |
| **Q&A must be adversarial** | Polite questions get polite non-answers |

Disagree? Fork it.

---

## Learn More

- [Charter](charter.md) — The covenant itself
- [Lineage](lineage.md) — Heritage from spec-kit and GovZero
- [Concepts](concepts/README.md) — The three concerns explained

---

<p style="text-align: center; color: #666; font-style: italic;">
The human is index zero.
</p>
