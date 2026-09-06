---
id: OBPI-0.36.0-04-agent-door
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 4
lane: Heavy
status: Draft
allowlist:
  - .gzkit/skills/second-opinion/
  - src/gzkit/second_opinion_door.py
  - tests/governance/test_second_opinion_agent_door.py
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-04-01
  - REQ-0.36.0-04-02
  - REQ-0.36.0-04-03
  - REQ-0.36.0-04-04
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_agent_door -v
  - uv run gz validate --req-kind-discipline
---

# OBPI-0.36.0-04-agent-door: Agent Door

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #4 - "OBPI-0.36.0-04: **agent-door** — The agent-invoked door, fired on the A4 tier rules and never on the agent's own unvalidated confidence"

**Status:** Draft

## Objective

Make the `second-opinion` skill **agent-invocable**, with the decision to invoke
taken by OBPI-06's tier rules and **never** by the agent's own assessment of how
confident it feels.

That negative clause is the whole substance. The agent asking for review is the
same agent that produced the conclusion under review, so its confidence is the
one input structurally disqualified from setting the threshold — a critic fired
only when the primary already doubts itself never fires on the confident-wrong
case, which is the case the ADR exists for. § Target Scope states it as the unit
definition: fired *"on the A4 tier rules rather than on the agent's own
unvalidated confidence."* A4 is recorded at § Promotion plan item 3 as *"the one
thing both passes independently reached"* — the sole point of agreement between
two critics that otherwise both returned PERFORATED.

This door is an entry point only. The skill and verdict schema are OBPI-01's, the
transport is OBPI-02's, and `second_opinion_door.py` is shared with OBPI-03 — this
brief adds the agent-side entry to that module and does not re-implement any of it.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/skills/second-opinion/` — the canonical skill gains its agent-invocation contract. Verified convention: canonical skills live at `.gzkit/skills/<slug>/SKILL.md` and are mirrored by `gz agent sync control-surfaces`.
- `src/gzkit/second_opinion_door.py` — the shared door module introduced by OBPI-03; this brief adds the agent-side entry. Verified convention: flat modules under `src/gzkit/` (siblings `second_opinion.py` OBPI-01, `second_opinion_transport.py` OBPI-02).
- `tests/governance/test_second_opinion_agent_door.py` — covering tests. Verified convention: `tests/governance/test_*.py`.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

## Denied Paths

- `src/gzkit/second_opinion_tiering.py` — OBPI-06 owns the tier rules. This door **calls** the tier decision; authoring it here would let the door set its own firing threshold, which is the exact inversion this OBPI exists to prevent.
- `.claude/skills/**`, `.agents/skills/**`, `.github/skills/**`, `src/gzkit/skills/**` — generated mirrors (`.gzkit/rules/skill-surface-sync.md` #4/#5). Edit canonical, then sync.
- `.claude/hooks/**`, `.claude/settings.json` — OBPI-09's dark `PreToolUse` adapter. A hook wired here would light the dark door outside its own brief (Boundary Invariant #3).
- `src/gzkit/cli/**` — Boundary Invariant #2, no new `gz` verb.
- `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, any Step-4b gate — Boundary Invariant #1, verbatim operator canon: *"we will NOT alter the OBPI process, at all!"*
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. ALWAYS: The firing decision MUST come from OBPI-06's tier resolution. The agent supplies the decision under review and its category; it never supplies the verdict on whether review is warranted.
2. NEVER: Read, accept, or infer the primary agent's self-reported confidence as an input to whether the door fires. A confidence field arriving from the caller is dropped, not weighted. This is the requirement the whole OBPI turns on.
3. ALWAYS: Render the critic's verdict **unedited**, including the UNASKED (scope-challenge) line — identical to OBPI-03's rendering contract, because a verdict softened on the agent path is softened in exactly the moments the operator is not watching.
4. NEVER: Let the primary agent's summary of the verdict substitute for the verdict. The ADR's persona names this as the failure *"an agent building it is most likely to commit."*
5. ALWAYS: Reuse OBPI-02's transport and OBPI-01's schema, and extend OBPI-03's `second_opinion_door.py` rather than forking a parallel module.
6. NEVER: Set `disable-model-invocation: true` on the skill. That key is how a skill is made operator-only (verified live in `.gzkit/skills/git-sync/SKILL.md`); setting it would make this door structurally unreachable.
7. NEVER: Add a `gz` verb, edit a generated mirror, or wire a hook.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Target Scope — R2's ruling that the unit is one skill with three doors, and this door's one-line definition.
- [ ] Parent ADR § Boundary Invariants #2 — no new `gz` verb; this brief is one of the three units it fences.
- [ ] Parent ADR § Promotion plan item 3 — A4 is *"the one thing both passes independently reached"*; that agreement is the warrant for tier-driven firing.
- [ ] Parent ADR § Appendices `A2` / `A3` — the two PERFORATED verdicts verbatim. These are primary sources and, per that section, **govern where the ADR's prose disagrees with them**; read them before treating any prose summary of the critique as settled.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Behavior Rules — Always #7 — *"<90% sure of direction? Ask the human"*; this door is the mechanical counterpart, and #7's threshold is agent-self-assessed where this door's must not be.
- [ ] `.gzkit/rules/agent-failure-modes.md` — pattern **Metagaming / gaming the gate** and pattern **Fabrication**; a door fired by the primary's own confidence is the shape both name.
- [ ] `.gzkit/rules/skill-surface-sync.md` — canonical-first editing, the `metadata.skill-version` bump, and the mandatory sync step.

**Context:**

- [ ] OBPI-0.36.0-01 — the skill and the JSON-Schema-pinned verdict this door dispatches and renders.
- [ ] OBPI-0.36.0-02 — the composed transport this door calls; do not re-implement it.
- [ ] OBPI-0.36.0-03 — the operator door, which owns `second_opinion_door.py`; this brief extends that module.
- [ ] OBPI-0.36.0-06 — the tier rules that decide whether this door fires. This brief consumes that decision and must not author it.

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/skills/` exists with at least one `<slug>/SKILL.md` — verified: `.gzkit/skills/gz-arb/SKILL.md`.
- [ ] `uv run gz skill list` prints the active catalog.
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/skills/second-opinion/` (created by OBPI-01)
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion_door.py` (created by OBPI-03)
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_agent_door.py`
- [ ] STOP if OBPI-06 has not landed: this door has no tier source to call, and wiring a placeholder threshold would ship the defect requirement #2 forbids.

**Existing Code (understand current state):**

- [ ] `.gzkit/skills/git-sync/SKILL.md:7` — read the `disable-model-invocation: true` frontmatter key. Verified present on exactly one skill; this door must NOT set it.
- [ ] `.gzkit/skills/gz-arb/SKILL.md` — read for the standard frontmatter block and Output Contract shape.
- [ ] `src/gzkit/second_opinion_door.py` — read OBPI-03's operator entry before adding the agent entry; the two share verdict rendering and must not diverge.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.governance.test_second_opinion_agent_door -v
uv run gz validate --req-kind-discipline
uv run gz skill list
uv run gz agent sync control-surfaces
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The skill is agent-invocable — it appears in the catalog without the
# operator-only key that git-sync carries.
uv run gz skill list

# A consequential-category decision routed through the agent door: the tier
# decides, and the critic reaches the raw surface itself.
uv run gz arb step --name adversary -- codex exec --sandbox read-only "Refute: the agent door may fire on the primary agent's self-reported confidence."
```

## Acceptance Criteria

- [ ] REQ-0.36.0-04-01 [BEHAVIOR]: Given a decision whose category OBPI-06 tiers as mandatory, when the agent door is invoked, then the critic is dispatched — and given a decision the tier resolves as not-selected, then it is not, regardless of any confidence value supplied by the caller.
- [ ] REQ-0.36.0-04-02 [BEHAVIOR]: Given a caller-supplied confidence field on the door's input, when the firing decision is computed, then that field is dropped and never reaches the tier resolution — a door that weights it fails.
- [ ] REQ-0.36.0-04-03 [BEHAVIOR]: Given a verdict carrying PREMISE-ATTACK, VERDICT and UNASKED, when the agent door renders it, then all three fields appear verbatim — identical to OBPI-03's contract, so the agent path cannot soften what the operator path preserves.
- [ ] REQ-0.36.0-04-04 [SUPPORT]: `.gzkit/skills/second-opinion/SKILL.md` declares the agent-invocation contract and does NOT carry `disable-model-invocation`, keeping the same skill reachable from both doors. Witnessed by `artifact_edited` citing `.gzkit/skills/second-opinion/SKILL.md` + `gz validate --documents`.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
