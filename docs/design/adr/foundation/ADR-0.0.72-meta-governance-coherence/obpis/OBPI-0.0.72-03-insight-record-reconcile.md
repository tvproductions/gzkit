---
id: OBPI-0.0.72-03-insight-record-reconcile
parent: ADR-0.0.72-meta-governance-coherence
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.72-03-insight-record-reconcile: Insight Record Reconcile

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- **Checklist Item:** #3 - "ADAPTER (C4): reconcile `InsightRecord` ↔ authoring contract — provide an InsightRecord-backed append helper (mechanical writer); align AGENTS.md Behavior Rule 11 + agent-contract-rationale 'required fields' prose with the model envelope (add ts/type; evidence as list[str]); verify a helper-produced append round-trips clean through the OBPI-01 validator."

**Status:** Draft

## Objective

An `InsightRecord`-backed append helper under `src/gzkit/insights/` becomes the single mechanical writer for `.gzkit/insights/agent-insights.jsonl`, so a hand-authored append can no longer drift from the schema that gates the file. The AGENTS.md Behavior Rule 11 authoring contract — edited at its composition source, never the rendered surface — and the agent-contract-rationale 'required fields' prose name exactly the model's required fields (`ts`, `type`, `scope`, `summary`) and specify `evidence` as a list, closing contradiction C4 (the model required `ts`/`type`/`evidence: list[str]` that the prose omitted, which failed a hand-authored append this session).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md` — parent ADR for intent and scope
- `src/gzkit/insights/model.py` — read/extend: the `InsightRecord` envelope (`ts`, `type`, `scope`, `summary` required; `evidence: list[str]`) is the contract the helper and prose reconcile to
- `src/gzkit/insights/append.py` — **CREATE** the `InsightRecord`-backed append helper (the mechanical writer); it constructs an `InsightRecord` and serializes one JSONL line so the append path cannot drift from the model
- `tests/governance/test_insight_append.py` — **CREATE** TDD tests: the helper's emitted line validates against `InsightRecord` and round-trips clean
- `.gzkit/templates/agents.md` — the AGENTS.md **composition source** consumed by `gz governance render --target agents-md` and re-rendered/byte-compared by `gz validate --invariant-coherence` (ADR-0.0.37). Behavior Rule 11 lives here (line 138). EDIT THIS, never the rendered `AGENTS.md` directly.
- `src/gzkit/templates/agents.md` — the wheel-distributed copy of the composition source; kept byte-equivalent to `.gzkit/templates/agents.md` per the ADR-0.0.31 distribution invariant (`gz validate --distribution`)
- `docs/governance/agent-contract-rationale.md` — the Behavior Rule 11 'Required fields' prose (lines 209-214) aligned to the model envelope

> **Composition nuance (ADR-0.0.37):** `AGENTS.md` is a COMPOSED surface — `gz validate --invariant-coherence` re-renders it from `.gzkit/templates/agents.md` and byte-compares against the committed file. Editing `AGENTS.md` directly breaks invariant-coherence. The implementer edits the composition source (`.gzkit/templates/agents.md`, mirrored to `src/gzkit/templates/agents.md`), then re-renders with `gz governance render --target agents-md`. If the exact source path is ever in doubt, resolve via the `gz content` surface — but it is NOT the rendered `AGENTS.md`.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `AGENTS.md` — the RENDERED composition target; NEVER hand-edit it (breaks `gz validate --invariant-coherence`). Edit `.gzkit/templates/agents.md` and re-render instead.
- `.gzkit/insights/agent-insights.jsonl` — the live trust surface; not rewritten by this OBPI (the helper appends to it at runtime, but no historical line is touched — trust-doctrine T2)
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The append helper MUST produce records that validate cleanly against `InsightRecord` (`src/gzkit/insights/model.py`) — every helper-written line passes `audit_insights_shape` / `gz validate --insights-shape`. The helper constructs the model first, then serializes; it never hand-builds a dict that could omit `ts`/`type`.
1. REQUIREMENT: The AGENTS.md Behavior Rule 11 prose MUST name EXACTLY the model's required fields — `ts`, `type`, `scope`, `summary` — and specify `evidence` as a list (not scalar-or-list). The agent-contract-rationale 'Required fields' list MUST match the same envelope.
1. NEVER: Edit the rendered `AGENTS.md` directly. Edit the composition source `.gzkit/templates/agents.md`, keep `src/gzkit/templates/agents.md` byte-equivalent, re-render via `gz governance render --target agents-md`; `gz validate --invariant-coherence` MUST stay clean.
1. ALWAYS: stdlib + Pydantic only — no new runtime dependency (STDLIB-FIRST doctrine; `InsightRecord` is the already-attested Pydantic surface).
1. ALWAYS: TDD — a failing test derived from the REQ (helper output validating against `InsightRecord`) is authored before the helper exists.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths; denied paths (especially the rendered `AGENTS.md`) remain untouched.
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief.
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
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
uv run gz validate --invariant-coherence
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Append a defect insight through the mechanical helper — no hand-authoring.
# The helper builds an InsightRecord (ts/type/scope/summary + evidence list),
# then serializes one JSONL line, so the append cannot omit ts/type.
uv run python -m gzkit.insights.append --type defect --scope insights/model.py --summary "InsightRecord required ts/type that AGENTS.md Rule 11 omitted (C4)" --evidence src/gzkit/insights/model.py:32

# The helper-written line validates against InsightRecord — the exact append
# that failed closed this session now passes the gating audit.
uv run gz validate --insights-shape

# The reconciled Behavior Rule 11 prose re-renders byte-identically — the
# composition source was edited, not the rendered AGENTS.md.
uv run gz validate --invariant-coherence
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.72-03-01 [behavior]: Given the `InsightRecord`-backed append helper invoked with a `defect` (or `improvement`) payload, when it writes a line to `.gzkit/insights/agent-insights.jsonl`, then the emitted line parses as JSON and validates against `InsightRecord` — `ts` (ISO8601+tz), `type`, `scope`, `summary` present and `evidence` a `list[str]`. (@covers test)
- [ ] REQ-0.0.72-03-02 [behavior]: Given a record produced by the append helper, when it is round-tripped through the OBPI-0.0.72-01 `gz validate --writer-model-roundtrip` validator's registered insight-append target, then the writer's actual emitted output re-validates against `InsightRecord` with no divergence (exit 0). (@covers test)
- [ ] REQ-0.0.72-03-03 [support]: AGENTS.md Behavior Rule 11 — edited at its composition source `.gzkit/templates/agents.md` (mirrored to `src/gzkit/templates/agents.md`) and re-rendered — names the model's required fields (`ts`, `type`, `scope`, `summary`) and specifies `evidence` as a list. Proof: the `artifact_edited` ledger event for `.gzkit/templates/agents.md` plus `gz validate --invariant-coherence` exit 0.
- [ ] REQ-0.0.72-03-04 [support]: The `docs/governance/agent-contract-rationale.md` 'Required fields' prose (Behavior Rule 11 rationale) is aligned with the `InsightRecord` envelope — adds `ts`/`type` and specifies `evidence` as a list. Proof: the `artifact_edited` ledger event for `agent-contract-rationale.md` plus `gz validate --documents` exit 0.

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
