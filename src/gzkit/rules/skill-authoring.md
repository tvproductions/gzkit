---
id: skill-authoring
paths:
  - ".gzkit/skills/**"
description: How a gzkit skill is written — what it carries, parsimony, model alignment, and the authority lines a step may not cross
---

<!-- rule-version: 0.1.0 -->

# Skill Authoring (gzkit)

> **Rule version:** `0.1.0` — the declared standard for skill bodies (operator ruling 2026-09-19, *"its both an authoring AND chore scope"*); until now the only statement of it lived inside the `skill-authoring-quality` chore.

Skills are canonical files, not corpus constructed (`docs/governance/agent-control-surface-rendering-substrate.md` § Binding claim), so review is their control. This rule is the standard three chores read, each in its own class: `skill-authoring-quality` checks conformance to it, `instructions-files-diet` curates bodies against § Parsimony, and `frontier-model-card-currency` re-sources wording against § Model alignment. Versioning and sync mechanics are `skill-surface-sync.md`; the `model:` field is `model-selection.md`.

## What a skill carries

- **Procedure plus the judgment a step needs:** which `gz` verb, in what order, what stops the run, what the operator decides. A skill that wraps one command and adds no judgment is an alias: make it user-invoked (`disable-model-invocation: true`) or remove it.
- **A one-line description that says when to reach for the skill and what it produces.** It is the only part loaded every turn (`agents-md-map-doctrine.md` § Writing levers).
- **Where it ends.** Every skill states its terminal state and what it does not do.

## Parsimony (binding)

1. **Procedure stays; history leaves.** Dated incident narrative, regression stories and version notes go to a rationale doc under `docs/governance/` or a `references/` file beside the skill. The body keeps one sentence of reason and the pointer.
2. **One home per meaning.** Point at `AGENTS.md`, a rule, `--help` or a model; do not restate them. Text attributed to `AGENTS.md` is quoted from the current file, by section name, or not quoted.
3. **Name the verb, not its work.** Where a `gz` verb scaffolds, validates or books something, the step names the verb; it does not describe doing that work by hand.
4. **Branch test.** Material only some runs reach goes behind a pointer to `references/`.
5. **A rationalization or red-flag row earns its place** by naming a failure observed in this repository for this skill. These tables are not required sections, and a skill is not better for having them.
6. **Size is a finding.** A body past the threshold `skill-authoring-quality` declares is decomposed or lifted, not excused.

## Model alignment (binding)

Skill wording follows the current tuning docs, `docs/governance/opus-tuning.md` and `docs/governance/gpt-tuning.md`; cite the doc, never a card. When a card rotates, wording tuned to the old one is up for re-sourcing.

1. **State scope and stop conditions.** Current models widen a task unless told where it ends.
2. **Add no verification or re-check step where a mechanical witness exists** (a test, a hook, `gz check`, a receipt), and no anti-laziness pressure.
3. **Reserve `MUST` and `NEVER` for a constraint the skill itself owns.** A constraint owned elsewhere is cited in plain words.
4. **Keep written constraints.** "Capability gains are not evidence that a written constraint has become less necessary" (`opus-tuning.md` § Recalibration on model change).
5. **State the behavior wanted**; keep a prohibition only as a guardrail paired with its positive target.

## Authority lines a step may not cross

A skill step never instructs what the root contract forbids. The recurring cases, each by its authority:

- initiating, claiming or completing OBPI work — `AGENTS.md` § OBPI Acceptance Protocol;
- `gh issue create` or a bare `gh issue close` — the `ghi-author` and `ghi-close` skills;
- a real name in an attestor field — `AGENTS.md` § Execution Rules;
- treating Gate 5 as lane-dependent — `AGENTS.md` § Gate Covenant;
- a retired command or a path that does not exist — run it and resolve it before writing it.

## Enforcement posture

**Advisory, with three mechanical neighbors.** `gz skill audit` checks frontmatter, lifecycle, review age and mirror parity, and reads no body. `gz validate --cli-alignment` resolves every `gz <verb>` a skill names. `gz validate --skill-alignment` holds every verb to a wielding skill. Body parsimony and model alignment have no witness: they are judged at authoring and at the three chores above, in propose-rule-land mode, because a repair that touches a skill is operator-only. Reclassify a clause when a check for it lands.
