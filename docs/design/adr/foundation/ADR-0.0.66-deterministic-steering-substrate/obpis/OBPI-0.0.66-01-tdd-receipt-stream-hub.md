---
id: OBPI-0.0.66-01-tdd-receipt-stream-hub
parent: ADR-0.0.66-deterministic-steering-substrate
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.66-01-tdd-receipt-stream-hub: Tdd Receipt Stream Hub

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- **Checklist Item:** #1 - "tdd-receipt-stream-hub: Establish the tdd-receipt-stream as THE shared append-only governance-event receipt stream - event-kind registry plus append-only emission path. Fold in the rival ADR-pool.tdd-emission-and-graph-rot-remediation (verified RED/GREEN emission semantics). This is the hub the Harness Hardening enforcement spine ALSO consumes; the receipt event-kind schema is the one-way-ish element, so it lands FIRST and is got right before any consumer. Layer-3-never-source-of-truth; the ledger remains system-of-record. (heavy lane: new ledger event types)."

**Status:** Draft

## Objective

Establish the `tdd-receipt-stream` as THE single append-only governance-event receipt stream: a closed event-kind registry plus a verified emission path, with TDD RED/GREEN as the inaugural kind (folding in the rival `ADR-pool.tdd-emission-and-graph-rot-remediation`'s verified-emission semantics — RED must actually fail, GREEN must actually pass). This is the shared hub both this ADR's orientation surfaces (OBPIs 02-05) and the return-to-health Harness Hardening enforcement spine consume. Because the receipt event-kind schema is the one-way-ish element of the whole ADR, this OBPI lands FIRST and gets the registry + schema right before any consumer depends on it. The ledger remains system-of-record; the stream is append-only and never source-of-truth for derived views. This OBPI delivers the hub (registry + schema + emit + ledger event types) only — no gz next, no read-views, no queryability.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/events.py` — new receipt event types for the stream's inaugural kind(s)
- `src/gzkit/schemas/` — new `*_receipt.schema.json` for the event-kind(s); event-kind registry schema
- `src/gzkit/` — the stream emission module (append path) and event-kind registry module
- `src/gzkit/cli/` — the emit verb wiring for the inaugural TDD kind (gz tdd red|green or the generic gz event emit per the design-tension resolution)
- `tests/` — REQ-derived tests for registry, schema, and verified emission
- `docs/user/manpages/` — manpage for any new CLI verb (Heavy-lane CLI doctrine)
- `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/ledger.jsonl` — the ledger is system-of-record; never hand-edited (write only via gzkit emission code)
- Any gz next / gz metrics / gz search / gz insights surface — those are OBPIs 02-05, not this hub
- The six coalesced pool ADRs and ADR-0.0.46/0.0.47/0.0.48 frontmatter — this ADR declares supersession; demotion is a separate follow-up (Boundary Invariant 5)
- New runtime dependencies (stdlib-first; the stream is JSON + ledger, no new deps)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS keep the stream append-only and the ledger system-of-record: receipt events are appended through gzkit emission code, never hand-written; the stream is Layer-3-never-source-of-truth (ADR § Boundary Invariant 3, Architectural Boundary 6).
2. ALWAYS make emission VERIFIED, not trust-based, for the inaugural TDD kind: a `tdd_red_observed` event is emitted only after the test target is actually run and observed to fail (non-zero exit, classified failure kind); a `tdd_green_observed` event only after it is observed to pass. This is the load-bearing property folded in from `ADR-pool.tdd-emission-and-graph-rot-remediation` — it closes the write-tests-after-implementation-and-claim-RED loophole.
3. ALWAYS define the event-kind registry as the single source for what kinds exist (kind name, schema path, emit path, pairing rule). NEVER let a consumer (OBPIs 02-05 or the enforcement spine) invent a parallel receipt store; the registry is the one place kinds are declared.
4. ALWAYS use Pydantic `BaseModel` with `ConfigDict(extra="forbid")` for the event models per `.gzkit/rules/models.md`; render any path-shaped identifier via `.as_posix()` per `.gzkit/rules/cross-platform.md`.
5. NEVER reject collection-errors as RED: a test that fails to collect is "infrastructure broken", not a valid RED observation — classify and reject it (inherited from the rival ADR's verification semantics).
6. NEVER use `Optional[str]` / `List[str]` syntax per `.gzkit/rules/pythonic.md`; write `str | None` and `list[str]`.
7. ALWAYS get the event-kind schema right in THIS OBPI: it is the one-way-ish element of the ADR (ADR § Reversibility). A later schema change is migration-shaped; no consumer OBPI may land until this schema is stable.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 1 — quote verbatim into Implementation Summary:** *"tdd-receipt-stream hub (event-kind registry plus append-only emission; the one-way-ish receipt event-kind schema lands FIRST and is got right before any consumer)."* The Decision item is the contract; everything else hangs off it. Read also the COALESCES clause naming `tdd-receipt-stream` (THE HUB) folding in `ADR-pool.tdd-emission-and-graph-rot-remediation`.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**`
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
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz tdd red tests/test_steering_substrate_demo.py --req REQ-0.0.66-01-01
uv run gz tdd green tests/test_steering_substrate_demo.py --req REQ-0.0.66-01-01
uv run gz tdd chain REQ-0.0.66-01-01
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.66-01-01 [BEHAVIOR]: Given a closed event-kind registry, when a kind is looked up, then the registry returns its name, schema path, emit path, and pairing rule; a `@covers`-decorated test asserts the inaugural TDD kind(s) are registered and that an unknown kind raises rather than silently registering.
- [ ] REQ-0.0.66-01-02 [BEHAVIOR]: Given a test target that actually fails, when the RED emit path runs, then a `tdd_red_observed` event is appended with the classified failure kind; given a target that passes on first run, the RED emit path REJECTS it (the pass-on-first-run defect signal). A `@covers`-decorated test asserts both branches.
- [ ] REQ-0.0.66-01-03 [BEHAVIOR]: Given a test target that fails to collect, when the RED emit path runs, then it is classified "infrastructure broken" and rejected — NOT recorded as RED. A `@covers`-decorated test asserts the collection-error rejection.
- [ ] REQ-0.0.66-01-04 [BEHAVIOR]: Given the receipt event models, when instantiated with an unknown field, then `ValidationError` is raised per `ConfigDict(extra="forbid")`; a `@covers`-decorated test asserts the strict-shape rejection on each new event model.
- [ ] REQ-0.0.66-01-05 [SUPPORT]: The new receipt event types validate against their `*_receipt.schema.json` and the registry schema parses — `uv run gz validate --documents` passes and an `artifact_edited` ledger event records the schema addition.
- [ ] REQ-0.0.66-01-06 [STRUCTURAL-FENCE]: The stream is append-only and the ledger remains system-of-record; no code path in this OBPI makes any derived view a write target or source-of-truth. Parent ADR-0.0.66 § Boundary Invariant 3 (ledger-system-of-record / Layer-3-never-source-of-truth) names this invariant.

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
