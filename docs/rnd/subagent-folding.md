# R&D run — subagent-folding

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-10-27T09:30Z.

**Challenge.** Operator g0, 2026-10-27, verbatim, pasting the URL of the claude.com article
*Building agents: When to fold subagents into your main agent loop*:

> ok, so provide gzkit recommendations based on this

and, after the agent's first-pass recommendations and its offer of a run:

> Yes, start a gz-rnd run on the subagent-folding article.

---

## source · the article

<https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop>
· Diane Sarkis, Claude by Anthropic, dated 2026-10-22 · read 2026-10-27, full text (fetched
HTML, stripped to text in the session scratchpad; not landed here because the article is
copyrighted — the URL is the citation).

Secondary for any claim about gzkit: it is vendor guidance about enterprise agents built on
Claude Platform, and verifies nothing about this repository. Its own claims are reports of the
vendor's comparisons, not published measurements.

The passages that bear on the challenge, verbatim:

> dividing by context: give each subagent a piece of work that needs little from the rest of
> the system and have it hand back a compact result

> When agents are split by problem type, they engage in a "telephone game,"

> the model that writes the plan is also the one carrying it out, so it can change the plan
> mid-turn.

> Ordering and domain procedure move into skills. Hard limits (validation, approval gates)
> [...] move into the tools.

Its three conditions for keeping a subagent:

> A single agent loop hits measurable performance degradation from context bloat, or
> Multiple tasks need to be tackled in parallel with fresh context windows that can be
> discarded once the task is done, or
> A single agent struggles to select appropriate tools or there are conflicting instructions
> in the system prompt.

On method:

> Even a set of 10 golden examples is enough to start.

> don't just examine the final score, take a look at which tasks flipped.

> run each task more than once, since a break like this one only showed up in one run out of
> two.

> keep it as a subagent only if the folded version scores worse, then rinse and repeat.

On tool count:

> once you exceed 30-50 tool definitions in the system prompt, tool choice tends to degrade.

Note the threshold is stated for **tool definitions**, not skill descriptions; carrying it to
gzkit's skill catalog would be an analogy, not the source's claim.

## source · the agent's first-pass recommendations (earlier dialogue)

This session, 2026-10-27, the agent's reply to the challenge, before this run opened. Entered
as material the run reads, never as decisions. Its seven points, in its own headings:

1. Keep the reviewers and Explore as they are.
2. Test the per-task `implementer` dispatch; don't assume it's right.
3. The `narrator` is the clearest candidate to fold into the main loop (`git-sync-repo`
   flagged as a possible same case, explicitly unread).
4. The contractor-kit run decides this directly.
5. Build evals before changing any architecture.
6. Watch for skill sprawl and "frankenprompts".
7. Review older-model-style prompting ("DO NOT STOP HERE").

Point 6 applied the article's 30–50 *tool* threshold to *skills* — an analogy the article does
not make (see above).

## source · gzkit's subagent fan-out doctrine

`docs/governance/opus-tuning.md` § Subagent fan-out · read 2026-10-27

> Spawn an `Agent` only when work fans out across independent items:

> Independent reviews where the agent must not see the operator's prior reasoning
> (`spec-reviewer`, `quality-reviewer`).

> a verification-only subagent duplicates what the model already does.

## source · model-selection: a subagent's claim is not evidence

`.gzkit/rules/model-selection.md` operative claim 5 · read 2026-10-27

> A subagent's claim is not evidence. Never relay a subagent's factual assertion into
> ceremony, attestation, or an operator-facing conclusion on the subagent's word

Same file, § Subagent effort levels: *"Today every definition under `.claude/agents/` carries
`model: inherit` and no `effort:`"*.

## source · the agent definitions

`.claude/agents/*.md` frontmatter · read 2026-10-27 (frontmatter and opening lines only;
bodies unread)

- `implementer` — *"Implements plan tasks with TDD discipline. Dispatched per-task by the
  pipeline controller."* `maxTurns: 25`, `permissionMode: acceptEdits`.
- `spec-reviewer`, `quality-reviewer` — *"Independent review by reading; cannot execute
  commands (GHI #968)."* `maxTurns: 15`.
- `narrator` — *"Presents evidence for ceremony and documentation sync. Reads implementation
  and verification outputs."* `maxTurns: 10`.
- `git-sync-repo` — *"guarded repository sync operations"*.

## source · the pipeline's dispatch

`.gzkit/skills/gz-obpi-pipeline/SKILL.md` § Persona Dispatch · read 2026-10-27 (§ Stage 2
body unread)

> The pipeline dispatches four subagent personas across its stages.

AGENTS.md § OBPI Acceptance Protocol, verbatim: *"Once initiated, follow the skill's
implementer dispatch and spec-reviewer then quality-reviewer review; never substitute inline
Stage 2."* — the dispatch is canon, not habit.

## source · the contractor-kit run

`docs/rnd/contractor-kit.md` § decision · a contractor is a runtime-driven session that
dispatches each act · read 2026-10-27

> Recommended C. Operator: *"c"*.

> Tension carried, not resolved: per-act reviewer dispatch costs against the contract's
> *"Cheaper sessions execute the deterministic repair orders"*.

And the operator in the same record, on the pipeline: *"I am VERY, VERY fond of, and
protective of, the pipeline as a premier feature of gzkit."*

## decision · the run's subject is both gzkit's own harness and what it ships to adopters

Ruled. Question 1: what is this run's subject? Options put: **A** gzkit's own agent harness
(pipeline dispatch, agent definitions, fan-out doctrine), adopter guidance reached through
distribution, recommended; **B** the agent-design guidance gzkit ships to adopters; **C** both,
broader, two readers. Operator, verbatim: *"C — both gzkit's own harness and the agent-design
guidance gzkit ships to adopters."*

The recommendation was not taken. The adopter surface is therefore a subject in its own right,
not a by-product of distribution; the sources below establish what that surface is.

## source · the adopter AGENTS.md template

`src/gzkit/templates/agents.md` · read 2026-10-27 (lines 22–26 and 132–133)

Ships a persona table naming the four pipeline roles as subagents, e.g. *"`implementer` |
Task implementation subagent"*, and two numbered rules:

> 5. Offload online research, codebase exploration, and log analysis to subagents when work
> splits across independent items, when direct `rg`/read commands would not suffice, or when
> context isolation is the goal. Do not spawn subagents for single-surface checks, direct
> grep/read tasks, or work whose next step depends on the result.

> 6. When spawning a subagent, always include a 'Why' parameter in the subagent system prompt
> to filter signal from noise.

## source · the canonical role bodies

`.gzkit/agents/README.md` · read 2026-10-27

> These neutral Markdown definitions own the role instruction bodies delivered to Codex.

The directory holds `implementer`, `narrator`, `quality-reviewer`, `spec-reviewer`,
`git-sync-repo` and `roles.json`. The role bodies are the vendor-neutral form of the four
pipeline roles plus git-sync; whether `gz init` ships them to adopters is **unverified** —
the distribution path was not read.

## source · shipped pipeline skill

`src/gzkit/skills/gz-obpi-pipeline/` exists with `references/stage-2-implement.md` and
`references/stage-3-verify.md` · seen 2026-10-27 (listed, unread). Adopters who receive the
pipeline receive its dispatch shape.

## decision · "divide by context" is an admission test for new roles; existing roles wait on measurement

Ruled. Question 2: what standing does the article's "divide by context" test get? Options
put: **A** adopt as doctrine now and audit every existing role against it; **B** no doctrine
change, build the eval first and decide per role; **C** adopt it as the admission test for new
subagent roles (gzkit's and shipped), and measure before touching existing roles,
recommended. Operator, verbatim: *"C — adopt it as the admission test for new subagent roles;
measure before touching existing roles."*

Reasoning: the admission test is witnessable and reversible; touching the pipeline's roles on
vendor guidance alone would be pattern-matching the anti-vibing mantra excludes, and the
article itself says to measure first. The existing roles — `implementer`, `spec-reviewer`,
`quality-reviewer`, `narrator`, `git-sync-repo` — are therefore out of any change until an
instrument exists. Note the canon fence: AGENTS.md forbids *"inline Stage 2"*, so any
folded-implementer arm of a measurement runs on probe material, never on live OBPI work.

**commissions:** 4 — the admission test as text in the surfaces that govern subagent roles
(where, and whether witnessed, is open).

## source · gzkit's existing eval harness

`src/gzkit/eval/scorer.py` module docstring · read 2026-10-27

> Scoring is fully deterministic — no network calls, no LLM invocations.

`data/eval/` holds golden sets for `adr`, `agents`, `instruction`, `rules`, `skills`; the
`agents_eval_golden.json` cases score an AGENTS.md text for required sections. The harness
scores **surfaces**, not agent runs. gzkit has no task-completion eval of agent behaviour —
no instrument for the measurement Q2 requires.

## source · Agent Skills Can Be Harmful (arXiv 2608.11888)

<https://arxiv.org/abs/2608.11888> · Dong, Gao, Li, Xu, Hua, Yang, submitted 2026-08-12 ·
preprint, not peer-reviewed · supplied by the operator mid-run, 2026-10-27, verbatim *"this?"*
· read 2026-10-27: abstract, § IV findings 1–2, § V findings 3–4 with Table IV, § IX
conclusion (PDF text-extracted in the session scratchpad; §§ VI–VIII on the SkillTriage tool
and threats skimmed, not read closely).

Method, from the abstract:

> comparing a target skill-guided run against a no-skill or semantically matched skill
> reference run that solves the same task, or solves it more cheaply.

Findings, verbatim:

> Finding 1: Only 2 of 125 functional failures are classified as Applicability Mismatch
> (1.6%), while most fall under Task-Implementation Fault, indicating that on-topic skills
> more often induce task-implementation faults in required implementation elements.

> Implication: Skill authors should separate mandatory task requirements from examples,
> defaults, reusable templates, and optional workflows

> Finding 3: When efficiency regressions arise from context overhead, the overhead is almost
> entirely caused by mandatory skill-body text.

> Finding 4: High-confidence efficiency regressions are dominated by Excessive Procedure
> rather than prompt length alone, and the largest sources within Excessive Procedure are
> excessive verification and heavy implementation pipelines.

> skill authors should condition verification scope and pipeline depth on task uncertainty,
> change size, and budget rather than prescribing exhaustive workflows by default.

> skill loading should be treated as a costed and validated configuration decision,
> supported by compatibility checks, cost prediction, and paired correctness/cost
> evaluation.

Bearing: it is the counterweight to the article. The article's remedy is to turn subagents
into skills; this paper measures skills as a failure source in their own right, and its two
largest efficiency causes — excessive verification and heavy implementation pipelines — are
the shapes gzkit's ceremony takes. Its paired-run differential method is a candidate for the
instrument Q2 requires. Its benchmarks (SkillsBench, SWE-Skills-Bench) are generic coding
tasks, not governance work; carrying its rates to gzkit would be an extrapolation.

## decision · the measurement instrument is a paired-run differential on probe tasks

Ruled. Question 3: what instrument does "measure before touching existing roles" use?
Options put: **A** a paired-run differential instrument (the paper's method plus the
article's run-each-task-more-than-once) on probe tasks in throwaway local worktrees, graded by
gzkit's own deterministic gates, cost and time recorded per run, flipped tasks compared
individually, recommended; **B** observational only, mining the ledger's existing pipeline
runs; **C** defer the instrument to a pool ADR. Operator, verbatim: *"A — a paired-run
differential instrument on probe tasks in throwaway worktrees, graded by gzkit's own gates,
each arm run at least twice."*

Reasoning: B has no counterfactual arm and cannot answer fold-versus-keep; C leaves the
existing roles frozen indefinitely. Probe tasks keep the folded-implementer arm off live OBPI
work (the *"inline Stage 2"* fence); local worktrees are canon for subagents (operator
2026-09-27, *"local worktrees are fine"*); gates as grader avoid an LLM judge.

**commissions:** pending Q4 — the instrument's route collides with ADR-0.0.5 (below).

## source · ADR-0.0.5 rejected live calls per eval run

`docs/design/adr/foundation/ADR-0.0.5-evaluation-infrastructure/ADR-0.0.5-evaluation-infrastructure.md`
· status `Validated`, kind `foundation` · read 2026-10-27 (frontmatter, Problem Statement,
Decision 1)

Its declared intent:

> When a model changes, a prompt is updated, or an instruction surface is modified, there is
> no systematic way to measure whether the quality of AI-assisted workflows improved or
> regressed.

Its Decision 1, alternatives considered:

> *Live API calls per eval run* -- rejected: introduces flakiness, network dependency, and
> cost. Violates test policy (no external services).

Bearing: the Q3 instrument runs live agents, which this ruled decision rejected. The
rejection's stated grounds are flakiness, cost and the **test** policy, and the ADR's harnesses
are *"unittest extensions"* integrated into Gate 2 (its Decisions 2 and 4, headings read). The
instrument would also serve the ADR's own declared intent — detecting behaviour regressions on
model or instruction change — which its offline harness, scoring surface texts, does not
reach. Canon and the Q3 ruling disagree; the run stops on it (AGENTS.md § Behavior Rules).

## decision · the instrument is an operator-run experiment, and goes to a new feature ADR

Ruled. Question 4: how does the paired-run instrument stand against ADR-0.0.5 Decision 1?
Options put: **A** a distinct surface — an operator-run experiment, never a Gate-2 test;
Decision 1 stands for the test suite; the instrument goes to a new feature ADR that names and
distinguishes Decision 1, recommended; **B** a correction under ADR-0.0.5, its declared intent
unfulfilled, Decision 1 revisited there; **C** reverse Q3, observational only. Operator,
verbatim: *"A — a distinct surface: an operator-run experiment, never a Gate-2 test; Decision
1 stands for the test suite, and the instrument goes to a new feature ADR that names and
distinguishes Decision 1."*

Admission question for disposition 1, answered: hard to reverse — it introduces live agent
runs as a governed gzkit capability; surprising without context — it reads as contradicting a
Validated foundation decision; a real trade-off — experimental evidence against cost and
flakiness. All three hold.

**commissions:** 1 — propose a feature ADR for the paired-run instrument, naming ADR-0.0.5
Decision 1 and the distinction. Proposed only; the operator initiates. Its vehicle is open
(prior art below).

## source · ADR-0.18.0 made the pipeline's dispatch, and its first reason is context

`docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
· status `Validated`, kind `feature`, dated 2026-03-17 · read 2026-10-27 (Intent, Decision,
Rationale)

> On complex OBPIs with 8+ plan tasks, Stage 2 alone can consume 40-60% of the session's
> context window, leaving Stages 3-5 (verification, ceremony, sync) operating in compressed
> or degraded context.

> This pattern is proven at scale by the [superpowers](https://github.com/obra/superpowers)
> methodology (92k+ stars)

Bearing: the implementer dispatch was decided **by context**, which is the article's first
keep-condition, not the split-by-stage it warns against. The agent's first-pass point 2 called
it a stage split; that reading is contradicted by the ADR's own rationale. What has moved
since 2026-03-17 is the model generation, which the article says absorbs more in one loop.
The 40–60% figure is stated as measured, with no measurement cited; the external evidence is
adoption count. Both are what the instrument would re-test, not refute.

## source · ADR-pool.skill-efficacy-measurement

`docs/design/adr/pool/ADR-pool.skill-efficacy-measurement.md` · status `Pool` · read
2026-10-27 (Intent, Decision, Alternatives Considered)

> 70 skills load into agent turns on the claim that they improve outcomes, and the claim has
> no witness.

> **EFFICACY IS MEASURED FROM RUNTIME EVIDENCE, NEVER FROM THE SKILL'S OWN TEXT.**

> **BUILD ON `gzkit.efficacy`, DO NOT AUTHOR A SECOND MEASUREMENT MODEL.**

Bearing: prior art for disposition 1. It asks the paper's question — do skills earn their
place — by observation (ledger, insights, ARB), with no counterfactual arm. Its "no second
measurement model" decision constrains where a paired-run instrument may live.

## decision · the vehicle is ADR-pool.skill-efficacy-measurement, promoted and widened

Ruled. Question 5: which ADR carries the paired-run instrument? Options put: **A** a
standalone new feature ADR, the pool ADR cited as sibling; **B** promote
ADR-pool.skill-efficacy-measurement as the vehicle, widened to skills and subagent roles,
observational and experimental, recommended; **C** a new ADR, with the pool ADR amended to
defer its measurement to it. Operator, verbatim: *"B — promote
ADR-pool.skill-efficacy-measurement as the vehicle, widened to skills and subagent roles,
observational and experimental."*

Reasoning: promotion yields a feature ADR, so Q4 holds; one ADR measuring every
behaviour-shaping surface keeps the pool's *"DO NOT AUTHOR A SECOND MEASUREMENT MODEL"*
whole. The pool's own Alternative D already provides for splitting its provenance half at
promotion. The paper's question (do skills earn their cost) and the article's (do subagent
roles earn their handoff) become one subject with two methods.

**commissions:** 1 — the proposal names `ADR-pool.skill-efficacy-measurement` for promotion
through `gz-adr-promote`, widened as ruled. Proposed only; the operator initiates.

## source · the role registry

`.gzkit/agents/roles.json` · read 2026-10-27 (head)

Per role it carries `description` and `legacy_codex_body_sha256`; nothing about the context a
role isolates or what it returns. It is read by `src/gzkit/codex_roles.py`; no copy exists
under `src/gzkit/`, so it is not shipped to adopters by the wheel (searched for the file name,
distribution code not read).

## decision · the admission test is a declared, validator-witnessed field per role

Ruled. Question 6: where does the "divide by context" admission test live, and what witnesses
it? Options put: **A** a declared field on each role (`isolates` / `returns`) in
`.gzkit/agents/roles.json`, witnessed by a validator; prose surfaces and the shipped template
point at it, recommended; **B** prose only, an AGENTS.md corpus entry and the shipped
template's rule 5, advisory; **C** A plus shipping the registry and validator to adopters.
Operator, verbatim: *"A — a declared field on each role (isolates / returns) in
.gzkit/agents/roles.json, witnessed by a validator; prose surfaces and the shipped template
point at it."*

The substance — declared and witnessed, not prose — is settled. The **placement** named in
the option rested on an incomplete read: the agent stated that nothing records what a role
returns, and the next source contradicts it. Placement is put again as Q6b.

## source · the typed role registry already carries a handoff contract

`src/gzkit/roles.py` · read 2026-10-27 (models, Implementer and Reviewer definitions);
`uv run gz roles` run 2026-10-27 · from ADR-0.18.0 (OBPI-0.18.0-01, *"role taxonomy data model
and handoff contracts"*; REQ-0.18.0-05-05, *"`gz roles` CLI MUST list the four roles with
their handoff contracts"*)

```python
class ArtifactContract(BaseModel):
    """What a role produces and consumes."""
    produces: list[str] = Field(..., description="Artifact types this role outputs")
    consumes: list[str] = Field(..., description="Artifact types this role requires as input")
```

The Implementer's `consumes` begins *"plan task with scoped context"*; its `produces` ends
*"structured result status"*. `RoleDefinition` carries `artifacts: ArtifactContract`, an
`AgentFileSpec` (tools, model, permission mode, max turns) and `can_write`. It ships in the
wheel (it is under `src/gzkit/`).

Bearing: `produces` is the ruled `returns`, already typed and enforced by Pydantic; only
`isolates` is missing. gzkit has **two role registries** — `roles.py` (four roles: Planner,
Implementer, Reviewer with spec and quality sub-roles, Narrator) and `.gzkit/agents/roles.json`
(five Codex bodies, including `git-sync-repo`, which `roles.py` does not model). Placing the
field in `roles.json` would make a second contract surface beside the first.

## decision · the field lives in roles.py; produces is the return contract

Ruled. Question 6b: which registry carries the declared field? Options put: **A** `roles.py`
— add `isolates` beside the existing `ArtifactContract`, `produces` serving as the return
contract, the validator reading `roles.py`, recommended; **B** `roles.json` as ruled at Q6;
**C** both, with a coherence check. Operator, verbatim: *"A — roles.py: add isolates beside
the existing ArtifactContract (produces is the returns); the validator reads roles.py."*

This supersedes Q6's placement; Q6's substance (declared, validator-witnessed) stands.
Adopters receive the field through the wheel. The ruled name `returns` is not coined: the
source's own term `produces` is kept.

Routing, from canon: a new `RoleDefinition` field plus a `gz validate` flag changes a schema
and a CLI, which AGENTS.md § Defect-fix routing makes OBPI work, proposed *"only as a Feature
Checklist item of a named ADR"*. Which ADR is put as Q7.

**commissions:** 4 — the prose half: opus-tuning § Subagent fan-out, the AGENTS.md corpus
subagent rule, and the shipped template's rule 5 point at `RoleDefinition.isolates`. The code
half routes by Q7.

## decision · the isolates field and its validator are a checklist item of the promoted ADR

Ruled. Question 7: which ADR carries the `isolates` field and its validator? Options put:
**A** a Feature Checklist item of the promoted skill-efficacy ADR (row 1), recommended; **B** a
correction under ADR-0.18.0; **C** its own small feature ADR. Operator, verbatim: *"A — a
Feature Checklist item of the promoted skill-efficacy ADR (row 1)."*

Reasoning: the admission test and the measurement govern one population; each role's declared
`isolates` is the hypothesis the paired-run experiment tests. B was set aside because
`isolates` is a new admission rule, not an unfulfilled intent of ADR-0.18.0 — enhancement by
the correction-vs-enhancement test — and the ADR is Validated.

Coverage note for that item: `roles.py` models four pipeline roles; `git-sync-repo` has an
agent file and no `RoleDefinition`. A validator reading `roles.py` alone would not see it.
Whether every `.claude/agents/` file must map to a `RoleDefinition` belongs to the item's
specification (diamond 2), and is named here so it is not lost.

**commissions:** 1 — added to the row-1 proposal as a Feature Checklist item.

## decision · the paper's findings split: one admission criterion, one hypothesis

Ruled. Question 8: what standing do the paper's two skill-authoring findings get? Options
put: **A** split — Finding 1's implication (*"separate mandatory task requirements from
examples, defaults, reusable templates, and optional workflows"*) becomes an admission
criterion for new skills (row 4); Finding 4's (*"condition verification scope and pipeline
depth on task uncertainty, change size, and budget"*) goes to the promoted ADR's experiment as
a hypothesis, not doctrine, recommended; **B** both to measurement, no doctrine change from the
paper; **C** both adopted as authoring doctrine. Operator, verbatim: *"A — split: separating
mandatory steps from examples becomes an admission criterion for new skills (row 4);
verification depth goes to the promoted ADR's experiment, not doctrine."*

Reasoning: Finding 1 follows Q2's pattern — admission for new, measurement for existing — and
does not contest canon. Finding 4 contests canon directly (universal gates, Gate 5 on every
lane, AGENTS.md § DO IT RIGHT *"The most thorough and comprehensive fix is always
preferred"*); moving that on a preprint over generic coding benchmarks is the pattern-matching
the anti-vibing mantra excludes. Existing skills are untouched by the criterion, as existing
roles are by Q2.

**commissions:** 4 — the skill-authoring admission criterion for new skills. 1 — Finding 4 as
a named hypothesis for the promoted ADR's experimental arm.

## decision · row 2 is not pursued; the unsourced "measured" claim is an insight

Ruled. Question 9: what does row 2 (GHI / direct fix) carry? Options put: **not pursued** — no
defect outside rows 1 and 4; record ADR-0.18.0's unsourced "measured" claim as an insight,
recommended; **file a GHI** on that claim. Operator, verbatim: *"Not pursued — no defect
outside rows 1 and 4; record the 'measured' claim as an insight."*

The only defect-shaped finding, `git-sync-repo` lacking a `RoleDefinition`, already rides on
row 1's checklist item. A GHI on the claim could close only by the measurement row 1 proposes,
so it would duplicate that row. Insight recorded: `discovery`, scope `subagent-folding`,
`ts` 2026-10-27T09:35:57.761156+00:00.

## decision · row 3 is not pursued until the instrument exists

Ruled. Question 10: what does row 3 (chore) carry? Options put: **not pursued**, revisit once
the promoted ADR's instrument exists, recommended; **advise a chore now** that re-runs the
paired-run measurement on each frontier model release. Operator, verbatim: *"Not pursued —
revisit once the promoted ADR's instrument exists."*

A chore with no instrument to run is doctrine without mechanism. The pool ADR's Alternative A
already keeps a chore wrapper available once measurement lands; opus-tuning § Recalibration on
model change already carries the per-release cadence in prose.

## decision · row 5 is not pursued; each fold waits on the instrument's verdict

Ruled. Question 11: what does row 5 (one-shot refactoring) carry? Options put: **not
pursued**, folding existing roles waits on the instrument's verdict per role, recommended;
**propose a fold-one-role-at-a-time program now**, gated on the instrument. Operator,
verbatim: *"Not pursued — folding existing roles waits on the instrument's verdict per
role."*

A program ordered before any evidence exists would be diamond-2 planning without its input.
The article's own rule governs the revisit: *"keep it as a subagent only if the folded version
scores worse"*.

## decision · row 6 records first-pass points 6 and 7 as no action

Ruled. Question 12: does row 6 record first-pass points 6 and 7 as no action? Options put:
**both no action**, with reasons, recommended; **point 6 no action, point 7 to row 1** as a
hypothesis. Operator, verbatim: *"Yes — record points 6 and 7 as no action, with the reasons
given."*

- Point 6 (skill sprawl) rested on carrying the article's 30–50 **tool-definition** threshold
  to skills, an analogy the article does not make. Whether 70 skills earn their place is the
  promoted ADR's observational arm (row 1).
- Point 7 (older-model prompting, e.g. the pipeline's *"DO NOT STOP HERE"*) is governed by
  opus-tuning § Recalibration on model change, which re-derives guidance on each frontier
  release.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | commissioned | propose promoting ADR-pool.skill-efficacy-measurement to a feature ADR, widened to skills and subagent roles, observational and paired-run experimental, naming ADR-0.0.5 Decision 1; Feature Checklist item: `RoleDefinition.isolates` in `roles.py` and its validator; named hypothesis: the paper's Finding 4 (verification depth) | decisions Q4, Q5, Q7, Q8; proposed only, the operator initiates |
| 2 | GHI / direct fix | not pursued | — | decision Q9: no defect outside rows 1 and 4; ADR-0.18.0's unsourced "measured" claim recorded as an insight (2026-10-27T09:35:57Z) and re-tested by row 1; revisit if row 1 is killed |
| 3 | chore | not pursued | — | decision Q10: no instrument to run yet; revisit once the promoted ADR's paired-run instrument exists — a per-frontier-release re-measurement chore is the candidate |
| 4 | control surface, rule, doc, skill, hook | commissioned | the "divide by context" admission test: prose in opus-tuning § Subagent fan-out, the AGENTS.md corpus subagent rule and the shipped template's rule 5, pointing at `RoleDefinition.isolates`; and in the skill-authoring rule, the admission criterion that new skills separate mandatory steps from examples, defaults, templates and optional workflows | decisions Q2, Q6, Q6b, Q8; drafted on the operator's go on this row; the field and validator are row 1 |
| 5 | one-shot refactoring | not pursued | — | decision Q11: folding any existing role waits on the instrument's verdict for that role; revisit when the instrument shows a folded role scoring no worse than the kept one |
| 6 | no action | not pursued | first-pass points 6 (skill sprawl) and 7 (older-model prompting) | decision Q12: point 6's threshold was an unsupported analogy and skill efficacy is row 1's observational arm; point 7 is governed by opus-tuning § Recalibration on model change |

## Close

**Challenge restated.** Opened as *"provide gzkit recommendations based on"* a vendor article
on folding subagents into the main loop. Restated at the close, on purpose: gzkit's
subagent roles and skills — its own and those it ships — shape agent behaviour on claims no
instrument has tested. The run defines how new roles and skills are admitted (declared
context isolation; mandatory steps separated from examples), and how existing ones are judged
(a paired-run experiment, outside the test suite), so that fold-or-keep is decided by evidence
rather than by the article, the paper, or the adoption counts behind ADR-0.18.0.

**Frontier.** Empty. Every decision whose prerequisites were settled has been put and ruled
(Q1–Q12, with Q6b). Open matters remaining are diamond-2 specification, named where they
arose: which `.claude/agents/` files the `isolates` validator covers (Q7 entry), and the
instrument's probe set and grading rubric (row 1).

**Review.** `docs/rnd/subagent-folding/review.md`, written 2026-10-27. Operator, verbatim, 2026-10-27:
*"I have read the review."*

**Sign-off.** Operator, verbatim, 2026-10-27: *"Fund."* — fund. Diamond 1 is closed. Row 1
waits on the operator's initiation of the promotion; row 4 waits on the operator's go on that
row.

## What this record does not license

No ADR, OBPI, chore, GHI or edit to the pipeline, agent definitions or tuning doctrine is
started by this run. Every row awaits the operator's go on that row.
