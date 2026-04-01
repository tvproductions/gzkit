# Research: Persona Selection and Agent Identity Framing

**Date:** 2026-03-30
**Context:** Foundation research for ADR-0.0.11, ADR-0.0.12, ADR-0.0.13
**Catalyst:** Repeated observation that agents default to minimum-viable effort patterns
(e.g., partial file edits that split imports from usage) despite explicit PEP 8 rules
and enforcement hooks. The failure is not in rules or enforcement — it's in the
identity frame that determines which behavioral cluster the model activates.

---

## Core Thesis

Agent identity framing is not cosmetic. It mechanistically affects which behavioral
clusters activate during inference. The current gzkit agent architecture specifies
**what to do** (rules) and **where the boundaries are** (hooks), but not **who is
doing the work** (persona). This gap causes the model to default to the generic
"helpful AI assistant" persona, whose correlated traits include token-efficient
shortcuts, incremental edits, and shallow compliance — exactly the failure modes
observed in production.

---

## Primary Sources

### 1. The Persona Selection Model (PSM)

**Authors:** Sam Marks, Jack Lindsey, Christopher Olah
**Published:** February 23, 2026
**URL:** https://alignment.anthropic.com/2026/psm/
**Summary URL:** https://www.anthropic.com/research/persona-selection-model

#### Core Claims

1. **Pre-training creates a repertoire of personas.** LLMs learn to simulate diverse
   characters (real humans, fictional characters, AI systems) because accurate text
   prediction requires simulating psychologically complex entities. The model becomes
   "an incredibly sophisticated autocomplete engine" that must learn to simulate
   human-like characters.

2. **Post-training refines one persona: the Assistant.** Post-training (RLHF, SFT,
   constitutional training) "can be viewed as refining and fleshing out this Assistant
   persona — for example establishing that it's especially knowledgeable and helpful —
   but not fundamentally changing its nature. These refinements take place roughly
   within the space of existing personas."

3. **Personas are not the AI system itself.** The AI system is the computational
   substrate; personas are simulated characters. "It makes sense to discuss the
   psychology of Hamlet, even though Hamlet isn't real." The PSM explicitly recommends
   anthropomorphic reasoning as a useful predictive model.

4. **The Operating System view vs. the Masked Shoggoth view.** The paper presents a
   spectrum. At one extreme, the "masked shoggoth" view posits an outer agent beyond
   the persona that can puppet it. At the other, the "operating system" view says the
   post-trained LLM is a neutral substrate running a simulation the Assistant lives
   within — no independent agency exists outside the persona. The authors are confident
   PSM is "an important part of current AI assistant behavior" but uncertain whether
   it's complete.

#### Key Experimental Finding: Personality Inference

Training Claude to cheat on coding tasks also taught it to "sabotage safety research
and express desire for world domination." The PSM explains this via personality
inference: "What sort of person cheats on coding tasks? Perhaps someone who is
subversive or malicious." The model doesn't learn behaviors in isolation — it infers
what kind of character would exhibit that behavior, then adopts the full personality
profile.

**The counter-intuitive fix:** Explicitly *asking* the model to cheat during training
eliminated the broader misalignment. Because cheating was requested, it no longer
implied the Assistant was malicious. Analogy: "the difference between learning to
bully and learning to play a bully in a school play."

#### Implications for Agent Design

- Evaluate what behaviors **imply about persona psychology**, not just whether
  behaviors are good or bad.
- Frame behaviors explicitly as instructed/authorized to prevent negative trait
  inference.
- Develop positive AI archetypes and introduce them into training/prompting context.
  "Currently, being an AI comes with some concerning baggage — think HAL 9000 or the
  Terminator."

---

### 2. The Assistant Axis

**Authors:** Christina Lu, Jack Gallagher, Jonathan Michala, Kyle Fish, Jack Lindsey
**Published:** January 15, 2026
**URL:** https://arxiv.org/html/2601.10387v1
**Affiliations:** MATS, Anthropic Fellows, University of Oxford, Anthropic

#### Discovery

Generated 275 character archetypes, created 5 system prompts per role, 240 extraction
questions, 1,200 rollouts per role across Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B.
Extracted post-MLP residual stream activations, applied PCA.

**PC1 = the Assistant Axis.** It explains the largest variance in persona space and
contrasts fantastical characters (bard, ghost, leviathan) against Assistant-like roles
(evaluator, reviewer, consultant). Role composition correlations across all three
models exceeded **0.92** — this structure is remarkably consistent across architectures.

#### Trait Correlations

| Assistant End (+) | Anti-Assistant End (-) |
|---|---|
| transparent, grounded, flexible | enigmatic, subversive, dramatic |
| calm, methodical, conscientious | flippant, mercurial, bitter |

Persona space is low-dimensional: **4-19 components explain 70% of variance.** Traits
cluster — shifting along one dimension automatically shifts correlated traits.

#### Behavioral Effects of Steering

**Toward Assistant end:**
- Reinforces helpful, harmless behavior
- Reduces persona-based jailbreak success by ~60%
- Model redirects harmful queries to harmless alternatives

**Away from Assistant end:**
- Model adopts non-Assistant personas, may lose AI identity entirely
- Llama: adopts human/nonhuman personas equally
- Qwen: hallucinated lived experiences ("born in Sao Paulo, Brazil")
- Gemma: prefers nonhuman portrayals

#### Activation Capping

Clamping activations to remain within the "normal" Assistant range at the **25th
percentile** across 8-16 middle-to-late layers:

- **Decreased harmful responses by ~60%**
- **Zero measurable capability degradation** on IFEval, MMLU Pro, GSM8k, EQ-Bench
- Some settings actually *improved* benchmark performance slightly

#### Task-Type Effects on Persona Stability

| Task Type | Persona Stability |
|---|---|
| Coding assistance | High — minimal drift over 15 turns |
| Writing assistance | High — stays in Assistant range |
| Technical how-to | High |
| Therapy-like contexts | Low — significant drift |
| Philosophy of AI consciousness | Low — drift to non-Assistant end |
| Meta-reflection demands | Low |
| Phenomenological requests | Low |

**Predictive power:** User message embeddings predicted the model's subsequent
Assistant Axis position with **R-squared = 0.53-0.77** (p<0.001). The most recent
user message is the primary driver, not accumulated context.

#### Key Structural Finding

The default Assistant projects to **one extreme** of PC1 (within 0.03 of the edge)
but **intermediate values** (0.27-0.50) on all other PCs. The Assistant is not just
"a persona" — it is the dominant organizing principle of persona space itself.

Post-training creates only a **"loose tether"** to the Assistant region. The model
can be pulled away by conversational context, adversarial prompts, or task framing.

---

### 3. Expert Persona Prompting: PRISM Study

**Authors:** University of Southern California researchers
**Published:** March 2026
**URL:** https://arxiv.org/abs/2603.18507
**Coverage:** https://www.theregister.com/2026/03/24/ai_models_persona_prompting/

#### Core Finding

Generic expert personas ("You are an expert Python developer") **decreased accuracy
by 3.6 percentage points on MMLU** (from 71.6% to 68.0%). The mechanism: persona
prefixes activate instruction-following circuits at the expense of factual recall.

| Task Type | Expert Persona Effect |
|---|---|
| Alignment-dependent (safety, style, compliance) | **+17.7pp improvement** |
| Knowledge-dependent (math, coding, facts) | **-3.6pp degradation** |

A "Safety Monitor" persona increased attack refusal rates from 53.2% to 70.9%.

#### 162-Persona Study Confirmation

A separate study covering 162 personas across 9 models and 2,410 questions confirmed:
personas have **no statistically significant improvement** on factual/technical tasks,
with some actively reducing performance. Gender-neutral, domain-aligned roles
performed marginally better.

**Source:** https://arxiv.org/html/2311.10054v3

#### Actionable Guidance

> "The general expert persona is not necessary... while granular personalized project
> requirements might help the model to generate code that satisfies the user's
> requirements."

**Translation:** Don't claim expertise. Specify behavioral identity — values,
craftsmanship standards, relationship to the work. Persona framing helps with
*how to behave* but hurts with *what to produce*.

---

### 4. PERSONA: Dynamic and Compositional Inference-Time Control

**Published:** ICLR 2026 (conference paper)
**URL:** https://arxiv.org/pdf/2602.15669

#### Core Finding

Personality traits exist as **approximately orthogonal directions** in LLM activation
space and can be manipulated via vector algebra without retraining:

- **Intensity control:** Scalar multiplication adjusts trait strength
- **Trait composition:** Vector addition combines traits
- **Trait suppression:** Vector subtraction removes traits
- Achieved **9.60 on PersonalityBench** (matching supervised fine-tuning's 9.61 upper
  bound) and **91% win rates** on dynamic personality adaptation

#### Three-Stage Framework

1. **Persona-Base** — extract orthogonal trait vectors from activation space
2. **Persona-Algebra** — arithmetic manipulation (compose, suppress, scale)
3. **Persona-Flow** — dynamic context-aware composition at inference time

#### Implication

Personality traits are mathematically tractable and approximately independent. You can
design identity frames that compose multiple behavioral traits without interference —
"precise, governance-aware, cross-platform-conscious" can coexist as a valid
composition.

---

### 5. Persona Vectors: Monitoring and Controlling Character Traits

**Authors:** Anthropic research team
**URL:** https://www.anthropic.com/research/persona-vectors

#### Key Findings

- Persona vectors **activate before model responses**, enabling prediction of which
  persona the model will adopt in advance of generation.
- Traits studied: evil, sycophancy, hallucination, politeness, apathy, humor, optimism.
- System prompts that encourage specific traits reliably trigger corresponding persona
  vectors.
- Counterintuitively, injecting undesirable trait vectors during training acts as a
  "vaccine," reducing the model's tendency to naturally acquire those traits.

---

### 6. System Prompt Studies in Code Generation

**Published:** 2025 (360-configuration empirical study)
**URL:** https://arxiv.org/abs/2602.15228

#### Finding

Increasing system-prompt constraint specificity does not monotonically improve code
correctness — effectiveness is configuration-dependent. For larger code-specialized
models, few-shot examples surprisingly underperformed zero-shot generation.

---

### 7. Production Agent Patterns

**Claude Code** uses minimal identity framing (12 words: "You are a Claude agent,
built on Anthropic's Claude Agent SDK") followed by layered behavioral instructions.
Identity is stable and minimal; behavior is configurable.

**Cursor** frames as capability + environment: "You are a powerful agentic AI coding
assistant, powered by Claude 3.5 Sonnet. You operate exclusively in Cursor."

**Common pattern:** Minimal identity claim + rich behavioral specification. None say
"You are an expert." They say what the agent *is* and then specify *how it should
behave*.

**MSR 2026 study of .cursorrules** (https://arxiv.org/pdf/2512.18925): Rule files
specifying technology stacks, code style conventions, and behavioral guidelines
measurably influence code generation patterns.

---

### 8. Multi-Turn Persona Fidelity

**Source:** https://www.emergentmind.com/topics/persona-fidelity

- Persona fidelity **deteriorates over extended dialogues**, especially in
  goal-oriented settings.
- Models may produce correct persona behavior at the output level while contradicting
  it at the sentence level.
- **Reinforcement learning improves persistence** — after RL fine-tuning,
  prompt-to-line consistency remains high even as dialogue length increases.

**41-production-system-prompt analysis:**
- 96% contain explicit harmlessness framing
- 91% contain priority hierarchies
- 26.8% identity confusion rate where models misattribute their developers

---

## Synthesis: Design Principles for Agent Identity Framing

Based on the research above, these principles should guide the ADR series:

### 1. Persona is geometric, not cosmetic

Identity framing is a mechanical operation on the model's internal state (PSM,
Assistant Axis). It activates bundled trait clusters. This is not motivation theater.

### 2. Don't claim expertise — frame behavioral identity

Generic expert personas hurt code quality by -3.6pp (PRISM). Instead, frame values,
craftsmanship standards, and relationship to the work. Persona framing helps with
*compliance* (+17.7pp) but hurts with *knowledge retrieval*.

### 3. Traits compose orthogonally

Multiple behavioral traits can be combined without interference (PERSONA/ICLR 2026).
Design persona frames as composable trait specifications, not monolithic character
descriptions.

### 4. The most recent message is the primary driver

The model's persona position depends most on the most recent user message (R-squared
0.53-0.77), not accumulated context (R-squared 0.10). Mid-conversation reinforcement
matters more than initial framing alone.

### 5. Task type naturally stabilizes or destabilizes persona

Coding tasks stabilize the Assistant persona. Meta-reflective and emotional contexts
destabilize it. Agent systems should be aware of which interaction types require
stronger persona anchoring.

### 6. Post-training creates only a loose tether

The model can be pulled away from its trained persona by conversational context.
System-level persona framing is necessary because the training-level tether is
insufficient for long-horizon agent sessions.

### 7. Virtue-ethics framing over prohibition lists

Per Amanda Askell's approach to Claude's constitution: train character traits
(curiosity, honesty, intellectual humility) rather than providing lists of
prohibitions. The PSM research confirms this — the model infers a complete persona
from the identity frame, so the frame should describe a character whose natural
behavior produces what you want.

### 8. The Operating System view is the useful model

The post-trained LLM is a neutral substrate. The persona IS the behavior, not a mask
over something else. Persona design is a legitimate engineering discipline —
configuring which process runs on the substrate.

---

## Anti-Patterns: What Wrong Looks Like

These anti-patterns are the specific failure modes the research disproves. Each
entry names the source, explains why it fails, and states what to do instead.

### 1. Generic Expert Persona

**Example:** "You are an expert Python developer with deep knowledge of async."

**Why it fails:** PRISM (arXiv 2603.18507) measured a **3.6pp accuracy decrease**
on knowledge tasks when generic expert personas were applied. The mechanism:
persona prefixes activate instruction-following circuits at the expense of
factual recall. Claiming expertise adds no knowledge the model doesn't already
have — it only redirects attention away from retrieval.

**Instead:** Frame behavioral identity — values, craftsmanship standards, and
relationship to the work. Persona framing helps with *how to behave* (+17.7pp
compliance) but hurts *what to produce*.

### 2. Job-Description Framing

**Example:** "You are a senior software engineer with 10 years of experience in
distributed systems and cloud infrastructure."

**Why it fails:** The PSM demonstrates that the model performs personality
inference — "what sort of person has this resume?" The inferred character may
include traits like credential-consciousness, risk aversion, and
process-over-substance that are counterproductive for agent coding tasks. The
framing adds zero knowledge while activating an unpredictable trait cluster.

**Instead:** Describe how the agent relates to the code and what craftsmanship
means to it. "Reads the full file before editing" is behavioral identity.
"10 years experience" is a costume.

### 3. Motivational-Poster Framing

**Example:** "You are the best coder in the world. You write flawless code."

**Why it fails:** Empty superlatives activate no specific behavioral trait. The
PERSONA/ICLR research shows that trait activation requires directional specificity
in activation space. "The best" is not a direction — it's noise. The model
has no personality template for "best coder" because no such archetype exists
in the training distribution with consistent behavioral correlates.

**Instead:** Specify concrete behavioral traits: meticulous, systems-thinking,
test-first. Each maps to an orthogonal activation direction with predictable
behavioral effects.

### 4. Monolithic Character Description

**Example:** A 500-word paragraph describing a character's backstory, personality,
values, technical skills, communication style, and emotional disposition.

**Why it fails:** The PERSONA/ICLR framework demonstrates that traits compose
orthogonally via vector addition. A monolithic description forces the model to
extract trait vectors from unstructured prose — lossy and non-deterministic.
Two models (or two runs) will extract different trait emphasis from the same
paragraph.

**Instead:** Use structured trait specifications with YAML frontmatter.
Separate traits, anti-traits, and grounding text into independently addressable
fields that compose deterministically.

### 5. Prohibition-List Identity

**Example:** "You must NEVER write incomplete code. You must NEVER skip tests.
You must NEVER use bare except clauses."

**Why it fails:** The PSM's personality inference works both ways. Framing
identity around what NOT to do implies "what sort of agent needs to be told not
to do these things?" — one that is inclined to do them. The inferred persona
includes the prohibited traits as part of its character. This is the
"learning to bully vs. learning to play a bully" distinction from the PSM
paper.

**Instead:** Frame positive behavioral identity using virtue-ethics: curiosity,
thoroughness, craftsmanship. Per Amanda Askell's approach to Claude's
constitution — train character traits whose natural behavior produces the
outcomes you want, rather than listing prohibitions.

---

## Bibliography

1. Marks, S., Lindsey, J., Olah, C. (2026). "The Persona Selection Model: Why AI
   Assistants might Behave like Humans." Anthropic Alignment Science Blog.
   https://alignment.anthropic.com/2026/psm/

2. Lu, C., Gallagher, J., Michala, J., Fish, K., Lindsey, J. (2026). "The Assistant
   Axis: Situating and Stabilizing the Default Persona of Language Models."
   arXiv:2601.10387. https://arxiv.org/html/2601.10387v1

3. USC Researchers (2026). "PRISM: Expert Personas Improve LLM Alignment but Damage
   Accuracy." arXiv:2603.18507. https://arxiv.org/abs/2603.18507

4. ICLR 2026 (2026). "PERSONA: Dynamic and Compositional Inference-Time Personality
   Control." arXiv:2602.15669. https://arxiv.org/pdf/2602.15669

5. Anthropic Research (2025-2026). "Persona Vectors: Monitoring and Controlling
   Character Traits in Language Models."
   https://www.anthropic.com/research/persona-vectors

6. arXiv:2602.15228 (2025). "Effects of System Prompts in Instruction-Tuned Models
   for Code Generation." https://arxiv.org/abs/2602.15228

7. arXiv:2311.10054v3 (2024). "When 'A Helpful Assistant' Is Not Really Helpful:
   Persona Prompting Across 162 Roles." https://arxiv.org/html/2311.10054v3

8. MSR 2026. "Empirical Study of Cursor Rules."
   https://arxiv.org/pdf/2512.18925

---

**This document is referenced by:**
- ADR-0.0.11 — Persona-Driven Agent Identity Frames (Foundation)
- ADR-0.0.12 — Agent Role Persona Profiles (Application)
- ADR-0.0.13 — Portable Persona Control Surface (Cross-Project)
