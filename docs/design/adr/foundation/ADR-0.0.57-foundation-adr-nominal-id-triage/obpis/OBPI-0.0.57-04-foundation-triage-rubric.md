---
id: OBPI-0.0.57-04-foundation-triage-rubric
parent: ADR-0.0.57-foundation-adr-nominal-id-triage
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.57-04-foundation-triage-rubric: Foundation Triage Rubric

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- **Checklist Item:** #4 - "OBPI-0.0.57-04: **foundation-triage-rubric** — Define the ranking rubric: structured signal dimensions (insights-signal count, GHI-occurrence count, feature-unblocking count), judgment-assisted ranking with structural-only output, evidence citations; register the governance-triage vocabulary in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR (per ADR-0.0.43 cascade contract)."

**Status:** Draft

## Objective

**foundation-triage-rubric** — Define the ranking rubric: structured signal dimensions (insights-signal count, GHI-occurrence count, feature-unblocking count), judgment-assisted ranking with structural-only output, evidence citations; register the governance-triage vocabulary in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR (per ADR-0.0.43 cascade contract).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/foundation/rubric.py` — rubric scoring module: signal-dimension counters (insights-signal, GHI-occurrence, feature-unblocking) + scoring function emitting `FoundationTriageRankEntry`
- `src/gzkit/schemas/foundation_triage_rank_input.json` — JSON schema for the structural-only rank-input contract `{id, priority_score, evidence: [...]}`
- `docs/governance/foundation-triage-rubric.md` — governance documentation explaining each signal dimension and how the rubric composes them
- `docs/design/prd/PRD-GZKIT-1.0.0.md` — register the governance-triage vocabulary section per ADR-0.0.43 cascade contract; cite ADR-0.0.57 as provenance
- `tests/test_foundation_triage_rubric.py` — REQ-derived tests covering signal-dimension counters, structural-only output, and PRD vocabulary registration
- `tests/fixtures/foundation_triage_rubric/` — fixture foundation backlogs + insights JSONL + GHI corpus + expected rank-input output
- `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-04-foundation-triage-rubric.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/skills/gz-foundation-triage/SKILL.md` — skill body is OBPI-0.0.57-03's surface (this OBPI's modules are imported by the skill, not authored by the skill)
- `src/gzkit/foundation/triage.py` — composer module is OBPI-0.0.57-03's surface
- `src/gzkit/commands/plan.py` — allocator change is OBPI-0.0.57-02's surface
- `docs/design/adr/foundation/ADR-0.0.17-*/**`, `docs/design/adr/foundation/ADR-0.0.18-*/**` — doctrine amendments are OBPI-0.0.57-01's surface
- `docs/user/manpages/**`, `docs/governance/governance_runbook.md`, `docs/user/runbook.md` — manpage/runbook updates are OBPI-0.0.57-05's surface
- Mutations to any foundation ADR file under `docs/design/adr/foundation/` other than the parent ADR package
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `FoundationTriageRankEntry` MUST be a frozen Pydantic `BaseModel` with `extra="forbid"` exposing exactly `id: str`, `priority_score: int` (or composite score per fixture), and `evidence: tuple[EvidenceRef, ...]` with `Field(min_length=1)` so every ranked foundation cites at least one source signal.
2. REQUIREMENT: The rubric MUST compose three signal dimensions named in ADR § Decision item 2: `insights_signal_count` (from `.gzkit/insights/agent-insights.jsonl`), `ghi_occurrence_count` (from open GHIs), and `feature_unblocking_count` (count of pool/feature ADRs whose `depends_on` references this foundation).
3. REQUIREMENT: The output MUST be structural-only — `{id, priority_score, evidence}`; NEVER prose narrative or per-entry rationale strings (mirrors `ghi-triage` round-3 hardening per GHI #424).
4. REQUIREMENT: `docs/design/prd/PRD-GZKIT-1.0.0.md` MUST register the governance-triage vocabulary section per ADR-0.0.43 cascade contract, with provenance citing `ADR-0.0.57-foundation-adr-nominal-id-triage`. NOTE: OBPI-0.51.0-01 also registers a sibling skill-evaluation vocabulary section in the same file under a distinct heading; both registrations follow the ADR-0.0.43 cascade. The two OBPIs add ADDITIVE sections (no overlap of heading anchors), so merge order does not matter — but each section heading anchor MUST be unique within the PRD.
5. REQUIREMENT: The JSON schema MUST validate identical examples to the Pydantic model — schema/model drift fail-closes the test suite.
6. NEVER: Read or mutate the rubric scoring inside the skill body (OBPI-03); the rubric is a callable surface, not a procedure baked into prose.
7. NEVER: Emit a rank entry with empty `evidence` — every score must cite at least one source signal (`Field(min_length=1)` binding mirrors the ADR-0.0.29 advisor-proof binding precedent).
8. ALWAYS: Render any relative path in `evidence` via `.as_posix()` per `.claude/rules/cross-platform.md`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/foundation/rubric.py` **CREATE**
- `src/gzkit/schemas/foundation_triage_rank_input.json` **CREATE**
- `docs/governance/foundation-triage-rubric.md` **CREATE**
- `tests/test_foundation_triage_rubric.py` **CREATE**
- `tests/fixtures/foundation_triage_rubric/` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/**`
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
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_foundation_triage_rubric

# OBPI-specific surface checks
test -f src/gzkit/foundation/rubric.py
test -f src/gzkit/schemas/foundation_triage_rank_input.json
test -f docs/governance/foundation-triage-rubric.md
grep -q "governance-triage" docs/design/prd/PRD-GZKIT-1.0.0.md
grep -q "ADR-0.0.57" docs/design/prd/PRD-GZKIT-1.0.0.md

# Schema/model parity
uv run python -c "from gzkit.foundation.rubric import FoundationTriageRankEntry; import json; print(json.dumps(FoundationTriageRankEntry.model_json_schema(), indent=2))" | diff - src/gzkit/schemas/foundation_triage_rank_input.json
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Score a fixture foundation backlog
uv run python -m gzkit.foundation.rubric --foundation-root tests/fixtures/foundation_triage_rubric/backlog --insights tests/fixtures/foundation_triage_rubric/insights.jsonl --format json | jq '.rank_input'

# Inspect evidence citations on the top-ranked entry
uv run python -m gzkit.foundation.rubric --foundation-root tests/fixtures/foundation_triage_rubric/backlog --insights tests/fixtures/foundation_triage_rubric/insights.jsonl --format json | jq '.rank_input[0].evidence'

# Confirm structural-only output (no prose fields)
uv run python -m gzkit.foundation.rubric --foundation-root tests/fixtures/foundation_triage_rubric/backlog --format json | jq '.rank_input[0] | keys'
# Expected output: ["evidence", "id", "priority_score"]
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.57-04-01: Given `FoundationTriageRankEntry`, when an entry is constructed with non-empty `evidence`, then construction succeeds; when constructed with empty `evidence=()`, then `ValidationError` is raised (`Field(min_length=1)` binding).
- [ ] REQ-0.0.57-04-02: Given the rubric module, when scoring a fixture foundation, then the three signal dimensions named in ADR § Decision item 2 (`insights_signal_count`, `ghi_occurrence_count`, `feature_unblocking_count`) are each computed and contribute to `priority_score`.
- [ ] REQ-0.0.57-04-03: Given a rank entry, when extra fields like `rationale` or `why` are passed, then `extra="forbid"` raises `ValidationError` (structural-only invariant).
- [ ] REQ-0.0.57-04-04: Given `docs/design/prd/PRD-GZKIT-1.0.0.md`, when read, then a governance-triage vocabulary section exists with provenance citing `ADR-0.0.57-foundation-adr-nominal-id-triage` (ADR-0.0.43 cascade contract).
- [ ] REQ-0.0.57-04-05: Given the JSON schema at `src/gzkit/schemas/foundation_triage_rank_input.json`, when a Pydantic-emitted entry is validated against it, then validation succeeds — schema/model drift fail-closes the test suite.
- [ ] REQ-0.0.57-04-06: Given a fixture pool/feature ADR whose `depends_on` references a foundation ADR, when the rubric counts `feature_unblocking_count`, then that foundation's count increments by exactly one per matching dependent.

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
