---
id: OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion
parent: ADR-0.34.0-foundation-sunset
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion: Grandfather Manifest And Closed Kind Assertion

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`
- **Checklist Item:** #1 - "grandfather-manifest-and-closed-kind-assertion: Land data/foundation_grandfather.json and the frozen Pydantic FoundationGrandfatherManifest model (identity-only: id, title, semver, frozen_at; extra=forbid; NO lifecycle field). Extend gz validate --taxonomy with the closed-kind assertion (every on-disk kind:foundation ADR must be in the manifest -> finding foundation_kind_closed) and the manifest-integrity assertion (manifest subset-of on-disk foundations -> finding grandfather_dangling). Add the golden-file tamper-guard test pinning the manifest to the sunset roster so reopening surfaces as a deliberate diff. (heavy lane: new schema/manifest, new validator scope)."

**Status:** Draft

## Objective

Land the committed closed grandfather manifest (`data/foundation_grandfather.json`) and its frozen identity-only `FoundationGrandfatherManifest` Pydantic model, then extend `gz validate --taxonomy` with a closed-kind assertion (`foundation_kind_closed`) and a manifest-integrity assertion (`grandfather_dangling`), guarded by a golden-file test that pins the manifest to the sunset roster — so the foundation kind's membership becomes a committed, machine-checked, two-way-door set rather than an implicit on-disk drift surface.

## Lane

**Heavy** - This OBPI adds a new committed data manifest, a new frozen Pydantic model (a schema-bearing contract), and two new fail-closed `gz validate --taxonomy` findings that change the validator's runtime exit contract. New schema/manifest and new validator scope are external-contract surfaces per the lane rules; this OBPI is Heavy.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new files (existence-gate exempt, GHI #419). -->

- `data/foundation_grandfather.json` — **CREATE**: the committed closed grandfather manifest instance (identity-only entries)
- `src/gzkit/models/foundation_grandfather.py` — **CREATE**: the frozen `FoundationGrandfatherManifest` Pydantic model + `TypeAdapter` loader; home follows the `src/gzkit/models/security_surfaces.py` data-registry precedent — a `data/*.json` registry validated by a frozen model, no separate JSON schema
- `src/gzkit/governance/trust_audits/taxonomy.py` — additive ONLY: extend the `--taxonomy` audit with the `foundation_kind_closed` and `grandfather_dangling` assertions; no existing assertion touched
- `tests/governance/test_foundation_grandfather_manifest.py` — **CREATE**: model-validation tests (extra="forbid" / lifecycle rejection / required-field tests) and the golden-file tamper-guard test
- `tests/governance/test_taxonomy_closed_kind.py` — **CREATE**: the two-finding validator behavior tests (`foundation_kind_closed`, `grandfather_dangling`)
- `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md` — parent ADR, READ-ONLY (intent and scope reference only)
- `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/obpis/OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/cli/**` — CLI authoring-rejection of `--kind foundation` is OBPI-0.34.0-02, not this OBPI
- The terminal-partition / `foundation_limbo` gate, the `foundation_grandfathered` ledger event, and the coupled-surface doctrine sweep — OBPI-0.34.0-03 and OBPI-0.34.0-04
- `data/foundation_grandfather.json` POPULATION with the real ~51-entry sunset roster and the `gz adr demote` migration — that is OBPI-0.34.0-04 (execute-migration); this OBPI lands the manifest structure/model/validator and the golden-file guard, not the migration action
- `src/gzkit/schemas/adr.json` — the `kind` enum stays intact; this OBPI does not touch the schema enum (closure is enforced around the enum, not by editing it)
- `.gzkit/ledger.jsonl` — never edited directly
- Wiring `--taxonomy` into `gz check` (gate registration is OBPI-04's last act; the ADR forbids landing the gate green while the tree is non-terminal)
- New runtime dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: `data/foundation_grandfather.json` is a committed closed manifest of IDENTITY-ONLY entries — each entry carries exactly `id`, `title`, `semver`, `frozen_at` and nothing else.
2. NEVER: store a `lifecycle` field (or any Layer-2 lifecycle fact) in the manifest — lifecycle is read live from the ledger; baking it into a committed Layer-1 file is the exact state-doctrine drift the ADR-0.0.37 frontmatter-lie demonstrated (parent ADR § Decision, Alternative 3 REJECTED).
3. ALWAYS: `FoundationGrandfatherManifest` uses `model_config = ConfigDict(frozen=True, extra="forbid")`; extra keys and a `lifecycle` key both raise `ValidationError`; `id`/`title`/`semver`/`frozen_at` are all required.
4. ALWAYS: the `foundation_kind_closed` assertion fails closed (exit 3) when any on-disk `kind: foundation` ADR is absent from the manifest — the manifest is the closed membership set, and the on-disk foundation set must be a subset of it.
5. ALWAYS: the `grandfather_dangling` assertion fails closed (exit 3) when any manifest entry has no on-disk foundation ADR package — the manifest must not name a foundation that does not exist on disk.
6. ALWAYS: the golden-file test fails when `data/foundation_grandfather.json` diverges from the pinned sunset roster, so reopening the kind (adding/removing an entry) surfaces as a deliberate, reviewable diff — a closed set with a freely-editable manifest is not closed (parent ADR § Consequences, Review Refinement (a)).
7. NEVER: edit the `kind` enum in `src/gzkit/schemas/adr.json` — `foundation` stays a valid schema value so it continues to validate the grandfathered ADRs; closure is enforced AROUND the enum.
8. REQUIREMENT: new findings emit three-part guardrail-feedback prose (what failed / why forbidden with the cited invariant / governed next step) per `.gzkit/rules/guardrail-feedback-prose.md`.
9. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief; denied paths remain untouched.
10. ALWAYS: Reconcile the brief with the parent ADR § Decision before implementation begins; every acceptance REQ derives from the Decision item, not from a run of the code.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — the line this OBPI implements**, quoted verbatim: "DATA MODEL: data/foundation_grandfather.json with a frozen Pydantic FoundationGrandfatherManifest (extra=forbid) holding IDENTITY-ONLY entries (id, title, semver, frozen_at) and NO lifecycle field - storing lifecycle would bake a Layer-2 fact into a committed Layer-1 file, the exact state-doctrine drift the 0.0.37 frontmatter-lie demonstrated." plus "extend 'gz validate --taxonomy' (ADR-0.0.17) with two fail-closed assertions - closed-kind (every on-disk kind:foundation ADR must appear in a committed grandfather manifest) and terminal-partition ...", and Review Refinement (a): "the grandfather manifest is protected by a golden-file test pinning it to the sunset roster, so reopening the kind surfaces as a deliberate reviewable diff." (This OBPI owns closed-kind + manifest-integrity + golden-file; terminal-partition is OBPI-03/04.)
- [ ] Parent ADR § Intent — the sunset why-frame: the kind is SEALED not deleted; the enum stays valid for the grandfathered set.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/models.md` — frozen Pydantic model contract (`ConfigDict(frozen=True, extra="forbid")`, `Field(...)` discipline)
- [ ] `.gzkit/rules/guardrail-feedback-prose.md` — three-part fail-closed recovery prose for the new findings
- [ ] `docs/governance/state-doctrine.md` — Layer-1/Layer-2/Layer-3 separation; why lifecycle stays out of the committed manifest
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context (existing surfaces to mirror):**

- [ ] `src/gzkit/models/security_surfaces.py` — the data-registry frozen-model + `TypeAdapter` loader precedent to mirror (no separate JSON schema)
- [ ] `src/gzkit/governance/trust_audits/taxonomy.py` — the `audit_adr_taxonomy` function, `_parse_adr_frontmatter`, and the `_is_nested_adr_artifact` skip convention to extend
- [ ] Related OBPIs in same ADR (02 authoring-rejection, 03 terminal-partition, 04 execute-migration) — respect the seam boundaries in Denied Paths

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md` exists
- [ ] `src/gzkit/governance/trust_audits/taxonomy.py` exists (the audit to extend)
- [ ] `src/gzkit/models/` exists (the model home)

**Existing Code (understand current state):**

- [ ] Existing `tests/governance/` taxonomy tests reviewed before authoring new ones
- [ ] `audit_adr_taxonomy` frontmatter/kind reading reviewed for the on-disk foundation enumeration this OBPI reuses

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from the four acceptance REQs, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated (manifest/validator behavior; no operator-doc verb change lands in this OBPI)

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (brief-level, universal per ADR-0.0.36)

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
uv run gz validate --taxonomy
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. -->

```bash
uv run gz validate --taxonomy
uv run gz validate --taxonomy --json
uv run -m unittest tests.governance.test_foundation_grandfather_manifest -v
uv run -m unittest tests.governance.test_taxonomy_closed_kind -v
```

The `--taxonomy` run exits 0 when every on-disk `kind: foundation` ADR appears
in `data/foundation_grandfather.json` and every manifest entry has an on-disk
package. The `--json` form prints the findings array; when a foundation ADR is
absent from the manifest it carries a `foundation_kind_closed` finding and the
process exits 3, and when a manifest entry names a nonexistent package it
carries a `grandfather_dangling` finding and exits 3. The two unittest modules
demonstrate the model rejecting a `lifecycle`/extra key and the golden-file
guard failing on a manifest that diverges from the pinned roster.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
Each REQ declares exactly one [kind] per ADR-0.0.59.
-->

- [ ] REQ-0.34.0-01-01 [BEHAVIOR]: `gz validate --taxonomy` emits finding `foundation_kind_closed` and exits 3 when an on-disk `kind: foundation` ADR is absent from `data/foundation_grandfather.json`.
- [ ] REQ-0.34.0-01-02 [BEHAVIOR]: `gz validate --taxonomy` emits finding `grandfather_dangling` and exits 3 when a manifest entry has no on-disk foundation ADR package.
- [ ] REQ-0.34.0-01-03 [BEHAVIOR]: `FoundationGrandfatherManifest` raises `ValidationError` for an entry carrying a `lifecycle` field or any extra key (`extra="forbid"`), and for an entry missing any of `id`, `title`, `semver`, `frozen_at`.
- [ ] REQ-0.34.0-01-04 [BEHAVIOR]: the golden-file test fails when `data/foundation_grandfather.json` diverges from the pinned sunset roster, so reopening the kind surfaces as a deliberate reviewable diff.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build clean
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Brief-level human attestation recorded
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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before: the foundation set was whatever `kind: foundation` files happened to sit
on disk — anyone could drop a new foundation ADR into the tree and it was
silently a member, with no committed, reviewable record of the closed roster.
After: `data/foundation_grandfather.json` is the committed closed membership
set, `FoundationGrandfatherManifest` mechanically forbids storing Layer-2
lifecycle in the Layer-1 file, and `gz validate --taxonomy` fails closed on both
an unlisted on-disk foundation (`foundation_kind_closed`) and a manifest entry
with no package (`grandfather_dangling`) — with the golden-file guard making any
change to the roster a deliberate reviewable diff.

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

```text
# uv run gz validate --taxonomy --json   (after adding an unlisted kind:foundation ADR)
# -> findings array carries {"type": "foundation_kind_closed", ...}; exit 3
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
