---
id: OBPI-0.36.0-01-critic-skill-contract
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 1
lane: Heavy
status: Draft
allowlist:
  - .gzkit/skills/second-opinion/
  - src/gzkit/schemas/second_opinion_verdict.json
  - src/gzkit/second_opinion.py
  - tests/governance/test_second_opinion_contract.py
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-01-01
  - REQ-0.36.0-01-02
  - REQ-0.36.0-01-03
  - REQ-0.36.0-01-04
verification:
  - uv run gz validate --documents
  - uv run gz skill list
  - uv run -m unittest tests.governance.test_second_opinion_contract -v
---

# OBPI-0.36.0-01-critic-skill-contract: Critic Skill Contract

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #1 - "OBPI-0.36.0-01: **critic-skill-contract** — The `second-opinion` skill as one unit — both mandatory questions (scope challenge and conclusion challenge), a full-context read of the raw surface, and a schema-pinned verdict shape"

**Status:** Draft

## Objective

Ship `.gzkit/skills/second-opinion/SKILL.md` plus a JSON-Schema-pinned verdict
shape, such that a critic invocation is **structurally incapable** of returning a
verdict that omits either mandatory question. The unit of delivery is the skill —
not a hook, not a verb — because R2 dissolved the gate-vs-skill conflict in favor
of one skill with three doors, and the doors (OBPI-03, OBPI-04, OBPI-09) all
dispatch *this* contract.

Done looks like: a malformed verdict is **rejected by the schema**, not tolerated
and narrated around. The failure this closes is a critic that answers only *"is
the conclusion strong?"* and silently drops *"what question should be asked?"* —
which is the half that catches scope capture, and the half a primary agent's own
framing is least able to supply.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/skills/second-opinion/` — the canonical skill. Verified convention: every skill under `.gzkit/skills/` is a directory containing `SKILL.md` (e.g. `.gzkit/skills/gz-arb/SKILL.md`); this directory is green-field and is created by this OBPI.
- `src/gzkit/schemas/second_opinion_verdict.json` — the verdict schema. Verified convention: `src/gzkit/schemas/` holds `.json` schema files (`adr.json`, `ledger.json`, `authoring_guide_protocol.json`).
- `src/gzkit/second_opinion.py` — the verdict parser/validator the doors import. Verified convention: flat modules under `src/gzkit/` (`tasks.py`, `events.py`, `handoff_api.py`).
- `tests/governance/test_second_opinion_contract.py` — covering tests. Verified convention: `tests/governance/*.py`.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

## Denied Paths

- `src/gzkit/commands/obpi_complete_adversarial.py` — Step 4b. Boundary Invariant #1; read-only reference for OBPI-07, never edited here.
- `src/gzkit/cli/**` — no new `gz` verb (Boundary Invariant #2). The skill is dispatched by the skill runtime, not by a registered verb.
- `.claude/hooks/**` and `.claude/settings.json` — the `PreToolUse` adapter is OBPI-09 and lands dark. Wiring it here would collapse the split § Why nine forced.
- `src/gzkit/skills/**`, `.claude/skills/**`, `.agents/skills/**`, `.github/skills/**` — generated mirrors. `.gzkit/rules/skill-surface-sync.md` #4/#5: edit canonical, then `gz agent sync control-surfaces`.
- New runtime dependencies — STDLIB-FIRST; the schema is validated with stdlib `json` plus the existing Pydantic surface.

## Requirements (FAIL-CLOSED)

1. ALWAYS: The skill MUST pose BOTH mandatory questions — *"what question should be asked"* (scope challenge) and *"is the encountered conclusion strong?"* (conclusion challenge). The ADR's § The critic asks two questions records the operator ruling verbatim: *"both are possible, both are necessary, or we are resigned to the mire."*
2. NEVER: Accept a verdict object missing either question's field. The schema is the fence — a verdict that answers one question is invalid, not partial.
3. ALWAYS: The skill directs the critic to read the **raw surface** itself, never a primary-agent-curated digest. Operator verbatim: *"Of course it would be directed to explore the raw surface. This is necessary for it to impugn your misgivings, or validate the cogence of your work."*
4. NEVER: Introduce a `gz` verb, edit any file under `src/gzkit/cli/`, or modify Step 4b. Boundary Invariants #1 and #2.
5. ALWAYS: Carry `metadata.skill-version` and `last_reviewed` in frontmatter per `.gzkit/rules/skill-surface-sync.md` #2/#6, and run `gz agent sync control-surfaces` before completion.
6. NEVER: Let the verdict schema permit a free-text-only response. The UNASKED line must be a distinct field, because OBPI-03/04/09 render it as a *separate appended option* and cannot parse it out of prose.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Target Scope — the `critic-skill-contract` bullet and § Why nine, which explain why the skill is the unit and the hook is not.
- [ ] Parent ADR § Boundary Invariants — invariants #1 and #2 bind this brief.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § STDLIB-FIRST DOCTRINE — the schema uses stdlib `json`, not a new validator dependency.
- [ ] `.gzkit/rules/skill-surface-sync.md` — canonical-first editing, `metadata.skill-version` nesting, and the mandatory sync step.
- [ ] `.gzkit/rules/models.md` — Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` if the verdict is modeled in Python.

**Context:**

- [ ] OBPI-0.36.0-02 (transport) — consumes this verdict shape across the vendor boundary.
- [ ] OBPI-0.36.0-03/04/09 (the three doors) — all dispatch this skill; the UNASKED field becomes an appended option.

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/skills/` exists and contains at least one `<slug>/SKILL.md` to copy conventions from — verified: `.gzkit/skills/gz-arb/SKILL.md`.
- [ ] `src/gzkit/schemas/` exists and holds `.json` schemas — verified: `adr.json`, `ledger.json`, `authoring_guide_protocol.json`.
- [ ] `tests/governance/` exists — verified.
- [ ] `uv run gz skill list` runs and prints the active catalog — the post-sync discovery check.
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/skills/second-opinion/`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/schemas/second_opinion_verdict.json`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_contract.py`

**Existing Code (understand current state):**

- [ ] `.gzkit/skills/gz-arb/SKILL.md` — read for frontmatter shape (`name`, `persona`, `description`, `lifecycle_state`, `owner`, `last_reviewed`, `metadata.skill-version`, `model`).
- [ ] `src/gzkit/schemas/authoring_guide_protocol.json` — read as the precedent for a runtime-validated JSON envelope (ADR-0.0.30).
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py` lines 44-52 — the existing verdict vocabulary (`refuted`, `not-refuted`, `refuted-with-caveats`). Read-only: reuse the vocabulary rather than inventing a second one, per hexagonal rule 8 (prefer subsumption to a parallel model).
- [ ] `src/gzkit/events.py` `adversarial_validation` (line ~762) — the existing verdict event whose `verdict` Literal this schema must not contradict.

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.governance.test_second_opinion_contract -v
uv run gz skill list
uv run gz validate --req-kind-discipline
uv run gz agent sync control-surfaces
```

## Demo

```bash
# The skill is discoverable in the active catalog after sync
uv run gz skill list

# The verdict schema rejects a one-question verdict (the failure this OBPI closes)
uv run python -m gzkit.second_opinion --validate tests/fixtures/second_opinion/missing_unasked.json

# ...and admits a well-formed two-question verdict
uv run python -m gzkit.second_opinion --validate tests/fixtures/second_opinion/well_formed.json
```

## Acceptance Criteria

- [ ] REQ-0.36.0-01-01 [BEHAVIOR]: Given a verdict object that omits the scope-challenge (UNASKED) field, when it is validated against `second_opinion_verdict.json`, then validation fails with a message naming the missing question — a one-question verdict is invalid, never partial.
- [ ] REQ-0.36.0-01-02 [BEHAVIOR]: Given a verdict carrying both PREMISE-ATTACK/VERDICT and UNASKED fields, when it is validated, then it passes and the UNASKED text is retrievable as a discrete field rather than parsed out of prose.
- [ ] REQ-0.36.0-01-03 [SUPPORT]: `.gzkit/skills/second-opinion/SKILL.md` exists carrying both mandatory questions and the raw-surface directive, and declares `metadata.skill-version`. Witnessed by `artifact_edited` citing `.gzkit/skills/second-opinion/SKILL.md` + `gz validate --documents`.
- [ ] REQ-0.36.0-01-04 [BEHAVIOR]: Given the delivered verdict vocabulary, when it is compared against `events.py::adversarial_validation`, then the two agree on the verdict tokens — a second, differently-spelled vocabulary for the same concept fails.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
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

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
