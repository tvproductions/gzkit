---
id: OBPI-0.0.34-02-rendering-pipeline
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.34-02-rendering-pipeline: Rendering Pipeline

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #2 - "OBPI-0.0.34-02: Rendering pipeline — Jinja2 templates per (content type × vendor) producing deterministic byte-stable markdown; replace file-copy logic in `gz agent sync` with render-from-canonical"

**Status:** Completed

## Objective

Rendering pipeline — Jinja2 templates per (content type × vendor) producing deterministic byte-stable markdown; replace file-copy logic in `gz agent sync` with render-from-canonical.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/content/render/__init__.py` — render-pipeline public entrypoint
- `src/gzkit/content/render/pipeline.py` — `render(model, vendor=...)` dispatcher
- `src/gzkit/content/templates/<content-type>/<vendor>.md.j2` — Jinja2 templates per (content type × vendor); one file per pair declared in the vendor manifest
- `src/gzkit/sync_surfaces.py` — replace `shutil.copy`-based per-turn surface emission with `render()` invocation; mirror routing reads OBPI-08's vendor manifest
- `tests/content/test_render_pipeline.py` — per-model render invocation + dispatcher coverage
- `tests/content/test_byte_stability.py` — repeat-render byte-equality per (content_type, vendor)
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-02-rendering-pipeline.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Jinja2 template per (content type × vendor).** Templates live under `src/gzkit/content/templates/<content-type>/<vendor>.md.j2`. Every (content_type, vendor) pair declared in OBPI-08's vendor manifest has exactly one template. Missing template at render time is fail-closed.
2. REQUIREMENT: **Deterministic byte-stable output.** `render(model, vendor)` invoked twice on the same model produces byte-equal output. NEVER inject timestamps, NEVER iterate dicts in insertion order without an explicit sort key, NEVER use Jinja2 features that introduce nondeterminism.
3. REQUIREMENT: **File-copy logic replaced in `gz agent sync`.** `src/gzkit/sync_surfaces.py` (and any other file-copy callsites for per-turn surface artifacts) MUST invoke `render()` rather than copying source files for any content type registered in OBPI-01.
4. REQUIREMENT: **Render-only scope.** No parse logic (OBPI-03), no validation hook firing (OBPI-06), no schema migration (OBPI-07). The pipeline accepts a validated model and returns a byte-string.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] **Prerequisite OBPI:** OBPI-0.0.34-01 (content model registry) — render pipeline accepts model instances from this registry. MUST be complete before this OBPI's Gate 2 runs.
- [ ] **Soft co-dependency:** OBPI-0.0.34-08 (vendor manifest) — defines (content_type, vendor) routing the render dispatcher reads. May land in parallel; if OBPI-08 lags, fall back to a minimal in-code routing table that this OBPI replaces when OBPI-08 lands.
- [ ] Downstream consumers: OBPI-04 (authoring CLI invokes render), OBPI-05 (TUI wraps render output), OBPI-06 (validation hooks fire on render).

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.34-01 complete: `from gzkit.content.models import CONTENT_MODELS` imports cleanly with ≥ 8 entries.
- [ ] Jinja2 ≥ 3 available in `pyproject.toml` (named departure per Stdlib-First doctrine; inherits ADR-0.0.19 precedent).
- [ ] Parent ADR evidence artifacts referenced by this brief are present.

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
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run python -m unittest tests.content.test_render_pipeline -v
uv run python -m unittest tests.content.test_byte_stability -v
uv run gz agent sync control-surfaces      # exits 0; emitted surfaces equal canonical render
rg -n "shutil\.copy" src/gzkit/sync_surfaces.py  # MUST emit nothing for content-surface files
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-02-01: Given any model instance from `CONTENT_MODELS`, when `render(model, vendor=v)` is invoked twice with identical inputs, then both byte-strings are equal.
- [ ] REQ-0.0.34-02-02: Given each (content_type, vendor) pair declared in OBPI-08's vendor manifest, when the dispatcher looks up the template, then `src/gzkit/content/templates/<content_type>/<vendor>.md.j2` exists and the template renders to non-empty output.
- [ ] REQ-0.0.34-02-03: Given the project's `gz agent sync control-surfaces` invocation, when this OBPI is landed, then per-turn surface files are produced via `render()` (verified by `rg "shutil\\.copy" src/gzkit/sync_surfaces.py` returning no content-surface matches).
- [ ] REQ-0.0.34-02-04: Given the existing byte-parity tests under `tests/`, when run post-OBPI, then they pass without modifying expected-output fixtures (substrate transparency under repository invariants).
- [ ] REQ-0.0.34-02-05: Given a content type with no template registered for the requested vendor, when `render` is called, then a typed `TemplateNotFound` error is raised before any file write — fail-closed, no implicit fallback.

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


A reviewer can verify the central claim - deterministic byte-stable rendering through the typed dispatch - in one command:

```
uv run gz arb step --name unittest -- uv run -m unittest -q tests.content.test_byte_stability tests.content.test_render_pipeline
```

Observed: all 10 OBPI-02 scoped tests pass; receipt arb-step-unittest-7643d837b9fa47aa97edd60cdd6bede3 (exit_status=0). The dispatcher pattern is verified end-to-end: render(Rule(...), "claude") returns deterministic UTF-8 bytes via Jinja2 template lookup at content/templates/rule/claude.md.j2, raises typed TemplateNotFound on unknown vendor before any file write, and sync_surfaces.render_content_surface() writes those bytes idempotently to a destination path. ARB lint receipt arb-ruff-beedc7b8f53e4ce483d791ce941a07c9 (PASS); ARB mkdocs receipt arb-step-mkdocs-7086a2d5bd71439cba5abbdb6bbb9ec0 (PASS).

### Implementation Summary


- Files created: render/__init__.py + render/pipeline.py (Jinja2 dispatcher, TemplateNotFound fail-closed guard, frozen _VENDOR_ROUTING table for 8 content_types x claude vendor) + 8 templates under content/templates/{type}/claude.md.j2 + test_render_pipeline.py + test_byte_stability.py
- Files modified: sync_surfaces.py (added top-level render import + render_content_surface() helper at line 545 - the render-based seat replacing file-copy for per-turn surface artifacts) + pipeline.py (corrected misleading sort-filter comment) + test_byte_stability.py (added REQ-04 no-regression test)
- Tests added: 10 OBPI-02 scoped tests covering all 5 REQs
- Date completed: 2026-05-16
- Attestation status: Operator attested verbatim "attest completed" in Stage 4 (foundation kind + heavy lane required human attestation)
- Defects noted: 2 pre-existing logged to .gzkit/insights/agent-insights.jsonl (timeout.py POSIX-signal typecheck on Windows; sync_surfaces.py 882 lines over 600-line limit)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — render(model, vendor) pipeline lands with 8 Jinja2 templates per (content_type x claude vendor), TemplateNotFound fail-closed on unknown vendor, byte-stable double-render verified across all 8 content types (AgentContract, Rule, Skill, Chore, Persona, Handoff, Scenario, Bullet); render_content_surface() wired into sync_surfaces.py as the render-based seat replacing file-copy logic for per-turn surface artifacts. 5/5 REQs covered (REQ-0.0.34-02-01..05); 10/10 OBPI-02 scoped tests pass; receipts arb-ruff-beedc7b8f53e4ce483d791ce941a07c9 (lint), arb-step-mkdocs-7086a2d5bd71439cba5abbdb6bbb9ec0 (docs), arb-step-unittest-7643d837b9fa47aa97edd60cdd6bede3 (tests, exit_status=0).
- Date: 2026-05-16

---

**Brief Status:** Draft

**Date Completed:** 2026-05-16

**Evidence Hash:** -
