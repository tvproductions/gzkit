---
id: OBPI-0.36.0-06-risk-tiering
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 6
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/second_opinion_tiering.py
  - data/second_opinion_tiers.json
  - tests/governance/test_second_opinion_tiering.py
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-06-01
  - REQ-0.36.0-06-02
  - REQ-0.36.0-06-03
  - REQ-0.36.0-06-04
  - REQ-0.36.0-06-05
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_tiering -v
  - uv run gz validate --req-kind-discipline
---

# OBPI-0.36.0-06-risk-tiering: Risk Tiering

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #6 - "OBPI-0.36.0-06: **risk-tiering** — A4 narrowed — mandatory for the enumerated consequential categories and explicit operator requests, sampling the routine"

**Status:** Draft

## Objective

Ship the tier resolver that decides **whether the critic fires** — the one
OBPI-04's agent door calls and is forbidden to second-guess. § Target Scope
states the unit definition: *"A4 narrowed: mandatory for the enumerated
consequential categories and for explicit operator requests, sampling the
routine, with the primary agent's own confidence barred from setting the tier."*

The trailing clause is the load-bearing one, and it is a **negative**. The agent
asking for review is the same agent that produced the conclusion under review, so
its confidence is the single input structurally disqualified from setting the
threshold: a critic that fires only when the primary already doubts itself never
fires on the confident-wrong case, and the confident-wrong case is the entire
reason this ADR exists. The operator named that failure directly — *"every
pothole-ridden street seems to have been a marvel of expert engineerin when we
first reviewed the design and implementation"* — and the structural reason for it
— *"can't trust you to be judge|jury|executioner as you unwind through the meander
of an accreting context window."*

A4 carries unusual warrant. § Promotion plan item 3 records it as *"risk tiering
— the one thing both passes independently reached"*: the sole point of agreement
between two cross-family critics that otherwise both returned PERFORATED. It is
also still marked *"live and unruled"* there, which is what this brief closes.

Done looks like three resolvable outcomes — `mandatory`, `sampled-selected`,
`not-selected` — each carrying a recorded reason, produced by a function whose
signature makes a confidence argument *unpassable*. Not ignored; unpassable. A
field that can be passed and silently dropped is a field a future caller will
re-weight; a parameter that does not exist cannot be re-weighted without a
visible signature change.

This brief owns the decision only. It dispatches nothing, renders nothing, and
never mints an envelope: OBPI-05 mints, OBPI-02 transports, OBPI-03/04/09 render.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/second_opinion_tiering.py` — the tier resolver plus the Pydantic model that validates the category registry. Verified convention: flat modules under `src/gzkit/`; siblings in this ADR are `second_opinion.py` (OBPI-01), `second_opinion_transport.py` (OBPI-02), `second_opinion_door.py` (OBPI-03/04), `second_opinion_envelope.py` (OBPI-05).
- `data/second_opinion_tiers.json` — the declared registry of consequential categories and the sampling rate for the routine. Verified convention: `data/` holds JSON registries validated by a Pydantic model in code — `data/flags.json` (`src/gzkit/flags/models.py::FlagSpec`) and `data/security_surfaces.json`, both of which carry a per-entry `rationale`-style justification field.
- `tests/governance/test_second_opinion_tiering.py` — covering tests. Verified convention: `tests/governance/test_*.py`.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

## Denied Paths

- `src/gzkit/second_opinion_door.py` — OBPI-03/04. The doors **call** this resolver. Authoring the door here would let the caller set its own firing threshold, which is the exact inversion OBPI-04's requirement #2 exists to prevent.
- `src/gzkit/second_opinion_envelope.py` — OBPI-05. This resolver **reads** an envelope id as its sampling seed and never mints one.
- `src/gzkit/second_opinion_transport.py`, `src/gzkit/second_opinion.py` — OBPI-02/01. A tier decision is not a dispatch and not a verdict.
- `data/flags.json` — OBPI-09's dark-door switch. A tier rule is not a feature flag, and touching that registry here would light the dark door outside its own brief (Boundary Invariant #3).
- `src/gzkit/cli/**` — no new `gz` verb. The resolver is a library surface.
- `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, any Step-4b gate — Boundary Invariant #1, verbatim operator canon: *"we will NOT alter the OBPI process, at all!"* Step 4b has its own tier order (`_CROSS_VENDOR_ADVERSARY_PREFIXES`, GHI #678); read it, never edit it.
- `.claude/hooks/**`, `.claude/settings.json`, `src/gzkit/hooks/**` — OBPI-09.
- Paths not listed in Allowed Paths
- New dependencies — STDLIB-FIRST: `hashlib` supplies the deterministic sampling seed; `random` is explicitly not used (see requirement #4).
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. NEVER: Accept the primary agent's confidence — self-reported, inferred, or derived — as an input to the tier decision. The public entry point MUST NOT declare a confidence parameter at all, so that a caller attempting to supply one fails loudly rather than having it silently dropped. § Target Scope: *"with the primary agent's own confidence barred from setting the tier."*
2. ALWAYS: Resolve `mandatory` for any decision whose category appears in the registry's consequential set, and for any explicit operator request, **independently of the sampling rate**. A sampling rate of zero must not suppress a mandatory tier; that would make the whole enumerated set a dead letter through one data edit.
3. ALWAYS: Declare the consequential categories in `data/second_opinion_tiers.json`, never as literals in the resolver, and require a per-entry justification naming the canon that makes the category consequential. Verified precedent: every entry in `data/security_surfaces.json` carries a `rationale`; every entry in `data/flags.json` carries `description` plus `owner`. An unjustified category is how a tier list quietly becomes whatever the last editor felt.
4. ALWAYS: Make the routine-sampling decision a **deterministic function of the OBPI-05 envelope id**. Unseeded randomness would make the same decision sample differently on re-run, which destroys OBPI-08's ability to measure false blocks and makes any pilot result unreproducible.
5. ALWAYS: Return a reason with every outcome — which registry entry matched, or that the operator asked, or the sampling draw and the rate it was drawn against. A bare boolean cannot be audited at closeout and cannot be read by OBPI-08.
6. NEVER: Let the registry load with a malformed or unjustified entry. The loader validates through a Pydantic model and rejects, mirroring `FlagSpec`'s category rules (`src/gzkit/flags/models.py`) rather than tolerating a partial registry.
7. NEVER: Add a `gz` verb, wire a hook, edit a door, or modify Step 4b.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above, and § The problem being solved for the operator's statement of the wound this tiering answers.
- [ ] Parent ADR § Target Scope — the `risk-tiering` one-line definition, including the confidence prohibition.
- [ ] Parent ADR § Promotion plan item 3 — A4 recorded as *"the one thing both passes independently reached"* and still *"live and unruled"*. That agreement is the warrant for tier-driven firing; this brief is where it stops being unruled.
- [ ] Parent ADR § Mechanics (measured, not assumed) — the Refinement row: *"we can experimentally refine this moving forward"*. The sampling rate is a calibration dial, not a constant to defend.
- [ ] `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/appendices/A2-codex-verdict-pass1-perforated.txt` — what pass 1 independently said about tiering, in its own words.
- [ ] `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/appendices/A3-codex-verdict-pass2-perforated.txt` — the same for pass 2. Tiering is the one point the two passes reached independently, so their agreement is only legible by reading both.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Behavior Rules — Always #7 — *"<90% sure of direction? Ask the human."* That threshold is agent-self-assessed by design; this resolver is its mechanical counterpart precisely because a self-assessed threshold cannot catch the confident-wrong case.
- [ ] `AGENTS.md` § Defect-fix routing — read the "OBPI ceremony is required when ANY hold" list as a worked example of an *enumerated consequential set with stated thresholds*. It is the in-repo model for what a defensible category list looks like; it is not the list itself.
- [ ] `AGENTS.md` § STDLIB-FIRST DOCTRINE — the registry is plain JSON read with stdlib `json` and validated with the already-named Pydantic departure.
- [ ] `.gzkit/rules/agent-failure-modes.md` — patterns **Metagaming / gaming the gate** and **Skipped cheap verification**. A tier driven by the primary's own confidence is the shape both name.
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — every REQ in this brief is BEHAVIOR; each needs a `@covers` test and has no other proof channel.

**Context:**

- [ ] OBPI-0.36.0-04 — the consumer. Read its requirement #1 (*"The firing decision MUST come from OBPI-06's tier resolution"*) and requirement #2 (the confidence prohibition) before designing this signature; the two briefs state the same fence from opposite sides.
- [ ] OBPI-0.36.0-05 — the envelope whose id seeds sampling. Read REQ-0.36.0-05-01: the id is a deterministic hash, which is what makes requirement #4 achievable without a counter.
- [ ] OBPI-0.36.0-08 — the pilot reads tier outcomes and reasons. A reason string that cannot be aggregated is a measurement this ADR cannot take.
- [ ] OBPI-0.36.0-09 — the dark door will call this same resolver when it is eventually lit. Nothing here may assume an `AskUserQuestion` payload.

**Prerequisites (check existence, STOP if missing):**

- [ ] `data/` exists and holds JSON registries validated by Pydantic models — verified: `data/flags.json`, `data/security_surfaces.json`.
- [ ] `src/gzkit/flags/models.py::FlagSpec` exists and enforces per-category metadata rules — verified; it is the registry-model pattern this brief copies.
- [ ] `src/gzkit/second_opinion_envelope.py` exists (created by OBPI-05) — STOP if missing: without a stable envelope id there is no deterministic sampling seed, and requirement #4 cannot be met.
- [ ] `tests/governance/` exists and holds `test_*.py` — verified.
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion_tiering.py`
- [ ] Required path exists or is intentionally created in this OBPI: `data/second_opinion_tiers.json`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_tiering.py`

**Existing Code (understand current state):**

- [ ] `src/gzkit/flags/models.py::FlagSpec` — read the `model_config = ConfigDict(frozen=True, extra="forbid")` and the `_enforce_category_rules` model validator. This is the in-repo answer to requirement #6: a registry whose invalid states are unrepresentable rather than reviewed.
- [ ] `src/gzkit/flags/registry.py::load_registry` — read the load-and-reject path, including duplicate-key detection, before writing the tier registry loader.
- [ ] `data/security_surfaces.json` — read the per-entry `rationale` convention that requirement #3 adopts, and note that the file is a flat JSON array of category objects.
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py:47-71` — read `ADVERSARY_VERDICTS` and `_CROSS_VENDOR_ADVERSARY_PREFIXES` **read-only**. Step 4b already encodes a tier order and an explicit allowlist that fails CLOSED on an unrecognized adversary; borrow the shape, never the file. Boundary Invariant #1.

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
uv run -m unittest tests.governance.test_second_opinion_tiering -v
uv run gz validate --req-kind-discipline
uv run gz validate --pydantic-models
uv run gz covers
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The declared registry: every consequential category with its justification,
# plus the sampling rate for the routine.
uv run python -m gzkit.second_opinion_tiering registry

# A consequential decision resolves mandatory, and says which entry matched.
uv run python -m gzkit.second_opinion_tiering resolve --category dependency-addition --envelope-id 3f2b91c07d4e5a68

# The same decision with sampling forced to zero still resolves mandatory —
# a data edit cannot silence the enumerated set (REQ-06-01).
uv run python -m gzkit.second_opinion_tiering resolve --category dependency-addition --envelope-id 3f2b91c07d4e5a68 --sampling-rate 0.0

# An explicit operator request resolves mandatory on a routine category.
uv run python -m gzkit.second_opinion_tiering resolve --category routine-edit --envelope-id 3f2b91c07d4e5a68 --operator-requested

# A routine decision samples deterministically from the envelope id: run it
# twice, get the same outcome and the same reason.
uv run python -m gzkit.second_opinion_tiering resolve --category routine-edit --envelope-id 3f2b91c07d4e5a68
uv run python -m gzkit.second_opinion_tiering resolve --category routine-edit --envelope-id 3f2b91c07d4e5a68

# Passing a confidence value is refused by the signature, not weighted (REQ-06-04).
uv run python -m gzkit.second_opinion_tiering resolve --category routine-edit --envelope-id 3f2b91c07d4e5a68 --confidence 0.95

# The verdict the tier decision leads to, dispatched cross-family.
uv run gz arb step --name adversary -- codex exec --sandbox read-only "Refute: a second-opinion tier may be set by the primary agent's own confidence."
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.36.0-06-01 [BEHAVIOR]: Given a decision whose category is in the registry's consequential set, when the tier is resolved, then the outcome is `mandatory` and its reason names the matched registry entry — and it remains `mandatory` with the sampling rate set to zero, so no rate edit can suppress the enumerated set.
- [ ] REQ-0.36.0-06-02 [BEHAVIOR]: Given an explicit operator request on a routine category, when the tier is resolved, then the outcome is `mandatory` and its reason records that the operator asked — an operator request never routes through the sampler.
- [ ] REQ-0.36.0-06-03 [BEHAVIOR]: Given a routine category and one envelope id, when the tier is resolved repeatedly, then the outcome and reason are identical every time, and across a spread of distinct envelope ids the selected proportion tracks the registry's declared rate — an unseeded draw fails both halves.
- [ ] REQ-0.36.0-06-04 [BEHAVIOR]: Given a caller that supplies a confidence value to the public tier entry point, when the call is made, then it raises rather than resolving a tier — the parameter does not exist, so confidence cannot be weighted or silently dropped.
- [ ] REQ-0.36.0-06-05 [BEHAVIOR]: Given a `data/second_opinion_tiers.json` entry missing its justification, carrying a duplicate category key, or declaring a sampling rate outside 0.0–1.0, when the registry is loaded, then the load raises naming the offending entry and no tier resolves from a partially valid registry.

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
