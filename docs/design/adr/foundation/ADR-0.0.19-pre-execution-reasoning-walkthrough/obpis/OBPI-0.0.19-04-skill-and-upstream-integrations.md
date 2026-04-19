---
id: OBPI-0.0.19-04-skill-and-upstream-integrations
parent: ADR-0.0.19
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.19-04-skill-and-upstream-integrations: Skill definition and upstream integrations

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md`
- **Checklist Item:** #4 — Skill definition + upstream integrations. `.gzkit/skills/gz-justify/SKILL.md` with persona and Edit-tool-driven fill body; `gz-adr-evaluate` low-score footer; `gz-obpi-pipeline` low-confidence prompt; surface sync via `gz agent sync control-surfaces`.

**Status:** Draft

## Objective

Deliver the skill authoring and two upstream skill integrations that turn a usable CLI verb into a discoverable operator capability. This OBPI ships `.gzkit/skills/gz-justify/SKILL.md` with the `main-session` persona, Common Rationalizations + Red Flags tables, and a body that instructs the invoking agent to run the CLI, read the rendered scaffold, and use the Edit tool to replace each `_[To be filled]_` reasoning block with grounded reasoning. It also edits two neighboring skills: `gz-adr-evaluate` appends a low-score suggestion footer (weighted score <3.0 AND ADR has a tracking GHI or OBPIs), and `gz-obpi-pipeline` adds a low-confidence prompt at the Stage 1→2 boundary. Finally, the OBPI runs `gz agent sync control-surfaces` so `.claude/skills/` and `.github/skills/` mirrors are regenerated from canon.

## Lane

**Heavy** — Edits governance-canon skills (`gz-adr-evaluate`, `gz-obpi-pipeline`) and introduces a new canonical skill. Surface sync is mechanical; the behavior change in two existing skills requires version bumps and mirror regeneration.

> Heavy is reserved for command/API/schema/runtime-contract changes.

## Allowed Paths

- `.gzkit/skills/gz-justify/SKILL.md` — new canonical skill
- `.gzkit/skills/gz-justify/assets/` — any assets the skill body references (templates, cheat sheets); create only if needed
- `.gzkit/skills/gz-adr-evaluate/SKILL.md` — extend with low-score footer guidance; skill-version bump required
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — extend with low-confidence prompt at Stage 1→2; skill-version bump required
- `.claude/skills/gz-justify/**`, `.claude/skills/gz-adr-evaluate/**`, `.claude/skills/gz-obpi-pipeline/**` — regenerated outputs of `gz agent sync control-surfaces`; the sync command writes these; authoring edits are forbidden per `.gzkit/rules/skill-surface-sync.md`
- `.github/skills/gz-justify/**`, `.github/skills/gz-adr-evaluate/**`, `.github/skills/gz-obpi-pipeline/**` — regenerated outputs; same rule applies
- `tests/skills/test_gz_justify_skill.py` — unit tests asserting skill frontmatter validity, body sections present, `gz_command:` target resolves to a registered CLI verb
- `tests/skills/test_skill_surface_sync_justify.py` — tests that sync from `.gzkit/` produces equivalent `.claude/` and `.github/` mirrors for the three touched skills
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md` — parent ADR (read-only)

## Denied Paths

- `src/gzkit/justify/**`, `src/gzkit/commands/justify_cmd.py`, `src/gzkit/cli/parser_artifacts.py` — owned by OBPI-01/02/03; this OBPI consumes the public API, does not modify it
- `docs/user/commands/**`, `docs/user/manpages/**`, `features/**`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — owned by OBPI-05
- Any `.gzkit/skills/` edit that does not bump the skill-version per `.gzkit/rules/skill-surface-sync.md` § Version discipline
- Direct edits to `.claude/skills/` or `.github/skills/` (these are generated mirrors)
- New third-party dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/skills/gz-justify/SKILL.md` exists with frontmatter at minimum: `name: gz-justify`, `persona: main-session`, `description:` (>=40 chars describing investigatory use), `category: obpi-pipeline` (or equivalent), `metadata.skill-version: "6.0.0"`, `govzero-framework-version: "v6"`, `gz_command: justify`, `lifecycle_state: active`, `owner: gzkit-governance`, `last_reviewed: <today-ISO-date>`.
2. REQUIREMENT: The skill body contains the following sections in order: Purpose, Common Rationalizations, Red Flags, Persona, Trust Model, Invocation, When to Use, Procedure (numbered steps instructing the agent to invoke the CLI, read the scaffold, and fill `_[To be filled]_` blocks via the Edit tool), Acceptance Criteria for the skill's own completion state, Related Skills.
3. REQUIREMENT: The skill body NEVER instructs the agent to fabricate evidence — the Procedure explicitly requires the agent to ground each filled reasoning block in the evidence the CLI already gathered. Fabrication is listed as a Red Flag.
4. REQUIREMENT: The skill's declared `gz_command: justify` MUST resolve against the CLI parser per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 1. Enforced by the surface-sync test suite.
5. REQUIREMENT: The skill's Output Contract (if declared in body) must match the verb's default human-readable output per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 3. For `gz-justify`, the contract is "markdown scaffold with 8 H2 sections" — verified by a test that runs the CLI with a mocked anchor and asserts the first line of output contains an H1 or YAML frontmatter delimiter.
6. REQUIREMENT: `.gzkit/skills/gz-adr-evaluate/SKILL.md` is extended with a new subsection in the Procedure: after scoring completes and the weighted total is <3.0 AND the ADR's frontmatter `parent:` is a `GHI-<N>` or the ADR has at least one OBPI, the scorecard output appends a footer line: `"Consider: uv run -m gzkit justify <parent-GHI-or-first-OBPI>"` with the concrete identifier substituted. The skill-version is bumped to the next minor per version-discipline rules.
7. REQUIREMENT: `.gzkit/skills/gz-obpi-pipeline/SKILL.md` is extended at the Stage 1→2 boundary with a new guidance block: when the agent's self-reported confidence is <90% (per Prime Directive invariant 11), the skill body instructs running `uv run -m gzkit justify <current-OBPI-id> --save` before proceeding to Stage 2. The skill-version is bumped to the next minor.
8. REQUIREMENT: Both neighbor-skill edits explicitly cite `ADR-0.0.19` in a new "Related ADRs" or equivalent section of the skill body, so the coupling is traceable.
9. REQUIREMENT: After all three skills are authored/edited, `uv run gz agent sync control-surfaces` completes with exit 0, and the resulting `.claude/skills/gz-justify/SKILL.md` + mirrors match canon byte-for-byte (modulo any deterministic vendor-specific rendering).
10. REQUIREMENT: `uv run gz validate --surfaces` (or the equivalent surface validator) passes after sync.
11. REQUIREMENT: Skill tests pin all REQ-IDs. Test naming matches `.gzkit/rules/tests.md` conventions. Tests NEVER call `gz agent sync control-surfaces` in a way that mutates the live repo — they operate on tempfile copies of the canonical skill paths.
12. REQUIREMENT: Skill-version discipline per `.gzkit/rules/skill-surface-sync.md`: new skill starts at `6.0.0`; neighbor-skill edits increment the minor (governance-rule change category). Any edit without a bump fails the test suite.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.gzkit/rules/skill-surface-sync.md` — version discipline, canonical-vs-mirror rule, sync command
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` — Invariants 1/2/3 (the three invariants this skill will be checked against)
- [ ] `.gzkit/rules/behavioral-invariants.md` — Invariant 11 (the <90% confidence rule this skill mechanizes)
- [ ] Parent ADR — full context

**Context:**

- [ ] OBPI-0.0.19-02 brief + its delivered CLI surface (`uv run -m gzkit justify <anchor>`)
- [ ] OBPI-0.0.19-03 brief + its delivered validate subverb
- [ ] `.gzkit/skills/gz-adr-evaluate/SKILL.md` (current canon before edit)
- [ ] `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (current canon before edit)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01/02/03 complete and merged (skill body instructs invoking commands these OBPIs deliver)
- [ ] `uv run gz agent sync control-surfaces` command exists and exits 0 on the current canon (smoke before this OBPI begins)
- [ ] `.gzkit/skills/gz-adr-evaluate/SKILL.md` and `.gzkit/skills/gz-obpi-pipeline/SKILL.md` exist (confirmed via Glob)

**Existing Code (understand current state):**

- [ ] `.gzkit/skills/gz-plan-audit/SKILL.md` — exemplar of a skill with `gz_command:` frontmatter that resolves to a registered verb
- [ ] `.gzkit/skills/gz-design/SKILL.md` — exemplar of a non-mechanical advisory skill with main-session persona
- [ ] `tests/skills/` — existing skill test patterns (if present)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief REQ-IDs, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Surface-sync test passes after skill authoring

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`
- [ ] Markdown lint passes on all three skill files

### Gate 3: Docs (Heavy only)

- [ ] `uv run gz validate --surfaces` exits 0
- [ ] Surface mirrors regenerated and committed alongside canon

### Gate 4: BDD (Heavy only)

- [ ] No BDD scenarios in this OBPI; deferred to OBPI-05.

### Gate 5: Human (Heavy only)

- [ ] Human attestation deferred to ADR-level closeout per lane inheritance protocol.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest-justify-04 -- uv run -m unittest tests.skills.test_gz_justify_skill tests.skills.test_skill_surface_sync_justify

# Skill frontmatter + body shape
test -f .gzkit/skills/gz-justify/SKILL.md
grep -q "^name: gz-justify$" .gzkit/skills/gz-justify/SKILL.md
grep -q "^persona: main-session$" .gzkit/skills/gz-justify/SKILL.md
grep -q "gz_command: justify" .gzkit/skills/gz-justify/SKILL.md

# Neighbor-skill version bumps
grep -E "skill-version.*6\." .gzkit/skills/gz-adr-evaluate/SKILL.md
grep -E "skill-version.*6\." .gzkit/skills/gz-obpi-pipeline/SKILL.md

# Surface sync + validation
uv run gz agent sync control-surfaces
uv run gz validate --surfaces
```

## Acceptance Criteria

- [ ] REQ-0.0.19-04-01: Given `.gzkit/skills/gz-justify/SKILL.md` after this OBPI lands, when its frontmatter is parsed, then it contains all required keys per REQ-01 and `gz_command: justify` is present.
- [ ] REQ-0.0.19-04-02: Given the skill body, when scanned for required sections, then all of the following headings appear in order: Purpose, Common Rationalizations, Red Flags, Persona, Trust Model, Invocation, When to Use, Procedure, Acceptance Criteria, Related Skills.
- [ ] REQ-0.0.19-04-03: Given the skill body's Red Flags table, when scanned, then it contains a row naming fabrication of filled reasoning as a red flag.
- [ ] REQ-0.0.19-04-04: Given the skill's declared `gz_command: justify`, when resolved against the CLI parser (via `verify_gz_chain(["justify"])`), then the chain resolves successfully (per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 1).
- [ ] REQ-0.0.19-04-05: Given `.gzkit/skills/gz-adr-evaluate/SKILL.md` before vs after this OBPI, when diffed, then the post-edit file contains a new footer-guidance block that (a) cites the <3.0 threshold, (b) requires a tracking GHI or OBPI to exist, and (c) produces a `uv run -m gzkit justify <id>` suggestion line. The skill-version is incremented.
- [ ] REQ-0.0.19-04-06: Given `.gzkit/skills/gz-obpi-pipeline/SKILL.md` before vs after this OBPI, when diffed, then the post-edit file contains a new Stage 1→2 guidance block that cites Prime Directive invariant 11, fires when the agent's self-reported confidence is <90%, and suggests `uv run -m gzkit justify <current-OBPI-id> --save`. The skill-version is incremented.
- [ ] REQ-0.0.19-04-07: Given all three canon skill files authored/edited, when `uv run gz agent sync control-surfaces` runs, then it exits 0 and the resulting `.claude/skills/gz-justify/SKILL.md`, `.claude/skills/gz-adr-evaluate/SKILL.md`, and `.claude/skills/gz-obpi-pipeline/SKILL.md` match canon (allowing vendor-specific rendering), and equivalent `.github/skills/` mirrors are produced.
- [ ] REQ-0.0.19-04-08: Given `uv run gz validate --surfaces`, when it runs after sync, then it exits 0.
- [ ] REQ-0.0.19-04-09: Given the skill body declares an Output Contract for rendered scaffolds, when the verb is invoked with a mocked anchor, then the first line of default human-readable output is either an H1 (`# `) or a YAML frontmatter delimiter (`---`) — verified by an Invariant-3-style test.
- [ ] REQ-0.0.19-04-10: Given the test suite for this OBPI, when run, then no test mutates `.gzkit/skills/` or `.claude/skills/` at the live repo path; every test uses tempfile-based copies.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQ-IDs, surface-sync test passing
- [ ] **Code Quality:** Lint, format, type checks clean; markdown-lint clean
- [ ] **Value Narrative:** Skill is discoverable via Claude Code and the two upstream skills now suggest invocation at the right moments
- [ ] **Key Proof:** Diffs of the two neighbor skills pasted in Evidence alongside the new skill file path and `gz agent sync control-surfaces` exit 0 output
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
# Paste `gz validate --surfaces` output
```

### Gate 4 (BDD)

Not applicable at this OBPI; deferred to OBPI-05.

### Gate 5 (Human)

Deferred to ADR-level closeout.

### Value Narrative

**Before:** Even after the CLI verb exists (OBPI-02/03), there is no skill that tells an agent when to invoke it; upstream skills do not suggest it. The Prime Directive invariant remains unsurfaced at the moments it matters.

**After:** A new canonical skill at `.gzkit/skills/gz-justify/` is discoverable by Claude Code via slash-command and by terminal operators via `gz` help. Two upstream skills now surface `justify` at the right moments — `gz-adr-evaluate` after a low score, `gz-obpi-pipeline` at Stage 1→2 when confidence is low.

### Key Proof

```text
# Paste a short excerpt of the new skill's Procedure section
# Paste the new footer line added to gz-adr-evaluate
# Paste the new Stage 1→2 guidance added to gz-obpi-pipeline
# Paste the `gz agent sync control-surfaces` exit-0 output
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (deferred to ADR-level closeout)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
