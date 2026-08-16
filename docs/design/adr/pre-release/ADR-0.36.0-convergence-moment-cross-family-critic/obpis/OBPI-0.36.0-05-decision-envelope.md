---
id: OBPI-0.36.0-05-decision-envelope
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 5
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/second_opinion_envelope.py
  - src/gzkit/schemas/second_opinion_envelope.json
  - tests/governance/test_second_opinion_envelope.py
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-05-01
  - REQ-0.36.0-05-02
  - REQ-0.36.0-05-03
  - REQ-0.36.0-05-04
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_envelope -v
  - uv run gz validate --req-kind-discipline
---

# OBPI-0.36.0-05-decision-envelope: Decision Envelope

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #5 - "OBPI-0.36.0-05: **decision-envelope** — A3 narrowed to one decision-scoped envelope carrying prompt hash, scope manifest and primary-output hash — the strong subject binding both adversary passes recorded as unbuilt"

**Status:** Draft

## Objective

Give the critic a **subject that cannot be swapped**. Ship one decision-scoped
envelope — prompt hash, scope manifest, primary-output hash — minted before the
critic is dispatched and re-checked before the verdict is rendered, so that the
thing the critic argued about is provably the thing the operator is about to
decide.

§ Target Scope states the unit definition: *"A3 narrowed to one decision-scoped
envelope carrying prompt hash, scope manifest and primary-output hash — the
strong subject binding both adversary passes recorded as explicitly unbuilt."*
That last clause is why this brief exists rather than being folded into a door.
§ Promotion plan #3 carries the same finding forward as owed work: *"the
mechanism-hardening list (strong subject binding, deterministic checks first)
remain live and unruled."* Two independent critics reached the same gap, and
neither verdict has been answered.

The failure it closes is precise and quiet. Without an envelope, "the decision"
is whatever prose the primary agent chose to hand the transport, and
nothing downstream can tell a critic that reviewed the operator's actual choice
from a critic that reviewed a friendlier paraphrase of it. That is the ADR's own
wound one level down — *"can't trust you to be judge|jury|executioner as you
unwind through the meander of an accreting context window"* — applied to the
subject rather than the judgment. A critic pointed at a softened subject returns
a sound verdict about the wrong thing, and the verdict reads clean.

**Decision-scoped, never session-scoped.** § Why nine records the State Anchor
split that produced this unit: *"The envelope is durable state with a hash
contract; a door is a stateless entry point. Bundling them would anchor a schema
to an invocation path."* One session presents many decisions; each mints its own
envelope, and an envelope carries no session identifier. A session-scoped
envelope would re-introduce exactly the accreting-context subject this closes.

This brief ships the envelope and its hash contract only. It dispatches nothing:
the transport is OBPI-02's, the verdict shape is OBPI-01's, and the doors that
mint envelopes are OBPI-03, OBPI-04 and OBPI-09.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/second_opinion_envelope.py` — the envelope model, its hash contract, and the on-disk store. Verified convention: flat modules under `src/gzkit/`; siblings in this ADR are `second_opinion.py` (OBPI-01) and `second_opinion_transport.py` (OBPI-02).
- `src/gzkit/schemas/second_opinion_envelope.json` — the JSON Schema pinning the three-hash shape. Verified convention: `src/gzkit/schemas/` holds `.json` schema files (`adr.json`, `ledger.json`, `obpi_brief_structure.json`); OBPI-01 lands `second_opinion_verdict.json` in the same directory.
- `tests/governance/test_second_opinion_envelope.py` — covering tests. Verified convention: `tests/governance/test_*.py`.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

The envelope **store root** is resolved in code the way `gzkit.arb.paths.receipts_root()`
resolves receipts — a configured root, created on demand, defaulting under the
git-ignored `artifacts/` tree. It is runtime state, not a committed surface, and
therefore appears in no allowlist. Read `src/gzkit/arb/paths.py` before writing
the resolver; do not hardcode a literal path.

## Denied Paths

- `src/gzkit/second_opinion.py`, `src/gzkit/schemas/second_opinion_verdict.json` — OBPI-01 owns the verdict shape. This envelope is the *subject* of a verdict, never the verdict.
- `src/gzkit/second_opinion_transport.py` — OBPI-02. The envelope is minted before dispatch and read after; it never shells out.
- `src/gzkit/second_opinion_door.py` — OBPI-03/04. § Why nine split the envelope out of the doors precisely so a schema is not anchored to an invocation path; re-entering the door module would undo that split.
- `src/gzkit/arb/**` — read-only reference for the store-root pattern. A registered security surface (`data/security_surfaces.json`, category `arb_receipt_chain`); editing it here would also make this brief `sensitivity: security` for no gain.
- `src/gzkit/cli/**` — no new `gz` verb. The envelope is a library surface consumed by the doors.
- `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, any Step-4b gate — Boundary Invariant #1, verbatim operator canon: *"we will NOT alter the OBPI process, at all!"*
- `.claude/hooks/**`, `.claude/settings.json`, `src/gzkit/hooks/**` — OBPI-09's dark adapter (Boundary Invariant #3).
- Paths not listed in Allowed Paths
- New dependencies — STDLIB-FIRST: `hashlib` and `json` supply the hash contract; Pydantic is the already-named departure for the model.
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. ALWAYS: An envelope MUST carry all three components — prompt hash, scope manifest, primary-output hash. A two-of-three envelope is invalid, not partial; the schema is the fence, exactly as OBPI-01's verdict schema fences the two mandatory questions.
2. ALWAYS: Hashing MUST be deterministic over canonicalized input — same prompt text, same scope manifest, same primary output yield the same envelope id on any machine, at any time. A non-deterministic id cannot detect a swapped subject, which is the only thing this unit exists to do.
3. NEVER: Admit a session identifier, transcript path, or invocation-path field into the envelope. The unit is **decision**-scoped (§ Why nine, State Anchor split). A session field would let one envelope cover several decisions and silently restore the accreting-context subject.
4. ALWAYS: The scope manifest MUST name the surfaces the critic was pointed at *with a content hash per path*, so that "the critic read the raw surface" is checkable rather than asserted. Operator verbatim, § The critic must reach the raw surface itself: *"Of course it would be directed to explore the raw surface."*
5. ALWAYS: Re-check the primary-output hash before a verdict is rendered to the operator. If the primary's conclusion changed after the envelope was minted, the verdict no longer binds to what the operator sees and MUST NOT be presented as if it does.
6. NEVER: Let a verdict be rendered against an envelope id it does not carry. A verdict with a mismatched or absent envelope id is refused, not rendered with a caveat — a caveat is exactly the "softened into something more comfortable" failure the ADR's persona names.
7. NEVER: Add a `gz` verb, edit OBPI-01/02/03/04 surfaces, wire a hook, or modify Step 4b.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Target Scope — the `decision-envelope` one-line definition, and the staging paragraph that names strong subject binding as *"unbuilt"*.
- [ ] Parent ADR § Why nine, and where the Matrix of Four forced a split — the **State Anchor** bullet is this brief's charter: *"Bundling them would anchor a schema to an invocation path."*
- [ ] Parent ADR § Promotion plan item 3 — A3 and the mechanism-hardening list *"remain live and unruled"*; this brief discharges the A3 half.
- [ ] `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/appendices/A2-codex-verdict-pass1-perforated.txt` — what pass 1 actually said about subject binding, in its own words.
- [ ] `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/appendices/A3-codex-verdict-pass2-perforated.txt` — the same for pass 2. § Appendices is explicit that where the ADR's prose and an appendix disagree, **the appendix governs** — so read these before treating any prose summary of the subject-binding critique as settled.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § STDLIB-FIRST DOCTRINE — `hashlib` is the answer to "which hash"; a third-party hashing dependency here needs a named departure and does not have one.
- [ ] `.gzkit/rules/models.md` — Pydantic is the named departure for validation semantics; the envelope model follows it rather than `@dataclass` (`gz validate --pydantic-models`).
- [ ] `.gzkit/rules/agent-failure-modes.md` — pattern **Skipped cheap verification**. Re-checking a hash before rendering is the cheap verification this unit adds; skipping it is the named failure.
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — this brief's REQs are all BEHAVIOR; each needs a `@covers` test and there is no other proof channel for them.

**Context:**

- [ ] OBPI-0.36.0-01 — the verdict shape that will carry this envelope's id. Read `REQ-0.36.0-01-04`: the verdict vocabulary is pinned to `events.py::adversarial_validation`, so the envelope must not invent a second spelling of anything it shares.
- [ ] OBPI-0.36.0-03 and OBPI-0.36.0-04 — the doors that will mint envelopes. Confirm the mint/read API is callable from both without either door owning state.
- [ ] OBPI-0.36.0-06 — the tier resolver seeds its sampling decision from the envelope id. The id must therefore be stable and uniformly distributed; a sequential counter would bias sampling.
- [ ] OBPI-0.36.0-08 — the pilot's *decisions changed* measurement is computed from the primary-output hash before and after the critic ran. That consumer is the reason requirement #5 re-checks rather than merely records.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/schemas/` exists and holds `.json` schema files — verified: `src/gzkit/schemas/ledger.json`, `src/gzkit/schemas/adr.json`.
- [ ] `src/gzkit/arb/paths.py` exists and exposes `receipts_root()` — verified; it is the store-root resolution pattern this module copies.
- [ ] `tests/governance/` exists and holds `test_*.py` — verified.
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion_envelope.py`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/schemas/second_opinion_envelope.json`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_envelope.py`

**Existing Code (understand current state):**

- [ ] `src/gzkit/arb/paths.py::receipts_root` — read the full resolution order (env override → config → default under `artifacts/`) and the `mkdir(parents=True, exist_ok=True)` on-demand creation. The envelope store copies this shape; do not hardcode `artifacts/`.
- [ ] `src/gzkit/schemas/ledger.json` — read for the in-repo JSON Schema authoring conventions (`$schema`, `additionalProperties`, `required`) before writing `second_opinion_envelope.json`.
- [ ] `src/gzkit/events.py::_EventBase` — read the `model_config = ConfigDict(frozen=True, extra="forbid")` pattern. A frozen, extra-forbidding envelope model is what makes requirement #3 structural rather than advisory.
- [ ] `data/security_surfaces.json` — read the `crypto_primitives` globs (`src/gzkit/**/*hash*.py`). This module deliberately is **not** named `*hash*.py`: it is an envelope with a hash field, not a crypto primitive, and a name that trips the glob would force `sensitivity: security` on a brief that handles no secret.

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
uv run -m unittest tests.governance.test_second_opinion_envelope -v
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
# Mint an envelope for a real decision: the prompt, the two surfaces the critic
# is pointed at, and the primary's conclusion. Prints the envelope id and the
# three hashes.
uv run python -m gzkit.second_opinion_envelope mint --prompt "Should the second-opinion store live under artifacts/ or under .gzkit/?" --scope src/gzkit/arb/paths.py --scope src/gzkit/config.py --primary-output "Recommend artifacts/, matching receipts_root()."

# Mint the identical decision again. Same envelope id — determinism (REQ-05-01).
uv run python -m gzkit.second_opinion_envelope mint --prompt "Should the second-opinion store live under artifacts/ or under .gzkit/?" --scope src/gzkit/arb/paths.py --scope src/gzkit/config.py --primary-output "Recommend artifacts/, matching receipts_root()."

# Change one byte of the primary's conclusion. Different envelope id — the swap
# the critic would otherwise never see.
uv run python -m gzkit.second_opinion_envelope mint --prompt "Should the second-opinion store live under artifacts/ or under .gzkit/?" --scope src/gzkit/arb/paths.py --scope src/gzkit/config.py --primary-output "Recommend .gzkit/, matching receipts_root()."

# Re-check the most recent envelope against the current tree. Reports which
# scope-manifest paths have drifted since minting.
uv run python -m gzkit.second_opinion_envelope recheck --latest

# Dispatch the critic with the envelope id carried as the subject, so the
# returned verdict binds to a specific decision rather than to a paraphrase.
uv run gz arb step --name adversary -- codex exec --sandbox read-only "Refute, against src/gzkit/arb/paths.py: the second-opinion envelope store should default under artifacts/ rather than .gzkit/."
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.36.0-05-01 [BEHAVIOR]: Given the same prompt text, scope manifest and primary output, when an envelope is minted twice, then both envelopes carry an identical id and identical component hashes — and given any single byte changed in any one of the three components, then the id differs. A minting path that is not a pure function of its three inputs fails.
- [ ] REQ-0.36.0-05-02 [BEHAVIOR]: Given a verdict whose envelope id does not match the envelope of the decision being rendered, when rendering is attempted, then it is refused and no verdict text reaches the operator — a mismatched subject is never rendered with a caveat.
- [ ] REQ-0.36.0-05-03 [BEHAVIOR]: Given an envelope payload carrying a session identifier, transcript path, or any invocation-path field, when it is validated against `second_opinion_envelope.json`, then validation fails naming the offending field — the envelope is decision-scoped and the schema, not a convention, is what keeps it so.
- [ ] REQ-0.36.0-05-04 [BEHAVIOR]: Given an envelope minted against a scope manifest, when the primary-output hash or any manifest path's content hash is re-checked after the referenced file has changed, then the drift is reported per path and the envelope resolves stale — a re-check that reports clean on drifted content fails.

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
