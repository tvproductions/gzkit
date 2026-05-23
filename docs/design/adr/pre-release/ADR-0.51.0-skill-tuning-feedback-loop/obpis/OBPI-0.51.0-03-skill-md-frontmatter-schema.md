---
id: OBPI-0.51.0-03-skill-md-frontmatter-schema
parent: ADR-0.51.0-skill-tuning-feedback-loop
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.51.0-03-skill-md-frontmatter-schema: **skill-md-frontmatter-schema** — Define the optimize: metadata block in SKILL.md frontmatter: tested_against (model + date), content_hash, rubric_score, prior_opinion_trail. Persists the evaluation genealogy with no per-model skill forks.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`
- **Checklist Item:** #3 - "OBPI-0.51.0-03: **skill-md-frontmatter-schema** — Define the optimize: metadata block in SKILL.md frontmatter: tested_against (model + date), content_hash, rubric_score, prior_opinion_trail. Persists the evaluation genealogy with no per-model skill forks."

**Status:** Draft

## Objective

**skill-md-frontmatter-schema** — Define the optimize: metadata block in SKILL.md frontmatter: tested_against (model + date), content_hash, rubric_score, prior_opinion_trail. Persists the evaluation genealogy with no per-model skill forks.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/core/models.py` — extend `SkillFrontmatter` with an optional `optimize: SkillOptimizeBlock | None` field; declare `SkillOptimizeBlock` as a new frozen Pydantic `BaseModel` with `extra="forbid"` exposing `tested_against`, `content_hash`, `rubric_score`, `prior_opinion_trail`
- `src/gzkit/models/frontmatter.py` — re-export `SkillOptimizeBlock` alongside the existing `SkillFrontmatter` exports
- `src/gzkit/validate_pkg/surface.py` — extend validation to recognize the `optimize:` block; reject malformed blocks fail-closed
- `tests/test_skill_frontmatter_optimize.py` — REQ-derived tests covering: optimize-block absence is valid, well-formed block validates, malformed/extra-key block rejected
- `tests/fixtures/skill_frontmatter_optimize/` — fixture SKILL.md files: no-optimize-block, valid-optimize-block, malformed-optimize-block
- `docs/governance/skill-optimize-frontmatter.md` — governance documentation explaining the block's fields, the evaluation-genealogy semantics, and why no per-model skill forks
- `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/obpis/OBPI-0.51.0-03-skill-md-frontmatter-schema.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/skills/**/SKILL.md` — this OBPI defines the schema; populating the `optimize:` block on real skill files is OBPI-04's chore output (deferred until Optimize chore writes evaluation episodes)
- `src/gzkit/skills_tuning/**` — episode model is OBPI-0.51.0-01's surface (this OBPI imports from it for reference but does not edit)
- `src/gzkit/chores/skill-authoring-quality/**`, `src/gzkit/chores/skill-trigger-testing/**` — chore extension is OBPI-02's surface
- Optimize chore directory — OBPI-04's surface
- `.gzkit/chores/**` — no chore canon edits in this OBPI
- `docs/user/manpages/**`, `docs/user/runbook.md` — docs/runbook updates are OBPI-06's surface
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `SkillOptimizeBlock` MUST be a frozen Pydantic `BaseModel` with `extra="forbid"` exposing the four fields named in ADR § Checklist item 3: `tested_against: TestedAgainst` (model + date), `content_hash: str`, `rubric_score: float`, `prior_opinion_trail: tuple[PriorOpinion, ...]`.
2. REQUIREMENT: `SkillFrontmatter` MUST gain a NEW optional field `optimize: SkillOptimizeBlock | None = None` (default None) — pre-existing SKILL.md files without the block MUST continue to validate (backward compatibility invariant).
3. REQUIREMENT: When `optimize:` is present, EVERY field MUST be present — a partial `optimize:` block fail-closes validation (no half-populated genealogy).
4. REQUIREMENT: `content_hash` MUST be a stable SHA-256 hex digest of the canonical SKILL.md body (excluding frontmatter) — drift between recorded hash and computed hash is the signal for "the skill body changed since last evaluation."
5. REQUIREMENT: `prior_opinion_trail` MUST be an ordered tuple (oldest → newest) so the genealogy is reproducible — never a set or unordered collection.
6. REQUIREMENT: `gz validate --surfaces` MUST recognize the `optimize:` block; presence of an unknown frontmatter key inside `optimize:` MUST fail-close per `extra="forbid"`.
7. NEVER: Fork a skill into per-model variants (`SKILL.opus.md`, `SKILL.haiku.md`) — the genealogy lives in `prior_opinion_trail` (ADR § Intent "no per-model skill forks").
8. NEVER: Populate the `optimize:` block on any existing canonical SKILL.md from this OBPI — schema authoring only; population is OBPI-04's runtime output.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `tests/test_skill_frontmatter_optimize.py` **CREATE**
- `tests/fixtures/skill_frontmatter_optimize/` **CREATE**
- `docs/governance/skill-optimize-frontmatter.md` **CREATE**

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
uv run gz validate --surfaces
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_skill_frontmatter_optimize

# OBPI-specific surface checks
uv run python -c "from gzkit.core.models import SkillFrontmatter, SkillOptimizeBlock; print(SkillFrontmatter.model_fields['optimize'])"
uv run python -c "from gzkit.models.frontmatter import SkillOptimizeBlock; print('export OK')"

# Backward compatibility: every existing canonical SKILL.md still validates
uv run gz validate --surfaces
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Validate a fixture SKILL.md with a well-formed optimize: block
uv run python -c "
from gzkit.core.models import SkillFrontmatter
import yaml
fm = yaml.safe_load(open('tests/fixtures/skill_frontmatter_optimize/valid_optimize.yaml'))
print(SkillFrontmatter(**fm))
"

# Validate a malformed optimize: block — expect ValidationError
uv run python -c "
from gzkit.core.models import SkillFrontmatter
import yaml
fm = yaml.safe_load(open('tests/fixtures/skill_frontmatter_optimize/malformed_optimize.yaml'))
try:
    SkillFrontmatter(**fm)
except Exception as e:
    print(f'Rejected: {e}')
"

# Confirm backward compatibility on the live skill corpus
uv run gz validate --surfaces 2>&1 | tail -10
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.51.0-03-01: Given `SkillFrontmatter`, when constructed WITHOUT an `optimize:` block, then construction succeeds (backward compatibility invariant); existing canonical SKILL.md files MUST validate post-change.
- [ ] REQ-0.51.0-03-02: Given `SkillOptimizeBlock`, when constructed with all four fields (`tested_against`, `content_hash`, `rubric_score`, `prior_opinion_trail`), then construction succeeds.
- [ ] REQ-0.51.0-03-03: Given `SkillOptimizeBlock`, when constructed with three of four fields (partial block), then `ValidationError` is raised — no half-populated genealogy.
- [ ] REQ-0.51.0-03-04: Given `SkillOptimizeBlock`, when constructed with an unknown key, then `extra="forbid"` raises `ValidationError`.
- [ ] REQ-0.51.0-03-05: Given two SKILL.md states differing only in body, when `content_hash` is computed for each, then the hashes differ — body-change detection invariant.
- [ ] REQ-0.51.0-03-06: Given `prior_opinion_trail` is constructed as a tuple of three entries in order [A, B, C], when the field is read back, then the order is preserved as [A, B, C] — never reshuffled.
- [ ] REQ-0.51.0-03-07: Given `gz validate --surfaces` runs against the current `.gzkit/skills/**` corpus, when no skill carries an `optimize:` block, then exit code is 0 (no false positives introduced by the new schema).

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
