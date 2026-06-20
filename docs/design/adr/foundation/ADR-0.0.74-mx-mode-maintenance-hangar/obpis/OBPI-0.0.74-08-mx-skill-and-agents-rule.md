---
id: OBPI-0.0.74-08-mx-skill-and-agents-rule
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 8
lane: Heavy
status: Draft
req_atomic:
  - REQ-0.0.74-08-01  # one SUPPORT artifact (the gz-mx skill as the operator's interface) — delivered with the scope, not separable labor
  - REQ-0.0.74-08-02  # one SUPPORT artifact (the binding mx-mode rule) — single indivisible unit
  - REQ-0.0.74-08-03  # one tool-skill-alignment behavior (gz_command resolves to gz mx) + its tests — single indivisible TDD unit
---

# OBPI-0.0.74-08-mx-skill-and-agents-rule: Mx Skill And Agents Rule

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #8 - "The gz-mx skill + AGENTS.md binding rule — operator operates skill, skill invokes tool, never shell out; AGENTS.md rule: honor the marker and PRIME DIRECTIVE binds the whole session; surface sync; unit tests"

**Status:** Draft

## Objective

Ship the two human/agent-facing companions to the marker mechanism: a `gz-mx` skill and a
binding `mx-mode` rule. The skill is the operator's interface to the hangar — the operator
<!-- gz-validate-skip: command-shape -->
operates the skill, the skill invokes `gz mx`, nobody shells out. This is the skill+tool
symbiont that satisfies tool-skill-runbook Invariant 1 (every CLI tool has a wielding skill):
gzkit is a meta-harness inside the vendor harness, so the operator's moves go through the skill,
not raw shell. The rule tells every agent to honor the marker AND that the PRIME DIRECTIVE binds
the entire hangar session — guards drop to advisory, but OWNERSHIP never does: fix what you know
AND what you find, and "not my work" / "out of scope" stays forbidden in the bay.

<!-- gz-validate-skip: command-shape -->
"Done" = a `gz-mx` skill exists whose declared `gz_command` resolves to the real `gz mx` verb;
a binding `mx-mode` rule exists carrying the honor-the-marker + PRIME-DIRECTIVE-binds doctrine;
both are propagated to every vendor surface by `gz agent sync control-surfaces`; unit tests
confirm the skill catalogs and the `gz_command` resolves.

## Lane

**Heavy** — the `gz-mx` skill declares a `gz_command` that must resolve to a real CLI verb
(tool-skill alignment is a contract surface humans rely on), and the parent ADR is
foundation/heavy. Gates 1-5 all apply; Gate 5 brief-level human attestation is universal
(ADR-0.0.36).

## Allowed Paths

- `.gzkit/skills/gz-mx/SKILL.md` **CREATE** — canonical `gz-mx` skill (edit here per skill-surface-sync doctrine; `gz_command: mx`); the operator's interface to the hangar
- `.gzkit/rules/mx-mode.md` **CREATE** — canonical binding rule: honor the marker + PRIME DIRECTIVE binds the whole hangar session (carries `paths:` scope per ADR-0.0.20 — no unscoped rule under a vendor surface)
<!-- gz-validate-skip: command-shape -->
- `tests/commands/test_skills.py` — unit tests: the `gz-mx` skill catalogs and its `gz_command` resolves to the real `gz mx` verb
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — read-only parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-08-mx-skill-and-agents-rule.md` — this brief (evidence recording)

## Creates These Files

- `.gzkit/rules/mx-mode.md`
- `.gzkit/skills/gz-mx/SKILL.md`

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md` body — the agent-facing binding lands as the scoped `mx-mode` rule file, not as new AGENTS.md prose (avoids the invariant-coherence re-render surface)
- `src/gzkit/mx/**` and `.claude/hooks/**` — the marker, checkpoint, and awareness-hook surface (OBPI-0.0.74-01/02/03/07)
<!-- gz-validate-skip: command-shape -->
- `gz mx enter` / `gz mx exit` command code (OBPI-0.0.74-04/05 surface) — this OBPI WIELDS `gz mx`, it does not implement it
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- gz-validate-skip: command-shape -->
1. REQUIREMENT: A `gz-mx` skill MUST exist as the operator's interface — operator operates the skill, the skill invokes `gz mx`, nobody shells out (tool-skill Invariant 1: the `gz mx` tool has a wielding skill) (maps to REQ-0.0.74-08-01).
2. REQUIREMENT: A binding `mx-mode` rule MUST tell agents to honor the marker AND that the PRIME DIRECTIVE binds the whole hangar session — guards advisory, OWNERSHIP not: fix what you know AND what you find; "not my work" / "out of scope" stays forbidden (maps to REQ-0.0.74-08-02).
<!-- gz-validate-skip: command-shape -->
3. REQUIREMENT: The skill's declared `gz_command` MUST resolve to the real `gz mx` verb (maps to REQ-0.0.74-08-03).
4. REQUIREMENT: The canonical skill and rule MUST be edited under `.gzkit/` and propagated to every vendor surface by `gz agent sync control-surfaces` (skill-surface-sync doctrine); the rule MUST carry a `paths:` scope (no unscoped rule under a vendor surface, ADR-0.0.20).
<!-- gz-validate-skip: command-shape -->
5. NEVER: Instruct the operator or agent to shell out to `gz mx` directly — the skill is the interface (skill+tool symbiont).
6. ALWAYS: Reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item #8 — quote it verbatim** into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — "doctrine and rule are inseparable for agents" (naked doctrine is rationalized away — every doctrinal claim ships with coupled enforcement) and "PRIME DIRECTIVE binds the entire session".
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote parent ADR § Decision item #8, STOP and re-read. Do not proceed until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` — Invariant 1 (every tool has a wielding skill) and Invariant 2 (`gz_command` resolves to the runbook-prescribed verb)
- [ ] `.gzkit/rules/skill-surface-sync.md` — edit `.gzkit/` first, bump the version marker, run `gz agent sync control-surfaces`
- [ ] A sibling skill's frontmatter (e.g. `.gzkit/skills/gz-implement/SKILL.md`, `.gzkit/skills/gz-arb/SKILL.md`) — the `gz_command:` field shape to mirror
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution — every `gz <verb>` in a SKILL.md must resolve to a registered parser verb

**Context:**

<!-- gz-validate-skip: command-shape -->
- [ ] Related OBPIs in same ADR — OBPI-0.0.74-04/05 deliver the `gz mx enter`/`gz mx exit` verb this skill wields; OBPI-0.0.74-07 the awareness hook this rule's doctrine pairs with

**Prerequisites (check existence, STOP if missing):**

<!-- gz-validate-skip: command-shape -->
- [ ] The `gz mx` verb is registered (delivered by sibling OBPI-0.0.74-04/05) so the `gz_command` resolves and `gz validate --cli-alignment` passes
- [ ] `tests/commands/test_skills.py` exists
- [ ] `gz agent sync control-surfaces` renders new canonical skills/rules to vendor mirrors

**Existing Code (understand current state):**

- [ ] An existing skill that declares `gz_command:` reviewed for frontmatter conventions before authoring `gz-mx`
- [ ] An existing scoped rule under `.gzkit/rules/` reviewed for the `paths:` + version-marker shape

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #8 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated; `gz validate --cli-alignment` green

### Gate 4: BDD (Heavy)

- [ ] `@REQ-0.0.74-08-03` scenario passes: `uv run -m behave --tags=@REQ-0.0.74-08-03 features/`

### Gate 5: Human

- [ ] Human attestation recorded (universal per ADR-0.0.36)

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --cli-alignment
uv run gz skill list
uv run mkdocs build --strict
test -f .gzkit/skills/gz-mx/SKILL.md
test -f .gzkit/rules/mx-mode.md
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# The gz-mx skill catalogs as the operator's hangar interface:
uv run gz skill list

# The skill's gz_command resolves to the real verb (operator operates the skill, the skill invokes the tool):
uv run gz mx --help
```

## Acceptance Criteria

<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.74-08-01 [support]: A `gz-mx` skill exists as the operator's interface to the hangar — the operator operates the skill, the skill invokes `gz mx`, nobody shells out (tool-skill Invariant 1: the `gz mx` tool has a wielding skill). Proof: `artifact_edited` ledger event for `.gzkit/skills/gz-mx/SKILL.md` + `gz validate --documents` exit 0 admitting the skill shape and `gz skill list` cataloging it.
- [ ] REQ-0.0.74-08-02 [support]: A binding `mx-mode` rule tells agents to honor the marker AND that the PRIME DIRECTIVE binds the whole hangar session — guards advisory, OWNERSHIP not: "fix what you know AND what you find; 'not my work' / 'out of scope' stays forbidden". Proof: `artifact_edited` ledger event for `.gzkit/rules/mx-mode.md` + `gz validate --documents` and `gz validate --unscoped-rules` exit 0 admitting the scoped rule shape.
<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.74-08-03 [behavior]: Given the `gz-mx` skill's declared `gz_command`, when tool-skill alignment is checked, then it resolves to the real `gz mx` verb. (@covers test in `tests/commands/test_skills.py`; `gz validate --cli-alignment` exit 0)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** mkdocs --strict + `gz validate --cli-alignment` green
- [ ] **Gate 4 (BDD):** scenario passes
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
