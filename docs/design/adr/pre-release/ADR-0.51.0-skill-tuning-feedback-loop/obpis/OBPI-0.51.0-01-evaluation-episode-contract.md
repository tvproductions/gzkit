---
id: OBPI-0.51.0-01-evaluation-episode-contract
parent: ADR-0.51.0-skill-tuning-feedback-loop
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.51.0-01-evaluation-episode-contract: **evaluation-episode-contract** — Define the skill_tuning episode shape: dry-run walkthrough method (evaluator narrates the tool calls it would make against reference tasks, scored on call-shape fidelity), rubric dimensions (comprehension + tool-fidelity; tool-fidelity weight → 0 for non-tool skills), pass threshold, cross-model-family evaluator protocol, AND register the skill-evaluation vocabulary in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR (per ADR-0.0.43 cascade contract).

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`
- **Checklist Item:** #1 - "OBPI-0.51.0-01: **evaluation-episode-contract** — Define the skill_tuning episode shape: dry-run walkthrough method (evaluator narrates the tool calls it would make against reference tasks, scored on call-shape fidelity), rubric dimensions (comprehension + tool-fidelity; tool-fidelity weight → 0 for non-tool skills), pass threshold, cross-model-family evaluator protocol, AND register the skill-evaluation vocabulary in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR (per ADR-0.0.43 cascade contract)."

**Status:** Draft

## Objective

**evaluation-episode-contract** — Define the skill_tuning episode shape: dry-run walkthrough method (evaluator narrates the tool calls it would make against reference tasks, scored on call-shape fidelity), rubric dimensions (comprehension + tool-fidelity; tool-fidelity weight → 0 for non-tool skills), pass threshold, cross-model-family evaluator protocol, AND register the skill-evaluation vocabulary in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR (per ADR-0.0.43 cascade contract).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/skills_tuning/__init__.py` — new `gzkit.skills_tuning` subpackage
- `src/gzkit/skills_tuning/episode.py` — Pydantic model `SkillTuningEpisode` (named departure from stdlib per `.claude/rules/models.md`) exposing every field named in ADR § "Candidate episode shape" plus the rubric/dry-run/threshold contract
- `src/gzkit/skills_tuning/rubric.py` — rubric-dimension functions: `comprehension_score`, `tool_fidelity_score` (with `weight = 0` short-circuit for non-tool skills), composite `episode_score`
- `src/gzkit/skills_tuning/evaluator_protocol.py` — cross-model-family evaluator contract: structured prompts for the dry-run walkthrough, expected output shape, fail-closed on same-family evaluator
- `src/gzkit/schemas/skill_tuning_episode.json` — JSON schema dual of the Pydantic model (mirrors the `authoring_guide_protocol.json` precedent)
- `docs/governance/skill-tuning-episode-contract.md` — governance documentation explaining the episode shape, dry-run walkthrough method, rubric dimensions, pass threshold, and cross-model-family protocol
- `docs/design/prd/PRD-GZKIT-1.0.0.md` — register the skill-evaluation vocabulary section per ADR-0.0.43 cascade contract; cite ADR-0.51.0 as provenance
- `tests/test_skill_tuning_episode.py` — REQ-derived tests covering model validation, rubric short-circuit for non-tool skills, schema/model parity, PRD vocabulary registration
- `tests/fixtures/skill_tuning_episode/` — fixture episodes: tool skill happy path, non-tool skill (tool-fidelity weight → 0), cross-family evaluator pass/fail
- `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/obpis/OBPI-0.51.0-01-evaluation-episode-contract.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/chores/skill-authoring-quality/**`, `src/gzkit/chores/skill-trigger-testing/**` — chore extension is OBPI-0.51.0-02's surface (this OBPI defines the episode contract that those chores consume)
- `.gzkit/chores/skill-authoring-quality/**`, `.gzkit/chores/skill-trigger-testing/**` — same (canonical surface; OBPI-02 owns)
- `.gzkit/skills/**/SKILL.md` — the `optimize:` frontmatter block is OBPI-0.51.0-03's surface (this OBPI is consumed by OBPI-03's schema extension, not authored here)
- The Optimize chore directory (does not yet exist) — that's OBPI-0.51.0-04's surface
- The evaluator prose-improvement loop — OBPI-0.51.0-05's surface
- `docs/user/manpages/**`, `docs/user/runbook.md` — docs/runbook updates are OBPI-0.51.0-06's surface
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `SkillTuningEpisode` MUST be a frozen Pydantic `BaseModel` with `extra="forbid"` exposing every field named in ADR § Candidate episode shape: `skill_id`, `skill_version`, `baseline_skill_path`, `candidate_skill_patch`, `hard_goal_basket_id`, `source_evidence_refs`, `validation_results`, `trigger_alignment_score`, `output_contract_score`, `safety_boundary_score`, `scope_violation_count`, `trace_refs`, `arb_receipt_refs`, `promotion_decision`.
2. REQUIREMENT: `SkillTuningEpisode` MUST additionally encode the dry-run walkthrough contract: `dry_run_tool_calls: tuple[ToolCallNarration, ...]` with `Field(min_length=1)` so every episode cites at least one narrated tool call against the reference tasks.
3. REQUIREMENT: The rubric MUST expose two dimensions named in ADR § Intent — `comprehension` and `tool_fidelity` — and the `tool_fidelity` weight MUST short-circuit to 0 when the candidate skill declares no tool-call surface in its description (non-tool skills).
4. REQUIREMENT: A `pass_threshold: float` MUST be declared on the episode model — drift between threshold semantics is a contract change requiring an ADR amendment.
5. REQUIREMENT: The cross-model-family evaluator protocol MUST fail-closed when the evaluator's model family equals the session model family (per ADR § Anti-pattern "Do not evaluate skill fidelity with the same model family as the session model").
6. REQUIREMENT: The JSON schema at `src/gzkit/schemas/skill_tuning_episode.json` MUST validate identical examples to the Pydantic model — schema/model drift fail-closes the test suite.
7. REQUIREMENT: `docs/design/prd/PRD-GZKIT-1.0.0.md` MUST register the skill-evaluation vocabulary section per ADR-0.0.43 cascade contract, with provenance citing `ADR-0.51.0-skill-tuning-feedback-loop`. NOTE: OBPI-0.0.57-04 also registers a sibling governance-triage vocabulary section in the same file under a distinct heading; both registrations follow the ADR-0.0.43 cascade. The two OBPIs add ADDITIVE sections (no overlap of heading anchors), so merge order does not matter — but each section heading anchor MUST be unique within the PRD.
8. NEVER: Mutate any SKILL.md frontmatter from this OBPI — OBPI-03 owns the `optimize:` block extension on `SkillFrontmatter`.
9. NEVER: Author the chore that *consumes* this contract — OBPI-04 owns the Optimize chore; OBPI-02 owns the hard-basket-builder extension to the existing skill chores.
10. ALWAYS: Render any relative path in `baseline_skill_path`/`trace_refs`/`source_evidence_refs` via `.as_posix()` per `.claude/rules/cross-platform.md`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/skills_tuning/__init__.py` **CREATE**
- `src/gzkit/skills_tuning/episode.py` **CREATE**
- `src/gzkit/skills_tuning/rubric.py` **CREATE**
- `src/gzkit/skills_tuning/evaluator_protocol.py` **CREATE**
- `src/gzkit/schemas/skill_tuning_episode.json` **CREATE**
- `docs/governance/skill-tuning-episode-contract.md` **CREATE**
- `tests/test_skill_tuning_episode.py` **CREATE**
- `tests/fixtures/skill_tuning_episode/` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_skill_tuning_episode

# OBPI-specific surface checks
test -f src/gzkit/skills_tuning/episode.py
test -f src/gzkit/skills_tuning/rubric.py
test -f src/gzkit/skills_tuning/evaluator_protocol.py
test -f src/gzkit/schemas/skill_tuning_episode.json
test -f docs/governance/skill-tuning-episode-contract.md
grep -q "skill-evaluation" docs/design/prd/PRD-GZKIT-1.0.0.md
grep -q "ADR-0.51.0" docs/design/prd/PRD-GZKIT-1.0.0.md

# Schema/model parity
uv run python -c "from gzkit.skills_tuning.episode import SkillTuningEpisode; import json; print(json.dumps(SkillTuningEpisode.model_json_schema(), indent=2))" | diff - src/gzkit/schemas/skill_tuning_episode.json
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Construct an episode from a tool-skill fixture
uv run python -c "
from gzkit.skills_tuning.episode import SkillTuningEpisode
import json
data = json.load(open('tests/fixtures/skill_tuning_episode/tool_skill_happy.json'))
ep = SkillTuningEpisode.model_validate(data)
print(ep.model_dump_json(indent=2))
"

# Score a non-tool skill — expect tool_fidelity weight = 0
uv run python -c "
from gzkit.skills_tuning.rubric import episode_score
import json
data = json.load(open('tests/fixtures/skill_tuning_episode/non_tool_skill.json'))
print(episode_score(data))
"

# Demonstrate cross-family evaluator fail-closed
uv run python -c "
from gzkit.skills_tuning.evaluator_protocol import validate_evaluator_family
validate_evaluator_family(session_model_family='opus', evaluator_model_family='opus')  # raises
"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.51.0-01-01: Given `SkillTuningEpisode`, when constructed with all fields named in ADR § Candidate episode shape, then construction succeeds; when any required field is missing or an unknown key is passed, then `ValidationError` is raised (`extra="forbid"`).
- [ ] REQ-0.51.0-01-02: Given `SkillTuningEpisode.dry_run_tool_calls`, when constructed with empty tuple, then `ValidationError` is raised (`Field(min_length=1)` binding mirrors ADR-0.0.29 advisor-proof precedent).
- [ ] REQ-0.51.0-01-03: Given a non-tool skill (description declares no tool-call surface), when `tool_fidelity_score` is called, then the score component contributes `weight=0` to the composite — short-circuit confirmed.
- [ ] REQ-0.51.0-01-04: Given an evaluator whose model family equals the session model family, when `validate_evaluator_family` runs, then it raises a fail-closed error per ADR § Anti-pattern (no same-family evaluation).
- [ ] REQ-0.51.0-01-05: Given the JSON schema at `src/gzkit/schemas/skill_tuning_episode.json`, when a Pydantic-emitted episode is validated against it, then validation succeeds — schema/model drift fail-closes the test suite.
- [ ] REQ-0.51.0-01-06: Given `docs/design/prd/PRD-GZKIT-1.0.0.md`, when read, then a skill-evaluation vocabulary section exists with provenance citing `ADR-0.51.0-skill-tuning-feedback-loop` (ADR-0.0.43 cascade contract).
- [ ] REQ-0.51.0-01-07: Given `pass_threshold: float` on the episode model, when the episode is constructed without it, then `ValidationError` is raised; threshold semantics are recorded in `docs/governance/skill-tuning-episode-contract.md`.

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
